"""mpu6050.py 의 MPU6050 클래스를 import 해서 센서 값을 MQTT 로 publish 한다.

실행 예:
    python3 mpu6050_mqtt.py --host 192.168.0.10 --topic sensors/mpu/data --rate 20

Claude가 작성해줌. 추후 코듣 분석 필요.
"""

# 매번 버츄얼 환경을 읽어오는 게 귀찮아서, 로컬 라이브러리를 읽어오도록 하는 local_library.py를 import 함.
import local_library

# argpare는 파일 뒤에 arguments를 붙여서 실행할 때, 그 arguments를 읽어오는 모듈임
import argparse
import json
import signal
import time

import paho.mqtt.client as mqtt

from mpu6050 import MPU6050


def make_client(client_id):
    """paho-mqtt 2.x / 1.x 모두 지원.
    2.x부터는 Client를 만들 때 콜백 API 버전을 반드시 지정해야 해서, 실패하면 1.x 방식으로 만든다."""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:          # paho-mqtt 1.x
        return mqtt.Client(client_id=client_id)


def parse_args():
    """명령줄 옵션을 읽는다. 코드를 고치지 않고 브로커 주소 등을 바꿀 수 있다."""
    # 프로그램 실행 후에 argument를 읽어오는 방식도 있지만, 쉘에서 실행할 때에는 argument를 붙이는 편이 더 편할 것 같다.
    p = argparse.ArgumentParser(description="MPU 센서 값을 MQTT 로 publish")
    # 
    p.add_argument("--host", default="ptjoker95MacPro.local", help="브로커 주소")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--topic", default="sensors/mpu/data", help="데이터 토픽")
    p.add_argument("--client-id", default="mpu-rpi")   # 브로커가 클라이언트를 구분하는 이름
    p.add_argument("--user", default=None)
    p.add_argument("--password", default=None)
    p.add_argument("--rate", type=float, default=20.0, help="초당 publish 횟수(Hz)")
    p.add_argument("--dlpf", type=int, default=0, help="자이로/온도 DLPF (0~6)")
    p.add_argument("--accel-dlpf", type=int, default=0,
                   help="가속도 DLPF (0~7, MPU-6500 계열만 적용)")
    return p.parse_args()


def main():
    args = parse_args()
    status_topic = f"{args.topic}/status"   # online/offline 상태를 알리는 토픽
    # 콜백(별도 스레드)과 메인 루프가 함께 보는 상태값
    state = {"connected": False, "running": True}

    # ---- MQTT 설정 ----
    client = make_client(args.client_id)
    if args.user:
        client.username_pw_set(args.user, args.password)
    # 비정상 종료 시 브로커가 대신 "offline" 을 알려준다 (Last Will)
    client.will_set(status_topic, "offline", qos=1, retain=True)
    # 연결이 끊기면 1초부터 시작해 최대 30초 간격으로 재연결을 시도한다
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(client, userdata, flags, reason_code, properties=None):
        # 1.x는 reason_code가 정수(0이 성공), 2.x는 객체(is_failure로 판단)라서 둘 다 처리
        ok = (reason_code == 0) or (getattr(reason_code, "is_failure", None) is False)
        state["connected"] = ok
        print(f"MQTT 연결 {'성공' if ok else '실패'}: {reason_code}")
        if ok:
            # retain=True: 나중에 구독을 시작한 쪽도 현재 상태를 바로 받는다
            client.publish(status_topic, "online", qos=1, retain=True)

    def on_disconnect(client, userdata, *rest):
        # 버전마다 인자 개수가 달라서 *rest로 받는다
        state["connected"] = False
        print("MQTT 연결 끊김 (자동 재연결 시도)")

    def on_connect_fail(client, userdata):
        # 브로커에 접속조차 못 했을 때 호출된다 (주소 오류, 포트 닫힘, 방화벽 등)
        print(f"MQTT 연결 시도 실패: {args.host}:{args.port} "
              f"(주소, 포트, 브로커의 listener 설정, 방화벽을 확인하세요)")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_connect_fail = on_connect_fail

    # connect_async: 연결이 안 돼도 여기서 멈추지 않고 백그라운드에서 계속 시도한다
    client.connect_async(args.host, args.port, keepalive=30)
    client.loop_start()             # 네트워크 처리와 재연결은 별도 스레드가 담당

    # ---- 센서 설정 ----
    mpu = MPU6050(dlpf=args.dlpf, accel_dlpf=args.accel_dlpf)
    print(f"칩: {mpu.chip_name} (WHO_AM_I=0x{mpu.who_am_i:02X})")
    ox, oy, oz = mpu.calibrate_gyro()   # 시작 시 센서를 움직이지 말 것
    print(f"gyro offset: x={ox:.2f}, y={oy:.2f}, z={oz:.2f}")

    # Ctrl+C / kill 로 깨끗하게 종료
    # 시그널 핸들러에서는 플래그만 바꾸고, 실제 정리는 아래 finally에서 한다
    def stop(signum, frame):
        state["running"] = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    period = 1.0 / args.rate          # 한 번 publish하는 간격(초)
    next_t = time.perf_counter()      # 다음 샘플을 보낼 목표 시각
    sent = 0                          # 지금까지 publish한 개수
    last_report = next_t              # 마지막으로 상태를 출력한 시각
    try:
        while state["running"]:
            (ax, ay, az), temp, (gx, gy, gz) = mpu.read()

            # 연결이 안 된 동안에는 publish를 건너뛴다 (샘플은 버려짐)
            if state["connected"]:
                payload = json.dumps({
                    "ts": int(time.time() * 1000),                 # epoch ms
                    "accel": {"x": round(ax, 4), "y": round(ay, 4), "z": round(az, 4)},   # g
                    "gyro": {"x": round(gx, 3), "y": round(gy, 3), "z": round(gz, 3)},    # dps
                    "temp": round(temp, 2),                        # °C
                }, separators=(",", ":"))   # 공백 없이 압축해서 메시지 크기를 줄인다
                # qos=0: 최신 값이 중요한 센서 스트림이라 재전송 없이 보낸다
                client.publish(args.topic, payload, qos=0)
                sent += 1

            # 5초마다 연결 상태와 전송 건수를 출력 (조용히 멈춘 것처럼 보이지 않도록)
            now = time.perf_counter()
            if now - last_report >= 5.0:
                print(f"[상태] 연결={'O' if state['connected'] else 'X'}, "
                      f"지금까지 publish {sent}건")
                last_report = now

            # 읽는 데 걸린 시간만큼 빼고 쉬어서 주기를 일정하게 유지한다
            next_t += period
            time.sleep(max(0.0, next_t - time.perf_counter()))
    finally:
        # 정상 종료할 때 "offline"을 직접 알리고 (최대 2초 대기) 연결을 정리한다
        if state["connected"]:
            info = client.publish(status_topic, "offline", qos=1, retain=True)
            info.wait_for_publish(timeout=2)
        client.loop_stop()
        client.disconnect()
        mpu.close()
        print("종료")


# 이 파일을 직접 실행할 때만 main()이 돈다
if __name__ == "__main__":
    main()
