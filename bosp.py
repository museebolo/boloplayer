#!/usr/bin/env python3
import RPi.GPIO as GPIO
import signal
import sys
import time
from omxplayer.player import OMXPlayer

video='/home/bolo/Vidéos/robin_masur_4_3.mp4'
video='/home/bolo/Vidéos/Adola_Fofana_test_barre_noire.mp4'
intro_delay=3 # Délais pour bloquer le bouton pour qu'il évite de se répéter.
intro_lock=False

player = OMXPlayer(video,
        args=['--no-osd', '-o', 'local', '--loop', '--align', 'center'],
        dbus_name='org.mpris.MediaPlayer2.omxplayer',
        pause=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
bouncetime=300
gpio_led = 23
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.output(gpio_led, GPIO.HIGH)
gpio_but = 24
GPIO.setup(gpio_but, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def restart(ch):
    global intro_lock
    print("Push")
    if int(player.position()) > intro_delay or intro_lock == False:
        print("Restart")
        if player.can_pause():
            player.pause()
            player.set_position(0.0)
        if player.can_play():
            player.play()
        GPIO.output(gpio_led, GPIO.LOW)
        intro_lock = True
GPIO.add_event_detect(gpio_but, GPIO.RISING, callback=restart, bouncetime=bouncetime)

def signal_handler(sig, frame):
    player.quit()
    print('\nYou pressed Ctrl+C!\n')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        if int(player.position()) == int(player.duration()):
            player.pause()
            player.set_position(0.0)
            player.play()
            time.sleep(0.5)
            player.pause()
            GPIO.output(gpio_led, GPIO.HIGH)
            intro_lock = False
        time.sleep(0.1)
