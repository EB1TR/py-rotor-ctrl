""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt
import random
import time
# import Adafruit_ADS1x15
# adc = Adafruit_ADS1x15.ADS1115()


flag_connected = False

with open('../../cfg/config.json') as json_file:
    data = json.load(json_file)
    CONFIG = dict(data)
    MQTT_HOST = CONFIG['MQTT_HOST']
    MQTT_PORT = CONFIG['MQTT_PORT']
    MQTT_KEEP = CONFIG['MQTT_KEEP']


def on_connect(client, userdata, flags, rc):
    global flag_connected
    print("Conectado a MQTT")
    flag_connected = True


def on_disconnect(client, userdata, msg):
    global flag_connected
    print("Conexión MQTT perdida")
    flag_connected = False


def conn_mqtt():
    c = mqtt.Client("rotor-feedback")
    c.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP)
    c.on_connect = on_connect
    c.on_disconnect = on_disconnect
    return c


GAIN = 2/3

while True:
    if not flag_connected:
        try:
            mqtt_client = conn_mqtt()
            flag_connected = True
        except:
            pass
    else:
        tw1rand = random.randint(0, 450)
        tw2rand = random.randint(0, 450)
        # value = adc.read_adc(0, gain=GAIN)
        # value = (value * 6.144) / 32768
        mqtt_client.publish("tw1/deg", tw1rand)
        mqtt_client.publish("tw2/deg", tw2rand)
        mqtt_client.loop(timeout=1.0, max_packets=1)
    time.sleep(0.25)
