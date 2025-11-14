#!/bin/bash

python main.py &
MAIN_PID=$!

sleep 3

python web_panel.py &
WEB_PID=$!

wait
