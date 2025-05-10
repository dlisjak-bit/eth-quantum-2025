import pennylane as qml
import numpy as np

mixed_device = qml.device("default.mixed", wires=8)
N = 8


@qml.qnode(device=mixed_device)
def circuit():
    qml.QFT(wires=range(N))
    return qml.density_matrix(wires=range(N))


def compiled_circuit(gates_schedule) -> qml.QNode:
    """
    Build the compiled circuit from the gates schedule.

    Args:
        gates_schedule (list): A list of gates where each gate is represented as a tuple.

    Returns:
        qml.QNode: A Pennylane QNode representing the circuit.
    """

    @qml.qnode(device=mixed_device)
    def circuit():
        for step in gates_schedule:
            for gate in step:
                if gate[0] == "RX":
                    qml.RX(gate[1], wires=gate[2])
                elif gate[0] == "RY":
                    qml.RY(gate[1], wires=gate[2])
                elif gate[0] == "MS":
                    qml.IsingXX(gate[1], wires=gate[2])
                ################ Custom extra gates----------------------------------------------------------
                elif gate[0] == "H":
                    qml.Hadamard(wires=gate[2])
                elif gate[0] == "RZ":
                    qml.ctrl(qml.RZ, control=gate[2][0])(gate[1], wires=gate[2][1])
        # qml.GlobalPhase(np.pi/2)
        return qml.density_matrix(wires=range(N))

    return circuit


def create_circuit_dummy() -> qml.QNode:
    """
    Buuild only RZ with np.pi/2 circuit for testing purposes."""

    @qml.qnode(device=mixed_device)
    def circuit():
        qml.Hadamard(wires=0)
        # qml.RX(np.pi, wires=0)
        return qml.density_matrix(wires=range(N))

    return circuit


def create_qft_dummy() -> qml.QNode:
    """
    Build a dummy circuit for testing purposes.
    """

    @qml.qnode(device=mixed_device)
    def qft_explicit(wires=range(N)):
        for i in range(len(wires)):
            qml.Hadamard(wires=wires[i])
            for j in range(i + 1, len(wires)):
                angle = np.pi / (2 ** (j - i))
                qml.ctrl(qml.RZ, control=wires[j])(angle, wires=wires[i])
        return qml.density_matrix(wires=wires)

    return qft_explicit


circuit_dummy = create_circuit_dummy()
qft_dummy = create_qft_dummy()


def verifier_qft(gates_schedule, use_dummy=False) -> None:
    user_result = compiled_circuit(gates_schedule)()
    if use_dummy:
        expected_result = circuit_dummy()
    else:
        expected_result = circuit()
    if not np.allclose(expected_result, user_result, atol=1e-5):
        raise ValueError("The compiled circuit does not implement QFT(8).")
    print("The compiled circuit implements QFT(8).")


def verifier_qft_dummy() -> None:
    user_result = qft_dummy()
    expected_result = circuit()
    if not np.allclose(expected_result, user_result, atol=1e-5):
        raise ValueError("The compiled circuit does not implement QFT(8).")
    print("The compiled circuit implements QFT(8).")
