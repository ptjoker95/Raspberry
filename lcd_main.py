from rpi_lcd import LCD
import time

lcd = LCD ( address = 0x27 )
lcd.text( "Hello, World!", 1 )
lcd.text( "Working Great!", 2 )
