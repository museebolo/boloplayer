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


# Variables globales
###
intro_delay = 3                     # Délais pour bloquer le bouton pour qu'il évite de se répéter.
bouncetime = 300                    # Anti-rebond du bouton [ms]


# Fonctions
###

# Affiche l'aide.
def usage():
    print("Usage: {name} file".format(name=sys.argv[0]))

# Interuption lorsque que le bouton est pressé.
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

# Signal pour quitter le programme
def signal_handler(sig, frame):
    player.quit()
    print('\nYou pressed Ctrl+C!\n')
    sys.exit(0)


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


# Configuration du GPIO
###
GPIO.setwarnings(False)             # Désactive les messages d'avertissement.
GPIO.setmode(GPIO.BCM)              # Utilise la numérotation des pattes BCM

gpio_led = 23                       # Configuration de la led pour lecture
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.output(gpio_led, GPIO.HIGH)

gpio_but = 24                       # Configuration du bouton play/restart
GPIO.setup(gpio_but, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(gpio_but, GPIO.RISING, callback=restart, bouncetime=bouncetime)


# Main
###

# Démarre la lecture de la vidéo
player = OMXPlayer(video,
        args=['--no-osd', '-o', 'local', '--loop', '--align', 'center'],
        dbus_name='org.mpris.MediaPlayer2.omxplayer',
        pause=True)

# Capture le signal INT (^c) pour arrêter proprement le programme
signal.signal(signal.SIGINT, signal_handler)

# Boucle principale pour voir si la lecture est terminée.
intro_lock = False
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
