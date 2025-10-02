import socket
import time

UDP_PORT = 5005
BUFFER_SIZE = 1024

def get_broadcasted_ip(timeout=30):
    """
    Wartet auf eine Broadcast-Nachricht vom Broker.
    Gibt die IP zurück oder None bei Timeout.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", UDP_PORT))
    sock.settimeout(timeout)

    start_time = time.time()

    try:
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                message = data.decode()
                if message.startswith("BROKER_IP:"):
                    broker_ip = message.split(":")[1]
                    print(f"[Client] Broker-IP empfangen: {broker_ip}")
                    return broker_ip
            except socket.timeout:
                if time.time() - start_time > timeout:
                    print("[Client] Timeout: Keine Broker-IP empfangen.")
                    return None
    finally:
        sock.close()
