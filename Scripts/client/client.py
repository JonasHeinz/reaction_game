import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
from discover_broker import get_broadcasted_ip
from Arrowgame import Arrowgame

# --------------------------------------------------------------------------
# Hilfsfunktionen
def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# --------------------------------------------------------------------------
# MQTT-Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"[Client] Mit MQTT-Broker verbunden (Code: {rc})")
    client.subscribe("Master")                          # hört allgemeine Nachrichten
    client.subscribe(f"Master/{get_local_ip()}")        # hört nur Nachrichten an diese IP

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)  # JSON -> dict
    except:
        pass
   
    if data["info"] == "command": 
        command = data.get("command")
        print(f"[Client] Befehl erhalten: {command}")

        # Blockierend: Arrowgame läuft, bis Ergebnis vorliegt
        result = Arrowgame(command)
        print(f"[Client] Ergebnis: {result}")
        
        data = {
        "info": "Antwort",
        "client_ip": get_local_ip(),
        "result": result,
        }
        message = json.dumps(data)
        
        # Antwort an Broker senden
        publish.single("Master", message, hostname=broker_ip, port=1883)
        print(f"[Client] Antwort an Broker gesendet")
       

# --------------------------------------------------------------------------
# Hauptskript
if __name__ == "__main__":
    broker_ip = get_broadcasted_ip(timeout=3000)
    if not broker_ip:
        print("[Client] Kein Broker gefunden. Beende.")
        exit(1)

    print(f"[Client] Verbinde mit Broker {broker_ip}...")

    # MQTT-Client erzeugen und starten
    client = mqtt.Client(userdata={"broker_ip": broker_ip})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_ip, 1883, 60)
    client.loop_start()

    print(f"[Client] Broker-IP ist {broker_ip}")

    if broker_ip:
        data = {
        "info": "Subscribe",
        "client_ip": get_local_ip(),
        }
        message = json.dumps(data)
        
    publish.single("Master", message, hostname=broker_ip, port=1883)
    print(f"[Client] IP-Adresse an Broker gesendet.")

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Client] 🛑 Beendet.")