#!/bin/bash
HOST_CMD_VENV=/home/pi/venvs/mando
HOST_CMD_PYTH=/home/pi/py-rotor-ctrl/svc/mando
. $HOST_CMD_VENV/bin/activate
python $HOST_CMD_PYTH/mando.py &