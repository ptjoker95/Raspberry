"""
CPU의 온도를 측정해서, 정해진 온도 초과가 되면 GPIO 포트 17번에서 신호를 보내고,
정해진 온도 이하가 되면 신호를 끊는다.

"""

import os
import subprocess

import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings( False )

GPIO.setmode( GPIO.BCM )
GPIO.setup( 17, GPIO.OUT )

# 기준이 되는 CPU온도를 정한다.
Check_CPU_Temperature = 45.5

def get_cpu_temp():
    with open( "/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_str = f.read().strip()
        return float( temp_str ) / 1000.0

print( f"CPU Temperature: {get_cpu_temp():.1f} C")

def clear_screen():
    cmd = 'cls' if os.name == 'nt' else 'clear'

    subprocess.run( [cmd] )


while True:
    # 화면을 깨끗하게 지운다.
    clear_screen()

    if get_cpu_temp() > Check_CPU_Temperature:
        GPIO.output( 17, True )
    elif get_cpu_temp() <= Check_CPU_Temperature:
        GPIO.output( 17, False )
    
    print( f"CPU Temperature: {get_cpu_temp():.1f} C")
    sleep(3)
