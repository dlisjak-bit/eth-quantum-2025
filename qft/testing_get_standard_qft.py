
import sys
import os
import pennylane as qml
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
sys.path.insert(0, qftdir)
print(qftdir)
import verify_only_qft

# import verifier

print(os.getcwd())

dev = qml.device("default.qubit", wires=8)

def qft_explicit(wires):
    """Apply the Quantum Fourier Transform using H and controlled R_k gates."""
    for i in range(len(wires)):
        qml.Hadamard(wires=wires[i])
        for j in range(i + 1, len(wires)):
            angle = np.pi / (2 ** (j - i))
            qml.ctrl(qml.RZ, control=wires[j])(angle, wires=wires[i])

# TRANSLATION INTO gates_schedule:
# !IMPORTANT!

# format:

gates_schedule_example = [
    # step 0
    # [("RX", np.pi, 0),   ("RY", np.pi/2, 1)],

    # # step 1
    # [("MS", np.pi/2, [0,1])],

    # # step 2
    # [("RX", np.pi/4, 2)],

    [("RZ", np.pi/2, (0, 1))], # first element of wires is control, second is target
]

# check if equivalent to normal RZ gate.

def qft_explicit_schedule(wires):
    """Apply the Quantum Fourier Transform using H and controlled R_k gates."""
    gate_schedule = []
    for i in range(len(wires)):
        gate_schedule.append([("H",0, wires[i])])
        for j in range(i + 1, len(wires)):
            angle = np.pi / (2 ** (j - i))
            # qml.ctrl(qml.RZ, control=wires[j])(angle, wires=wires[i])
            gate_schedule.append([("RZ", angle, (wires[j], wires[i]))])
    return gate_schedule

gate_sequence_test = qft_explicit_schedule([0, 1, 2, 3, 4, 5, 6, 7])
print(gate_sequence_test)
print("with gate sequences")
verify_only_qft.verifier_qft(gate_sequence_test)

# ta del dela!
print("qft with just explicit gates")
verify_only_qft.verifier_qft_dummy()
