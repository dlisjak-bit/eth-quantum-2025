import pennylane as qml
import numpy as np

N = 2
dev = qml.device("default.qubit", wires=N)


# $wire parameter can possibly be a Sequence[int]
def minihadamard(wire: int):
    qml.RY(np.pi / 2, wires=wire)
    qml.RX(np.pi, wires=wire)


def Rz(theta: float, wire: int):
    qml.RX(np.pi, wires=wire)
    qml.RY(-theta, wires=wire)
    qml.RX(np.pi, wires=wire)




def controlled_rk(k, control_wire, target_wire):
    # Define the rotation angle
    theta = np.pi / (2 ** (k - 1))

    # Apply MS gate with specific angle
    qml.MS(np.pi / 4, wires=[control_wire, target_wire])

    # Apply RZ on target qubit
    qml.RZ(theta / 2, wires=target_wire)

    # Apply MS gate with negative angle to "undo" the entanglement
    qml.MS(-np.pi / 4, wires=[control_wire, target_wire])

    # Apply phase correction on control qubit
    qml.RZ(-theta / 3, wires=control_wire)


@qml.qnode(dev)
def circuit():
    for i in range(N):
        minihadamard(i)

    theta = np.pi / 2
    qml.ctrl(qml.RZ, control=0)(theta, wires=1)

    return qml.state()


print(len(circuit()))
print(np.round(circuit(), 2))
