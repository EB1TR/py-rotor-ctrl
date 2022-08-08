""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt

TW1DEG = 0
TW2DEG = 0
TW1SET = 0
TW2SET = 0

with open('../../cfg/config.json') as json_file:
    data = json.load(json_file)
    CONFIG = dict(data)


def on_disconnect(client, userdata, msg):
    print("Conexión MQTT perdida")
    exit(0)


def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT")
    client.subscribe([
        ("tw1/deg", 0),
        ("tw2/deg", 0),
        ("tw1/set/deg", 0),
        ("tw2/set/deg", 0)
    ])


def nec(dx, pos):
    if dx > pos + 1:
        xx = (dx - pos) - 180
        if xx > 0:
            return -1
        elif xx < 0:
            return 1
        else:
            return 0
    elif dx < pos - 1:
        xx = (dx - pos) + 180
        if xx > 0:
            return -1
        elif xx < 0:
            return 1
        else:
            return 0
    else:
        return 0


def on_message(client, userdata, msg):
    global TW1DEG, TW2DEG, TW1SET, TW2SET
    dato = msg.payload.decode('utf-8')
    # Mensajes recibidos desde FRONT
    if msg.topic == "tw1/deg":
        TW1DEG = dato
        print("TW1DEG:", TW1DEG)
    elif msg.topic == "tw2/deg":
        TW2DEG = dato
        print("TW1DEG:", TW2DEG)
    elif msg.topic == "tw1/set/deg":
        TW1SET = dato
        print("TW1SET:", TW1SET)
    elif msg.topic == "tw2/set/deg":
        TW2SET = dato
        print("TW2SET:", TW2SET)
    print("TW1NEC:", nec(int(TW1SET), int(TW1DEG)))
    print("TW2NEC:", nec(int(TW2SET), int(TW2DEG)))


mqtt_client = mqtt.Client("rotor-mando")
mqtt_client.connect(CONFIG["MQTT_HOST"], CONFIG["MQTT_PORT"], CONFIG["MQTT_KEEP"])
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
mqtt_client.loop_forever()
