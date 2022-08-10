#!/bin/bash
HOST_MANDO_VENV=/home/pi/venvs/mando
HOST_MANDO_PYTH=/home/pi/py-rotor-ctrl/svc/mando
cd $HOST_MANDO_PYTH
. $HOST_MANDO_VENV/bin/activate
python $HOST_MANDO_PYTH/mando.py &