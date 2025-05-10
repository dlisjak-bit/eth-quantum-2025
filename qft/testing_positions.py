import sys
import os
import pennylane as qml
import numpy as np

qftdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, qftdir)
import trap
position= [(0, 0), (0, 1), (1, 0), (1, 2), (2, 0), (2, 1), (3, 0), (3, 1)]
trap_graph = trap.create_trap_graph()
trap.plot_trap_graph(trap_graph)
# trap.plot_trap_graph_positions(trap_graph, qubit_positions=position)

