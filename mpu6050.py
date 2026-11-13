"""MPU-6050 / MPU-6500 계열 6축 센서(가속도 + 자이로 + 온도) 드라이버.

라즈베리 파이의 I2C 버스에서 smbus2로 센서 값을 읽는다.
다른 파일에서 `from mpu6050 import MPU6050` 으로 가져다 쓸 수 있다.

Claude에서 수정받음
"""
import struct
import time

import smbus2

# ---- 레지스터 주소 (데이터시트 Register Map 기준) ----
REG_SMPLRT_DIV = 0x19      # 샘플링 속도 분주기
REG_CONFIG = 0x1A          # 자이로/온도용 디지털 저역 통과 필터(DLPF) 설정
REG_GYRO_CONFIG = 0x1B     # 자이로 풀스케일 범위
REG_ACCEL_CONFIG = 0x1C    # 가속도 풀스케일 범위
REG_ACCEL_CONFIG2 = 0x1D   # 가속도 전용 DLPF 설정 (MPU-6500/9250/9255에만 있음)
REG_DATA_START = 0x3B      # ACCEL_XOUT_H (가속도 6B + 온도 2B + 자이로 6B = 14B 연속)
REG_PWR_MGMT_1 = 0x6B      # 전원 관리 (슬립 해제, 클럭 선택)
REG_WHO_AM_I = 0x75        # 칩 종류를 알려주는 고정 ID

# WHO_AM_I 값별 칩 정보: (이름, 온도 감도[LSB/°C], 온도 오프셋[°C])
# 칩마다 온도 변환 공식이 달라서 칩을 먼저 알아내야 한다.
#   MPU-6050 : °C = raw / 340    + 36.53
#   MPU-6500 / 9250 / 9255 : °C = raw / 333.87 + 21.0
CHIP_INFO = {
    0x68: ("MPU-6050", 340.0, 36.53),
    0x70: ("MPU-6500", 333.87, 21.0),
    0x71: ("MPU-9250", 333.87, 21.0),
    0x73: ("MPU-9255", 333.87, 21.0),
}
UNKNOWN_CHIP = ("알 수 없음", 340.0, 36.53)   # 표에 없으면 MPU-6050 공식으로 대체

# ACCEL_CONFIG2(0x1D)가 있는 칩. MPU-6050은 가속도 필터를 CONFIG의 DLPF와 공유한다.
HAS_ACCEL_DLPF = {0x70, 0x71, 0x73}

# 풀스케일 설정값(0~3)별 감도 (LSB per g / LSB per dps)
# 범위를 넓힐수록 측정 가능한 최대값은 커지고 해상도(감도)는 낮아진다.
ACCEL_SCALE = {0: 16384.0, 1: 8192.0, 2: 4096.0, 3: 2048.0}   # ±2/4/8/16 g
GYRO_SCALE = {0: 131.0, 1: 65.5, 2: 32.8, 3: 16.4}            # ±250/500/1000/2000 dps


