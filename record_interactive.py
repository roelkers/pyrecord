#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

import sys
import datetime
import subprocess
import os
import string

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# GPIO define
RST_PIN = 25  # Reset
CS_PIN = 8
DC_PIN = 24
JS_U_PIN = 6  # Joystick Up
JS_D_PIN = 19  # Joystick Down
JS_L_PIN = 5  # Joystick Left
JS_R_PIN = 26  # Joystick Right
JS_P_PIN = 13  # Joystick Pressed
BTN1_PIN = 21
BTN2_PIN = 20
BTN3_PIN = 16

# Some constants
SCREEN_LINES = 4
SCREEN_SAVER = 20.0
CHAR_WIDTH = 19
font = ImageFont.load_default()
width = 128
height = 64
x0 = 0
x1 = 84
y0 = -2
y1 = 12
y2 = 24
y3 = 36
y4 = 48
x2 = x1+7
x3 = x1+14
x4 = x1+9
x5 = x2+9
x6 = x3+9

choices = [
 "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
 "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "!", "@", "#",
    "$", "%", "^", "&", "*", "(", ")", ",", ".", "?", ":", ";", "'", " "
]


# init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(JS_U_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_D_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_L_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_R_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_P_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up

# Initialize the display...
serial = spi(device=0, port=0, bus_speed_hz=8000000,
             transfer_size=4096, gpio_DC=DC_PIN, gpio_RST=RST_PIN)
device = sh1106(serial, rotate=2)  # sh1106
draw = ImageDraw.Draw(Image.new('1', (width, height)))
draw.rectangle((0, 0, width, height), outline=0, fill=0)

PATH = '/home/patch/Workspace/Tests'

# Platform specific constants
if sys.platform == 'win32':
    print("recording-test.py, running on windows")
    PIPE_TO_AUDACITY = '\\\\.\\pipe\\ToSrvPipe'
    PIPE_FROM_AUDACITY = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    print("recording-test.py, running on linux or mac")
    PIPE_TO_AUDACITY = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    PIPE_FROM_AUDACITY = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

print("Write to  \"" + PIPE_TO_AUDACITY +"\"")
if not os.path.exists(PIPE_TO_AUDACITY):
    print(""" ..does not exist.
    Ensure Audacity is running with mod-script-pipe.""")
    sys.exit()

print("Read from \"" + PIPE_FROM_AUDACITY +"\"")
if not os.path.exists(PIPE_FROM_AUDACITY):
    print(""" ..does not exist.
    Ensure Audacity is running with mod-script-pipe.""")
    sys.exit()

print("-- Both pipes exist.  Good.")

TOPIPE = open(PIPE_TO_AUDACITY, 'w')
print("-- File to write to has been opened")
FROMPIPE = open(PIPE_FROM_AUDACITY, 'r')
print("-- File to read from has now been opened too\r\n")


def send_command(command):
    """Send a command to Audacity."""
    print("Send: >>> "+command)
    TOPIPE.write(command + EOL)
    TOPIPE.flush()


def get_response():
    """Get response from Audacity."""
    line = FROMPIPE.readline()
    result = ""
    while True:
        result += line
        line = FROMPIPE.readline()
        # print(f"Line read: [{line}]")
        if line == '\n':
            return result


def do_command(command):
    """Do the command. Return the response."""
    send_command(command)
    # time.sleep(0.1) # may be required on slow machines
    response = get_response()
    print("Rcvd: <<< " + response)
    return response


def start_recording():
    # Now we can start recording.
    do_command("Record2ndChoice")
    print('Started Recording ...')

def export(filename):
    """Export the new track, and deleted both tracks."""
    do_command("Select: Track=0 mode=Set")
    do_command("SelTrackStartToEnd")
    do_command(f"Export2: Filename={os.path.join(PATH, filename)} NumChannels=1.0")
    print('Exported')

def remove_tracks():
    do_command("SelectAll")
    do_command("RemoveTracks")

def stop_recording_export(name):
    """Run test with one input file only."""
    do_command('PlayStop')
    print('Stopped')
    export(name + "-out.wav")
    print('Exported' + name)

def stop_recording():
    """Run test with one input file only."""
    do_command('PlayStop')
    print('Stopped')

