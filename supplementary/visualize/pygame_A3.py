import pygame
import sys
import os
import csv
import numpy as np
from itertools import combinations
import json

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
    # (3, 0),
    # (4, 0),
    # (5, 0),
    # (6, 1),
    # (5, 4),
]
current_positions = list(initial_positions)
num_qubits = len(initial_positions)
current_positions = []
current_operations = [None] * num_qubits
positions_by_timestep = []
gates_schedule = []
conv_schedule = []
operation_sequences = []
operation_indices = [0] * num_qubits
# Raw operations (user-provided) and translation
# read A0, A1, A2, A3, A4, A5, A6, A7 from the file test.json
A0 = [
    ("RY", 1.5707963267948966, 0),
    ("RX", 3.141592653589793, 0),
    ("RX", -1.5707963267948966, 0),
    ("RY", 1.5707963267948966, 0),
    ("RX", 1.5707963267948966, 0),
    ("MS", 1.5707963267948966, [1, 0]),
    ("RX", -1.5707963267948966, 0),
    ("RX", -1.5707963267948966, 0),
    ("RY", -1.5707963267948966, 0),
    ("RX", 1.5707963267948966, 0),
    ("MS", 1.5707963267948966, [1, 0]),
    ("RX", -1.5707963267948966, 0),
    ("RX", -1.5707963267948966, 0),
    ("RY", 0.7853981633974483, 0),
    ("RX", 1.5707963267948966, 0),
    ("MS", 1.5707963267948966, [2, 0]),
    ("RX", -1.5707963267948966, 0),
    ("RX", -1.5707963267948966, 0),
    ("RY", -0.7853981633974483, 0),
    ("RX", 1.5707963267948966, 0),
    ("MS", 1.5707963267948966, [2, 0]),
    ("RX", -1.5707963267948966, 0),
]

A1 = [
    ("RX", -1.5707963267948966, 1),
    ("RY", 1.5707963267948966, 1),
    ("RX", 1.5707963267948966, 1),
    ("RY", 1.5707963267948966, 1),
    ("MS", 1.5707963267948966, [1, 0]),
    ("RX", -1.5707963267948966, 1),
    ("RY", -1.5707963267948966, 1),
    ("RY", 1.5707963267948966, 1),
    ("MS", 1.5707963267948966, [1, 0]),
    ("RX", -1.5707963267948966, 1),
    ("RY", -1.5707963267948966, 1),
    ("RY", 1.5707963267948966, 1),
    ("RX", 3.141592653589793, 1),
    ("RX", -1.5707963267948966, 1),
    ("RY", 1.5707963267948966, 1),
    ("RX", 1.5707963267948966, 1),
    ("MS", 1.5707963267948966, [2, 1]),
    ("RX", -1.5707963267948966, 1),
    ("RX", -1.5707963267948966, 1),
    ("RY", -1.5707963267948966, 1),
    ("RX", 1.5707963267948966, 1),
    ("MS", 1.5707963267948966, [2, 1]),
    ("RX", -1.5707963267948966, 1),
]
A2 = [
    ("RX", -1.5707963267948966, 2),
    ("RY", 0.7853981633974483, 2),
    ("RX", 1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("MS", 1.5707963267948966, [2, 0]),
    ("RX", -1.5707963267948966, 2),
    ("RY", -1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("MS", 1.5707963267948966, [2, 0]),
    ("RX", -1.5707963267948966, 2),
    ("RY", -1.5707963267948966, 2),
    ("RX", -1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("RX", 1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("MS", 1.5707963267948966, [2, 1]),
    ("RX", -1.5707963267948966, 2),
    ("RY", -1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("MS", 1.5707963267948966, [2, 1]),
    ("RX", -1.5707963267948966, 2),
    ("RY", -1.5707963267948966, 2),
    ("RY", 1.5707963267948966, 2),
    ("RX", 3.141592653589793, 2),
]

operations_raw = [A0, A1, A2]
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


def load_state():

    global positions_by_timestep, gates_schedule, conv_schedule, current_positions, timestep
    # Load positions.csv
    if os.path.exists("positions.csv"):
        with open("positions.csv", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        positions_by_timestep = []
        for row in rows:
            # row: [t, q0x, q0y, q0idle, q1x, ...]
            pos = []
            for i in range(num_qubits):
                x = int(row[1 + i * 3])
                y = int(row[2 + i * 3])
                idle = bool(int(row[3 + i * 3]))
                if idle:
                    pos.append((x, y, "idle"))
                else:
                    pos.append((x, y))
            positions_by_timestep.append(pos)
        print(f"Loaded {len(positions_by_timestep)} timesteps from positions.csv")
    # Load gates_schedule.npz
    if os.path.exists("gates_schedule.npz"):
        data = np.load("gates_schedule.npz", allow_pickle=True)
        gates_schedule[:] = list(data["gates_schedule"])
        conv_schedule[:] = list(data["conv_schedule"])
        if "operation_indices" in data:
            operation_indices[:] = list(data["operation_indices"])
        else:
            print(
                "WARNING: operation_indices not found in gates_schedule.npz, using default values."
            )
        print(f"Loaded {len(gates_schedule)} timesteps from gates_schedule.npz")
    # Set current positions and timestep
    timestep = len(positions_by_timestep)
    if positions_by_timestep:
        current_positions[:] = positions_by_timestep[-1]
    else:
        current_positions[:] = list(initial_positions)


load_state()
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
                    for q, op in enumerate(current_operations):
                        if op in ("RX", "RY", "MS1", "MS2"):
                            # operation_indices[q] was bumped already, so the last applied index is -1
                            idx = operation_indices[q] - 1
                            # fetch name and angle (we ignore the 'pair' field here)
                            name, angle, *_ = operation_sequences[q][idx]
                            this_gates.append((name, angle, q))

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
                        operation_indices=np.array(operation_indices),
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
