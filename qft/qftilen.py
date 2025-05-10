import pennylane as qml
import numpy as np

N = 2
dev = qml.device("default.qubit", wires=N)
dev1 = qml.device("default.qubit", wires=N)


# $wire parameter can possibly be a Sequence[int]
def minihadamard(wire: int):
    qml.RY(np.pi / 2, wires=wire)
    qml.RX(np.pi, wires=wire)


def Rz(theta: float, wire: int):
    qml.RX(-np.pi / 2, wires=wire)
    qml.RY(theta, wires=wire)
    qml.RX(np.pi / 2, wires=wire)


def CNOT(control: int, target: int):
    qml.RY(np.pi / 2, wires=control)
    qml.IsingXX(np.pi / 2, wires=[control, target])
    qml.RX(-np.pi / 2, wires=target)
    qml.RX(-np.pi / 2, wires=control)
    qml.RY(-np.pi / 2, wires=control)


def Rk(k: int, wire: int):
    Rz(2 * np.pi / 2**k, wire)


def Rk_dag(k: int, wire: int):
    Rz(-2 * np.pi / 2**k, wire)


def CRk(k: int, control: int, target: int):
    Rk(k + 1, target)
    Rk(k + 1, control)
    CNOT(control, target)
    Rk_dag(k + 1, target)
    CNOT(control, target)


@qml.qnode(dev)
def circuit(k=2):
    # qml.RZ(theta, 1)
    qml.ctrl(qml.RZ(2 * np.pi / (2**k), wires=1), control=0)
    return qml.density_matrix(wires=range(N))


@qml.qnode(dev1)
def cnot(k=2):
    CRk(k, control=0, target=1)
    # Rz(theta, 1)
    return qml.density_matrix(wires=range(N))


expected_results = circuit()
user_results = cnot()

if np.allclose(expected_results, user_results, atol=1e-5):
    print("Correct")
else:
    print("Wrong")
    print(expected_results - user_results)
