import time
import subprocess
import os
import numpy as np 
import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings( False )


GPIO.setmode( GPIO.BOARD )
GPIO.setup( 36, GPIO.OUT )
GPIO.setup( 35, GPIO.OUT )
GPIO.setup( 38, GPIO.OUT )
GPIO.setup( 40, GPIO.OUT )
GPIO.setup( 37, GPIO.OUT )
GPIO.setup( 31, GPIO.OUT )
GPIO.setup( 29, GPIO.OUT )
GPIO.setup( 33, GPIO.OUT )


SEGMENT_MAP = {
        0: ( False, False, False, False, False, False, True ), 
        1: ( True, False, False, True, True, True, True ),
        2: ( False, False, True, False, False, True, False ),
        3: ( False, False, False, False, True, True, False ),
        4: ( True, False, False, True, True, False, False ),
        5: ( False, True, False, False, True, False, False ),
        6: ( False, True, False, False, False, False, False ),
        7: ( False, False, False, True, True, True, True ),
        8: ( False, False, False, False, False, False, False ),
        9: ( False, False, False, False, True, False, False )
        }

pins = [ 36, 35, 38, 40, 37, 31, 29 ]

def display_number( num ):
    pattern = SEGMENT_MAP[ num ]

    for pin, state in zip( pins, pattern ):
        GPIO.output( pin, state )

try:
    for i in range( 10 ):

        display_number( i )
        sleep( 1 )

except:
    GPIO.cleanup()

else:
    GPIO.cleanup()

finally:
    GPIO.cleanup()

GPIO.cleanup()
