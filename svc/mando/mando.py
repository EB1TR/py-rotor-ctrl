""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from gpiozero import LED
import time

TW1DEG = 0
TW2DEG = 0
TW1SET = 0
TW2SET = 0
TW1NEC = 0
TW2NEC = 0

tw1_cw = LED(6)
tw1_ccw = LED(13)
tw2_cw = LED(19)
tw2_ccw = LED(26)
tw1_cw.off()
tw1_ccw.off()
tw2_cw.off()
tw2_ccw.off()

try:
    with open('../../cfg/config.json') as json_file:
        data = json.load(json_file)
        CONFIG = dict(data)
        MQTT_HOST = CONFIG['MQTT_HOST']
        MQTT_PORT = CONFIG['MQTT_PORT']
        MQTT_KEEP = CONFIG['MQTT_KEEP']
        TW1MODE = CONFIG['TW1MODE']
        TW2MODE = CONFIG['TW2MODE']
except Exception as e:
    print("Error abriendo fichero de configuración.")
    print(e)


def on_disconnect(client, userdata, msg):
    print("Conexión MQTT perdida.")


def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT.")
    client.subscribe([
        ("tw1/deg", 0),
        ("tw2/deg", 0),
        ("tw1/set/deg", 0),
        ("tw2/set/deg", 0),
        ("tw1/set/mode", 0),
        ("tw2/set/mode", 0)
    ])


def nec(dx, pos, drift):
    if abs(dx + 360 - pos) < abs(dx - pos) and dx + 360 < 450:
        dx = dx + 360
        if dx < pos - drift:
            return "CCW"
        elif dx > pos + drift:
            return "CW"
        else:
            return "0"
    else:
        if dx < pos - drift:
            return "CCW"
        elif dx > pos + drift:
            return "CW"
        else:
            return "0"


def twn_to_off(twn):
    if twn == 1:
        tw1_cw.off()
        tw1_ccw.off()
    else:
        tw2_cw.off()
        tw2_ccw.off()


def gpio_status(twx):
    global TW1DEG, TW2DEG, TW1SET, TW2SET, TW1NEC, TW2NEC
    if twx == 1:
        print("TW1DEG:", str(TW1DEG).ljust(3), " | TW1SET:", str(TW1SET).ljust(3), " | TW1NEC:", TW1NEC)
        if TW1NEC == "CW":
            tw1_ccw.off()
            tw1_cw.on()
        elif TW1NEC == "CCW":
            tw1_cw.off()
            tw1_ccw.on()
        else:
            tw1_cw.off()
            tw1_ccw.off()
    elif twx == 2:
        print("TW2DEG:", str(TW2DEG).ljust(3), " | TW2SET:", str(TW2SET).ljust(3), " | TW2NEC:", TW2NEC)
        if TW2NEC == "CW":
            tw2_ccw.off()
            tw2_cw.on()
        elif TW2NEC == "CCW":
            tw2_cw.off()
            tw2_ccw.on()
        else:
            tw2_cw.off()
            tw2_ccw.off()
    else:
        pass


def on_message(client, userdata, msg):
    try:
        global TW1DEG, TW2DEG, TW1SET, TW2SET, TW1NEC, TW2NEC, TW1MODE, TW2MODE
        dato = msg.payload.decode('utf-8')
        if msg.topic == "tw1/deg":
            TW1DEG = int(dato)
        elif msg.topic == "tw2/deg":
            TW2DEG = int(dato)
        elif msg.topic == "tw1/set/deg":
            TW1SET = int(dato)
        elif msg.topic == "tw2/set/deg":
            TW2SET = int(dato)
        elif msg.topic == "tw1/set/mode":
            if TW1MODE == "rem":
                TW1MODE = "loc"
                twn_to_off(1)
            else:
                TW1MODE = "rem"
        elif msg.topic == "tw2/set/mode":
            if TW2MODE == "rem":
                TW2MODE = "loc"
                twn_to_off(2)
            else:
                TW2MODE = "rem"
        if TW1MODE == "rem":
            TW1NEC = nec(TW1SET, TW1DEG, 1)
            gpio_status(1)
        if TW2MODE == "rem":
            TW2NEC = nec(TW2SET, TW2DEG, 1)
            gpio_status(2)
        mqtt_client.publish("tw1/mode", TW1MODE)
        mqtt_client.publish("tw2/mode", TW2MODE)
        mqtt_client.publish("tw1/setdeg", TW1SET)
        mqtt_client.publish("tw2/setdeg", TW2SET)
        mqtt_client.publish("tw1/nec", TW1NEC)
        mqtt_client.publish("tw2/nec", TW2NEC)
    except Exception as e:
        print("Error procesando o publicando datos.")
        print(e)


while True:
    try:
        mqtt_client = mqtt.Client("rotor-mando")
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.loop_forever()
    except:
        print("MQTT no disponible.")
        time.sleep(2)
