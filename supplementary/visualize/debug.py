import numpy as np
import itertools
import json

# — after you load your 'positions' and call verifier/fidelity —

# load your converted schedule:
data = np.load("gates_schedule.npz", allow_pickle=True)
conv = list(
    data["conv_schedule"]
)  # list of timesteps, each is [(op, angle, qubit),...]
# print(len(conv))
# print(conv[0])
# build per-qubit actual streams:
print(conv[0])
print(conv[60])
N = 8
actual = [[] for _ in range(N)]
for t, timestep in enumerate(conv):
    # print(timestep)
    for ops in timestep:
        # print(ops)
        # check if ops[2] is list
        if isinstance(ops[2], tuple):
            # print("list")
            # print(ops[2])
            for qi in range(len(ops[2])):
                actual[ops[2][qi]].append((t, ops[0], ops[1], ops[2]))
                # print(actual[ops[2][qi]])
        else:
            actual[ops[2]].append((t, ops[0], ops[1], ops[2]))
            # print(actual[ops[2]])


# your reference sequences:
# for each qubit q, A[q] = list of (opname, angle) in the expected order
with open("test.json", "r") as f:
    data = json.load(f)
A = [
    data["A0"],
    data["A1"],
    data["A2"],
    data["A3"],
    data["A4"],
    data["A5"],
    data["A6"],
    data["A7"],
]
# print(actual)
# compare them:
for q in range(N):
    print(f"\nQubit {q}:")
    exp_seq = A[q]
    act_seq = actual[q]
    # print(f"expected: {exp_seq}")
    # print(f"actual:   {act_seq}")
    for i in range(len(exp_seq)):
        if i >= len(act_seq):
            print(f" step {i:2d}: expected={exp_seq[i]}, actual=None")
            continue
        # print(f" step {i:2d}: expected={exp_seq[i]}, actual={act_seq[i]}")
        if exp_seq[i] != act_seq[i]:
            print(f" step {i:2d}: expected={exp_seq[i]}, actual={act_seq[i]}")
    # maxlen = max(len(exp_seq), len(act_seq))
    # for i in range(maxlen):
    #     exp = exp_seq[i] if i < len(exp_seq) else None
    #     act = (act_seq[i][1], act_seq[i][2]) if i < len(act_seq) else None
    #     if exp != act:
    #         print(f" step {i:2d}: expected={exp!r}, actual={act!r}")
