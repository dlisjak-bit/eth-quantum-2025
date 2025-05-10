import pennylane as qml
import numpy as np

mixed_device = qml.device("default.mixed", wires=8)


@qml.qnode(device=mixed_device)
def circuit():
    qml.QFT(wires=range(8))
    return qml.density_matrix(wires=range(8))


def get_temperatures(positions_history, graph):
    """
    Calculate the temperature of each ion based on its positions history and the graph.

    Args:
        positions_history (list): A list of positions of the ions.
        graph (nx.Graph): The graph representing the circuit.

    Returns:
        list: A list of temperatures for each ion.
    """
    temperature = [[0.0] * len(positions_history[0])]
    for i, pos in enumerate(positions_history):
        temp = temperature[-1].copy()
        for j, p in enumerate(pos):
            if i > 0:
                if p == positions_history[i - 1][j]:
                    if graph.nodes[p]["type"] == "idle":
                        temp[j] += 0.01
                    else:
                        temp[j] += 0.02
                else:
                    temp[j] += 0.03
        temperature.append(temp)
    temperature.pop(0)
    return temperature


# Create noisy circuit

from pennylane.operation import Channel

eps = eps = 1e-14


class DepolarizingChannel(Channel):
    num_params = 1
    num_wires = 2
    grad_method = "A"
    grad_recipe = ([[1, 0, 1], [-1, 0, 0]],)

    def __init__(self, p, wires, id=None):
        super().__init__(p, wires=wires, id=id)

    @staticmethod
    def compute_kraus_matrices(p):  # pylint:disable=arguments-differ
        r"""Kraus matrices representing the depolarizing channel."""
        if not 0.0 <= p <= 1.0:
            raise ValueError("p must be in the interval [0,1]")

        I = np.array([[1, 0], [0, 1]], dtype=complex)
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        Z = np.array([[1, 0], [0, -1]], dtype=complex)

        pauli_2qubit = [
            np.kron(I, I),
            np.kron(X, I),
            np.kron(Y, I),
            np.kron(Z, I),
            np.kron(I, X),
            np.kron(I, Y),
            np.kron(I, Z),
            np.kron(X, X),
            np.kron(X, Y),
            np.kron(X, Z),
            np.kron(Y, X),
            np.kron(Y, Y),
            np.kron(Y, Z),
            np.kron(Z, X),
            np.kron(Z, Y),
            np.kron(Z, Z),
        ]
        return [
            np.sqrt(1 - p + eps) * pauli_2qubit[0],
            np.sqrt(p / 15 + eps) * pauli_2qubit[1],
            np.sqrt(p / 15 + eps) * pauli_2qubit[2],
            np.sqrt(p / 15 + eps) * pauli_2qubit[3],
            np.sqrt(p / 15 + eps) * pauli_2qubit[4],
            np.sqrt(p / 15 + eps) * pauli_2qubit[5],
            np.sqrt(p / 15 + eps) * pauli_2qubit[6],
            np.sqrt(p / 15 + eps) * pauli_2qubit[7],
            np.sqrt(p / 15 + eps) * pauli_2qubit[8],
            np.sqrt(p / 15 + eps) * pauli_2qubit[9],
            np.sqrt(p / 15 + eps) * pauli_2qubit[10],
            np.sqrt(p / 15 + eps) * pauli_2qubit[11],
            np.sqrt(p / 15 + eps) * pauli_2qubit[12],
            np.sqrt(p / 15 + eps) * pauli_2qubit[13],
            np.sqrt(p / 15 + eps) * pauli_2qubit[14],
            np.sqrt(p / 15 + eps) * pauli_2qubit[15],
        ]


def compiled_circuit_noisy(gates_schedule, temperature) -> qml.QNode:
    """
    Build a noisy circuit from the list of gates and the ion temperatures.

    Args:
        gates_schedule (list): A list of gates where each gate is represented as a tuple.

    Returns:
        qml.QNode: A Pennylane QNode representing the circuit.
    """
    dev = qml.device("default.mixed", wires=8)

    @qml.qnode(dev)
    def circuit():
        for i, step in enumerate(gates_schedule):
            temp = temperature[i]
            for gate in step:
                if gate[0] == "RX":
                    qml.RX(gate[1], wires=gate[2])
                elif gate[0] == "RY":
                    qml.RY(gate[1], wires=gate[2])
                elif gate[0] == "MS":
                    temp1 = temp[gate[2][0]]
                    temp2 = temp[gate[2][1]]
                    average_temp = (temp1 + temp2) / 2
                    prob = (
                        (np.pi**2 * (0.05) ** 4)
                        / 4
                        * average_temp
                        * (2 * average_temp + 1)
                    )
                    assert 0.0 <= prob <= 1.0, (
                        f"Average temperature too high: ion {gate[2][0]}: {temp1}, ion {gate[2][1]}: {temp2}"
                    )
                    qml.IsingXX(gate[1], wires=gate[2])
                    DepolarizingChannel(prob, wires=gate[2])
        return qml.density_matrix(wires=range(8))

    return circuit


def fidelity(positions_history, gates_schedule, graph) -> float:
    """
    Fidelity between the ideal and noisy circuit.

    Args:
        positions_history (list): A list of positions of the ions.
        gates_schedule (list): A list of gates where each gate is represented as a tuple.

    Returns:
        float: The fidelity of the circuit.
    """
    expected_result = circuit()
    noisy_user_result = compiled_circuit_noisy(
        gates_schedule, get_temperatures(positions_history, graph)
    )()
    noisy_user_fidelity = qml.math.fidelity(expected_result, noisy_user_result)
    print("Fidelity of the circuit when including noise:", noisy_user_fidelity)
    return noisy_user_fidelity
