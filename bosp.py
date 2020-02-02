#!/usr/bin/env python3
import os
import RPi.GPIO as GPIO
import signal
import subprocess
import sys
import time

video='/home/bolo/Vidéos/ys-s03e12.avi'
mp_fifo_f = "/tmp/mpc"

os.system('su bolo -c "DISPLAY=:0 mplayer {file} -input file={fifo}"'.format(file = video, fifo = mp_fifo_f))
#exec('mplayer', video, '-input', 'file={}'.format(mp_fifo_f))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
bouncetime=300
gpio_led = 23
GPIO.setup(gpio_led, GPIO.OUT)
gpio_but = 24
GPIO.setup(gpio_but, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def send_cmd(cmd):
    print('Command: {}'.format(cmd))
    with open(mp_fifo_f, 'w') as f:
        f.write('{}\n'.format(cmd))

def pause(ch):
    #send_cmd('stop')
    #send_cmd('pause')
    #send_cmd('loadfile {} 0'.format(video))
    send_cmd('seek 0 2')
GPIO.add_event_detect(gpio_but, GPIO.RISING, callback=pause, bouncetime=bouncetime)

def signal_handler(sig, frame):
    send_cmd('quit 1')
    print('\nYou pressed Ctrl+C!\n')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
    #while True:
     #   time.sleep(0.01)
