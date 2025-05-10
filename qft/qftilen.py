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


def cnot(controlwire: int, targetwire: int):
    qml.RY(np.pi/2, wires=controlwire)

    qml.IsingXX(np.pi/2, wires=[controlwire, targetwire])

    qml.RX(np.pi/2, wires=targetwire)

    qml.RX(-np.pi/2, wires=targetwire)
    qml.RY(-np.pi/2, wires=controlwire)


@qml.qnode(dev)
def circuit():
    cnot(0, 1)
    # for i in range(N):
    # minihadamard(i)
    # qml.IsingXX(np.pi, wires=)
    # controlled_rk(k=2, control_wire=0, target_wire=1)

    # theta = np.pi / (2 ** (2 - 1))
    # qml.ctrl(qml.RZ, control=0)(theta, wires=1)

    return qml.state()


print(len(circuit()))
print(np.round(circuit(), 2))
