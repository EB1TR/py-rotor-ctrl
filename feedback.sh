#!/bin/bash
HOST_FEEDBACK_VENV=/home/pi/venvs/feedback
HOST_FEEDBACK_PYTH=/home/pi/py-rotor-ctrl/svc/feedback
cd $HOST_FEEDBACK_PYTH
. $HOST_FEEDBACK_VENV/bin/activate
python $HOST_FEEDBACK_PYTH/feedback.py &