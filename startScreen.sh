#!/usr/bin/env bash

START_DIR=${0%/*}
[[ -d $START_DIR ]] && cd ${START_DIR}

SESSION_NAME=camera
screen -S "$SESSION_NAME" -d -m -U -A 
# screen -S "$SESSION_NAME" -p 0 -t timelapse -Adm python timelapse.py ~/webdata/camera
# screen -S "$SESSION_NAME" -t timelapse -p 2 python timelapse.py ~/webdata/camera
# screen -S "$SESSION_NAME" -t email -Adm python emailClient.py
# screen -S "$SESSION_NAME" -t email -p 3 python emailClient.py

NL=$(echo -ne '\015')
screen -S "$SESSION_NAME" -X screen 1
screen -S "$SESSION_NAME" -p 1 -X stuff "python timelapse.py ~/webdata/camera$NL"
screen -S "$SESSION_NAME" -X screen 2
screen -S "$SESSION_NAME" -p 2 -X stuff "python emailClient.py --section google$NL"
