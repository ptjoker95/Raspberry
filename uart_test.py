import serial
import time
import sys
from pathlib import Path

BASE_DIR = Path( __file__ ).resolve().parent
print( "BASE_DIR= ", BASE_DIR )

LIB_DIR = BASE_DIR / "libs"
print( "LIB_DIR= ", LIB_DIR )

sys.path.insert( 0, str( LIB_DIR ))

PORT = "/dev/serial0"
BAUDRATE = 115200

ser = serial.Serial() 

try:
    ser = serial.Serial( PORT, BAUDRATE, timeout= 1 )
    print( f"Connected to  {PORT} at {BAUDRATE} baud." )

except KeyboardInterrupt:
    print( "Program stopped by user.")

except Exception as e:
    print( f"Failed to open port: {e}" )
    exit()



try:
    count = 1

    while True:
        '''
        message = "Hello from Raspberry Pi! " + str( count )
        if ser.is_open:
            ser.write( message.encode( 'utf-8' ))
            print( f"Sent: {message}" )
            count = count + 1
        else:
            exit()

        if ser.in_waiting > 0:
            response = ser.readline().decode( 'utf-8' ).strip()
            print( f"Received from ESP32-S3: {response}" )
'''
        if ser.in_waiting > 0:
            incoming_data = ser.readline().decode( 'utf-8' ).strip()
            print( f"Received from ESP32-S3: {incoming_data}" )

        time.sleep( 1 )

except KeyboardInterrupt:
    print( "\nProgram is stopped by user." )

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print( "Serial Port is closed." )
    print( "\nCommunication closed by user." )
