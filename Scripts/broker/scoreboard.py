import csv
import os

DATEINAME = "../data/Scoreboard.csv"
def add_scoreboard(time, ip):
    rangliste = get_scoreboard()

    # Neuen Eintrag hinzufügen
    neuer_eintrag = {'ip': ip, 'time': time}
    rangliste.append(neuer_eintrag)

    # Rangliste nach time sortieren (kleinere Zeit = besser)
    rangliste = sorted(rangliste, key=lambda x: x['time'])

    # Position des neuen Eintrags finden (1-basiert)
    position = next(i + 1 for i, eintrag in enumerate(rangliste) if eintrag == neuer_eintrag)

    # In CSV schreiben (überschreiben)
    with open(DATEINAME, mode='w', newline='', encoding='utf-8') as f:
        feldnamen = ['ip', 'time']
        writer = csv.DictWriter(f, fieldnames=feldnamen)
        writer.writeheader()
        writer.writerows(rangliste)


    return position

def get_scoreboard():
    if not os.path.exists(DATEINAME):
        return []

    with open(DATEINAME, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rangliste = [
            {'ip': row['ip'], 'time': float(row['time'])} for row in reader
        ]
    # Nach time sortieren, kleinere Zeit zuerst
    return sorted(rangliste, key=lambda x: x['time'])