mode="stopped"
has_recorded = False
start_time=datetime.datetime.now().replace(microsecond=0)
vert=0
horz=0
filename=""
display_on=True

def update_filename():
    global filename
    filename = ''.join([filename[:horz],choices[vert],filename[horz+1:]])

def findVert():
    global vert
    char = filename[horz] 
    vert = choices.index(char)

def draw_scene():
  global has_recorded
  with canvas(device) as draw:
      stamp = datetime.datetime.now().replace(microsecond=0)
      if mode=="recording":
        draw.text((x0, y0), "Recording", font=font, fill=255)
        draw.text((x0, y1), str(stamp - start_time), font=font, fill=255)
        draw.text((x1, y2), "Stop", font=font, fill=255)
      if mode=="stopped":
        draw.text((x0, y0), "Stopped", font=font, fill=255)
        if has_recorded==True:
          draw.text((x1, y0), "Export", font=font, fill=255)
          draw.text((x1, y2), "Discard", font=font, fill=255)
        else:
          draw.text((x1, y0), "Record", font=font, fill=255)
      if mode=="export":
        draw.text((x0, y0), "Enter Filename", font=font, fill=255)
        draw.text((x0, y1), filename, font=font, fill=255)
        draw.text((x1, y2), "Save", font=font, fill=255)

def click_b1(channel):
  global mode
  global has_recorded
  global start_time
  if mode=="stopped" and has_recorded == True:
      mode = "export"
  elif mode=="stopped":
      mode="recording" 
      start_recording()
      start_time=datetime.datetime.now().replace(microsecond=0)

def click_b2(channel): 
  global mode
  global has_recorded
  global filename
  if mode=="recording":
      mode="stopped"
      stop_recording()
      has_recorded=True
  elif mode=="export" and has_recorded == True:
      export(filename + ".wav") 
      remove_tracks()
      has_recorded=False
      filename=""
      mode="stopped"
  elif mode=="stopped":
      mode="stopped"
      remove_tracks()
      has_recorded=False


def click_b3(channel): 
  #Restart Display
  serial = spi(device=0, port=0, bus_speed_hz=8000000,
               transfer_size=4096, gpio_DC=DC_PIN, gpio_RST=RST_PIN)
  device = sh1106(serial, rotate=2)  # sh1106
  draw_scene()
  
def select_up(channel):
  global vert
  if vert == len(choices)-1:
    vert = 0
  else:
    vert = vert + 1
  update_filename()
  main_fun(0)
  
def select_down(channel):
  global vert
  if vert == 0:
    vert = len(choices) -1 
  else:
    vert = vert - 1 
  update_filename()
  main_fun(0)
    
def select_left(channel):
  global horz
  if(horz >= 0):
    horz = horz - 1
    findVert()

def select_right(channel):
  global horz
  global filename
  if(horz < len(filename) - 1):
    horz = horz + 1
    findVert()
  else:
    filename += "_"
    horz = horz + 1
    update_filename()

def main_fun(channel):
  global display_on
  if display_on:
      serial = spi(device=0, port=0, bus_speed_hz=8000000,
                   transfer_size=4096, gpio_DC=DC_PIN, gpio_RST=RST_PIN)
      device = sh1106(serial, rotate=2)  # sh1106
      draw_scene()
      display_on = True
  else:
      GPIO.output(RST_PIN, GPIO.LOW)
      display_on = False


GPIO.add_event_detect(BTN1_PIN, GPIO.RISING, callback=click_b1, bouncetime=200)
GPIO.add_event_detect(BTN2_PIN, GPIO.RISING, callback=click_b2, bouncetime=200)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING, callback=click_b3, bouncetime=200)
GPIO.add_event_detect(JS_L_PIN, GPIO.RISING, callback=select_left, bouncetime=200)
GPIO.add_event_detect(JS_R_PIN, GPIO.RISING, callback=select_right, bouncetime=200)
GPIO.add_event_detect(JS_U_PIN, GPIO.RISING, callback=select_up, bouncetime=200)
GPIO.add_event_detect(JS_D_PIN, GPIO.RISING, callback=select_down, bouncetime=200)

# Main Loop
try:
    print ("Starting") 
    while True:
        main_fun(0)
        time.sleep(1)

except:
    print("Stopped", sys.exc_info()[0])
    raise
GPIO.cleanup()