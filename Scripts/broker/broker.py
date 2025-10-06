import socket
import time
import random
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from sense_hat import SenseHat   
import csv


# --------------------------------------------------------------------------
# Globale Variablen
client_ip_list = []
sense = SenseHat()

# Events & Spielzustände
response_event = threading.Event()
current_command = ""
current_client = ""
target_counter = 10 # Anzahl benötigter korrekter Reaktionen für 
game_running = False
correct_count = 0
start_time = 0

# --------------------------------------------------------------------------
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
    """Sendet die Broker-IP regelmäßig per UDP Broadcast ins Netzwerk"""
    ip = get_local_ip()
    message = f"BROKER_IP:{ip}"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        if broadcast_enabled:  # nur senden, wenn aktiviert
            sock.sendto(message.encode(), ("255.255.255.255", UDP_PORT))
        time.sleep(broadcast_interval)


# --------------------------------------------------------------------------
# Spiel-Logik

def start_game():
    """Initialisiert das Spiel"""
    global game_running, correct_count, start_time
    correct_count = 0
    game_running = True
    start_time = time.time()
    send_new_command()


def send_new_command():
    """Wählt zufällig Client + Befehl und sendet ihn"""
    global current_command, current_client
    commands = ["up", "down", "left", "right", "middle"]
    if not client_ip_list:
        print("[Broker] Keine Clients verbunden.")
        return

    current_client = random.choice(client_ip_list)
    current_command = random.choice(commands)

    msg = {"info": "command", "command": current_command}
    publish.single(f"Master/{current_client}", json.dumps(msg),
                   hostname=BROKER_IP, port=BROKER_PORT)
    print(f"[Broker] Neuer Befehl '{current_command}' an {current_client}")
    
# --------------------------------------------------------------------------
# MQTT Callbacks

def on_connect(client, userdata, flags, rc):
    """Wird aufgerufen, wenn die Verbindung mit dem MQTT-Broker steht"""
    print("[MQTT] Verbunden mit Code:", rc)
    client.subscribe("Master")
    for c_ip in client_ip_list:
        client.subscribe(f"Master/{c_ip}")
    

def on_message(client, userdata, msg):
    """Wird aufgerufen, wenn eine MQTT-Nachricht empfangen wurde"""
    global game_running, correct_count, target_counter
    try:
        data = json.loads(msg.payload)  # JSON -> dict
    except:
        print("[MQTT] ⚠️ Nachricht hat falsches Format")
        pass

    if data["info"] == "Subscribe":
        client_ip = data["client_ip"]
        if client_ip not in client_ip_list:   #doppelte Einträge vermeiden
            client_ip_list.append(client_ip)
        client.subscribe(f"Master/{client_ip}")
        print("Neue IP registriert", client_ip)
        return client_ip

    elif data["info"] == "Spielstart":
        # Countdown auf LED-Matrix
        for n in "321":
            sense.show_letter(n)
            time.sleep(1)
            sense.clear()
        start_game()
        

    #Validierung der Antwort
    elif data["info"] == "Antwort" and game_running:
        client_ip = data["client_ip"]
        result = data["result"]

        if client_ip == current_client:
            if result:
                correct_count += 1
                print(f"[Broker] ✅ {client_ip} korrekt! ({correct_count}/{target_counter})")

            else:
                print(f"[Broker] ❌ {client_ip} falsch, erwartet: '{current_command}'")

        if correct_count >= target_counter:
            game_running = False
            elapsed = time.time() - start_time
            print(f"[Broker] 🎉 Ziel erreicht in {elapsed:.2f} Sekunden!")
        else:
            send_new_command()  # sofort neuer Befehl
 

# --------------------------------------------------------------------------
# MQTT starten
def start_mqtt():
    """Erstellt MQTT-Client und startet Loop"""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_IP, BROKER_PORT, 60)
    client.loop_start()  # Thread für MQTT-Nachrichten
    return client

# --------------------------------------------------------------------------
# MAIN
if __name__ == "__main__":
    print("[Broker] Starte...")


    # MQTT starten
    mqtt_client = start_mqtt()
    # UDP-Broadcast in Thread starten
    t1 = threading.Thread(target=broadcast_ip, daemon=True)
    t1.start()

    try:
        while True:
             # Events vom Sense-HAT Joystick abfragen
            for event in sense.stick.get_events():
                if event.action == "pressed":  # auch "released" oder "held" möglich
                    if event.direction == "middle" and not game_running:   # middle = reindrücken
                        print(f"[Broker] Das Spiel wurde gestartet")
                        broadcast_enabled = False

                         # "Spielstart" an Clients senden
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


