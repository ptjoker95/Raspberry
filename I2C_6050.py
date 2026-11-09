import time
import smbus2

# MPU-6050 상수 정의
MPU_ADDR = 0x68
REG_PWR_MGMT_1 = 0x6B
REG_CONFIG = 0x1A
REG_ACCEL_XOUT_H = 0x38
REG_GYRO_CONFIG = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_WHO_AM_I = 0x75
# 오프셋 보정을 위한 샘플 수
SAMPLE_COUNT = 100
REG_GYRO_ADDR = 0x43
REG_ACCEL_ADDR = 0x3B


#I2C 버스 열기 ( 라즈베리 파이 보통 1번 버스 )
bus = smbus2.SMBus( 1 )

def mpu_init():
    # 슬립 모드 해제
    try:
        bus.write_byte_data( MPU_ADDR, REG_PWR_MGMT_1, 0x00 )
        time.sleep( 0.05 )
        bus.write_byte_data( MPU_ADDR, REG_ACCEL_CONFIG, 0x00 )
        print( "AFS_SEL value is written as: ", bus.read_byte_data( MPU_ADDR, REG_ACCEL_CONFIG ))
    except Exception as e:
        print( f'Exception is occered: {e}' )
    '''
    pwr = bus.read_byte_data( MPU_ADDR, REG_PWR_MGMT_1 )
    print( f'PWR_MGMT_1 : 0x{pwr:02X}' )
    who_am_i = bus.read_byte_data( MPU_ADDR, REG_WHO_AM_I )
    print( f'WHO_AM_I: {hex(who_am_i)}' )
    gyro_config = bus.read_byte_data( MPU_ADDR, REG_GYRO_CONFIG )
    print( f'Gyro Config: 0x{gyro_config:02X}' )
    accel_config = bus.read_byte_data( MPU_ADDR, REG_ACCEL_CONFIG )
    print( f'Accel Config: 0x{accel_config:02X}' )
    '''
def convert_to_signed( val ):
        if val >= 0x8000:
            val -= 0x10000
        return val

def check_data():
    for i in range(5):
        data = bus.read_i2c_block_data( MPU_ADDR, 0x3B, 6 )

        raw_z_combined = ( data[4] << 8 ) | data[5]
        signed_z = convert_to_signed( raw_z_combined )
        g_z = signed_z / 16384.0

        print(
                f'[{i+1}]회차 Z High: 0x{data[4]:02X}, Low: 0x{data[5]:02X} | 16비트'
                f'합산: {raw_z_combined} (Hex: 0x{raw_z_combined:04X}) | Signed 변환:'
                f' {signed_z} | 최종 g: {g_z:.2f}')
        time.sleep(0.5)


def set_offset( SAMPLE_COUNT ):
    gyro_offset_x = 0.0
    gyro_offset_y = 0.0
    gyro_offset_z = 0.0

    for _ in range( SAMPLE_COUNT ):
        data = bus.read_i2c_block_data( MPU_ADDR, REG_GYRO_ADDR, 6 )
        gx = convert_to_signed( ( data[0] << 8 ) | data[1] ) / 131.0
        gy = convert_to_signed( ( data[2] << 8 ) | data[3] ) / 131.0
        gz = convert_to_signed( ( data[4] << 8 ) | data[5] ) / 131.0       

        gyro_offset_x += gx
        gyro_offset_y += gy
        gyro_offset_z += gz

    gyro_offset_x /= SAMPLE_COUNT
    gyro_offset_y /= SAMPLE_COUNT
    gyro_offset_z /= SAMPLE_COUNT

    return ( gyro_offset_x, gyro_offset_y, gyro_offset_z )


def set_dlpf_bandwidth( config_value ):
    if config_value > 6:
        config_value = 6

    try:
        current_config = bus.read_byte_data( MPU_ADDR, REG_CONFIG )
        print( f'current config: {current_config}' )
        new_config = ( current_config & 0xF8 ) | ( config_value & 0x07 )
        print( f'new config: {new_config}' )

        bus.write_byte_data( MPU_ADDR, REG_CONFIG, new_config )
        print( f"[설정 변경] DLPF_CFG가 {config_value}로 설정되었습니다." )

    except Exception as e:
        print( f'Exception is occered as {e}' )


def read_raw_data():

    accel_x = accel_y = accel_z = 0.0
    temp_raw = temp_c = 0.0
    gx = gy = gz = 0.0


    try:
        data = bus.read_i2c_block_data( MPU_ADDR, REG_ACCEL_ADDR, 8 )
        
        accel_x = convert_to_signed( ( data[0] << 8 ) | data[1] ) / 16384.0 
        accel_y = convert_to_signed( ( data[2] << 8 ) | data[3] ) / 16384.0 
        accel_z = convert_to_signed( ( data[4] << 8 ) | data[5] ) / 16384.0 


        temp_raw = convert_to_signed( ( data[6] << 8 ) | data[7] )
        temp_c = ( temp_raw / 333.87 ) + 21.0

        data = bus.read_i2c_block_data( MPU_ADDR, REG_GYRO_ADDR, 6 )
        gx = convert_to_signed( ( data[0] << 8 ) | data[1] ) / 131.0
        gy = convert_to_signed( ( data[2] << 8 ) | data[3] ) / 131.0
        gz = convert_to_signed( ( data[4] << 8 ) | data[5] ) / 131.0       



    except Exception as e:
        print( f'Exception is occered as {e}' )

    return ( accel_x, accel_y, accel_z ), temp_c, ( gx, gy, gz )


mpu_init()

# check_data()

set_dlpf_bandwidth( 0 )

( gyro_offset_x , gyro_offset_y, gyro_offset_z ) = set_offset( SAMPLE_COUNT )

print( f'gyro_offset_x: {gyro_offset_x:.2f}, gyro_offset_y: {gyro_offset_y:.2f}, gyro_offset_z: {gyro_offset_z:.2f}' )

for i in range( 50 ):
    ( ax, ay, az ), temp_c, ( gx, gy, gz) = read_raw_data()

    # print( f'[{i+1}]회차] Gx: {gx:.2f}, Gy: {gy:.2f}, Gz: {gz:.2f}' )
    
    gx = gx - gyro_offset_x
    gy = gy - gyro_offset_y
    gz = gz - gyro_offset_z

    # print( f'[{i+1}]회차] Accel X: {ax:.2f} | Accel Y: {ay:.2f} | Accel Z: {az:.2f}' )
    # print( f'[{i+1}]회차] temperature : {temp_c:.2f}' )
    print( f'[{i+1}]회차] Gx: {gx:.2f}, Gy: {gy:.2f}, Gz: {gz:.2f}' )

'''
set_dlpf_bandwidth( 6 )
print( "현재 5Hz 모드 센서 값:", read_raw_data() )
'''
