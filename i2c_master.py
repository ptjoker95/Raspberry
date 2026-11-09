from smbus2 import SMBus, i2c_msg
import time

SLAVE_ADDR = 0x08
bus = SMBus( 1 )

def send_message( msg ):
    data = [ ord( char ) for char in msg ]
    bus.write_i2c_block_data( SLAVE_ADDR, 0, data )
    print( f'Sent: { msg }' )

try:
    MAX_BUFFER_SIZE = 32
    read_msg = i2c_msg.read( SLAVE_ADDR, MAX_BUFFER_SIZE )
    bus.i2c_rdwr( read_msg )

    while True:
        send_message( 'Hi ESP32' )
        time.sleep( 2 )

        # data = bus.read_i2c_block_data( SLAVE_ADDR, 0, 16 )
        # received_str = ''.join( [ chr( val ) for val in data if val != 0 ] )
        print( f'Received: { received_str }' )

        time.sleep( 2 )


except KeyboardInterrupt:
    bus.close()
    print( 'I2C communication stopped.' )
