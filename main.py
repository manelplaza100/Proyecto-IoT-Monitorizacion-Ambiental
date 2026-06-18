import network
import time
from machine import Pin, ADC
import dht
from simple import MQTTClient

# ---------- WIFI ----------
ssid = "Nombre wifi"
password = "**************"

# ---------- MQTT ----------
broker = "broker.hivemq.com"
client_id = "pico_manuel_plaza"

topic_temperatura = b"idc/manuel/temperatura"
topic_humedad = b"idc/manuel/humedad"
topic_humedad_suelo = b"idc/manuel/humedad_suelo"

# ---------- SENSORES ----------
sensor_dht = dht.DHT11(Pin(15))
sensor_suelo = ADC(Pin(26))

# Calibración del sensor de suelo
valor_seco = 65535
valor_mojado = 22000

# ---------- CONECTAR WIFI ----------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Conectando a WiFi...")

contador = 0
while not wlan.isconnected() and contador < 15:
    print("Intentando conectar...")
    time.sleep(1)
    contador += 1

if wlan.isconnected():
    print("WiFi conectado")
    print("IP:", wlan.ifconfig()[0])
else:
    print("No se ha podido conectar al WiFi")
    raise SystemExit

# ---------- CONECTAR MQTT ----------
print("Conectando a MQTT...")
client = MQTTClient(client_id, broker, port=1883)
client.connect()
print("MQTT conectado")

# ---------- BUCLE PRINCIPAL ----------
while True:
    try:
        sensor_dht.measure()

        temperatura = sensor_dht.temperature()
        humedad = sensor_dht.humidity()

        humedad_suelo_raw = sensor_suelo.read_u16()

        humedad_suelo_pct = int((valor_seco - humedad_suelo_raw) * 100 / (valor_seco - valor_mojado))

        if humedad_suelo_pct < 0:
            humedad_suelo_pct = 0

        if humedad_suelo_pct > 100:
            humedad_suelo_pct = 100

        print("Temperatura:", temperatura, "ºC")
        print("Humedad ambiental:", humedad, "%")
        print("Humedad suelo raw:", humedad_suelo_raw)
        print("Humedad suelo:", humedad_suelo_pct, "%")

        client.publish(topic_temperatura, str(temperatura))
        client.publish(topic_humedad, str(humedad))
        client.publish(topic_humedad_suelo, str(humedad_suelo_pct))

        print("Datos enviados por MQTT")
        print("----------------------")

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
