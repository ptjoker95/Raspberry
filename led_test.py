import time
import random
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import text

DIN = 10
CLK = 11
CS = 8

PINS = [ DIN, CLK, CS ]

serial = spi( port=0, device=0, gpio=None )

device = max7219( serial, cascaded=1, block_orientation=0, rotate=0, brightness=1 )

print( "LED 매트릭스 점등 테스트 시작..." )

Count16_Subdivision = [ '1', 'e', 'n', 'a', '2', 'e', 'n', 'a', '3', 'e', 'n', 'a', '4', 'e', 'n', 'a']

# 0부터 7사이의 두개의 좌표를 랜덤으로 뽑아서 선을 그림
def random_line():
    while True:
        with canvas( device ) as draw:
            i1 = random.randint( 0, 7 )
            j1 = random.randint( 0, 7 )
            i2 = random.randint( 0, 7 )
            j2 = random.randint( 0, 7 )
            draw.line( [ ( i1, j1 ), ( i2, j2 ) ], fill = 'white' )
            time.sleep( 0.5 )

# 0부터 7사이의 좌표 두개를 튜블로 입력하면 선을 그림
# 사용 방법
'''
    try:
        draw_a_line( ( 1, 1 ),( 7, 3 ) )
        time.sleep( 5 )
    except ValueError:
        print( f'자료 구조를 튜블로 입력해야 합니다.' )
'''
def draw_a_line( x : tuple, y : tuple ):
    with canvas( device ) as draw:
        draw.line( [ x, y ], fill='white' )

# 16비트를 카운트 함
def Count16( bpm : int ):
    while True:
        for C in Count16_Subdivision:
            with canvas( device ) as draw:
                text ( draw, ( 1, 0 ), C, fill='white' )
                time.sleep( bpm / 240 )

try:
    Count16( 153 )

except KeyboardInterrupt:
    print( f"\nCtrl+C로 프로그램이 종료되었습니다." )

finally:
    print( f'프로그램이 종료되었습니다.' )


# draw.rectangle(( 2, 2, 5, 5 ), outline="white", fill="white" )

device.clear()

# time.sleep(1)

serial.cleanup()

print("테스트 종료")
