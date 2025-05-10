import pennylane as qml
import numpy as np


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


if __name__ == "__main__":
    N = 2
    dev = qml.device("default.qubit", wires=N)
    dev1 = qml.device("default.qubit", wires=N)

    @qml.qnode(dev)
    def circuit():
        qml.X(wires=0)
        qml.ctrl(qml.X, control=0)(wires=1)

        return qml.density_matrix(wires=range(N))

    @qml.qnode(dev1)
    def cnot():
        qml.X(wires=0)
        CNOT(0, 1)
        
        return qml.state()


    # expected_results = circuit()
    user_results = cnot()
    print(np.round(user_results, 2))

    # if np.allclose(expected_results, user_results, atol=1e-5):
    #     print("Correct")
    # else:
    #     print(expected_results - user_results)

