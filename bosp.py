#!/usr/bin/env python3
# Project: Bolo Player
# File: bosp.py
# Version: 0.1
# Create by: Rom1 <romain@museebolo.ch> - Musée Bolo - https://www.museebolo.ch
# Date: 10/02/2020
# Licence: GNU GENERAL PUBLIC LICENSE v3
# Language: Python 3
# Description: Surcouche du lecteur de vidéo "omxplayer" pour Raspberry Pi pour
#              les bornes OSCAR du musée Bolo. 


from omxplayer.player import OMXPlayer
from pathlib import Path
import RPi.GPIO as GPIO
import signal
import sys
import time


# Configurations
###
intro_delay = 3                     # Délais pour bloquer le bouton pour qu'il évite de se répéter.
bouncetime = 300                    # Anti-rebond du bouton [ms]
blink_delay = 0.5                   # Délais du clignotement de la led [s].

stat_f = "/tmp/statistique.log"


# Fonctions
###

# Affiche l'aide.
def usage():
    print("Usage: {name} file".format(name=sys.argv[0]))

# Interuption lorsque que le bouton est pressé.
def restart(ch):
    global intro_lock
    global led_blink
    write_stat("{time} restart".format(time=time.time()))
    if int(player.position()) > intro_delay or intro_lock == False:
        if player.can_pause():
            player.pause()
            player.set_position(0.0)
        if player.can_play():
            player.play()
        led_blink = False
        intro_lock = True

# Signal pour quitter le programme
def signal_handler(sig, frame):
    player.quit()
    print('\nYou pressed Ctrl+C!\n')
    sys.exit(0)

def write_stat(text):
    with open(stat_f, 'a') as f:
        f.write(text)
        f.write('\n')


# Lecture et vérification des arguments
###
if len(sys.argv) != 2:
    print("N'a pas le bon nombre d'argument")
    usage()
    sys.exit(1)

if sys.argv[1] == "help":
    usage()
    sys.exit(0)

video = Path(sys.argv[1])

if not video.exists():
    print("Le fichier n'existe pas!")
    usage()
    sys.exit(1)


# GPIO
###
GPIO.setwarnings(False)             # Désactive les messages d'avertissement.
GPIO.setmode(GPIO.BCM)              # Utilise la numérotation des pattes BCM

gpio_led = 23                       # Configuration de la led pour lecture
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.output(gpio_led, GPIO.HIGH)

gpio_but = 24                       # Configuration du bouton play/restart
GPIO.setup(gpio_but, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(gpio_but, GPIO.RISING, callback=restart, bouncetime=bouncetime)

def led_on(ch):
    GPIO.output(ch, GPIO.HIGH)

def led_off(ch):
    GPIO.output(ch, GPIO.LOW)

time_tmp = 0.0
led_state = False
def led_blink_handler(ch, status):
    global led_state
    global time_tmp
    if status == True:
        if time.time() > (time_tmp + float(blink_delay)):
            if led_state == True:
                led_on(ch)
                led_state = False
            else:
                led_off(ch)
                led_state = True
            time_tmp = time.time()
    else:
        led_on(ch)



# Main
###

# Démarre la lecture de la vidéo
player = OMXPlayer(video,
        args=['--no-osd', '-o', 'local', '--loop', '--align', 'center'],
        dbus_name='org.mpris.MediaPlayer2.omxplayer',
        pause=True)

# Capture les signaux pour arrêter proprement le programme
signal.signal(signal.SIGINT, signal_handler)    # Singal INT (^c)
signal.signal(signal.SIGTERM, signal_handler)   # Signal TERM (kill)

# Boucle principale pour voir si la lecture est terminée.
intro_lock = False
led_blink = True
while True:
    led_blink_handler(gpio_led, led_blink)
    if int(player.position()) == int(player.duration()):
        player.pause()
        player.set_position(0.0)
        player.play()
        time.sleep(0.5)
        player.pause()
        led_blink = True
        intro_lock = False
    time.sleep(0.1)
