import pygame
import sys
import os
import csv
import numpy as np
from itertools import combinations

# Ensure trap module is importable
qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, qftdir)
import trap
import verifier

# Initialize Pygame
pygame.init()

# Styling constants
BG_COLOR = (30, 30, 30)
EDGE_COLOR = (100, 100, 100)
STANDARD_COLOR = (0, 120, 200)
INTERACTION_COLOR = (200, 80, 80)
IDLE_LABEL_COLOR = (0, 255, 0)
BUSY_LABEL_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 50)
DISABLED_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
FLASH_COLOR = (200, 0, 0)
FONT = pygame.font.SysFont(None, 24)
STEP_FONT = pygame.font.SysFont(None, 30)

# Checklist width and window dimensions
CHECK_WIDTH = 200
WIDTH, HEIGHT = 800 + CHECK_WIDTH, 700

# Load Penning trap graph
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

# UI layout constants
PADDING = 50
PANEL_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10

# Create display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Qubit Visualizer")

# State variables
selected_qubit = 0
initial_positions = [
    (0, 1),
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (5, 0),
    (6, 1),
    #  (5, 4),
]
current_positions = list(initial_positions)
current_operations = [None] * len(initial_positions)

timestep = 0
positions_by_timestep = []
gates_schedule = []
conv_schedule = []  # holds converted MS sequence for saving

