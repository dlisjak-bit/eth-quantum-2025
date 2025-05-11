all = []
N = 8
with open("positions.csv", "r") as f:
    for line in f:
        timestep = []
        if line.startswith("t"):
            continue
        line = line.strip().split(",")[1:]
        for i in range(N):
            x = int(line[i * 3])
            y = int(line[i * 3 + 1])
            idle = int(line[i * 3 + 2])
            if idle == 0:
                timestep.append((x, y))
            else:
                timestep.append((x, y, "idle"))
        all.append(timestep)
# print(all)
for i, timestep in enumerate(all):
    print(i, timestep)

import numpy as np

data = np.load("gates_schedule.npz", allow_pickle=True)
print(data)
gates = data["gates_schedule"]
for i, timestep in enumerate(gates):
    print(i, timestep)

print("_--------------------")
gates = data["conv_schedule"]
for i, timestep in enumerate(gates):
    print(i, timestep)
