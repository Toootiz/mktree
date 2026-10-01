import math
import random
from pathlib import Path
from html import escape

WIDTH = 107
HEIGHT = 14

CELL_W = 9
CELL_H = 18

SVG_WIDTH = WIDTH * CELL_W
SVG_HEIGHT = HEIGHT * CELL_H

OUTPUT = Path("../assets/tree.svg")

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

TREE_W = max(
    len(line)
    for line in TREE_LINES
)

TREE_H = len(TREE_LINES)

# Centrado dentro de las 107 columnas
TREE_X = (WIDTH - TREE_W) // 2

TREE_Y = 1

BLUE = "#00afff"

CYAN = "#00d7ff"

BROWN = "#875f00"

LIGHT_BROWN = "#af8700"

def svg_char(char):
    return escape(char)

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

TREE_CELLS = set()

for y, line in enumerate(TREE_LINES):

    for x, char in enumerate(line):

        if char != " ":

            TREE_CELLS.add(
                (
                    TREE_X + x,
                    TREE_Y + y
                )
            )

def get_color(char):

    if char == "*":
        return BLUE

    if char == "|":
        return CYAN

    if char in "/\\_-":
        return BROWN

    if char == "~":
        return LIGHT_BROWN

    return None

def generate_tree():

    elements = []

    for y, line in enumerate(TREE_LINES):

        for x, char in enumerate(line):

            if char == " ":
                continue

            color = get_color(char)

            if color is None:
                continue

            px = (
                TREE_X + x
            ) * CELL_W

            py = (
                TREE_Y + y + 1
            ) * CELL_H

            elements.append(
                f'''
<text
    x="{px}"
    y="{py}"
    fill="{color}"
>{svg_char(char)}</text>'''
            )

    return "\n".join(elements)

def generate_leaf(index):

    start_x, start_y = random.choice(
        LEAF_POSITIONS
    )

    direction = random.choice([
        1,
        1,
        1,
        1,
        1,
        -1
    ])

    horizontal_distance = random.uniform(
        7,
        17
    ) * direction

    vertical_distance = random.uniform(
        5,
        8
    )

    steps = random.randint(
        6,
        9
    )

    positions_x = []
    positions_y = []

    phase = random.uniform(
        0,
        math.tau
    )

    wave_amount = random.uniform(
        0.5,
        1.4
    )

    for step in range(steps):

        progress = (
            step
            / (steps - 1)
        )

        x = (
            start_x
            + horizontal_distance
            * progress
        )

        x += (
            math.sin(
                progress
                * math.tau
                * 1.5
                + phase
            )
            * wave_amount
        )

        y = (
            start_y
            + vertical_distance
            * progress
        )

        positions_x.append(
            x * CELL_W
        )

        positions_y.append(
            (y + 1) * CELL_H
        )

    positions_x = [

        max(
            0,
            min(
                SVG_WIDTH,
                value
            )
        )

        for value in positions_x
    ]

    positions_y = [

        max(
            0,
            min(
                SVG_HEIGHT,
                value
            )
        )

        for value in positions_y
    ]

    xs = ";".join(
        f"{value:.1f}"
        for value in positions_x
    )

    ys = ";".join(
        f"{value:.1f}"
        for value in positions_y
    )

    duration = random.uniform(
        3.5,
        6.5
    )

    delay = random.uniform(
        0,
        6
    )

    char = random.choice([
        "*",
        "*",
        "*",
        "✦",
        "·"
    ])

    return f'''
<text
    x="0"
    y="0"
    fill="{CYAN}"
    opacity="0"
>
    {svg_char(char)}

    <animate
        attributeName="x"
        values="{xs}"
        dur="{duration:.2f}s"
        begin="{delay:.2f}s"
        repeatCount="indefinite"
    />

    <animate
        attributeName="y"
        values="{ys}"
        dur="{duration:.2f}s"
        begin="{delay:.2f}s"
        repeatCount="indefinite"
    />

    <animate
        attributeName="opacity"
        values="0;1;1;1;0"
        keyTimes="0;0.08;0.60;0.85;1"
        dur="{duration:.2f}s"
        begin="{delay:.2f}s"
        repeatCount="indefinite"
    />

</text>
'''

def generate_svg():

    tree = generate_tree()

    # 8 hojas voladoras
    leaves = "\n".join(
        generate_leaf(i)
        for i in range(8)
    )

    return f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{SVG_WIDTH}"
    height="{SVG_HEIGHT}"
    viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}"
>

<style>

text {{
    font-family:
        "Cascadia Mono",
        "JetBrains Mono",
        "Consolas",
        monospace;

    font-size: 16px;
    font-weight: bold;

    white-space: pre;
}}

</style>


<!-- ====================================================== -->
<!-- HOJAS VOLANDO                                           -->
<!--                                                        -->
<!-- Se dibujan PRIMERO para quedar DETRÁS del árbol.       -->
<!-- ====================================================== -->

<g id="falling-leaves">

{leaves}

</g>


<!-- ====================================================== -->
<!-- ÁRBOL                                                  -->
<!--                                                        -->
<!-- Se dibuja DESPUÉS para quedar ENCIMA de las hojas.     -->
<!-- ====================================================== -->

<g id="tree">

{tree}

</g>


</svg>
'''

def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    svg = generate_svg()

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print(
        f"Generated: {OUTPUT}"
    )

    print(
        f"Grid: {WIDTH}x{HEIGHT}"
    )

    print(
        f"SVG: {SVG_WIDTH}x{SVG_HEIGHT}px"
    )

    print()

if __name__ == "__main__":
    main()