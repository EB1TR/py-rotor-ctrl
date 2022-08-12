""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt
import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()


flag_connected = False

try:
    with open('../../cfg/config.json') as json_file:
        data = json.load(json_file)
        CONFIG = dict(data)
        MQTT_HOST = CONFIG['MQTT_HOST']
        MQTT_PORT = CONFIG['MQTT_PORT']
        MQTT_KEEP = CONFIG['MQTT_KEEP']
except Exception as e:
    print("Error abriendo fichero de configuración.")
    print(e)


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


GAIN = 1

while True:
    if not flag_connected:
        try:
            mqtt_client = conn_mqtt()
            flag_connected = True
        except:
            pass
    else:
        raw_tw1 = adc.read_adc(0, gain=GAIN)
        # raw_tw2 = adc.read_adc(1, gain=GAIN)
        tw1_deg = (raw_tw1 * 450) / 26335
        # tw2_deg = (raw_tw2 * 450) / 26335
        mqtt_client.publish("tw1/deg", int(tw1_deg))
        # mqtt_client.publish("tw2/deg", tw2_deg)
        mqtt_client.loop(timeout=1.0, max_packets=1)
    time.sleep(0.2)
