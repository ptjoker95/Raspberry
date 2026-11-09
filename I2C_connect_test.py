import time
import smbus2

bus = smbus2.SMBus(1)

MPU_ADDR = 0x68
REG_PWR_MGMT_1 = 0x6B

try:
    val_before = bus.read_byte_data( MPU_ADDR, REG_PWR_MGMT_1 )
    print( f'쓰기 전 0x6B 레지스터 값: 0x{val_before:02X}' )

    bus.write_byte_data( MPU_ADDR, REG_PWR_MGMT_1, 0x11 )
    time.sleep( 0.05 )

    val_after = bus.read_block_data( MPU_ADDR, REG_PWR_MGMT_1 )
    print( f'쓴 후 0x6B 레지스터 값: 0x{ val_after[0]:02X}' )

    if val_after == 0x00:
        print( "라즈베리파이의 문제거나 모듈 통신선 문제" )
    else:
        print( '값이 정상적으로 반영' )

except Exception as e:
    print( f'통신 예외 발생{e}' )