class MPU6050:
    """센서 한 개를 다루는 클래스.

    accel_fs, gyro_fs : 풀스케일 범위 선택(0~3). 값의 의미는 위 SCALE 표 참고.
    dlpf              : 자이로/온도 필터 (0~6, 클수록 대역폭이 좁고 노이즈가 적음)
    accel_dlpf        : 가속도 필터 (0~7, MPU-6500 계열에서만 적용)
    sample_div        : 샘플링 속도 분주기 (속도 = 내부 출력 속도 / (1 + sample_div))
    """

    def __init__(self, bus_num=1, addr=0x68, accel_fs=0, gyro_fs=0,
                 dlpf=0, accel_dlpf=0, sample_div=0):
        self.bus = smbus2.SMBus(bus_num)   # 라즈베리 파이는 보통 1번 버스
        self.addr = addr
        self.accel_lsb = ACCEL_SCALE[accel_fs]   # raw 값을 g로 바꿀 때 나눌 값
        self.gyro_lsb = GYRO_SCALE[gyro_fs]      # raw 값을 dps로 바꿀 때 나눌 값
        self.gyro_offset = (0.0, 0.0, 0.0)       # calibrate_gyro()로 채워지는 보정값

        # WHO_AM_I로 실제 칩을 확인하고 온도 공식을 결정
        # (보드에 MPU-6050이라 적혀 있어도 실제로는 다른 칩일 수 있다)
        self.who_am_i = self.bus.read_byte_data(addr, REG_WHO_AM_I)
        if self.who_am_i not in CHIP_INFO:
            print(f"경고: 알 수 없는 WHO_AM_I 값 0x{self.who_am_i:02X} "
                  f"- 온도는 MPU-6050 공식으로 계산합니다.")
        self.chip_name, self.temp_sens, self.temp_offset = CHIP_INFO.get(
            self.who_am_i, UNKNOWN_CHIP)

        # 슬립 해제 + 자이로 X축 PLL 클럭 사용 (내부 8MHz RC보다 안정적)
        # 전원을 켜면 센서는 슬립 상태라서 이 설정을 해야 측정이 시작된다.
        self.bus.write_byte_data(addr, REG_PWR_MGMT_1, 0x01)
        time.sleep(0.05)   # 슬립 해제 후 센서가 안정될 때까지 잠시 대기

        # 풀스케일 선택 비트는 레지스터의 bit4:3 위치라서 3칸 왼쪽으로 민다
        self.bus.write_byte_data(addr, REG_ACCEL_CONFIG, accel_fs << 3)
        self.bus.write_byte_data(addr, REG_GYRO_CONFIG, gyro_fs << 3)
        self.set_dlpf(dlpf)
        self.set_accel_dlpf(accel_dlpf)
        self.bus.write_byte_data(addr, REG_SMPLRT_DIV, sample_div)

    def set_dlpf(self, cfg):
        """자이로/온도용 저역 통과 필터 설정. 0이면 필터가 거의 없고(빠르지만 노이즈 많음),
        6이면 약 5Hz로 강하게 거른다(부드럽지만 반응이 느림)."""
        cfg = max(0, min(6, cfg))   # 유효 범위(0~6)로 제한
        cur = self.bus.read_byte_data(self.addr, REG_CONFIG)
        # 하위 3비트(DLPF_CFG)만 바꾸고 나머지 비트는 기존 값을 유지한다
        self.bus.write_byte_data(self.addr, REG_CONFIG, (cur & 0xF8) | cfg)

    def set_accel_dlpf(self, cfg):
        """가속도 전용 저역 통과 필터 설정 (MPU-6500/9250/9255).
        cfg(A_DLPF_CFG) -> 대역폭: 0/1=218.1Hz, 2=99Hz, 3=44.8Hz, 4=21.2Hz,
                                   5=10.2Hz, 6=5.05Hz, 7=420Hz
        accel_fchoice_b 비트(bit3)는 0으로 두어 필터를 활성화한다.
        MPU-6050처럼 이 레지스터가 없는 칩에서는 아무것도 하지 않는다."""
        if self.who_am_i not in HAS_ACCEL_DLPF:
            if cfg:   # 0이 아닌 값을 요청했는데 무시되는 경우만 알려준다
                print(f"{self.chip_name}에는 가속도 전용 DLPF가 없어 설정을 건너뜁니다.")
            return False
        cfg = max(0, min(7, cfg))
        self.bus.write_byte_data(self.addr, REG_ACCEL_CONFIG2, cfg)
        return True

    def read(self):
        """한 번의 I2C 트랜잭션(14바이트)으로 모든 값을 읽는다.
        반환: (ax, ay, az) [g], temp [°C], (gx, gy, gz) [dps, 오프셋 보정 적용]

        가속도/온도/자이로를 따로 읽지 않고 연속된 14바이트를 한 번에 읽으면
        I2C 통신 횟수가 줄고, 모든 값이 같은 시점의 샘플이 된다."""
        raw = self.bus.read_i2c_block_data(self.addr, REG_DATA_START, 14)
        # ">7h": big-endian(상위 바이트 먼저) 부호 있는 16비트 정수 7개
        # 순서: 가속도 X,Y,Z / 온도 / 자이로 X,Y,Z
        ax, ay, az, t, gx, gy, gz = struct.unpack(">7h", bytes(raw))

        a = self.accel_lsb
        g = self.gyro_lsb
        ox, oy, oz = self.gyro_offset
        return (
            (ax / a, ay / a, az / a),               # raw -> g
            t / self.temp_sens + self.temp_offset,  # 칩별 온도 공식
            (gx / g - ox, gy / g - oy, gz / g - oz),  # raw -> dps 후 오프셋 제거
        )

    def calibrate_gyro(self, samples=200, delay=0.002):
        """정지 상태에서 자이로 평균값을 오프셋으로 저장.
        자이로는 가만히 있어도 0이 아닌 값을 내므로, 센서를 움직이지 않은 채 호출해야 한다."""
        # read()가 기존 오프셋을 빼므로, 평균을 구하기 전에 반드시 0으로 초기화한다
        self.gyro_offset = (0.0, 0.0, 0.0)
        sx = sy = sz = 0.0
        for _ in range(samples):
            _, _, (gx, gy, gz) = self.read()
            sx += gx
            sy += gy
            sz += gz
            time.sleep(delay)   # 연속 샘플이 같은 값으로 겹치지 않도록 약간의 간격
        self.gyro_offset = (sx / samples, sy / samples, sz / samples)
        return self.gyro_offset

    def close(self):
        """I2C 버스를 닫는다."""
        self.bus.close()


def main(count=100, period=0.05):
    """단독 실행용 테스트: count번 읽어서 화면에 출력한다."""
    mpu = MPU6050(dlpf=0)
    try:
        print(f"WHO_AM_I: 0x{mpu.who_am_i:02X} -> {mpu.chip_name}")
        ox, oy, oz = mpu.calibrate_gyro()
        print(f"gyro offset: x={ox:.2f}, y={oy:.2f}, z={oz:.2f}")

        # sleep 누적 오차를 피하기 위해 절대 시각 기준으로 주기를 맞춤
        next_t = time.perf_counter()
        for i in range(1, count + 1):
            (ax, ay, az), temp, (gx, gy, gz) = mpu.read()
            print(f"[{i}] Ax={ax:.2f} Ay={ay:.2f} Az={az:.2f} "
                  f"T={temp:.2f} Gx={gx:.2f} Gy={gy:.2f} Gz={gz:.2f}")
            next_t += period
            time.sleep(max(0.0, next_t - time.perf_counter()))
    finally:
        mpu.close()   # 중간에 오류가 나도 버스는 항상 닫는다


# 이 파일을 직접 실행할 때만 main()이 돌고, import 할 때는 실행되지 않는다
if __name__ == "__main__":
    main()