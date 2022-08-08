""" Six Pack, Stack & RX Control """

__author__ = 'EB1TR'

import json
import paho.mqtt.client as mqtt
#from gpiozero import LED
import time

TW1DEG = 0
TW2DEG = 0
TW1SET = 0
TW2SET = 0
TW1NEC = 0
TW2NEC = 0

#tw1_cw = LED(6)
#tw1_ccw = LED(13)
#tw2_cw = LED(19)
#tw2_ccw = LED(26)
#tw1_cw.off()
#tw1_ccw.off()
#tw2_cw.off()
#tw2_ccw.off()

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


def on_disconnect(client, userdata, msg):
    print("Conexión MQTT perdida.")


def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT.")
    client.subscribe([
        ("tw1/deg", 0),
        ("tw2/deg", 0),
        ("tw1/set/deg", 0),
        ("tw2/set/deg", 0)
    ])


def nec(dx, pos):
    if abs(dx + 360 - pos) < abs(dx - pos) and dx + 360 < 450:
        dx = dx + 360
        if dx < pos:
            return "CCW"
        elif dx > pos:
            return "CW"
        else:
            return "0"
    else:
        if dx < pos:
            return "CCW"
        elif dx > pos:
            return "CW"
        else:
            return "0"


def gpio_status():
    global TW1DEG, TW2DEG, TW1SET, TW2SET, TW1NEC, TW2NEC
    print("TW1DEG:", str(TW1DEG).ljust(3), " | TW1SET:", str(TW1SET).ljust(3), " | TW1NEC:", TW1NEC)
    print("TW2DEG:", str(TW2DEG).ljust(3), " | TW2SET:", str(TW2SET).ljust(3), " | TW2NEC:", TW2NEC)
    #if TW1NEC == 1:
        #tw1_ccw.off()
        #tw1_cw.on()
    #elif TW1NEC is -1:
        #tw1_cw.off()
        #tw1_ccw.on()
    #else:
        #tw1_cw.off()
        #tw1_ccw.off()
    #if TW2NEC == 1:
        #tw2_ccw.off()
        #tw2_cw.on()
    #elif TW2NEC == -1:
        #tw2_cw.off()
        #tw2_ccw.on()
    #else:
        #tw2_cw.off()
        #tw2_ccw.off()


def on_message(client, userdata, msg):
    try:
        global TW1DEG, TW2DEG, TW1SET, TW2SET, TW1NEC, TW2NEC
        dato = msg.payload.decode('utf-8')
        # Mensajes recibidos desde FRONT
        if msg.topic == "tw1/deg":
            TW1DEG = dato
        elif msg.topic == "tw2/deg":
            TW2DEG = dato
        elif msg.topic == "tw1/set/deg":
            TW1SET = dato
        elif msg.topic == "tw2/set/deg":
            TW2SET = dato
        TW1NEC = nec(int(TW1SET), int(TW1DEG))
        #TW2NEC = nec(int(TW2SET), int(TW2DEG))
        gpio_status()
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
