import os
import sys
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, qftdir)
import trap
import verifier
import fidelity

N = 3
all = []
trap_graph = trap.create_trap_graph()

with open("positions.csv", "r") as f:
    for line in f:
        timestep = []
        if line.startswith("t"):
            continue
        line = line.strip().split(",")[1:]
        for i in range(N):
            y = int(line[i * 3])
            x = int(line[i * 3 + 1])
            idle = int(line[i * 3 + 2])
            if idle == 0:
                timestep.append((x, y))
            else:
                timestep.append((x, y, "idle"))
        all.append(timestep)

data = np.load("gates_schedule.npz", allow_pickle=True)
print(data)
gates = data["gates_schedule"]
for i, timestep in enumerate(gates):
    print(i, timestep)

print("_--------------------")
gates = data["conv_schedule"]
for i, timestep in enumerate(gates):
    print(i, timestep)


verifier.verifier(all, gates, trap_graph)
fidelity.fidelity(all, gates, trap_graph)
