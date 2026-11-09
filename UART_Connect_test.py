import serial
import time
PORT = '/dev/serial0'
BAUDRATE = 115200

there_is_message = False

ser = serial.Serial()

counter = 1

while True:
    try:
        ser = serial.Serial( PORT, BAUDRATE, timeout=1 )
        print( f'Connected to {PORT}. Starting Echo Test...' )

        message = f'Ping #{counter}\n'

        if message is not None:
            there_is_message = True

        ser.write( message.encode( 'utf-8' ))
        print( f'Sent to ESP32: {message.strip()}')

        start_time = time.time()

        while time.time() - start_time < 2.0 and there_is_message:
            if ser.in_waiting > 0:
                response = ser.readline().decode( 'utf-8', errors= 'ignore').strip()
            
                if response:
                    there_is_message = False
                    print( f'-> Received Echo: {response}' )
                else:
                    ser.close()
                    print( 'No message. Serial port closed cleanly.' )
                    exit()
            if time.time() > start_time + 2.0:
                ser.close()
                print( 'No message. Serial port closed cleanly.' )
                exit()


        counter += 1
        time.sleep( 1 )

    except OSError as e:
        print( f'I/O Error 발생 ( 하드웨어/연결 끊김 ): {e}' )

    except Exception as e:
        print( f'기타 에러 발생: {e}' )

    finally:
        if ser.is_open:
            ser.close()
            print( 'Serial port closed cleanly.' )

