import pennylane as qml
import numpy as np

mixed_device = qml.device("default.mixed", wires=8)


@qml.qnode(device=mixed_device)
def circuit():
    qml.QFT(wires=range(8))
    return qml.density_matrix(wires=range(8))


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
        return qml.density_matrix(wires=range(8))

    return circuit


def verifier(positions_history, gates_schedule, graph) -> None:
    """
    Verify the positions and gates schedule of the circuit.

    Args:
        positions_history (list): A list of positions for each step in the circuit.
        gates_schedule (list): A list of gates where each gate is represented as a tuple.
        graph (networkx.Graph): The graph representing the Penning trap.
    """
    print("Verifying the positions history and gates schedule...")
    if len(positions_history) != len(gates_schedule):
        raise ValueError(
            f"Length of positions history ({len(positions_history)}) does not match length of gates schedule ({len(gates_schedule)})."
        )
    for i, positions in enumerate(positions_history):
        if len(positions) != 8:
            raise ValueError(f"Invalid number of ions at step {i}: {len(positions)}")
        for j, p in enumerate(positions):
            if p not in graph.nodes():
                raise ValueError(
                    f"Invalid position: {p} at step {i} for ion {j} is not part of the graph."
                )

        if i > 0:
            prev_pos_tuple = positions_history[i - 1]
            curr_pos_tuple = positions

            for ion_idx in range(len(curr_pos_tuple)):
                p_prev = prev_pos_tuple[ion_idx]
                p_curr = curr_pos_tuple[ion_idx]

                if p_prev != p_curr:
                    if not graph.has_edge(p_prev, p_curr):
                        raise ValueError(
                            f"Error: Invalid move for ion {ion_idx} from {p_prev} to {p_curr} at step {i}. Nodes are not adjacent in the graph."
                        )

            # Check for ions swapping over the same edge
            num_ions = len(curr_pos_tuple)
            for ion1_idx in range(num_ions):
                for ion2_idx in range(
                    ion1_idx + 1, num_ions
                ):  # Iterate over unique pairs
                    prev_pos_ion1 = prev_pos_tuple[ion1_idx]
                    curr_pos_ion1 = curr_pos_tuple[ion1_idx]

                    prev_pos_ion2 = prev_pos_tuple[ion2_idx]
                    curr_pos_ion2 = curr_pos_tuple[ion2_idx]

                    # Check if ion1 moved to ion2's previous spot AND ion2 moved to ion1's previous spot
                    if (
                        prev_pos_ion1 == curr_pos_ion2
                        and prev_pos_ion2 == curr_pos_ion1
                    ):
                        # Ensure they were at different positions before swapping.
                        if prev_pos_ion1 != prev_pos_ion2:
                            raise ValueError(
                                f"Error: Ions {ion1_idx} and {ion2_idx} swapped positions ({prev_pos_ion1} <-> {prev_pos_ion2}) at step {i}."
                            )

        gate = gates_schedule[i]

        for g in gate:
            # Check gate semantics
            name, param, wires = g
            if name not in ["RX", "RY", "MS"]:
                raise ValueError(
                    f"Error: Gate name at step {i} is not RX, RY, or MS. Found: {name}"
                )
            if not isinstance(name, str):
                raise ValueError(
                    f"Error: Gate name at step {i} is not a string. Found: {type(name)}"
                )
            if not isinstance(param, (float, int)):
                raise ValueError(
                    f"Error: Gate parameter at step {i} is not a float or int. Found: {type(param)}"
                )
            if not isinstance(wires, (int, list, tuple)) or (
                isinstance(wires, (list, tuple))
                and not all(isinstance(w, int) for w in wires)
            ):
                raise ValueError(
                    f"Error: Gate wires at step {i} are not an int or a list/tuple of ints. Found: {type(wires)}"
                )

            if isinstance(wires, int):
                if not (0 <= wires < 8):
                    raise ValueError(
                        f"Error: Gate wire at step {i} is out of range [0, 8). Found: {wires}"
                    )
            elif isinstance(wires, (list, tuple)):
                if not all(0 <= w < 8 for w in wires):
                    raise ValueError(
                        f"Error: One or more gate wires at step {i} are out of range [0, 8). Found: {wires}"
                    )
            if g[0] == "MS":
                ion_0 = g[2][0]
                ion_1 = g[2][1]

                pos_0 = positions[ion_0]
                pos_1 = positions[ion_1]
                if pos_0 != pos_1:
                    raise ValueError(
                        f"Error: Ions {ion_0} and {ion_1} are not at the same position {pos_0} at step {i}."
                    )
                if graph.nodes[pos_0]["type"] != "interaction":
                    raise ValueError(
                        f"Error: MS gate at step {i} is not at an interaction node. Position: {pos_0}"
                    )
                pos_next = positions_history[i + 1]
                if not (
                    positions[ion_0] == pos_next[ion_0]
                    and positions[ion_1] == pos_next[ion_1]
                ):
                    raise ValueError(
                        f"Error: Ions {ion_0} or {ion_1} moved during MS gate at step {i + 1}."
                    )
            elif g[0] == "RX" or g[0] == "RY":
                ion = g[2]
                pos_ion = positions[ion]
                if graph.nodes[pos_ion]["type"] == "interaction":
                    raise ValueError(
                        f"Error: RX/RY gate at step {i} is on interaction node. Position: {pos_ion}"
                    )
                if graph.nodes[pos_ion]["type"] == "idle":
                    raise ValueError(
                        f"Error: RX/RY gate at step {i} is on rest node. Position: {pos_ion}"
                    )
        # Check wires
        wires = [g[2] for g in gate]

        flattened_wires = []
        for wire in wires:
            if isinstance(wire, (list, tuple)):
                flattened_wires.extend(wire)
            else:
                flattened_wires.append(wire)
        if len(set(flattened_wires)) != len(flattened_wires):
            raise ValueError(
                f"Error: Duplicate wires in gate at step {i}. Wires: {flattened_wires}"
            )

        # Check for overlapping ions
        positions_set = set(positions)
        for p in positions_set:
            if p[-1] != "idle":
                corresponding_idle = (*p[:2], "idle")
                if positions.count(corresponding_idle) == 1:
                    raise ValueError(
                        f"Error: Overlapping ions at {p} with its corresponding idle position at step {i}."
                    )

        if len(positions_set) < len(positions):
            overlapping_positions = [p for p in positions if positions.count(p) > 1]

            for overlap in overlapping_positions:
                if graph.nodes[overlap]["type"] != "interaction":
                    raise ValueError(
                        f"Error: Overlapping ions at non-interaction node {overlap} at step {i}."
                    )
                if positions.count(overlap) > 2:
                    raise ValueError(
                        f"Error: More than two ions overlapping at interaction node {overlap} at step {i}."
                    )
                overlapping_ions = [
                    idx for idx, p in enumerate(positions) if p == overlap
                ]
                has_ms_gate_b = False
                has_ms_gate_d = False

                has_ms_gate = False
                for g in gates_schedule[i]:
                    if g[0] == "MS" and set(g[2]) == set(overlapping_ions):
                        has_ms_gate_d = True
                        has_ms_gate = True
                        break
                if i > 0:
                    for g in gates_schedule[i - 1]:
                        if g[0] == "MS" and set(g[2]) == set(overlapping_ions):
                            has_ms_gate_b = True
                            has_ms_gate = True
                            break
                if not has_ms_gate:
                    raise ValueError(
                        f"Error: Overlapping ions at {overlap} at step {i} without an MS gate before, or during the overlap."
                    )
                if sum([has_ms_gate_b, has_ms_gate_d]) != 1:
                    raise ValueError(
                        f"Error: Overlapping ions at {overlap} at step {i} and step {i - 1} have conflicting MS gate. Only one MS gate should be present."
                    )
    print("Positions and gates are valid.")
    print("Verifying the fidelity of the circuit without adding noise...")
    expected_result = circuit()
    user_result = compiled_circuit(gates_schedule)()
    user_fidelity = qml.math.fidelity(expected_result, user_result)
    print("Fidelity of the circuit:", user_fidelity)
    if not np.allclose(expected_result, user_result, atol=1e-5):
        raise ValueError("The compiled circuit does not implement QFT(8).")
    print("The compiled circuit implements QFT(8).")
