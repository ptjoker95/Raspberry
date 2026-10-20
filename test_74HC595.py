import time
import RPi.GPIO as GPIO

# 사용할 GPIO 번호를 지정한다.
DATAPIN = 17
CLOCKPIN = 27
LATCHPIN = 22

GPIO.setmode( GPIO.BCM )
GPIO.setup( DATAPIN, GPIO.OUT )
GPIO.setup( CLOCKPIN, GPIO.OUT )
GPIO.setup( LATCHPIN, GPIO.OUT )

def SHCP_get_data():
    GPIO.output( CLOCKPIN, GPIO.HIGH )
    GPIO.output( CLOCKPIN, GPIO.LOW )

def STCP_latch():
    GPIO.output( LATCHPIN, GPIO.HIGH )
    GPIO.output( LATCHPIN, GPIO.LOW )

def shift_out( data ):
    GPIO.output( LATCHPIN, GPIO.LOW )

    for i in range(8):
        bit = ( data >> ( 7 - i )) & 1
        GPIO.output( DATAPIN, bit )

        SHCP_get_data()

    STCP_latch()


try:
    print( "74HC595 러닝 라이트 테스트 시작 ( 종료하려면 Ctrl+C )|" )

    while True:
        for i in range(8):
               pattern = 1 << i
               shift_out( pattern )
               time.sleep( 0.15 )

        for i in range( 6, 0, -1 ):
               pattern = 1 << i
               shift_out( pattern )
               time.sleep( 0.15 )

except KeyboardInterrupt:
    shift_out( 0x00 )
    GPIO.cleanup()
    print( "\n테스트 종료 및 GPIO 설정 초기화 완료" )
