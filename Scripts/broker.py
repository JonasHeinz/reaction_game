import socket
import time
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from sense_hat import *

# Initalize 
client_ip_list = []
sense = SenseHat()
# Eigene IP ermitteln
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
# --------------------------------------------------------------------------
# UDP Broadcast Einstellungen
UDP_PORT = 5005
broadcast_interval = 5  # Sekunden zwischen den Broadcasts
broadcast_enabled = True  # Steuerung ob Broadcast gesendet wird
BROKER_IP = get_local_ip()  # kann dynamisch gesetzt werden, falls nötig
BROKER_PORT = 1883
# --------------------------------------------------------------------------
# IP-Adresse broadcasten
def broadcast_ip():
    ip = get_local_ip()
    message = f"BROKER_IP:{ip}"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        if broadcast_enabled:  # nur senden, wenn aktiviert
            sock.sendto(message.encode(), ("255.255.255.255", UDP_PORT))
        time.sleep(broadcast_interval)
# -------------------------------------------------------------------------
# Callback: Verbindung hergestellt
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Verbunden mit Code:", rc)
    client.subscribe("Master")
    for c_ip in client_ip_list:
        client.subscribe(f"Master/{c_ip}")
    
# Callback: Nachricht empfangen
def on_message(client, userdata, msg):
    #print(f"[MQTT] Nachricht empfangen: {msg.topic} -> {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload)  # JSON -> dict
    except:
        pass

    if data["info"] == "Subscribe":
        client_ip = data["client_ip"]
        client_ip_list.append(client_ip)
        client.subscribe(f"Master/{client_ip}")
        return client_ip
    
    if data["info"] == "Spielstart":
        for n in "321":
            sense.show_letter(n)
            time.sleep(1)
            sense.clear()
    # Insert here more mqtt- Message handlings

# MQTT-Client starten
def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_IP, BROKER_PORT, 60)
    client.loop_start()  # Thread für MQTT-Nachrichten
    return client

# Nachricht senden
#def send_message(client, topic, payload):
#    client.publish(topic, payload)
#    print(f"[MQTT] Nachricht gesendet: {topic} -> {payload}")

# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("[Broker] Starte...")

    # MQTT starten
    mqtt_client = start_mqtt()

    # UDP-Broadcast in Thread starten
    t1 = threading.Thread(target=broadcast_ip, daemon=True)
    t1.start()

    try:
        while True:
            for event in sense.stick.get_events():
                if event.action == "pressed":  # auch "released" oder "held" möglich
                    if event.direction == "middle":   # middle = reindrücken
                        print(f"[Broker] Das Spiel wurde gestartet")
                        broadcast_enabled = False
                        data = {
                            "info": "Spielstart",
                            "client_ip": get_local_ip(),
                            }
                        message = json.dumps(data)
                        publish.single("Master", message, hostname=BROKER_IP, port=1883)
                        time.sleep(3)
                        
            time.sleep(0.1)
            # Beispiel: Nachricht senden (optional, später an Spiel-Logik ankoppeln)
            # send_message(mqtt_client, "Master/gameStatus", "running")
    except KeyboardInterrupt:
        print("\n[Broker] Beendet.")


