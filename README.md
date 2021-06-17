# PyRecord - Record Audio with Audacity and Patchbox OS

This repository is a project setup for recording audio on your Raspberry Pi or Pisound. As scripting language python is used, which
can control Audacity using a FIFO pipe
I use it to record my music and sounds from Orac without having to connect an external display.
This project uses the SH1106 display with the SPI driver but can also run on a different display with some adjustments.
Tested on Patchbox OS

## Features

- Record arbitrary length of samples by pressing button
- Shows recording duration
- Discard recordings 
- Export recordings and enter a name on the display

## Installation

### Requirements

- Python3
- Audacity minimum version 2.4.2 (requires mod-script-pipe, for scripting audacity)
- pip3
- luma.core, luma.oled, PIL (maybe some other python libraries)

Audacity can be built from source as described here:
https://github.com/audacity/audacity/blob/master/BUILDING.md

### Start script

To start audacity in headless mode, run 

`export DISPLAY=:0`
`./path/to/audacity`

Then, run the interactive python script which will drive the display and start/stop recording in audacity on button presses.

`python3 record_interactive.sh`

### Auto start on boot with systemd

To start audacity and the script on reboot, we can configure an autostart with systemd:

`systemctl start pyrecord.service`
`systemctl enable pyrecord.service`

To check status:

`systemctl status pyrecord.service`

I added a short delay on startup to prevent audacity from crashing, so it takes a few seconds to startup.

### Necessary Adjustments 

You will need to adjust the executable path of the python script
and your audacity executable in both of the `.sh` files and the `.service` file
