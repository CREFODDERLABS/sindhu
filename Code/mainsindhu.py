import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit
import multiprocessing

import RPi.GPIO as GPIO
import os

import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image,ImageDraw,ImageFont

from random import randint


touch_pin = 17
vibration_pin = 22



# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)

# Raspberry Pi pin configuration for LCD:
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 

frame_count = {'blink':39, 'happy':60, 'sad':47,'dizzy':67,'excited':24,'neutral':61,'happy2':20,'angry':20,'happy3':26,'bootup3':124,'blink2':20}

emotion = ['angry','sad','excited']

normal = ['neutral','blink2']

q = multiprocessing.Queue()
event = multiprocessing.Event()

def check_sensor():
    previous_state = 1
    current_state = 0
    while True:
        if (GPIO.input(touch_pin) == GPIO.HIGH):
            if previous_state != current_state:
                if (q.qsize()==0):
                    event.set()
                    q.put('happy')
                current_state = 1
            else:
                current_state = 0
        if GPIO.input(vibration_pin) == 1:
            print('vib')
            if (q.qsize()==0):
                event.set()
                q.put(emotion[randint(0,2)])
        time.sleep(0.05)

def bootup():
    show('bootup3',1)
    for i in range(1):
        p2 = multiprocessing.Process(target=show,args=('blink2',3))
        p3 = multiprocessing.Process(target=rotate,args=(0,150,0.005))
        p4 = multiprocessing.Process(target=baserotate,args=(90,45,0.01))
        p2.start()
        p3.start()
        p4.start()
        p4.join()
        p2.join()
        p3.join()
def sound(emotion):
    for i in range(1):
	    os.system("aplay /home/pi/Desktop/EmoBot/sound/"+emotion+".wav")
    
def show(emotion,count):
    for i in range(count):
        try:
            disp = LCD_2inch.LCD_2inch()
            disp.Init()
            for i in range(frame_count[emotion]):
                image = Image.open('/home/pi/Desktop/EmoBot/emotions/'+emotion+'/frame'+str(i)+'.png')	
                disp.ShowImage(image)
        except IOError as e:
            logging.info(e)    
        except KeyboardInterrupt:
            disp.module_exit()
            servoDown()
            logging.info("quit:")
            exit()
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()
    bootup()
    while True:
        if event.is_set():
                p5.terminate()
                event.clear()
                emotion = q.get()
                q.empty()
                print(emotion)
                p2 = multiprocessing.Process(target=show,args=(emotion,4))
                p3 = multiprocessing.Process(target=sound,args=(emotion,))
                if emotion == 'happy':
                    p4 = multiprocessing.Process(target=happy)
                elif emotion == 'angry':
                    p4 = multiprocessing.Process(target=angry)
                elif emotion == 'sad':
                    p4 = multiprocessing.Process(target=sad)
                elif emotion == 'excited':
                    p4 = multiprocessing.Process(target=excited)
                elif emotion == 'blink':
                    p4 = multiprocessing.Process(target=blink)
                else:
                    continue
                p2.start()
                p3.start()
                p4.start()
                p2.join()
                p3.join()
                p4.join()
        else:
            p = multiprocessing.active_children()
            for i in p:
                if i.name not in ['p1','p5']:
                    i.terminate()
            neutral = normal[0]
            p5 = multiprocessing.Process(target=show,args=(neutral,4),name='p5')
            p5.start()
            p5.join()