# Raw operations (user-provided) and translation
A = operations_raw = [
    [
        ("RX", 0.024543688364597013, 0),
        ("RY", 1.5707963173527333, 0),
        ("MS", 1.5707963267948966, [1, 0]),
        ("RX", -1.5707963280748842, 0),
        ("RY", 1.5707963280748842, 0),
        ("MS", 1.5707963267948966, [1, 0]),
        ("RX", -1.5707963340356508, 0),
        ("RY", -0.7853981695598105, 0),
        ("MS", 1.5707963267948966, [2, 0]),
        ("RX", -1.5707963301374783, 0),
        ("RY", 0.7853981582156461, 0),
        ("MS", 1.5707963267948966, [2, 0]),
        ("RX", -1.5707963342929192, 0),
        ("RY", -0.39269908866409564, 0),
        ("MS", 1.5707963267948966, [3, 0]),
        ("RX", -1.5707963262626867, 0),
        ("RY", 0.3926990780625495, 0),
        ("MS", 1.5707963267948966, [3, 0]),
        ("RX", -1.5707963367316065, 0),
        ("RY", -0.19634954435153912, 0),
        ("MS", 1.5707963267948966, [4, 0]),
        ("RX", -1.5707963341635782, 0),
        ("RY", 0.19634953347333703, 0),
        ("MS", 1.5707963267948966, [4, 0]),
        ("RX", -1.5707963291914615, 0),
        ("RY", -0.09817476694813419, 0),
        ("MS", 1.5707963267948966, [5, 0]),
        ("RX", -1.570796334245162, 0),
        ("RY", 0.09817476297392279, 0),
        ("MS", 1.5707963267948966, [5, 0]),
        ("RX", -1.5707963285068935, 0),
        ("RY", -0.04908738398798296, 0),
        ("MS", 1.5707963267948966, [6, 0]),
        ("RX", -1.5707963268994758, 0),
        ("RY", 0.04908737776632521, 0),
        ("MS", 1.5707963267948966, [6, 0]),
        ("RX", -1.5707963341869307, 0),
        ("RY", -0.024543696565959793, 0),
        ("MS", 1.5707963267948966, [7, 0]),
        ("RX", -1.5707963242599559, 0),
        ("RY", 0.024543689290526898, 0),
        ("MS", 1.5707963267948966, [7, 0]),
        ("RX", -1.5707963305397592, 0),
        ("RY", 0.0, 0),
    ],
    [
        ("RX", 0.024543688364597013, 1),
        ("RY", 1.5707963173527333, 1),
        ("MS", 1.5707963267948966, [1, 0]),
        ("RX", -1.5707963291742124, 1),
        ("RY", 0.0, 1),
        ("MS", 1.5707963267948966, [1, 0]),
        ("RX", 1.5707963198137818, 1),
        ("RY", 1.5707963198137818, 1),
        ("MS", 1.5707963267948966, [2, 1]),
        ("RX", -1.5707963280748842, 1),
        ("RY", 1.5707963280748842, 1),
        ("MS", 1.5707963267948966, [2, 1]),
        ("RX", -1.5707963340356508, 1),
        ("RY", -0.7853981695598105, 1),
        ("MS", 1.5707963267948966, [3, 1]),
        ("RX", -1.5707963301374783, 1),
        ("RY", 0.7853981582156461, 1),
        ("MS", 1.5707963267948966, [3, 1]),
        ("RX", -1.5707963342929192, 1),
        ("RY", -0.39269908866409564, 1),
        ("MS", 1.5707963267948966, [4, 1]),
        ("RX", -1.5707963262626867, 1),
        ("RY", 0.3926990780625495, 1),
        ("MS", 1.5707963267948966, [4, 1]),
        ("RX", -1.5707963367316065, 1),
        ("RY", -0.19634954435153912, 1),
        ("MS", 1.5707963267948966, [5, 1]),
        ("RX", -1.5707963341635782, 1),
        ("RY", 0.19634953347333703, 1),
        ("MS", 1.5707963267948966, [5, 1]),
        ("RX", -1.5707963291914615, 1),
        ("RY", -0.09817476694813419, 1),
        ("MS", 1.5707963267948966, [6, 1]),
        ("RX", -1.570796334245162, 1),
        ("RY", 0.09817476297392279, 1),
        ("MS", 1.5707963267948966, [6, 1]),
        ("RX", -1.5707963285068935, 1),
        ("RY", -0.04908738398798296, 1),
        ("MS", 1.5707963267948966, [7, 1]),
        ("RX", -1.5707963268994758, 1),
        ("RY", 0.04908737776632521, 1),
        ("MS", 1.5707963267948966, [7, 1]),
        ("RX", -1.5707963305397592, 1),
        ("RY", 0.0, 1),
    ],
    [
        ("RX", 0.024543688364597013, 2),
        ("RY", 1.5707963173527333, 2),
        ("MS", 1.5707963267948966, [2, 0]),
        ("RX", -1.5707963291742124, 2),
        ("RY", 0.0, 2),
        ("MS", 1.5707963267948966, [2, 0]),
        ("RX", 0.0, 2),
        ("RY", 0.0, 2),
        ("MS", 1.5707963267948966, [2, 1]),
        ("RX", -1.5707963291742124, 2),
        ("RY", 0.0, 2),
        ("MS", 1.5707963267948966, [2, 1]),
        ("RX", 1.5707963198137818, 2),
        ("RY", 1.5707963198137818, 2),
        ("MS", 1.5707963267948966, [3, 2]),
        ("RX", -1.5707963280748842, 2),
        ("RY", 1.5707963280748842, 2),
        ("MS", 1.5707963267948966, [3, 2]),
        ("RX", -1.5707963340356508, 2),
        ("RY", -0.7853981695598105, 2),
        ("MS", 1.5707963267948966, [4, 2]),
        ("RX", -1.5707963301374783, 2),
        ("RY", 0.7853981582156461, 2),
        ("MS", 1.5707963267948966, [4, 2]),
        ("RX", -1.5707963342929192, 2),
        ("RY", -0.39269908866409564, 2),
        ("MS", 1.5707963267948966, [5, 2]),
        ("RX", -1.5707963262626867, 2),
        ("RY", 0.3926990780625495, 2),
        ("MS", 1.5707963267948966, [5, 2]),
        ("RX", -1.5707963367316065, 2),
        ("RY", -0.19634954435153912, 2),
        ("MS", 1.5707963267948966, [6, 2]),
        ("RX", -1.5707963341635782, 2),
        ("RY", 0.19634953347333703, 2),
        ("MS", 1.5707963267948966, [6, 2]),
        ("RX", -1.5707963291914615, 2),
        ("RY", -0.09817476694813419, 2),
        ("MS", 1.5707963267948966, [7, 2]),
        ("RX", -1.570796334245162, 2),
        ("RY", 0.09817476297392279, 2),
        ("MS", 1.5707963267948966, [7, 2]),
        ("RX", -1.5707963305397592, 2),
        ("RY", 0.0, 2),
    ],
    [
        ("RX", 0.024543688364597013, 3),
        ("RY", 1.5707963173527333, 3),
        ("MS", 1.5707963267948966, [3, 0]),
        ("RX", -1.5707963291742124, 3),
        ("RY", 0.0, 3),
        ("MS", 1.5707963267948966, [3, 0]),
        ("RX", -0.7853981632740932, 3),
        ("RY", -8.159136024436953e-09, 3),
        ("MS", 1.5707963267948966, [3, 1]),
        ("RX", -1.5707963291742124, 3),
        ("RY", 0.0, 3),
        ("MS", 1.5707963267948966, [3, 1]),
        ("RX", 0.0, 3),
        ("RY", 0.0, 3),
        ("MS", 1.5707963267948966, [3, 2]),
        ("RX", -1.5707963291742124, 3),
        ("RY", 0.0, 3),
        ("MS", 1.5707963267948966, [3, 2]),
        ("RX", 1.5707963198137818, 3),
        ("RY", 1.5707963198137818, 3),
        ("MS", 1.5707963267948966, [4, 3]),
        ("RX", -1.5707963280748842, 3),
        ("RY", 1.5707963280748842, 3),
        ("MS", 1.5707963267948966, [4, 3]),
        ("RX", -1.5707963340356508, 3),
        ("RY", -0.7853981695598105, 3),
        ("MS", 1.5707963267948966, [5, 3]),
        ("RX", -1.5707963301374783, 3),
        ("RY", 0.7853981582156461, 3),
        ("MS", 1.5707963267948966, [5, 3]),
        ("RX", -1.5707963342929192, 3),
        ("RY", -0.39269908866409564, 3),
        ("MS", 1.5707963267948966, [6, 3]),
        ("RX", -1.5707963262626867, 3),
        ("RY", 0.3926990780625495, 3),
        ("MS", 1.5707963267948966, [6, 3]),
        ("RX", -1.5707963367316065, 3),
        ("RY", -0.19634954435153912, 3),
        ("MS", 1.5707963267948966, [7, 3]),
        ("RX", -1.5707963341635782, 3),
        ("RY", 0.19634953347333703, 3),
        ("MS", 1.5707963267948966, [7, 3]),
        ("RX", -1.5707963305397592, 3),
        ("RY", 0.0, 3),
    ],
    [
        ("RX", 0.024543688364597013, 4),
        ("RY", 1.5707963173527333, 4),
        ("MS", 1.5707963267948966, [4, 0]),
        ("RX", -1.5707963291742124, 4),
        ("RY", 0.0, 4),
        ("MS", 1.5707963267948966, [4, 0]),
        ("RX", -1.1780972517962207, 4),
        ("RY", -7.261321924436939e-09, 4),
        ("MS", 1.5707963267948966, [4, 1]),
        ("RX", -1.5707963291742124, 4),
        ("RY", 0.0, 4),
        ("MS", 1.5707963267948966, [4, 1]),
        ("RX", -0.7853981632740932, 4),
        ("RY", -8.159136024436953e-09, 4),
        ("MS", 1.5707963267948966, [4, 2]),
        ("RX", -1.5707963291742124, 4),
        ("RY", 0.0, 4),
        ("MS", 1.5707963267948966, [4, 2]),
        ("RX", 0.0, 4),
        ("RY", 0.0, 4),
        ("MS", 1.5707963267948966, [4, 3]),
        ("RX", -1.5707963291742124, 4),
        ("RY", 0.0, 4),
        ("MS", 1.5707963267948966, [4, 3]),
        ("RX", 1.5707963198137818, 4),
        ("RY", 1.5707963198137818, 4),
        ("MS", 1.5707963267948966, [5, 4]),
        ("RX", -1.5707963280748842, 4),
        ("RY", 1.5707963280748842, 4),
        ("MS", 1.5707963267948966, [5, 4]),
        ("RX", -1.5707963340356508, 4),
        ("RY", -0.7853981695598105, 4),
        ("MS", 1.5707963267948966, [6, 4]),
        ("RX", -1.5707963301374783, 4),
        ("RY", 0.7853981582156461, 4),
        ("MS", 1.5707963267948966, [6, 4]),
        ("RX", -1.5707963342929192, 4),
        ("RY", -0.39269908866409564, 4),
        ("MS", 1.5707963267948966, [7, 4]),
        ("RX", -1.5707963262626867, 4),
        ("RY", 0.3926990780625495, 4),
        ("MS", 1.5707963267948966, [7, 4]),
        ("RX", -1.5707963305397592, 4),
        ("RY", 0.0, 4),
    ],
    [
        ("RX", 0.024543688364597013, 5),
        ("RY", 1.5707963173527333, 5),
        ("MS", 1.5707963267948966, [5, 0]),
        ("RX", -1.5707963291742124, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 0]),
        ("RX", -1.3744467876706388, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 1]),
        ("RX", -1.5707963291742124, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 1]),
        ("RX", -1.1780972517962207, 5),
        ("RY", -7.261321924436939e-09, 5),
        ("MS", 1.5707963267948966, [5, 2]),
        ("RX", -1.5707963291742124, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 2]),
        ("RX", -0.7853981632740932, 5),
        ("RY", -8.159136024436953e-09, 5),
        ("MS", 1.5707963267948966, [5, 3]),
        ("RX", -1.5707963291742124, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 3]),
        ("RX", 0.0, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 4]),
        ("RX", -1.5707963291742124, 5),
        ("RY", 0.0, 5),
        ("MS", 1.5707963267948966, [5, 4]),
        ("RX", 1.5707963198137818, 5),
        ("RY", 1.5707963198137818, 5),
        ("MS", 1.5707963267948966, [6, 5]),
        ("RX", -1.5707963280748842, 5),
        ("RY", 1.5707963280748842, 5),
        ("MS", 1.5707963267948966, [6, 5]),
        ("RX", -1.5707963340356508, 5),
        ("RY", -0.7853981695598105, 5),
        ("MS", 1.5707963267948966, [7, 5]),
        ("RX", -1.5707963301374783, 5),
        ("RY", 0.7853981582156461, 5),
        ("MS", 1.5707963267948966, [7, 5]),
        ("RX", -1.5707963305397592, 5),
        ("RY", 0.0, 5),
    ],
    [
        ("RX", 0.024543688364597013, 6),
        ("RY", 1.5707963173527333, 6),
        ("MS", 1.5707963267948966, [6, 0]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 0]),
        ("RX", -1.472621560366632, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 1]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 1]),
        ("RX", -1.3744467876706388, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 2]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 2]),
        ("RX", -1.1780972517962207, 6),
        ("RY", -7.261321924436939e-09, 6),
        ("MS", 1.5707963267948966, [6, 3]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 3]),
        ("RX", -0.7853981632740932, 6),
        ("RY", -8.159136024436953e-09, 6),
        ("MS", 1.5707963267948966, [6, 4]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 4]),
        ("RX", 0.0, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 5]),
        ("RX", -1.5707963291742124, 6),
        ("RY", 0.0, 6),
        ("MS", 1.5707963267948966, [6, 5]),
        ("RX", 1.5707963198137818, 6),
        ("RY", 1.5707963198137818, 6),
        ("MS", 1.5707963267948966, [7, 6]),
        ("RX", -1.5707963280748842, 6),
        ("RY", 1.5707963280748842, 6),
        ("MS", 1.5707963267948966, [7, 6]),
        ("RX", -1.5707963305397592, 6),
        ("RY", 0.0, 6),
    ],
    # [
    #     ("RX", 0.024543688364597013, 7),
    #     ("RY", 1.5707963173527333, 7),
    #     ("MS", 1.5707963267948966, [7, 0]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 0]),
    #     ("RX", -1.5217089438626108, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 1]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 1]),
    #     ("RX", -1.472621560366632, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 2]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 2]),
    #     ("RX", -1.3744467876706388, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 3]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 3]),
    #     ("RX", -1.1780972517962207, 7),
    #     ("RY", -7.261321924436939e-09, 7),
    #     ("MS", 1.5707963267948966, [7, 4]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 4]),
    #     ("RX", -0.7853981632740932, 7),
    #     ("RY", -8.159136024436953e-09, 7),
    #     ("MS", 1.5707963267948966, [7, 5]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 5]),
    #     ("RX", 0.0, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 6]),
    #     ("RX", -1.5707963291742124, 7),
    #     ("RY", 0.0, 7),
    #     ("MS", 1.5707963267948966, [7, 6]),
    #     ("RX", 1.5707963257426107, 7),
    #     ("RY", -1.0366307417929838e-09, 7),
    # ],
]
operation_sequences = []
for seq in operations_raw:
    new_seq = []
    for name, angle, pair in seq:
        if name != "MS":
            new_seq.append((name, angle, None))
        else:
            new_seq.append(("MS1", angle, tuple(pair)))
            new_seq.append(("MS2", angle, tuple(pair)))
    operation_sequences.append(new_seq)
