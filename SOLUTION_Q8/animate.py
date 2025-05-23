import pygame
import sys
import os
import csv
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, qftdir)
import trap
import imageio

# --- Configurable playback rate ---
FPS = 30
MOVES_PER_SEC = 15
FRAMES_PER_MOVE = FPS // MOVES_PER_SEC
GATE_PERSIST = 3

# --- Pygame & styling setup ---
pygame.init()
BG_COLOR = (30, 30, 30)
EDGE_COLOR = (100, 100, 100)
STANDARD_COLOR = (0, 120, 200)
INTERACTION_COLOR = (200, 80, 80)
IDLE_LABEL_COLOR = (0, 255, 0)
BUSY_LABEL_COLOR = (255, 255, 255)
# FONT = pygame.font.SysFont(None, 24)
BUTTON_TEXT_COLOR = (255, 255, 255)
# STEP_FONT = pygame.font.SysFont(None, 30)

FONT_PATH = os.path.join(qftdir, "fonts", "cmunrm.ttf")
FONT = pygame.font.Font(FONT_PATH, 16)
STEP_FONT = pygame.font.Font(FONT_PATH, 30)
RX_COLOR = (175, 175, 255)
RY_COLOR = (125, 125, 255)
MS_COLOR = (255, 255, 255)
QUBIT_COLOR = (50, 50, 100)

LEGEND_X = 10
LEGEND_Y = 10
LEGEND_SPACING = 40
# --- Layout & window size ---
CHECK_WIDTH = 200
WIDTH, HEIGHT = 800 + CHECK_WIDTH, 700
PADDING = 50
PANEL_WIDTH = 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Qubit Playback")

# --- Load trap graph ---
trap_graph = trap.create_trap_graph()
node_positions = {
    node: (node[1], node[0])
    for node, attrs in trap_graph.nodes(data=True)
    if attrs.get("type") in ("standard", "interaction")
}
xs = [x for x, y in node_positions.values()]
ys = [y for x, y in node_positions.values()]
MIN_X, MAX_X = min(xs), max(xs)
MIN_Y, MAX_Y = min(ys), max(ys)


def to_screen(pos):
    x, y = pos
    sx = (
        CHECK_WIDTH
        + PADDING
        + (x - MIN_X)
        / (MAX_X - MIN_X)
        * (WIDTH - CHECK_WIDTH - PANEL_WIDTH - 2 * PADDING)
    )
    sy = PADDING + (y - MIN_Y) / (MAX_Y - MIN_Y) * (HEIGHT - 2 * PADDING)
    return int(sx), int(sy)


def flip_positions(pos_list):
    """
    Given a list like [(x,y), (x,y,'idle'), …],
    return [(y,x), (y,x,'idle'), …].
    """
    flipped = []
    for entry in pos_list:
        x, y, *rest = entry
        if rest and rest[0] == "idle":
            flipped.append((y, x, "idle"))
        else:
            flipped.append((y, x))
    return flipped


