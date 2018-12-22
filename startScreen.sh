#!/usr/bin/env bash

START_DIR=${0%/*}
[[ -d $START_DIR ]] && cd ${START_DIR}

SESSION_NAME=camera
screen -S "$SESSION_NAME" -d -m -U
screen -S "$SESSION_NAME" -t timelapse -X exec python timelapse.py ~/webdata/camera
screen -S "$SESSION_NAME" -t email -X exec python emailClient.py