operation_indices = [0] * len(initial_positions)

# Define actions and UI buttons
actions = [
    "move left",
    "move right",
    "move up",
    "move down",
    "idle",
    "RX",
    "RY",
    "MS1",
    "MS2",
    "do nothing",
]
button_rects = []
x0 = WIDTH - PANEL_WIDTH + BUTTON_MARGIN
for i, act in enumerate(actions):
    y = BUTTON_MARGIN + i * (BUTTON_HEIGHT + BUTTON_MARGIN)
    button_rects.append(
        (act, pygame.Rect(x0, y, PANEL_WIDTH - 2 * BUTTON_MARGIN, BUTTON_HEIGHT))
    )

# Toggle buttons for qubit selection
toggle_labels = [str(i) for i in range(len(initial_positions))]
toggle_rects = []
yt = BUTTON_MARGIN + len(actions) * (BUTTON_HEIGHT + BUTTON_MARGIN) + BUTTON_MARGIN
w_toggle = (PANEL_WIDTH - 2 * BUTTON_MARGIN) // len(toggle_labels)
for i, lbl in enumerate(toggle_labels):
    rect = pygame.Rect(x0 + i * w_toggle, yt, w_toggle, BUTTON_HEIGHT)
    toggle_rects.append((i, lbl, rect))

