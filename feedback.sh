#!/bin/bash
HOST_CMD_VENV=/home/pi/venvs/feedback
HOST_CMD_PYTH=/home/pi/py-rotor-ctrl/svc/feedback
. $HOST_CMD_VENV/bin/activate
python $HOST_CMD_PYTH/feedback.py &