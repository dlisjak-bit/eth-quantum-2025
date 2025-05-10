import sys
import os
import pennylane as qml
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, qftdir)
import trap


position = [(1, 1), (1, 1), (1, 0), (1, 2), (2, 0), (2, 1), (3, 0), (3, 1, "idle")]
trap_graph = trap.create_trap_graph()
print(trap_graph.nodes(data=True))
trap.plot_trap_graph_positions(trap_graph, qubit_positions=position)
# trap.plot_trap_graph_positions(trap_graph, qubit_positions=position)
