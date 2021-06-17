#!/bin/bash

#start audacity
bash /home/patch/Workspace/Tests/start_audacity.sh & 

sleep 25

#start script that will interact with display
python3 /home/patch/Workspace/Tests/record_interactive.py
