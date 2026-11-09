import time
from gpiozero import DistanceSensor
from rpi_lcd import LCD

sensor = DistanceSensor( echo=24, trigger=23, max_distance=4 )

lcd = LCD()

try:
    print( f"HC-SR04 거리 측정 시작 ( Ctrl-C로 종료)" )
    while True:
        cm = sensor.distance * 100
        print( f'측정 거리: {cm:.2f} cm' )
        lcd.text( "Distance :", 1 )
        lcd.text( f" is {cm:.2f} cm", 2 )
        time.sleep(0.05)

except KeyboardInterrupt:
    lcd.clear()
    print( f'\n측정을 종료합니다.' )

finally:
    lcd.clear()

lcd.clear()

