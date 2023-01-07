#!/bin/bash
HOST_CONTROL_VENV=/home/pi/venvs/control
HOST_CONTROL_PYTH=/home/pi/py-rotor-ctrl
cd $HOST_CONTROL_PYTH
. $HOST_CONTROL_VENV/bin/activate
python $HOST_CONTROL_PYTH/control.py &