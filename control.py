""" Control de Rotores ED1B """

__author__ = 'EB1TR'

# Librería estándar ----------------------------------------------------------------------------------------------------
#
import json
import time
# ----------------------------------------------------------------------------------------------------------------------

# Librerías instaladas -------------------------------------------------------------------------------------------------
#
import paho.mqtt.client as mqtt
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
from gpiozero import LED
# ----------------------------------------------------------------------------------------------------------------------

# Intancia del ADC -----------------------------------------------------------------------------------------------------
#
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
# ----------------------------------------------------------------------------------------------------------------------

# Variables de uso GLOBAL ----------------------------------------------------------------------------------------------
#
TW1DEG = TW2DEG = TW3DEG = TW1SET = TW2SET = TW3SET = TW1NEC = TW2NEC = TW3NEC = 0
TS_ADC = time.time()
TS_ADC_SHIFT = 0.1
LAST_ADC = 3
# ----------------------------------------------------------------------------------------------------------------------


# Carga de configurtaciones --------------------------------------------------------------------------------------------
#
try:
    with open('cfg/config.json') as json_file:
        data = json.load(json_file)
        CONFIG = dict(data)
        MQTT_HOST = CONFIG['MQTT_HOST']
        MQTT_PORT = CONFIG['MQTT_PORT']
        MQTT_KEEP = CONFIG['MQTT_KEEP']
        TW1MODE = CONFIG['TW1MODE']
        TW2MODE = CONFIG['TW2MODE']
        TW3MODE = CONFIG['TW3MODE']
except Exception as e:
    print("Error abriendo fichero de configuración.")
    print(e)
    exit(0)
# ----------------------------------------------------------------------------------------------------------------------


# Puesta a OFF de los GPIOs --------------------------------------------------------------------------------------------
#
def twn_to_off(twn):
    if twn == 1:
        tw1_cw.off()
        tw1_ccw.off()
    elif twn == 2:
        tw2_cw.off()
        tw2_ccw.off()
    elif twn == 3:
        pass
        # tw3_cw.off()
        # tw3_ccw.off()
    else:
        tw1_cw.off()
        tw1_ccw.off()
        tw2_cw.off()
        tw2_ccw.off()
        # tw3_cw.off()
        # tw3_ccw.off()
# ----------------------------------------------------------------------------------------------------------------------


# Cálculo de CW, CCW o 0 (no mover) ------------------------------------------------------------------------------------
#
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
# ----------------------------------------------------------------------------------------------------------------------


# Modifica estado de los GPIO según necesidad --------------------------------------------------------------------------
#
def gpio_status(twx):
    global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC
    if twx == 1:
        print("TW1DEG:", str(TW1DEG).ljust(3), " | TW1SET:", str(TW1SET).ljust(3), " | TW1NEC:", TW1NEC)
        if TW1NEC == "CW":
            tw1_ccw.off()
            tw1_cw.on()
        elif TW1NEC == "CCW":
            tw1_cw.off()
            tw1_ccw.on()
        else:
            twn_to_off(1)
    elif twx == 2:
        print("TW2DEG:", str(TW2DEG).ljust(3), " | TW2SET:", str(TW2SET).ljust(3), " | TW2NEC:", TW2NEC)
        if TW2NEC == "CW":
            tw2_ccw.off()
            tw2_cw.on()
        elif TW2NEC == "CCW":
            tw2_cw.off()
            tw2_ccw.on()
        else:
            twn_to_off(2)
    else:
        pass
        # print("TW3DEG:", str(TW3DEG).ljust(3), " | TW3SET:", str(TW3SET).ljust(3), " | TW3NEC:", TW3NEC)
        # if TW3NEC == "CW":
        #    tw3_ccw.off()
        #    tw3_cw.on()
        # elif TW3NEC == "CCW":
        #    tw3_cw.off()
        #    tw3_ccw.on()
        # else:
        #    twn_to_off(3)
# ----------------------------------------------------------------------------------------------------------------------


# Corrección de dirección si está en remoto y es necesario -------------------------------------------------------------
#
def correct_deg():
    global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC
    if TW1MODE == "rem":
        TW1NEC = nec(TW1SET, TW1DEG, 1)
        gpio_status(1)
    if TW2MODE == "rem":
        TW2NEC = nec(TW2SET, TW2DEG, 1)
        gpio_status(2)
    if TW3MODE == "rem":
        TW2NEC = nec(TW3SET, TW3DEG, 1)
        gpio_status(3)
# ----------------------------------------------------------------------------------------------------------------------


# Acciones si la conexión MQTT falla -----------------------------------------------------------------------------------
#
def on_connect_fail(client, userdata, rc):
    print("Conexión fallida MQTT:  " + str(rc))
    time.sleep(1)
# ----------------------------------------------------------------------------------------------------------------------


