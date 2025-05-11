import os
import sys
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, qftdir)
import trap
import verifier_og
import fidelity

N = 8
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
# convert gates to list of lists
gates = gates.tolist()

for i, timestep in enumerate(gates):
    print(i, timestep)
    if i == 74:
        # add ['RY', 0.04908738075434768, 1] to gates[74]
        gates[74].append(["RY", 0.04908738075434768, 1])
    if i == 99:
        # add ['RY', 0.04908738075434768, 1] to gates[99]
        gates[99].append(["RY", -0.39269908027431993, 4])


print("_--------------------")
gates = data["conv_schedule"]
gates = gates.tolist()
# print(gates)
for i, timestep in enumerate(gates):
    # print(i, timestep)
    if i == 75:
        gates[75].remove(("RX", -1.5707963318606, 1))
        gates[75].append(("RY", 0.04908738075434768, 1))
        gates[76].append(("RX", -1.5707963318606, 1))

        gates[76].remove(("RY", 3.0894605733846035e-09, 1))
        gates[77].append(("RY", 3.0894605733846035e-09, 1))

# add ['RY', 0.04908738075434768, 1] to gates[99]
gates.insert(99, [])
print(gates[98], gates[99], gates[100], gates[101])
all100 = all[100].copy()
all.insert(99, all100)
all[99][3] = (3, 3)
all[100][3] = (3, 3)
all[99][7] = (3, 3)
all[99][6]
all[100][3] = all[101][3]
all[100][7] = all[101][7]
print(all[98][3], all[99][3], all[100][3], all[101][3])
print(all[98][7], all[99][7], all[100][7], all[101][7])
all[99][6] = (3, 5)
all[100][6] = all[101][6]
print(all[98][6], all[99][6], all[100][6], all[101][6])
all[99][4] = (3, 5)
all[100][4] = (3, 4)
print(all[98][4], all[99][4], all[100][4], all[101][4])


# gates.insert(100, [])
# all.insert(100, all[101])
gates[100].append(["RY", -0.39269908027431993, 4])
print(gates[98], gates[99], gates[100], gates[101])
print("------------")
print(all)
print("------------")
print(gates)

verifier_og.verifier(all, gates, trap_graph)
fidelity.fidelity(all, gates, trap_graph)
