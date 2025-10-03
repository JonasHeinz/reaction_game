import random
import time
from sense_hat import SenseHat

def Arrowgame(timer=5):
    sense = SenseHat()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Einstellungen
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Blinken des Pfeils
    steps = 6
    delay = timer / steps


    # Anzeigefarben
    ON  = (255, 255, 255)  # weiß
    RIGHT = (0, 255, 0)    # grün
    ERR = (255, 0, 0)      # rot
    OFF = (0, 0, 0)        # schwarz

    # Anzeigedauer der X resp CHECK Matrix
    freeze = 0.7

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Event auswählen
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    sense.clear()
    events = ["up", "down", "left", "right", "middle"]
    expected = random.choice(events)

    '''!! Auskommentieren !!'''
    print("Erwarte:", expected)
    '''!! Auskommentieren !!'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Anzeigematrizen
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # ❌ X-Matrix
    X_MATRIX = [
        [0,1,0,0,0,0,1,0],
        [1,1,1,0,0,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,1,0,0,1,1,1],
        [0,1,0,0,0,0,1,0],
    ]

    # ✅ CHECK-Matrix
    CHECK_MATRIX = [
        [0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,1,1],
        [0,0,0,0,0,1,1,0],
        [1,0,0,0,1,1,0,0],
        [1,1,0,1,1,0,0,0],
        [0,1,1,1,0,0,0,0],
        [0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ]

    # Pfeilmatrizen
    arrows = {
        "up": [
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
        ],
        "down": [
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0],
        ],
        "right": [
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,1,1,0,0],
            [0,0,0,0,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,0,0,0,1,1,1,0],
            [0,0,0,0,1,1,0,0],
            [0,0,0,0,1,0,0,0],
        ],
        "left": [
            [0,0,0,1,0,0,0,0],
            [0,0,1,1,0,0,0,0],
            [0,1,1,1,0,0,0,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,0,0,0,0],
            [0,0,1,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
        ],
        "middle": [
            [0,0,0,0,0,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,1,0,0,1,1,0],
            [0,1,1,0,0,1,1,0],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,0,0,0,0,0],
        ]
    }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Hilfsfunktionen
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def show_matrix(matrix, color=ON):
        pixels = [color if bit else OFF for row in matrix for bit in row]
        sense.set_pixels(pixels)

    def show_arrow(direction, color=ON):
        show_matrix(arrows[direction], color)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Gamelogik
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for i in range(steps):
        # Pfeil an
        show_arrow(expected, ON)
        start = time.time()
        while time.time() - start < delay / 2:
            for e in sense.stick.get_events():
                if e.action == "pressed":
                    if e.direction == expected:
                        show_matrix(CHECK_MATRIX, RIGHT)
                        time.sleep(0.5)
                        sense.clear()  # Matrix aus
                        return 't'

                    else:
                        show_matrix(X_MATRIX, ERR)
                        time.sleep(freeze)
                        sense.clear()  # Matrix aus
                        return 'f'

        # Pfeil aus
        sense.clear()
        start = time.time()
        while time.time() - start < delay / 2:
            for e in sense.stick.get_events():
                if e.action == "pressed":
                    if e.direction == expected:
                        show_matrix(CHECK_MATRIX, RIGHT)
                        time.sleep(freeze)
                        sense.clear()  # Matrix aus
                        return 't'
                    else:
                        show_matrix(X_MATRIX, ERR)
                        time.sleep(freeze)
                        sense.clear()  # Matrix aus
                        return 'f'

        delay *= freeze

    # Zeit abgelaufen
    show_matrix(X_MATRIX, ERR)
    time.sleep(freeze)
    sense.clear()  # Matrix aus
    return 'f'