# Acciones al conectar a MQTT ------------------------------------------------------------------------------------------
#
def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT.")
    client.subscribe([
        ("tw1/set/deg", 0),
        ("tw2/set/deg", 0),
        ("tw3/set/deg", 0),
        ("tw1/set/mode", 0),
        ("tw2/set/mode", 0),
        ("tw3/set/mode", 0)
    ])
    print("Suscrito a topics.")
    flag_connected = True
# ----------------------------------------------------------------------------------------------------------------------


# Acciones en eventual desconexión MQTT --------------------------------------------------------------------------------
#
def on_disconnect(client, userdata, rc):
    print("Desconectado de MQTT:  " + str(rc))
    time.sleep(1)
# ----------------------------------------------------------------------------------------------------------------------


# Acciones al recibir un mensaje por MQTT ------------------------------------------------------------------------------
#
def on_message(client, userdata, msg):
    try:
        global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC, TW1MODE, TW2MODE, TW3MODE
        dato = msg.payload.decode('utf-8')
        if msg.topic == "tw1/set/deg":
            TW1SET = int(dato)
        elif msg.topic == "tw2/set/deg":
            TW2SET = int(dato)
        elif msg.topic == "tw3/set/deg":
            TW3SET = int(dato)
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
        elif msg.topic == "tw3/set/mode":
            if TW3MODE == "rem":
                TW3MODE = "loc"
                twn_to_off(2)
            else:
                TW3MODE = "rem"
    except Exception as e:
        print("Error procesando datos.")
        print(e)
# ----------------------------------------------------------------------------------------------------------------------


# Definición de GPIO y puesta a OFF ------------------------------------------------------------------------------------
#
tw1_cw = LED(19)
tw1_ccw = LED(26)
tw2_cw = LED(6)
tw2_ccw = LED(13)
# tw3_cw = LED()
# tw3_ccw = LED()
twn_to_off(0)
# ----------------------------------------------------------------------------------------------------------------------

# Instancia, definición de acciones, conexión MQTT y comienzo de LOOP (asíncrono) --------------------------------------
#
mqtt_client = mqtt.Client("rotor-feedback")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_connect_fail = on_connect_fail
mqtt_client.connect_async(MQTT_HOST, MQTT_PORT, MQTT_KEEP)
mqtt_client.loop_start()
# ----------------------------------------------------------------------------------------------------------------------

# Loop principal (ADC, cálculos y publicación MQTT) --------------------------------------------------------------------
#
print("Arranca 'Control de Rotores'")
print("MQTT Desconectado, intentando conexión.")
while True:
    # Lectura de los ADC y conversión a grados -------------------------------------------------------------------------
    #
    if TS_ADC + TS_ADC_SHIFT <= time.time() and LAST_ADC == 3:
        raw_tw1 = adc.read_adc(0, gain=GAIN)
        TW1DEG = (raw_tw1 * 450) / 26335
        TS_ADC = time.time()
        LAST_ADC = 1
    elif TS_ADC + TS_ADC_SHIFT <= time.time() and LAST_ADC == 1:
        raw_tw2 = adc.read_adc(1, gain=GAIN)
        TW2DEG = (raw_tw2 * 450) / 26335
        TS_ADC = time.time()
        LAST_ADC = 2
    elif TS_ADC + TS_ADC_SHIFT <= time.time() and LAST_ADC == 2:
        # raw_tw3 = adc.read_adc(2, gain=GAIN)
        # TW3DEG = (raw_tw3 * 450) / 26335
        TS_ADC = time.time()
        LAST_ADC = 3
    else:
        pass
    # ------------------------------------------------------------------------------------------------------------------

    # Evaluación de corrección -----------------------------------------------------------------------------------------
    #
    correct_deg()
    # ------------------------------------------------------------------------------------------------------------------

    # Publicación a MQTT -----------------------------------------------------------------------------------------------
    #
    mqtt_client.publish("tw1/deg", int(TW1DEG))
    mqtt_client.publish("tw2/deg", int(TW2DEG))
    mqtt_client.publish("tw3/deg", int(TW3DEG))
    mqtt_client.publish("tw1/mode", TW1MODE)
    mqtt_client.publish("tw2/mode", TW2MODE)
    mqtt_client.publish("tw3/mode", TW2MODE)
    mqtt_client.publish("tw1/setdeg", TW1SET)
    mqtt_client.publish("tw2/setdeg", TW2SET)
    mqtt_client.publish("tw3/setdeg", TW3SET)
    mqtt_client.publish("tw1/nec", TW1NEC)
    mqtt_client.publish("tw2/nec", TW2NEC)
    mqtt_client.publish("tw3/nec", TW3NEC)
    # ------------------------------------------------------------------------------------------------------------------

    # Sleep para evitar sobrecarga de CPU ------------------------------------------------------------------------------
    #
    time.sleep(0.033)
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
