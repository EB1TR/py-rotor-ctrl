""" Control de Rotores ED1B """

__author__ = 'EB1TR'

# Librería estándar ----------------------------------------------------------------------------------------------------
#
import network
import time
import machine
from machine import Pin
import ubinascii
# ----------------------------------------------------------------------------------------------------------------------

# Librerías instaladas -------------------------------------------------------------------------------------------------
#
from umqtt import MQTTClient
# ----------------------------------------------------------------------------------------------------------------------

# Definición de datos de conexión WLAN
ssid = ""
password = ""

# Definición de datos del servidor MQTT
MQTT_HOST = ""
MQTT_PORT = 1883
MQTT_KEEP = 3
MQTT_ID = "rotor-control-dev"

client_id = ubinascii.hexlify(machine.unique_id())

# Instancia de WLAN
wlan = network.WLAN(network.STA_IF)

mqtt_flag = True



# Intancias del ADC ----------------------------------------------------------------------------------------------------
#
adc_tw1 = Pin(26, Pin.IN)
adc_tw2 = Pin(27, Pin.IN)
adc_tw3 = Pin(28, Pin.IN)
adc_tw1= machine.ADC(0)
adc_tw2= machine.ADC(1)
adc_tw3= machine.ADC(2)
# ----------------------------------------------------------------------------------------------------------------------

# Variables de uso GLOBAL ----------------------------------------------------------------------------------------------
#
TW1DEG = TW2DEG = TW3DEG = TW1SET = TW2SET = TW3SET = TW1NEC = TW2NEC = TW3NEC = 0
LAST_ADC = 3
# ----------------------------------------------------------------------------------------------------------------------


# Carga de configurtaciones --------------------------------------------------------------------------------------------
#

TW1MODE = TW2MODE = TW3MODE = "loc"
# ----------------------------------------------------------------------------------------------------------------------


# Puesta a OFF de los GPIOs --------------------------------------------------------------------------------------------
#
def twn_to_off(twn):
    if twn == 1:
        tw1_cw.value(0)
        tw1_ccw.value(0)
        tw1_act.value(0)
    elif twn == 2:
        tw2_cw.value(0)
        tw2_ccw.value(0)
        tw2_act.value(0)
    elif twn == 3:
        tw3_cw.value(0)
        tw3_ccw.value(0)
        tw3_act.value(0)
    else:
        tw1_cw.value(0)
        tw1_ccw.value(0)
        tw1_act.value(0)
        tw2_cw.value(0)
        tw2_ccw.value(0)
        tw2_act.value(0)
        tw3_cw.value(0)
        tw3_ccw.value(0)
        tw3_act.value(0)
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
    global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC, TW1MODE, TW2MODE, TW3MODE
    if twx == 1:
        # print("TW1DEG:", TW1DEG, " | TW1SET:", TW1SET, " | TW1NEC:", TW1NEC, " | TW1MODE:", TW1MODE)
        if TW1NEC == "CW":
            tw1_ccw.value(0)
            tw1_cw.value(1)
            tw1_act.value(1)
        elif TW1NEC == "CCW":
            tw1_cw.value(0)
            tw1_ccw.value(1)
            tw1_act.value(1)
        else:
            twn_to_off(1)
    elif twx == 2:
        # print("TW2DEG:", TW2DEG, " | TW2SET:", TW2SET, " | TW2NEC:", TW2NEC, " | TW2MODE:", TW2MODE)
        if TW2NEC == "CW":
            tw2_ccw.value(0)
            tw2_cw.value(1)
            tw2_act.value(1)
        elif TW2NEC == "CCW":
            tw2_cw.value(0)
            tw2_ccw.value(1)
            tw2_act.value(1)
        else:
            twn_to_off(2)
    else:
        print("TW3DEG:", TW3DEG, " | TW3SET:", TW3SET, " | TW3NEC:", TW3NEC, " | TW3MODE:", TW3MODE)
        if TW3NEC == "CW":
            tw3_ccw.value(0)
            tw3_cw.value(1)
            tw3_act.value(1)
        elif TW3NEC == "CCW":
            tw3_cw.value(0)
            tw3_ccw.value(1)
            tw3_act.value(1)
        else:
           twn_to_off(3)
