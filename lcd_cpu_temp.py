import time
from rpi_lcd import LCD

lcd = LCD()

def get_cpu_temp():
    with open( "/sys/class/thermal/thermal_zone0/temp", "r" ) as f:
        temp_raw = f.read()

    return float( temp_raw ) / 1000.0

try:
    print( "LCD에 CPU 온도 출력 중..." )
    while True:
        lcd.text( "CPU temperature", 1 )
        lcd.text( f" is {get_cpu_temp():.3f}", 2 )
        time.sleep( 1 )

except KeyboardInterrupt:
    lcd.clear()

finally:
    lcd.clear()
    
lcd.clear()
