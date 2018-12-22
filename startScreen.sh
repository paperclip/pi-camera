#!/usr/bin/env bash

START_DIR=${0%/*}
[[ -d $START_DIR ]] && cd ${START_DIR}

SESSION_NAME=camera
screen -S "$SESSION_NAME" -d -m -U
screen -S "$SESSION_NAME" -p 0 -X exec python timelapse.py
screen -S "$SESSION_NAME" -X screen 1
screen -S "$SESSION_NAME" -p 1 -X exec python emailClient.py
