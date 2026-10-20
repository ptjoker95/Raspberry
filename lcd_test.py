import time
from rpi_lcd import LCD

lcd = LCD()

try:
    print( "LCD에 텍스트 출력 중..." )
    lcd.text( "Hello, Raspberry!", 1 )
    lcd.text( "I2C 1602 LCD OK!", 2 )
    time.sleep( 5 )
finally:
    lcd.clear()
    