# ----------------------------------------------------------------------------------------------------------------------


# Corrección de dirección si está en remoto y es necesario -------------------------------------------------------------
#
def correct_deg():
    global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC
    if TW1MODE == "rem":
        TW1NEC = nec(TW1SET, TW1DEG, 2)
        gpio_status(1)

    if TW2MODE == "rem":
        TW2NEC = nec(TW2SET, TW2DEG, 2)
        gpio_status(2)

    if TW3MODE == "rem":
        if TW3NEC != "0":
            TW3DEG_SHIFT = TW3DEG + 8
            TW3NEC = nec(TW3SET, TW3DEG_SHIFT, 5)
        else:
            TW3NEC = nec(TW3SET, TW3DEG, 5)
        gpio_status(3)
# ----------------------------------------------------------------------------------------------------------------------


# Acciones al recibir un mensaje por MQTT ------------------------------------------------------------------------------
#
def sub_cb(topic, msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    try:
        global TW1DEG, TW2DEG, TW3DEG, TW1SET, TW2SET, TW3SET, TW1NEC, TW2NEC, TW3NEC, TW1MODE, TW2MODE, TW3MODE
        if topic == "tw1/set/deg":
            TW1SET = int(msg)
        elif topic == "tw2/set/deg":
            TW2SET = int(msg)
        elif topic == "tw3/set/deg":
            TW3SET = int(msg)
        elif topic == "tw1/set/mode":
            if TW1MODE == "rem":
                TW1MODE = "loc"
                twn_to_off(1)
            else:
                TW1MODE = "rem"
        elif topic == "tw2/set/mode":
            if TW2MODE == "rem":
                TW2MODE = "loc"
                twn_to_off(2)
            else:
                TW2MODE = "rem"
        elif topic == "tw3/set/mode":
            if TW3MODE == "rem":
                TW3MODE = "loc"
                twn_to_off(3)
            else:
                TW3MODE = "rem"
    except:
        print("Error procesando datos.")

# ----------------------------------------------------------------------------------------------------------------------


# Definición de GPIO y puesta a OFF ------------------------------------------------------------------------------------
#
tw1_cw = Pin(5, Pin.OUT)
tw1_ccw = Pin(4, Pin.OUT)
tw1_act = Pin(6, Pin.OUT)
tw2_cw = Pin(11, Pin.OUT)
tw2_ccw = Pin(10, Pin.OUT)
tw2_act = Pin(7, Pin.OUT)
tw3_cw = Pin(15, Pin.OUT)
tw3_ccw = Pin(14, Pin.OUT)
tw3_act = Pin(8, Pin.OUT)

led_mqtt = Pin(21, Pin.OUT)
led_wifi = Pin(20, Pin.OUT)

twn_to_off(0)
# ----------------------------------------------------------------------------------------------------------------------

# Instancia, definición de acciones, conexión MQTT y comienzo de LOOP (asíncrono) --------------------------------------
#

# ----------------------------------------------------------------------------------------------------------------------


# Loop principal (ADC, cálculos y publicación MQTT) --------------------------------------------------------------------
#
print("Arranca 'Control de Rotores'")

def connect_wlan():
    #Connect to WLAN
    led_wifi.value(0)
    led_mqtt.value(0)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Esperando WLAN...')
        time.sleep(1)
    led_wifi.value(1)
    print(wlan.ifconfig())

try:
    connect_wlan()
    need_mqtt = True
    while need_mqtt:
        led_mqtt.value(0)
        print('Instanciando MQTT')
        c =  MQTTClient(MQTT_ID, MQTT_HOST, port=MQTT_PORT, user=None, password=None, keepalive=MQTT_KEEP, ssl=False, ssl_params={})
        print('Intentando conexión MQTT')
        c.set_callback(sub_cb)
        try:
            c.connect()
            c.subscribe(b'tw1/set/deg')
            c.subscribe(b'tw2/set/deg')
            c.subscribe(b'tw3/set/deg')
            c.subscribe(b'tw1/set/mode')
            c.subscribe(b'tw2/set/mode')
            c.subscribe(b'tw3/set/mode')
            print('Conectado al Broker MQTT.')
            need_mqtt = False
            led_mqtt.value(1)
            if not need_mqtt:
                while wlan.isconnected():
                    c.check_msg()
                    # Lectura de los ADC y conversión a grados -------------------------------------------------------------------------
                    #
                    if LAST_ADC == 3:
                        raw_tw1 = adc_tw1.read_u16()
                        TW1DEG = int((raw_tw1 * 450) / 65535)
                        LAST_ADC = 1
                    elif LAST_ADC == 1:
                        raw_tw2 = adc_tw2.read_u16()
                        TW2DEG = int((raw_tw2 * 450) / 65535)
                        LAST_ADC = 2
                    elif LAST_ADC == 2:
                        raw_tw3 = adc_tw3.read_u16()
                        raw_tw3 = (raw_tw3 - 3800) * (65535 - 0) // (65535 - 3800) + 0
                        TW3DEG = int(((raw_tw3 * 450) / 65535))
                        if 0 <= TW3DEG <= 45:
                            TW3DEG = TW3DEG * 1.07
                        elif 46 <= TW3DEG <= 90:
                            TW3DEG = TW3DEG * 0.862
                        elif 91 <= TW3DEG <= 135:
                            TW3DEG = TW3DEG * 0.827
                        elif 136 <= TW3DEG <= 180:
                            TW3DEG = TW3DEG * 0.888
                        elif 181 <= TW3DEG <= 225:
                            TW3DEG = TW3DEG * 0.843
                        elif 226 <= TW3DEG <= 270:
                            TW3DEG = TW3DEG * 0.867
                        elif 271 <= TW3DEG <= 315:
                            TW3DEG = TW3DEG * 0.895
                        elif 316 <= TW3DEG <= 360:
                            TW3DEG = TW3DEG * 0.927
                        elif 361 <= TW3DEG <= 405:
                            TW3DEG = TW3DEG * 0.96
                        elif 406 <= TW3DEG <= 450:
                            TW3DEG = TW3DEG * 0.979
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
                    c.publish("tw1/deg", str(TW1DEG))
                    c.publish("tw2/deg", str(TW2DEG))
                    c.publish("tw3/deg", str(TW3DEG))
                    c.publish("tw1/mode", str(TW1MODE))
                    c.publish("tw2/mode", str(TW2MODE))
                    c.publish("tw3/mode", str(TW3MODE))
                    c.publish("tw1/setdeg", str(TW1SET))
                    c.publish("tw2/setdeg", str(TW2SET))
                    c.publish("tw3/setdeg", str(TW3SET))
                    c.publish("tw1/nec", str(TW1NEC))
                    c.publish("tw2/nec", str(TW2NEC))
                    c.publish("tw3/nec", str(TW3NEC))
                    time.sleep_ms(100)
                    # ------------------------------------------------------------------------------------------------------------------
                print("Desconexión WIFI")
                led_mqtt.value(0)
                led_wifi.value(0)
                machine.reset()
                connect_wlan()
                need_mqtt = True
        except:
            if wlan.isconnected() == False:
                print("Excepción WIFI")
                connect_wlan()
            else:
                print("Excepción MQTT")
                need_mqtt = True
            time.sleep(1)
except KeyboardIterrupt:
    print("Excepción WIFI")
    machine.reset()
    time.sleep(1)