positions = [
    [(1, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (1, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (1, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (1, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (1, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (0, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (2, 1), (1, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (2, 1), (1, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (2, 1), (1, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 1), (2, 1), (1, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 2), (2, 1), (1, 0), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (1, 1), (1, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (1, 1), (1, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (1, 1), (1, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (1, 1), (1, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 3), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 2), (0, 4), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 1), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (2, 1), (1, 1), (1, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (2, 1), (1, 1), (1, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 1), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 1), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (0, 1), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (2, 1), (1, 1), (1, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 3), (1, 1), (2, 1), (1, 1), (1, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (1, 0), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (1, 0), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 4), (1, 2), (2, 1), (1, 0), (0, 3), (0, 5), (3, 6), (4, 3)],
    [(1, 5), (1, 3), (1, 1), (1, 1), (1, 3), (1, 5), (3, 6), (4, 3)],
    [(1, 5), (1, 3), (1, 1), (1, 1), (1, 3), (1, 5), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(1, 5), (1, 3), (1, 1), (1, 1), (1, 3), (1, 5), (3, 6), (4, 3)],
    [(1, 5), (1, 3), (1, 1), (1, 1), (1, 3), (1, 5), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(2, 5), (1, 4), (1, 2), (2, 1), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(3, 5), (1, 5), (1, 3), (2, 2), (1, 3), (1, 5), (3, 5), (4, 3)],
    [(3, 5), (1, 5), (1, 3), (2, 2), (1, 3), (1, 5), (3, 5), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (3, 6), (4, 3)],
    [(3, 5), (1, 5), (1, 3), (2, 3), (1, 3), (1, 5), (3, 5), (4, 3)],
    [(3, 5), (1, 5), (1, 3), (2, 3), (1, 3), (1, 5), (3, 5), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 4), (2, 5), (1, 4), (2, 3), (0, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 3), (3, 5), (1, 5), (1, 3), (1, 3), (1, 5), (3, 5), (3, 3)],
    [(3, 3), (3, 5), (1, 5), (1, 3), (1, 3), (1, 5), (3, 5), (3, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 3), (3, 5), (1, 5), (1, 3), (1, 3), (1, 5), (3, 5), (3, 3)],
    [(3, 3), (3, 5), (1, 5), (1, 3), (1, 3), (1, 5), (3, 5), (3, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 2), (3, 4), (2, 5), (1, 4), (2, 3), (1, 6), (4, 5), (4, 3)],
    [(3, 2), (3, 3), (3, 5), (1, 5), (2, 4), (1, 5), (3, 5), (3, 3)],
    [(3, 2), (3, 3), (3, 5), (1, 5), (2, 4), (1, 5), (3, 5), (3, 3)],
    [(2, 2), (3, 2), (3, 4), (2, 5), (2, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 1), (3, 2), (3, 4), (2, 5), (1, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 1), (3, 2), (3, 4), (2, 5), (1, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 1), (3, 3), (3, 5), (1, 5), (1, 4), (1, 5), (3, 5), (3, 3)],
    [(2, 1), (3, 3), (3, 5), (1, 5), (1, 4), (1, 5), (3, 5), (3, 3)],
    [(2, 0), (3, 2), (3, 4), (2, 5), (1, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (3, 2), (3, 4), (2, 5), (1, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (3, 2), (3, 4), (2, 5), (1, 4), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 2), (3, 3), (3, 5), (1, 5), (1, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 2), (3, 3), (3, 5), (1, 5), (1, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (3, 3), (3, 5), (1, 5), (1, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (3, 3), (3, 5), (1, 5), (1, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (3, 2), (3, 4), (2, 5), (1, 6), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 2), (3, 3), (3, 5), (2, 6), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 3), (3, 5), (2, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 3), (3, 5), (2, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 3), (3, 5), (2, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (3, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 4), (2, 5), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 3), (3, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 3), (3, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 3), (3, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 3), (3, 5), (3, 5), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 4), (4, 5), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 3), (4, 4), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 3), (3, 4), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 3), (3, 4), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (3, 3), (3, 4), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 3), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 3), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 3), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 3), (3, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
    [(2, 0), (2, 1), (4, 1), (2, 2), (3, 2), (2, 3), (3, 4), (4, 3)],
]
gates = [
    [
        ("RY", 6.283185301777523, 0),
        ("RY", 1.5707963196347456, 1),
        ("RY", 1.5707963230668538, 2),
        ("RY", 1.5707963293856437, 3),
        ("RY", 1.570796300768315, 4),
        ("RY", 1.5707962924960288, 5),
        ("RY", 1.5707963756303551, 6),
        ("RY", 1.5707963299721883, 7),
    ],
    [
        ("RX", 4.712388972856014, 0),
        ("RX", 1.5707963195218244, 1),
        ("RX", 0.7853981568959068, 2),
        ("RX", 0.3926990741748478, 3),
        ("RX", 0.19634953319998275, 4),
        ("RX", 0.09817476311262731, 5),
        ("RX", 0.049087377796633226, 6),
        ("RX", 0.024543685187621584, 7),
    ],
    [
        ("RY", 4.712388976152028, 0),
        ("RY", -7.483611568778273e-09, 1),
        ("RY", -3.0572137086142845e-09, 2),
        ("RY", -9.746462286814996e-09, 3),
        ("RY", 2.2827042371108087e-08, 4),
        ("RY", 2.674905291574821e-08, 5),
        ("RY", -5.423580326297748e-08, 6),
        ("RY", -1.048736989030781e-08, 7),
    ],
    [("MS", 1.5707963267948966, (0, 1))],
    [],
    [("RY", 1.5707963198460084, 0), ("RX", -1.5707963290286613, 1)],
    [("RX", -1.5707963355021242, 0)],
    [("RY", -6.3509543606448165e-09, 0)],
    [("MS", 1.5707963267948966, (0, 1))],
    [],
    [("RY", -0.7853981700683805, 0), ("RY", 1.5707963271506342, 1)],
    [("RX", -1.570796336320499, 0), ("RX", 1.570796326414265, 1)],
    [("RY", -5.81128346884123e-09, 0), ("RY", -4.130337413429963e-09, 1)],
    [("MS", 1.5707963267948966, (0, 2))],
    [],
    [("RY", 0.7853981553799287, 0), ("RX", -1.5707963290286613, 2)],
    [("RX", -1.570796331114915, 0)],
    [("RY", -7.759214186096881e-09, 0)],
    [("MS", 1.5707963267948966, (0, 2))],
    [],
    [("RY", -0.39269908027431993, 0)],
    [("RX", -1.570796327770297, 0)],
    [("RY", -3.78177025153237e-09, 0)],
    [("MS", 1.5707963267948966, (0, 3)), ("MS", 1.5707963267948966, (1, 2))],
    [],
    [
        ("RY", 0.3926990769855605, 0),
        ("RY", 1.5707963198460084, 1),
        ("RX", -1.5707963290286613, 2),
        ("RX", -1.5707963290286613, 3),
    ],
    [("RX", -1.5707963252285955, 0), ("RX", -1.5707963355021242, 1)],
    [("RY", -5.741183374810102e-09, 0), ("RY", -6.3509543606448165e-09, 1)],
    [("MS", 1.5707963267948966, (0, 3)), ("MS", 1.5707963267948966, (1, 2))],
    [],
    [
        ("RY", -0.19634954820969636, 0),
        ("RY", -0.7853981700683805, 1),
        ("RY", 1.5707963271506342, 2),
        ("RY", -3.786750870871029e-09, 3),
    ],
    [
        ("RX", -1.570796334241153, 0),
        ("RX", -1.570796336320499, 1),
        ("RX", 1.570796326414265, 2),
        ("RX", -0.7853981710335645, 3),
    ],
    [
        ("RY", -7.401513552549239e-09, 0),
        ("RY", -5.81128346884123e-09, 1),
        ("RY", -4.130337413429963e-09, 2),
        ("RY", -3.786750562134138e-09, 3),
    ],
    [("MS", 1.5707963267948966, (0, 4)), ("MS", 1.5707963267948966, (1, 3))],
    [],
    [
        ("RY", 0.1963495406232804, 0),
        ("RY", 0.7853981553799287, 1),
        ("RX", -1.5707963290286613, 3),
        ("RX", -1.5707963290286613, 4),
    ],
    [("RX", -1.5707963323801992, 0), ("RX", -1.570796331114915, 1)],
    [("RY", 3.1397278628443187e-09, 0), ("RY", -7.759214186096881e-09, 1)],
    [("MS", 1.5707963267948966, (0, 4)), ("MS", 1.5707963267948966, (1, 3))],
    [],
    [
        ("RY", -0.09817477499652875, 0),
        ("RY", -0.39269908027431993, 1),
        ("RX", -1.178097248494103, 4),
    ],
    [("RX", -1.5707963304377508, 0), ("RX", -1.570796327770297, 1)],
    [("RY", -4.033128667533199e-09, 0), ("RY", -3.78177025153237e-09, 1)],
    [
        ("MS", 1.5707963267948966, (0, 5)),
        ("MS", 1.5707963267948966, (1, 4)),
        ("MS", 1.5707963267948966, (2, 3)),
    ],
    [],
    [
        ("RY", 0.09817476291501688, 0),
        ("RY", 0.3926990769855605, 1),
        ("RY", 1.5707963198460084, 2),
        ("RX", -1.5707963290286613, 3),
        ("RX", -1.5707963290286613, 4),
        ("RX", -1.5707963290286613, 5),
    ],
    [
        ("RX", -1.5707963339139528, 0),
        ("RX", -1.5707963252285955, 1),
        ("RX", -1.5707963355021242, 2),
    ],
    [
        ("RY", -7.233625197442878e-09, 0),
        ("RY", -5.741183374810102e-09, 1),
        ("RY", -6.3509543606448165e-09, 2),
    ],
    [
        ("MS", 1.5707963267948966, (0, 5)),
        ("MS", 1.5707963267948966, (1, 4)),
        ("MS", 1.5707963267948966, (2, 3)),
    ],
    [],
    [
        ("RY", -0.049087389442220505, 0),
        ("RY", -0.19634954820969636, 1),
        ("RY", -0.7853981700683805, 2),
        ("RY", 1.5707963271506342, 3),
        ("RY", -3.786750870871029e-09, 4),
        ("RY", -3.567668195234157e-09, 5),
    ],
    [
        ("RX", -1.5707963327553593, 0),
        ("RX", -1.570796334241153, 1),
        ("RX", -1.570796336320499, 2),
        ("RX", 1.570796326414265, 3),
        ("RX", -0.7853981710335645, 4),
        ("RX", -1.37444678983163, 5),
    ],
    [
        ("RY", -1.0739226760523147e-08, 0),
        ("RY", -7.401513552549239e-09, 1),
        ("RY", -5.81128346884123e-09, 2),
        ("RY", -4.130337413429963e-09, 3),
        ("RY", -3.786750562134138e-09, 4),
        ("RY", -3.5676681809163024e-09, 5),
    ],
    [
        ("MS", 1.5707963267948966, (0, 6)),
        ("MS", 1.5707963267948966, (1, 5)),
        ("MS", 1.5707963267948966, (2, 4)),
    ],
    [],
    [
        ("RY", 0.04908738075434768, 0),
        ("RY", 0.1963495406232804, 1),
        ("RY", 0.7853981553799287, 2),
        ("RX", -1.5707963290286613, 4),
        ("RX", -1.5707963290286613, 5),
        ("RX", -1.5707963290286613, 6),
    ],
    [
        ("RX", -1.5707963318606, 0),
        ("RX", -1.5707963323801992, 1),
        ("RX", -1.570796331114915, 2),
    ],
    [
        ("RY", 3.0894605733846035e-09, 0),
        ("RY", 3.1397278628443187e-09, 1),
        ("RY", -7.759214186096881e-09, 2),
    ],
    [
        ("MS", 1.5707963267948966, (0, 6)),
        ("MS", 1.5707963267948966, (1, 5)),
        ("MS", 1.5707963267948966, (2, 4)),
    ],
    [],
    [
        ("RY", -0.024543695347846346, 0),
        ("RY", -0.09817477499652875, 1),
        ("RY", -0.39269908027431993, 2),
        ("RX", -1.178097248494103, 5),
        ("RX", -1.472621558665239, 6),
    ],
    [
        ("RX", -1.5707963272131182, 0),
        ("RX", -1.5707963304377508, 1),
        ("RX", -1.570796327770297, 2),
    ],
    [
        ("RY", -8.66913339505866e-09, 0),
        ("RY", -4.033128667533199e-09, 1),
        ("RY", -3.78177025153237e-09, 2),
    ],
    [
        ("MS", 1.5707963267948966, (0, 7)),
        ("MS", 1.5707963267948966, (1, 6)),
        ("MS", 1.5707963267948966, (2, 5)),
        ("MS", 1.5707963267948966, (3, 4)),
    ],
    [],
    [
        ("RY", 0.024543686791448263, 0),
        ("RY", 0.09817476291501688, 1),
        ("RY", 0.3926990769855605, 2),
        ("RY", 1.5707963198460084, 3),
        ("RX", -1.5707963290286613, 4),
        ("RX", -1.5707963290286613, 5),
        ("RX", -1.5707963290286613, 6),
        ("RX", -1.5707963290286613, 7),
    ],
    [
        ("RX", -1.570796332771927, 0),
        ("RX", -1.5707963339139528, 1),
        ("RX", -1.5707963252285955, 2),
        ("RX", -1.5707963355021242, 3),
    ],
    [
        ("RY", -4.617859660643901e-09, 0),
        ("RY", -7.233625197442878e-09, 1),
        ("RY", -5.741183374810102e-09, 2),
        ("RY", -6.3509543606448165e-09, 3),
    ],
    [
        ("MS", 1.5707963267948966, (0, 7)),
        ("MS", 1.5707963267948966, (1, 6)),
        ("MS", 1.5707963267948966, (2, 5)),
        ("MS", 1.5707963267948966, (3, 4)),
    ],
    [],
    [
        ("RX", -1.5707963290286613, 0),
        ("RY", -0.049087389442220505, 1),
        ("RY", -0.19634954820969636, 2),
        ("RY", -0.7853981700683805, 3),
        ("RY", 1.5707963271506342, 4),
        ("RY", -3.786750870871029e-09, 5),
        ("RY", -3.567668195234157e-09, 6),
        ("RX", -1.5217089444498861, 7),
    ],
    [
        ("RX", -1.5707963327553593, 1),
        ("RX", -1.570796334241153, 2),
        ("RX", -1.570796336320499, 3),
        ("RX", 1.570796326414265, 4),
        ("RX", -0.7853981710335645, 5),
        ("RX", -1.37444678983163, 6),
    ],
    [
        ("RY", -1.0739226760523147e-08, 1),
        ("RY", -7.401513552549239e-09, 2),
        ("RY", -5.81128346884123e-09, 3),
        ("RY", -4.130337413429963e-09, 4),
        ("RY", -3.786750562134138e-09, 5),
        ("RY", -3.5676681809163024e-09, 6),
    ],
    [
        ("MS", 1.5707963267948966, (1, 7)),
        ("MS", 1.5707963267948966, (2, 6)),
        ("MS", 1.5707963267948966, (3, 5)),
    ],
    [],
    [
        ("RY", 0.1963495406232804, 2),
        ("RY", 0.7853981553799287, 3),
        ("RX", -1.5707963290286613, 5),
        ("RX", -1.5707963290286613, 6),
        ("RX", -1.5707963290286613, 7),
        ("RY", 0.04908738075434768, 1),
    ],
    [
        ("RX", -1.5707963323801992, 2),
        ("RX", -1.570796331114915, 3),
        ("RX", -1.5707963318606, 1),
    ],
    [
        ("RY", 3.1397278628443187e-09, 2),
        ("RY", -7.759214186096881e-09, 3),
        ("RY", 3.0894605733846035e-09, 1),
    ],
    [
        ("MS", 1.5707963267948966, (1, 7)),
        ("MS", 1.5707963267948966, (2, 6)),
        ("MS", 1.5707963267948966, (3, 5)),
    ],
    [],
    [
        ("RX", -1.5707963290286613, 1),
        ("RY", -0.09817477499652875, 2),
        ("RY", -0.39269908027431993, 3),
        ("RX", -1.178097248494103, 6),
        ("RX", -1.472621558665239, 7),
    ],
    [("RX", -1.5707963304377508, 2), ("RX", -1.570796327770297, 3)],
    [("RY", -4.033128667533199e-09, 2), ("RY", -3.78177025153237e-09, 3)],
    [
        ("MS", 1.5707963267948966, (2, 7)),
        ("MS", 1.5707963267948966, (3, 6)),
        ("MS", 1.5707963267948966, (4, 5)),
    ],
    [],
    [
        ("RY", 0.09817476291501688, 2),
        ("RY", 0.3926990769855605, 3),
        ("RY", 1.5707963198460084, 4),
        ("RX", -1.5707963290286613, 5),
        ("RX", -1.5707963290286613, 6),
        ("RX", -1.5707963290286613, 7),
    ],
    [
        ("RX", -1.5707963339139528, 2),
        ("RX", -1.5707963252285955, 3),
        ("RX", -1.5707963355021242, 4),
    ],
    [
        ("RY", -7.233625197442878e-09, 2),
        ("RY", -5.741183374810102e-09, 3),
        ("RY", -6.3509543606448165e-09, 4),
    ],
    [
        ("MS", 1.5707963267948966, (2, 7)),
        ("MS", 1.5707963267948966, (3, 6)),
        ("MS", 1.5707963267948966, (4, 5)),
    ],
    [],
    [
        ("RX", -1.5707963290286613, 2),
        ("RY", -0.19634954820969636, 3),
        ("RY", -0.7853981700683805, 4),
        ("RY", 1.5707963271506342, 5),
        ("RY", -3.786750870871029e-09, 6),
        ("RY", -3.567668195234157e-09, 7),
    ],
    [
        ("RX", -1.570796334241153, 3),
        ("RX", -1.570796336320499, 4),
        ("RX", 1.570796326414265, 5),
        ("RX", -0.7853981710335645, 6),
        ("RX", -1.37444678983163, 7),
    ],
    [
        ("RY", -7.401513552549239e-09, 3),
        ("RY", -5.81128346884123e-09, 4),
        ("RY", -4.130337413429963e-09, 5),
        ("RY", -3.786750562134138e-09, 6),
        ("RY", -3.5676681809163024e-09, 7),
    ],
    [("MS", 1.5707963267948966, (3, 7)), ("MS", 1.5707963267948966, (4, 6))],
    [],
    [
        ("RY", 0.1963495406232804, 3),
        ("RY", 0.7853981553799287, 4),
        ("RX", -1.5707963290286613, 6),
        ("RX", -1.5707963290286613, 7),
    ],
    [("RX", -1.5707963323801992, 3), ("RX", -1.570796331114915, 4)],
    [("RY", 3.1397278628443187e-09, 3), ("RY", -7.759214186096881e-09, 4)],
    [("MS", 1.5707963267948966, (3, 7)), ("MS", 1.5707963267948966, (4, 6))],
    [],
    [["RY", -0.39269908027431993, 4]],
    [
        ("RX", -1.5707963290286613, 3),
        ("RX", -1.570796327770297, 4),
        ("RX", -1.178097248494103, 7),
    ],
    [("RY", -3.78177025153237e-09, 4)],
    [("MS", 1.5707963267948966, (4, 7)), ("MS", 1.5707963267948966, (5, 6))],
    [],
    [
        ("RY", 0.3926990769855605, 4),
        ("RY", 1.5707963198460084, 5),
        ("RX", -1.5707963290286613, 6),
        ("RX", -1.5707963290286613, 7),
    ],
    [("RX", -1.5707963252285955, 4), ("RX", -1.5707963355021242, 5)],
    [("RY", -5.741183374810102e-09, 4), ("RY", -6.3509543606448165e-09, 5)],
    [("MS", 1.5707963267948966, (4, 7)), ("MS", 1.5707963267948966, (5, 6))],
    [],
    [
        ("RX", -1.5707963290286613, 4),
        ("RY", -0.7853981700683805, 5),
        ("RY", 1.5707963271506342, 6),
        ("RY", -3.786750870871029e-09, 7),
    ],
    [
        ("RX", -1.570796336320499, 5),
        ("RX", 1.570796326414265, 6),
        ("RX", -0.7853981710335645, 7),
    ],
    [
        ("RY", -5.81128346884123e-09, 5),
        ("RY", -4.130337413429963e-09, 6),
        ("RY", -3.786750562134138e-09, 7),
    ],
    [("MS", 1.5707963267948966, (5, 7))],
    [],
    [("RY", 0.7853981553799287, 5), ("RX", -1.5707963290286613, 7)],
    [("RX", -1.570796331114915, 5)],
    [("RY", -7.759214186096881e-09, 5)],
    [("MS", 1.5707963267948966, (5, 7))],
    [],
    [("RX", -1.5707963290286613, 5)],
    [("MS", 1.5707963267948966, (6, 7))],
    [],
    [("RY", 1.5707963198460084, 6), ("RX", -1.5707963290286613, 7)],
    [("RX", -1.5707963355021242, 6)],
    [("RY", -6.3509543606448165e-09, 6)],
    [("MS", 1.5707963267948966, (6, 7))],
    [],
    [("RX", -1.5707963290286613, 6), ("RY", -1.7195951339125712e-10, 7)],
    [("RX", 1.5707963242661283, 7)],
    [("RY", -1.8819445215028955e-10, 7)],
]

positions_by_timestep = [flip_positions(pos) for pos in positions]
# --- Load qubit positions ---
total_steps = len(positions_by_timestep)
if total_steps == 0:
    print("No timesteps to animate.")
    sys.exit(1)

new_gates = [[] for _ in range(len(gates) + 1)]
for g, gate in enumerate(gates):
    new_gates[g] = gate
    for entry in gate:
        if entry[0] == "MS":
            new_gates[g + 1].append(entry)
            print(entry)


# --- Draw a single timestep ---
def draw_gate(step):
    screen.fill(BG_COLOR)
    # draw trap edges
    for u, v in trap_graph.edges():
        if u in node_positions and v in node_positions:
            pygame.draw.line(
                screen,
                EDGE_COLOR,
                to_screen(node_positions[u]),
                to_screen(node_positions[v]),
                2,
            )
    # draw trap nodes
    for node, (x, y) in node_positions.items():
        color = (
            STANDARD_COLOR
            if trap_graph.nodes[node]["type"] == "standard"
            else INTERACTION_COLOR
        )
        pygame.draw.circle(screen, color, to_screen((x, y)), 25)

    # draw qubit labels
    bynode = {}
    flags = {}
    for q, entry in enumerate(positions_by_timestep[step]):
        is_idle = len(entry) == 3 and entry[2] == "idle"
        key = (entry[0], entry[1])
        bynode.setdefault(key, []).append(q)
        flags.setdefault(key, []).append(is_idle)
    # print(bynode)
    print(step)
    for (x, y), qs in bynode.items():
        lbl = ",".join(str(q) for q in qs)
        pygame.draw.circle(screen, QUBIT_COLOR, to_screen((x, y)), 17)
        pygame.draw.circle(screen, (255, 255, 255), to_screen((x, y)), 18, 1)
        col = IDLE_LABEL_COLOR if all(flags[(x, y)]) else BUSY_LABEL_COLOR
        txt = FONT.render(lbl, True, col)
        screen.blit(txt, txt.get_rect(center=to_screen((x, y))))
        gates = new_gates[step]

        for q in qs:
            for gate in gates:
                if gate[2] == q and gate[0] != "MS":
                    color = RX_COLOR if gate[0] == "RX" else RY_COLOR
                    # print("drawing R")
                    pygame.draw.circle(screen, color, to_screen((x, y)), 35, 3)
                if gate[0] == "MS":

                    if q in gate[2]:
                        color = MS_COLOR
                        pygame.draw.circle(screen, MS_COLOR, to_screen((x, y)), 40, 4)

    # draw step counter
    ts_txt = STEP_FONT.render(f"Step {step+1} / {total_steps}", True, (255, 255, 255))
    screen.blit(ts_txt, (10, HEIGHT - 30))


def draw_step_interp(step, subframe):
    # get integer positions for this step and next
    p0 = positions_by_timestep[step]
    p1 = positions_by_timestep[(step + 1) % total_steps]
    t = subframe / FRAMES_PER_MOVE
    # build interpolated list
    interp = []
    for e0, e1 in zip(p0, p1):
        x0, y0, *r0 = e0
        x1, y1, *r1 = e1
        xi = x0 + (x1 - x0) * t
        yi = y0 + (y1 - y0) * t
        # preserve idle flag only if both endpoints idle
        if r0 and r0[0] == "idle" and r1 and r1[0] == "idle":
            interp.append((xi, yi, "idle"))
        else:
            interp.append((xi, yi))
    # now draw exactly as before, but using interp instead of positions_by_timestep[step]
    # screen.fill(BG_COLOR)
    # ... draw trap edges/nodes ...
    # draw qubits at interp positions:

    screen.fill(BG_COLOR)
    # draw trap edges
    for u, v in trap_graph.edges():
        if u in node_positions and v in node_positions:
            pygame.draw.line(
                screen,
                EDGE_COLOR,
                to_screen(node_positions[u]),
                to_screen(node_positions[v]),
                2,
            )
    # draw trap nodes
    for node, (x, y) in node_positions.items():
        color = (
            STANDARD_COLOR
            if trap_graph.nodes[node]["type"] == "standard"
            else INTERACTION_COLOR
        )
        pygame.draw.circle(screen, color, to_screen((x, y)), 25)
    bynode, flags = {}, {}
    for q, entry in enumerate(interp):
        idle = len(entry) == 3 and entry[2] == "idle"
        key = (entry[0], entry[1])
        bynode.setdefault(key, []).append((q, idle))
    for (x, y), qubits in bynode.items():
        lbl = ",".join(str(q) for q, _ in qubits)
        clr = IDLE_LABEL_COLOR if all(idle for _, idle in qubits) else BUSY_LABEL_COLOR
        pos = to_screen((x, y))
        pygame.draw.circle(screen, QUBIT_COLOR, pos, 17)
        pygame.draw.circle(screen, (255, 255, 255), to_screen((x, y)), 18, 1)
        txt = FONT.render(lbl, True, clr)
        screen.blit(txt, txt.get_rect(center=pos))
    ts_txt = STEP_FONT.render(f"Step {step+1}/{total_steps}", True, (255, 255, 255))
    screen.blit(ts_txt, (10, HEIGHT - 30))


def draw_legend():
    """
    Draws a vertical legend at the top‐left of the screen:
      • A sample qubit icon with "Qubit n"
      • Each gate style with its name
      • Standard vs. Interaction node
    """
    x0, y0 = LEGEND_X, LEGEND_Y

    # 5) Standard node
    pygame.draw.circle(screen, STANDARD_COLOR, (x0 + 15, y0 + 15), 12)
    txt = FONT.render("Standard node", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    y0 += LEGEND_SPACING

    # 6) Interaction node
    pygame.draw.circle(screen, INTERACTION_COLOR, (x0 + 15, y0 + 15), 12)
    txt = FONT.render("Interaction node", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    y0 += LEGEND_SPACING

    # 1) Sample Qubit
    pygame.draw.circle(screen, QUBIT_COLOR, (x0 + 15, y0 + 15), 12)  # filled circle
    pygame.draw.circle(screen, (255, 255, 255), (x0 + 15, y0 + 15), 14, 1)
    txt = FONT.render("Ion n", True, BUSY_LABEL_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    clr = (255, 255, 255)
    txt1 = FONT.render("n", True, clr)
    screen.blit(txt1, txt1.get_rect(center=(x0 + 15, y0 + 15)))
    y0 += LEGEND_SPACING

    # 2) RX gate
    pygame.draw.circle(screen, RX_COLOR, (x0 + 15, y0 + 15), 12, 3)  # thick border
    txt = FONT.render("RX gate", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    y0 += LEGEND_SPACING

    # 3) RY gate
    pygame.draw.circle(screen, RY_COLOR, (x0 + 15, y0 + 15), 12, 3)
    txt = FONT.render("RY gate", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    y0 += LEGEND_SPACING

    # 4) MS gate (two‐qubit)
    pygame.draw.circle(screen, MS_COLOR, (x0 + 15, y0 + 15), 12, 3)
    txt = FONT.render("MS gate", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, (x0 + 35, y0 + 8))
    y0 += LEGEND_SPACING


clock = pygame.time.Clock()
step = 0
subframe = 0
step = 0
running = True
writer = imageio.get_writer("animation.mp4", fps=FPS)
first = True
while running:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    draw_step_interp(step, subframe)
    draw_legend()
    pygame.display.flip()
    frame = pygame.surfarray.array3d(screen)
    frame = frame.swapaxes(0, 1)
    writer.append_data(frame)

    subframe += 1
    if subframe > FRAMES_PER_MOVE:
        subframe = 0
        step = (step + 1) % total_steps
        if step == 0:
            running = False
        draw_gate(step)
        draw_legend()
        subsubframe = 0
        while subsubframe < GATE_PERSIST:
            subsubframe += 1
            draw_gate(step)
            draw_legend()
            pygame.display.flip()
            frame = pygame.surfarray.array3d(screen)
            frame = frame.swapaxes(0, 1)
            writer.append_data(frame)
            clock.tick(FPS)

    clock.tick(FPS)
writer.close()
pygame.quit()
sys.exit()
