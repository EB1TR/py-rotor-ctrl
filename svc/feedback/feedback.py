""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt

import time
# import Adafruit_ADS1x15
# adc = Adafruit_ADS1x15.ADS1115()

MQTT_HOST = "192.168.33.85"
MQTT_PORT = 1883
MQTT_KEEP = 600


try:
    with open('../../cfg/config.json') as json_file:
        data = json.load(json_file)
        STACKS = dict(data)
except Exception as e:
    print("Error abriendo la configuración: %s" % e)


def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT")


def on_disconect(client, userdata, msg):
    print("Conexión MQTT perdida")
    exit(0)


mqtt_client = mqtt.Client("rotor-feedback")
mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconect

GAIN = 2/3
val = 0
while True:
    value = 0.0
    # value = adc.read_adc(0, gain=GAIN)
    # value = (value * 6.144) / 32768
    mqtt_client.publish("tw1/deg", value)
    print(value)
    time.sleep(0.1)

