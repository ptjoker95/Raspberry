import RPi.GPIO as GPIO
import time

LATCH = 22 # ST_CP
CLOCK = 27 # SH_CP
DATA = 17 # DS

GPIO.setmode( GPIO.BCM )
GPIO.setup( LATCH, GPIO.OUT )
GPIO.setup( CLOCK, GPIO.OUT )
GPIO.setup( DATA, GPIO.OUT )

HEART = [
        0b00000000,
        0b01100110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000,
        0b00000000
        ]

def shift_out_16 ( row_data, col_data ):
    GPIO.output( LATCH, GPIO.LOW )

# 두번째 칩 ( 세로/Column ) - 788BS는 0일 때 해당 칸이 켜짐 (비트 반전)
    col_inverse = ~col_data & 0xFF
    for i in range( 8 ):
        bit = ( col_inverse >> ( 7 - i )) & 1
        GPIO.output( DATA, bit )
        GPIO.output( CLOCK, GPIO.HIGH )
        GPIO.output( CLOCK, GPIO.LOW )

    for i in range( 8 ):
        bit = ( row_data >> ( 7 - i )) & 1
        GPIO.output( DATA, bit )
        GPIO.output( CLOCK, GPIO.HIGH )
        GPIO.output( CLOCK, GPIO.LOW )

    GPIO.output( LATCH, GPIO.HIGH )

print( "저항 1개로 안전하게 788BS 작동 테스트를 시작합니다." )

try:
    while True:
        for row in range( 8 ):
            row_bits = ( 1 << row )

            col_bits = HEART[ row ]

            shift_out_16( row_bits, col_bits )
            time.sleep( 0.001 )

except KeyboardInterrupt:
    shift_out_16( 0x00, 0x00 )
    GPIO.cleanup()
    print( "\n테스트를 종료합니다." )

