import time
import subprocess
import os
import pygame
import numpy as np 
import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings( False )

GPIO.setmode( GPIO.BCM )
GPIO.setup( 17, GPIO.OUT )
GPIO.setup( 18, GPIO.OUT )

pygame.mixer.pre_init( 44100, -16, 1 )
pygame.init()

def generate_beep( frequency, duration_ms, volume=0.5 ):
    sample_rate = 44100
    n_samples = int( sample_rate * duration_ms / 1000 )
    t = np.linspace( 0, duration_ms / 1000, n_samples, False )
    wave = np.sin( frequency * t * 2 * np.pi )
    audio = ( wave * ( 2**15 - 1 ) * volume ).astype( np.int16 )
    sound = pygame.sndarray.make_sound( audio )
    return sound

high_beep = generate_beep( 800, 50, 0.5 )
mid_beep = generate_beep( 660, 50, 0.5 )
low_beep = generate_beep( 440, 50, 0.5 )

def precise_metronome( bpm ):
    interval_ns = int( (60*1_000_000_000) / bpm )

    print( f"고정밀 메트로놈 시작: {bpm} BPM (종료하려면 Ctrl + C)")

    next_tick_ns = time.perf_counter_ns()
    sub_interval_ns = interval_ns // 4 
    count = 0

    try:

        subprocess.run( 'cls' if os.name == 'nt' else 'clear', shell= True )

        while True:

            while time.perf_counter_ns() < next_tick_ns: pass
            beat_num = ( count % 4 ) + 1
            print( beat_num, " ", end="", flush= True )
            high_beep.play()
            GPIO.output( 17, True )
            next_tick_ns += sub_interval_ns

            while time.perf_counter_ns() < next_tick_ns: pass
            print( "e  ", end="", flush= True )
            low_beep.play()
            GPIO.output( 17, False )
            next_tick_ns += sub_interval_ns

            while time.perf_counter_ns() < next_tick_ns: pass
            print( "&  ", end="", flush= True )
            mid_beep.play()
            GPIO.output( 18, True )
            next_tick_ns += sub_interval_ns
        
            while time.perf_counter_ns() < next_tick_ns: pass
            print( "a  ", end="\n" if (count % 4) + 1 == 4 else "  ", flush= True )
            low_beep.play()
            GPIO.output( 18, False )
            next_tick_ns += sub_interval_ns

            count += 1

    except KeyboardInterrupt:
        print( "\n메트로놈이 종료되었습니다.")

    finally:
        GPIO.cleanup()

precise_metronome( 60 )

GPIO.cleanup()
