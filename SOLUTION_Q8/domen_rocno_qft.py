import sys
import os
import pennylane as qml
import numpy as np

import verify_only_qft
from gates import minihadamard, CRK

N = 8


def qft_explicit_schedule(wires):
    """Apply the Quantum Fourier Transform using H and controlled R_k gates."""
    gate_schedule = []
    for i in range(len(wires)):
        # gate_schedule.append([("H",0, wires[i])])
        gate_schedule.extend(minihadamard(wires[i]))
        for j in range(i + 1, len(wires)):
            angle = np.pi / (2 ** (j - i))
            # qml.ctrl(qml.RZ, control=wires[j])(angle, wires=wires[i])
            # gate_schedule.append(
            #     [("RZ", angle, (wires[j], wires[i]))]
            # )  # prvi wire: control, drugi: target
            gate_schedule.extend(CRK(j - i, wires[j], wires[i]))
    return gate_schedule


# hadamard_test_schedule = hadamard_test(0)
# verify_only_qft.verifier_qft(hadamard_test_schedule, use_dummy=True)


for qubit in range(N):
    Output = []
    gate_sequence_test = qft_explicit_schedule(range(N))
    count = 0
    print("Gate sequence test:", len(gate_sequence_test))
    for gate in gate_sequence_test:
        # print("Gate:", gate)
        if gate[0][2] == qubit:
            Output.append(gate[0])
            count += 1
        elif gate[0][0] == "MS":
            if qubit in gate[0][2]:
                count += 1
                Output.append(gate[0])
    print("Count:", count)
    verify_only_qft.verifier_qft(gate_sequence_test)
    print("QUBIT:", qubit)
    print(Output)
# qubit = 0  # 1-8 al 0-7

# gate_sequence_test = qft_explicit_schedule(range(N))
# count = 0
# print("Gate sequence test:", len(gate_sequence_test))
# for gate in gate_sequence_test:
#     # print("Gate:", gate)
#     if gate[0][2] == qubit:
#         Output.append(gate[0])
#         count += 1
#     elif gate[0][0] == "MS":
#         if qubit in gate[0][2]:
#             count += 1
#             Output.append(gate[0])
# print("Count:", count)
# verify_only_qft.verifier_qft(gate_sequence_test)

# print(Output)