# Flash & Undo buttons
yf = yt + BUTTON_HEIGHT + BUTTON_MARGIN
flash_rect = pygame.Rect(x0, yf, PANEL_WIDTH - 2 * BUTTON_MARGIN, BUTTON_HEIGHT)
undo_rect = pygame.Rect(
    x0,
    yf + BUTTON_HEIGHT + BUTTON_MARGIN,
    PANEL_WIDTH - 2 * BUTTON_MARGIN,
    BUTTON_HEIGHT,
)


# Coordinate transform (shift for checklist)
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


# Determine valid actions
def valid_actions():
    valid = {a: False for a in actions}
    if selected_qubit is None:
        return valid
    x, y = current_positions[selected_qubit][:2]
    node = (y, x)
    valid["move left"] = x > MIN_X
    valid["move right"] = x < MAX_X
    valid["move up"] = y > MIN_Y
    valid["move down"] = y < MAX_Y
    valid["idle"] = trap_graph.nodes[node]["type"] == "standard"
    valid["do nothing"] = True
    seq = operation_sequences[selected_qubit]
    idx = operation_indices[selected_qubit]
    if idx < len(seq):
        next_gate, _, _ = seq[idx]
        for g in ["RX", "RY", "MS1", "MS2"]:
            if g == next_gate:
                if g in ("MS1", "MS2"):
                    valid[g] = trap_graph.nodes[node]["type"] == "interaction"
                else:
                    valid[g] = True
            else:
                valid[g] = False
    return valid


