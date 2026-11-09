import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print( "BASE_DIR=", BASE_DIR )

LIB_DIR = BASE_DIR / "libs"
print( "LIB_DIR=", LIB_DIR )

sys.path.insert( 0, str( LIB_DIR ) )

from rpi_lcd import LCD
import paho.mqtt.client as mqtt
import paho.mqtt as paho

lcd = LCD()

def on_connect( client, userdata, flags, rc, properties=None ):

    if rc == 0:
        print( "MQTT 브로커 연결 성공")
        client.subscribe( "raspberry/esp32_distance" )

    else:
        print( f"연결 실패, 에러 코드:{rc}" )

def on_message( clinet, userdata, msg ):
    topic = msg.topic
    payload = msg.payload.decode( "utf-8" )

    print( f"[수신] 토픽: {topic} | 데이터: {payload} cm" )
    lcd.text( "Distance:", 1 )
    lcd.text( f"{payload} cm", 2 )

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

broker_address = "localhost"
port = 1883

print( "MQTT 브로커에 연결 시도 중..." )
client.connect( broker_address, port, keepalive=60 )

try:
    print( "LCD에 초음파 모듈로 받은 거리 출력 중\n" )
    """
    while True:
        lcd.text( "Distance:", 1 )
        print( f"{ msg.payload.decode("utf-8"}" )
        lcd.text( f"{payload}", 2 )
"""
except KeyboardInterrupt:
    lcd.clear()

finally:
    lcd.clear()

client.loop_forever()

lcd.clear()
