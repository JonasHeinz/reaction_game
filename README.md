# reaction_game

Wenn Probleme auf Raspberry PI mit RTIMU not found neues venv erstellen wie folgt:
python -m venv ~/.env --system-site-packages
source ~/.env/bin/activate
pip install paho-mqtt

-> So laufen lassen, es braucht ein venv dass Zugriff auf Systemvariablen hat.

Benutzung:
Auf Client client.py mit python client.py starten
Auf Broker broker.py mit python broker.py starten
-> Verbindung und Listenings auf Kanäle sollte automatisch erstellt werden.
Läuft auf allen Raspberrys, keine hardcoded IP-Adressen verwendet.
Client meldet sich automatisch bei Broker an als Mitspieler. Wenn Joystick auf Broker
gedrückt wird, endet anmeldesequenz und Spiel Startet. (Hier aktuell noch Countdown Clientseitig 
auskommentiert, das läuft bei mir am PC nicht. Ich habe immer Broker aufm Raspberry und Client aufm
Laptop laufen)