# Draw last 5 MS ops checklist
def draw_checklist():
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, CHECK_WIDTH, HEIGHT))
    hdr = FONT.render("Last 5 MS Ops", True, (255, 255, 255))
    screen.blit(hdr, (10, 10))
    ms_list = []
    for t, ops in enumerate(conv_schedule):
        for op in ops:
            if op[0] == "MS":
                ms_list.append((t, op[2]))
    for i, (t, pair) in enumerate(ms_list[-5:]):
        txt = FONT.render(f"t={t}: MS {pair[0]},{pair[1]}", True, (200, 200, 200))
        screen.blit(txt, (10, 40 + i * 30))


# Draw trap graph and qubit labels
def draw_graph():
    screen.fill(BG_COLOR)
    draw_checklist()
    for u, v in trap_graph.edges():
        if u in node_positions and v in node_positions:
            pygame.draw.line(
                screen,
                EDGE_COLOR,
                to_screen(node_positions[u]),
                to_screen(node_positions[v]),
                2,
            )
    for node, (x, y) in node_positions.items():
        col = (
            STANDARD_COLOR
            if trap_graph.nodes[node]["type"] == "standard"
            else INTERACTION_COLOR
        )
        pygame.draw.circle(screen, col, to_screen((x, y)), 25)
    byn, flags = {}, {}
    for q, entry in enumerate(current_positions):
        idle = len(entry) > 2 and entry[2] == "idle"
        key = (entry[0], entry[1])
        byn.setdefault(key, []).append(q)
        flags.setdefault(key, []).append(idle)
    for (x, y), qs in byn.items():
        lbl = ",".join(str(q) for q in qs)
        clr = IDLE_LABEL_COLOR if all(flags[(x, y)]) else BUSY_LABEL_COLOR
        txt = FONT.render(lbl, True, clr)
        screen.blit(txt, txt.get_rect(center=to_screen((x, y))))
    ts = STEP_FONT.render(f"Timestep: {timestep}", True, (255, 255, 255))
    screen.blit(ts, (10, HEIGHT - 30))


