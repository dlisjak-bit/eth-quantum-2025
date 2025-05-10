import pennylane as qml
import numpy as np


RY = lambda theta, wire: [("RY", theta, wire)]
RX = lambda theta, wire: [("RX", theta, wire)]


def minihadamard(wire: int):
    qml.RY(np.pi / 2, wires=wire)
    qml.RX(np.pi, wires=wire)

minihadamard = lambda wire: RY(np.pi / 2, wire) + RX(np.pi, wire)


def RZ(theta: float, wire: int):
    qml.RX(-np.pi / 2, wires=wire)
    qml.RY(theta, wires=wire)
    qml.RX(np.pi / 2, wires=wire)

RZ = lambda theta, wire: RX(-np.pi / 2, wire) + RY(theta, wire) + RX(np.pi / 2, wire)


def CNOT(control: int, target: int):
    qml.RY(np.pi / 2, wires=control)
    qml.IsingXX(np.pi / 2, wires=[control, target])
    qml.RX(-np.pi / 2, wires=target)
    qml.RX(-np.pi / 2, wires=control)
    qml.RY(-np.pi / 2, wires=control)

IsingXX = lambda theta, control, target: [("MS", np.pi / 2, control, target)]

CNOT = lambda control, target: RY(np.pi / 2, control) + IsingXX(np.pi / 2, control, target) + \
                            RX(-np.pi / 2, target) + RX(-np.pi / 2, control) + RY(-np.pi / 2, control)


def RK(k: int, wire: int):
    RZ(2 * np.pi / 2**k, wire)

RK = lambda k, wire: RZ(2 * np.pi / 2 ** k, wire)


def RK_dag(k: int, wire: int):
    RZ(-2 * np.pi / 2**k, wire)

RK_dag = lambda k, wire: RZ(-2 * np.pi / 2**k, wire)


def CRK(k: int, control: int, target: int):
    RK(k + 1, target)
    RK(k + 1, control)
    CNOT(control, target)
    RK_dag(k + 1, target)
    CNOT(control, target)

CRK = lambda k, control, target: RK(k + 1, target) + RK(k + 1, control) + CNOT(control, target) + RK_dag(k + 1, target) + CNOT(control, target)



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

