import random
import time

def start_game(client_ips, duration=60):
    global current_command, waiting_for_client
    start_time = time.time()

    commands = ["up", "down", "left", "right", "jump", "duck"]

    while time.time() - start_time < duration:
        # zufälligen Client wählen
        waiting_for_client = random.choice(client_ips)
        # zufälligen Befehl wählen
        current_command = random.choice(commands)

        # an genau diesen Client senden
        msg = {"info": "Command", "command": current_command}
        publish.single(f"Master/{waiting_for_client}", json.dumps(msg), hostname=BROKER_IP, port=BROKER_PORT)
        print(f"[Broker] Neuer Befehl '{current_command}' an {waiting_for_client}")

        # auf Antwort warten (max. 5 Sek.)
        response_event.clear()
        if response_event.wait(timeout=5):
            print("[Broker] Antwort erhalten.\n")
        else:
            print("[Broker] ⏱ Timeout bei", waiting_for_client, "\n")
        