# Draw UI buttons
def draw_buttons():
    v = valid_actions()
    for act, rect in button_rects:
        c = BUTTON_COLOR if v[act] else DISABLED_COLOR
        pygame.draw.rect(screen, c, rect)
        txt = FONT.render(act, True, BUTTON_TEXT_COLOR)
        screen.blit(txt, txt.get_rect(center=rect.center))
    for idx, lbl, rect in toggle_rects:
        if selected_qubit is None:
            c = DISABLED_COLOR
        elif idx == selected_qubit:
            c = (BUTTON_COLOR[0] + 50,) * 3
        else:
            c = BUTTON_COLOR
        pygame.draw.rect(screen, c, rect)
        t = FONT.render(lbl, True, BUTTON_TEXT_COLOR)
        screen.blit(t, t.get_rect(center=rect.center))
    pygame.draw.rect(screen, FLASH_COLOR, flash_rect)
    txt = FONT.render("flash timestep", True, BUTTON_TEXT_COLOR)
    screen.blit(txt, txt.get_rect(center=flash_rect.center))
    cu = BUTTON_COLOR if positions_by_timestep else DISABLED_COLOR
    pygame.draw.rect(screen, cu, undo_rect)
    u = FONT.render("undo timestep", True, BUTTON_TEXT_COLOR)
    screen.blit(u, u.get_rect(center=undo_rect.center))


# Handle actions
def handle_action(action, advance=True):
    global selected_qubit
    if not valid_actions().get(action, False):
        return
    moved = False
    if action in ("RX", "RY", "MS1", "MS2", "do nothing"):
        if action != "do nothing":
            current_operations[selected_qubit] = action
            operation_indices[selected_qubit] += 1
        moved = True
    else:
        x, y, *r = current_positions[selected_qubit]
        if action == "move left":
            x -= 1
            moved = True
        elif action == "move right":
            x += 1
            moved = True
        elif action == "move up":
            y -= 1
            moved = True
        elif action == "move down":
            y += 1
            moved = True
        elif action == "idle":
            if "idle" in r:
                r = []
            else:
                r = ["idle"]
            moved = True
        current_positions[selected_qubit] = (x, y, *r)
    if moved and advance:
        nxt = selected_qubit + 1
        selected_qubit = nxt if nxt < len(current_positions) else None


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


