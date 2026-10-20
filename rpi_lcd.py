import time

try:
    import smbus2 as smbus
except ImportError:
    import smbus

# I2C장치 주소 (i2cdetect 결과에 따라 0x27 또는 0x3f )

LCD_BACKLIGHT = 0x08
DEFAULT_I2C_ADDR = 0x27
En = 0x04
Rw = 0x02
Rs = 0x01

class LCD:
    def __init__( self, port=1, address=DEFAULT_I2C_ADDR ):
        self.bus = smbus.SMBus( port )
        self.addr = address
        self.init_lcd()

    def lcd_strobe( self, data ):
        self.bus.write_byte ( self.addr, data | En | LCD_BACKLIGHT )
        time.sleep( 0.0005 )
        self.bus.write_byte ( self.addr, ( data & ~En ) | LCD_BACKLIGHT )
        time.sleep( 0.0005 )

    def write_four_bits( self, data ):
        self.bus.write_byte( self.addr, data | LCD_BACKLIGHT )
        self.lcd_strobe( data )

    def write_cmd( self, cmd ):
        self.write_four_bits( 0x00 | ( cmd & 0xF0 ))
        self.write_four_bits( 0x00 | (( cmd << 4 ) & 0xF0 ))

    def write_data( self, data ):
        self.write_four_bits( Rs | ( data & 0xF0 ))
        self.write_four_bits( Rs | (( data << 4 ) & 0xF0 ))

    def init_lcd( self ):
        try:
            time.sleep( 0.05 ) 
            self.write_four_bits( 0x30 )
            time.sleep( 0.005 )
            self.write_four_bits( 0x30 )
            time.sleep( 0.0002 )
            self.write_four_bits( 0x30 )
            self.write_four_bits( 0x20 )

            self.write_cmd( 0x28 )
            self.write_cmd( 0x0C )
            self.write_cmd( 0x06 )
            self.clear()
        except Exception as e:
            print( f"LCD 초기화 중 오류 발생 (I2C 주소 확인 필요): {e}" )

    def clear( self ):
        self.write_cmd( 0x01 )
        time.sleep( 0.002 )

    def text( self, text, line ):
        if line == 1:
            self.write_cmd( 0x80 )
        elif line == 2:
            self.write_cmd( 0xC0 )
        for char in text.ljust( 16 ):
            self.write_data( ord( char ))

