import os
import sys
import time
import math
import random


# ============================================================
# CUADRÍCULA FIJA
# ============================================================

WIDTH = 107
HEIGHT = 14
FPS = 20


# ============================================================
# ÁRBOL
# ============================================================

TREE = r"""       ***        **  **  ***
     ******     ****** ********
    ***\/****  **\/**\/__/***
   **\  \   |  |  \__// **\*****
  ***/\_ \________/~_/   ***** |
******* \/~-_______/  **  **   |
|  **\__//~/____   \__/***
|  **/* \_____ ~\_   *\*******
|   ****      \_\~\  ******  |
      |        ////    * |   |
      |       ////       |
             /~~~\ """


TREE_LINES = TREE.splitlines()
TREE_W = max(len(line) for line in TREE_LINES)
TREE_H = len(TREE_LINES)

# Centrado REAL dentro de 107 columnas
TREE_X = (WIDTH - TREE_W) // 2

# Dejamos espacio debajo para que caigan hojas.
TREE_Y = 1


# ============================================================
# COLORES
# ============================================================

RESET = "\033[0m"

# *
BLUE = "\033[38;5;39m"

# |
CYAN = "\033[38;5;45m"

# / \ _ -
BROWN = "\033[38;5;94m"

# ~
LIGHT_BROWN = "\033[38;5;130m"


# ============================================================
# POSICIONES DE HOJAS REALES DEL ÁRBOL
# ============================================================

LEAF_POSITIONS = []

for y, line in enumerate(TREE_LINES):
    for x, char in enumerate(line):

        if char == "*":
            LEAF_POSITIONS.append(
                (
                    TREE_X + x,
                    TREE_Y + y
                )
            )


# ============================================================
# PARTÍCULA
# ============================================================

class Leaf:

    def __init__(self):
        self.active = False

    def spawn(self):

        x, y = random.choice(LEAF_POSITIONS)

        self.x = float(x)
        self.y = float(y)

        # ----------------------------------------------------
        # DIRECCIÓN DEL VIENTO
        #
        # Claramente diagonal.
        # ----------------------------------------------------

        direction = random.choice([
            1,
            1,
            1,
            -1
        ])

        self.vx = random.uniform(
            0.10,
            0.22
        ) * direction

        self.vy = random.uniform(
            0.08,
            0.14
        )

        # Cada hoja serpentea distinto
        self.phase = random.uniform(
            0,
            math.tau
        )

        self.wave_speed = random.uniform(
            0.15,
            0.28
        )

        self.wave_amount = random.uniform(
            0.05,
            0.12
        )

        self.char = random.choice([
            "*",
            "*",
            "*",
            "✦",
            "·"
        ])

        self.active = True

    def update(self, frame):

        if not self.active:
            return

        # Movimiento diagonal principal
        self.x += self.vx
        self.y += self.vy

        # ----------------------------------------------------
        # AIRE
        #
        # Hace que no sea una diagonal perfectamente recta.
        # ----------------------------------------------------

        self.x += (
            math.sin(
                frame * self.wave_speed
                + self.phase
            )
            * self.wave_amount
        )

        # Pequeña turbulencia ocasional
        if random.random() < 0.025:

            self.vx += random.uniform(
                -0.05,
                0.08
            )

        # ----------------------------------------------------
        # FUERA DE LA CUADRÍCULA
        # ----------------------------------------------------

        if (
            self.x < 0
            or self.x >= WIDTH
            or self.y >= HEIGHT
        ):
            self.active = False


# ============================================================
# POOL DE HOJAS
# ============================================================

particles = [
    Leaf()
    for _ in range(12)
]


# ============================================================
# SPAWN
# ============================================================

def spawn_leaf():

    inactive = [
        leaf
        for leaf in particles
        if not leaf.active
    ]

    if not inactive:
        return

    random.choice(inactive).spawn()


# ============================================================
# COLOR
# ============================================================

def get_color(char):

    # HOJAS
    if char == "*":
        return BLUE

    # LIANAS
    if char == "|":
        return CYAN

    # MADERA
    if char in "/\\_-":
        return BROWN

    # MADERA CLARA
    if char == "~":
        return LIGHT_BROWN

    return RESET


# ============================================================
# RENDER
# ============================================================

def render():

    # EXACTAMENTE:
    #
    # 107 columnas
    # 16 filas

    canvas = [
        [" "] * WIDTH
        for _ in range(HEIGHT)
    ]

    colors = [
        [None] * WIDTH
        for _ in range(HEIGHT)
    ]

    # --------------------------------------------------------
    # ÁRBOL
    # --------------------------------------------------------

    for y, line in enumerate(TREE_LINES):

        cy = TREE_Y + y

        if cy >= HEIGHT:
            break

        for x, char in enumerate(line):

            if char == " ":
                continue

            cx = TREE_X + x

            if 0 <= cx < WIDTH:

                canvas[cy][cx] = char
                colors[cy][cx] = get_color(char)

    # --------------------------------------------------------
    # HOJAS VOLANDO
    # --------------------------------------------------------

    for leaf in particles:

        if not leaf.active:
            continue

        x = round(leaf.x)
        y = round(leaf.y)

        if not (
            0 <= x < WIDTH
            and
            0 <= y < HEIGHT
        ):
            continue

        # No pisar el árbol
        if canvas[y][x] == " ":

            canvas[y][x] = leaf.char
            colors[y][x] = CYAN

    # --------------------------------------------------------
    # FRAME
    # --------------------------------------------------------

    output = ["\033[H"]

    for y in range(HEIGHT):

        line = []

        current_color = None

        for x in range(WIDTH):

            color = colors[y][x]
            char = canvas[y][x]

            if color != current_color:

                if current_color is not None:
                    line.append(RESET)

                if color is not None:
                    line.append(color)

                current_color = color

            line.append(char)

        if current_color is not None:
            line.append(RESET)

        output.append(
            "".join(line)
        )

    sys.stdout.write(
        "\n".join(output)
    )

    sys.stdout.flush()


# ============================================================
# MAIN
# ============================================================

def main():

    if os.name == "nt":
        os.system("")
        os.system("cls")
    else:
        os.system("clear")

    # Limpiar pantalla
    sys.stdout.write("\033[2J")

    # Cursor invisible
    sys.stdout.write("\033[?25l")

    frame = 0

    try:

        while True:

            frame += 1

            # -----------------------------------------------
            # CREAR HOJAS
            # -----------------------------------------------

            # No en cada frame.
            # Esto mantiene pocas hojas simultáneas.
            if random.random() < 0.07:
                spawn_leaf()

            # -----------------------------------------------
            # ACTUALIZAR
            # -----------------------------------------------

            for leaf in particles:
                leaf.update(frame)

            # -----------------------------------------------
            # DIBUJAR
            # -----------------------------------------------

            render()

            time.sleep(
                1 / FPS
            )

    except KeyboardInterrupt:
        pass

    finally:

        sys.stdout.write(RESET)

        # Cursor visible otra vez
        sys.stdout.write("\033[?25h")

        sys.stdout.write("\n")

        sys.stdout.flush()


# ============================================================
# GO
# ============================================================

if __name__ == "__main__":
    main()