# Main loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and e.mod & pygame.KMOD_SHIFT:
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN, {"pos": flash_rect.center}
                        )
                    )
                elif e.key == pygame.K_DELETE and e.mod & pygame.KMOD_SHIFT:
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN, {"pos": undo_rect.center}
                        )
                    )
                elif pygame.K_0 <= e.key <= pygame.K_9:
                    sel = e.key - pygame.K_0
                    if sel < len(current_positions):
                        selected_qubit = sel
                elif selected_qubit is not None:
                    if e.key in (
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                        pygame.K_UP,
                        pygame.K_DOWN,
                    ):
                        km = {
                            pygame.K_LEFT: "move left",
                            pygame.K_RIGHT: "move right",
                            pygame.K_UP: "move up",
                            pygame.K_DOWN: "move down",
                        }
                        handle_action(km[e.key], advance=False)
                    elif e.key == pygame.K_RETURN:
                        sel = selected_qubit + 1
                        selected_qubit = sel if sel < len(current_positions) else None
                    elif e.key == pygame.K_BACKSPACE:
                        sel = selected_qubit - 1
                        selected_qubit = sel if sel >= 0 else None
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for act, rect in button_rects:
                    if rect.collidepoint(e.pos):
                        handle_action(act)
                for idx, _, rect in toggle_rects:
                    if rect.collidepoint(e.pos) and selected_qubit is not None:
                        selected_qubit = idx
                if flash_rect.collidepoint(e.pos):
                    positions_by_timestep.append(list(current_positions))
                    this_gates = []
                    defaults = {"RX": 1.57, "RY": 3.14, "MS1": 0.78, "MS2": 0.78}
                    for q, op in enumerate(current_operations):
                        if op in defaults:
                            this_gates.append((op, defaults[op], q))
                    gates_schedule.append(this_gates)

                    # build conv: include non-MS1/MS2 gates
                    conv = [
                        (g, p, q) for g, p, q in this_gates if g not in ("MS1", "MS2")
                    ]
                    conv_schedule.append(conv)

                    # group MS2 by node, then append MS to previous conv
                    ms2_map = {}
                    for g, p, q in this_gates:
                        if g == "MS2":
                            y, x = current_positions[q][:2]
                            ms2_map.setdefault((y, x), []).append((q, p))
                    for qp_list in ms2_map.values():
                        if len(qp_list) < 2:
                            continue
                        qubits = [q for q, _ in qp_list]
                        angle = qp_list[0][1]
                        for q1, q2 in combinations(qubits, 2):
                            if len(conv_schedule) >= 2:
                                conv_schedule[-2].append(("MS", angle, (q1, q2)))

                    # save both schedules
                    np.savez_compressed(
                        "gates_schedule.npz",
                        gates_schedule=np.array(gates_schedule, dtype=object),
                        conv_schedule=np.array(conv_schedule, dtype=object),
                    )
                    # check verifier
                    try:
                        print("Verifying...")
                        print([flip_positions(t) for t in positions_by_timestep])
                        print(conv_schedule)
                        verifier.verifier(
                            [flip_positions(t) for t in positions_by_timestep],
                            conv_schedule,
                            trap_graph,
                        )
                    except ValueError as er:
                        print(f"Verifier error: {er}")
                    # save positions CSV
                    header = ["t"] + [
                        f"q{i}{f}"
                        for i in range(len(current_positions))
                        for f in ("x", "y", "idle")
                    ]
                    with open("positions.csv", "w", newline="") as f:
                        w = csv.writer(f)
                        w.writerow(header)
                        for t_idx, poses in enumerate(positions_by_timestep):
                            row = [t_idx]
                            for x, y, *rst in poses:
                                row.extend([x, y, int("idle" in rst)])
                            w.writerow(row)
                    current_operations = [None] * len(current_positions)
                    selected_qubit = 0
                    timestep += 1
                if undo_rect.collidepoint(e.pos) and positions_by_timestep:
                    last = gates_schedule.pop()
                    for name, _, q in last:
                        if name in ("RX", "RY", "MS1", "MS2"):
                            operation_indices[q] = max(0, operation_indices[q] - 1)
                    conv_schedule.pop()
                    positions_by_timestep.pop()
                    current_positions = list(
                        positions_by_timestep[-1]
                        if positions_by_timestep
                        else initial_positions
                    )
                    timestep = max(0, timestep - 1)
                    selected_qubit = 0
        draw_graph()
        draw_buttons()
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()
