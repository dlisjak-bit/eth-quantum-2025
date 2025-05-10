import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def create_trap_graph() -> nx.Graph:
    """Create a graph representing the Penning trap.

    The Penning trap is represented as a grid of nodes, where each node can be
    either an interaction node or a standard node. The interaction nodes are
    connected to their corresponding idle nodes, and the standard nodes are
    connected to their neighboring standard nodes.
    """

    trap = nx.Graph()

    rows = 5
    cols = 7

    interaction_nodes = [(1, 1), (1, 3), (3, 1), (3, 3), (1, 5), (3, 5)]

    for r in range(rows):
        for c in range(cols):
            base_node_id = (r, c)

            if base_node_id in interaction_nodes:
                trap.add_node(base_node_id, type="interaction")
            else:
                trap.add_node(base_node_id, type="standard")
                rest_node_id = (r, c, "idle")
                trap.add_node(rest_node_id, type="idle")
                trap.add_edge(base_node_id, rest_node_id)

    for r in range(rows):
        for c in range(cols):
            node_id = (r, c)
            if c + 1 < cols:
                neighbor_id = (r, c + 1)
                trap.add_edge(node_id, neighbor_id)
            if r + 1 < rows:
                neighbor_id = (r + 1, c)
                trap.add_edge(node_id, neighbor_id)
    return trap


def plot_trap_graph_positions(
    trap_graph,
    qubit_positions=None,
    idle_height=1.5,
    figsize=(8, 8),
    label_offset=0.1,
    label_size=10,
):
    """
    Plot the Penning trap graph in 3D, optionally annotating qubit indices.

    Parameters
    ----------
    trap_graph : nx.Graph
      Graph with node attr 'type' ∈ {'standard','interaction','idle'}.
    qubit_positions : list, optional
      A list of node‐IDs (e.g. positions_history[t]) giving where each qubit lives.
    idle_height : float, optional
      z‐coordinate for all idle nodes.
    figsize : tuple, optional
      passed to plt.figure.
    label_offset : float, optional
      how far above the node to draw the qubit index.
    label_size : int, optional
      fontsize for the qubit index text.
    """
    # 1) build 3D coords for every node
    pos3d = {}
    for n, data in trap_graph.nodes(data=True):
        t = data["type"]
        if t in ("standard", "interaction"):
            r, c = n
            z = 0
        else:  # idle
            r, c, _ = n
            z = idle_height
        pos3d[n] = (c, r, z)

    # 2) draw graph
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor((1, 1, 1, 0))
    ax.yaxis.pane.set_edgecolor((1, 1, 1, 0))
    ax.zaxis.pane.set_edgecolor((1, 1, 1, 0))
    ax.grid(False)

    # edges
    for u, v in trap_graph.edges():
        x0, y0, z0 = pos3d[u]
        x1, y1, z1 = pos3d[v]
        ax.plot([x0, x1], [y0, y1], [z0, z1], color="lightgray", lw=1)

    # nodes
    specs = {
        "standard": ("blue", 50),
        "interaction": ("red", 80),
        "idle": ("green", 50),
    }
    for t, (col, sz) in specs.items():
        nodes = [n for n, d in trap_graph.nodes(data=True) if d["type"] == t]
        xs = [pos3d[n][0] for n in nodes]
        ys = [pos3d[n][1] for n in nodes]
        zs = [pos3d[n][2] for n in nodes]
        ax.scatter(xs, ys, zs, c=col, s=sz, label=t.capitalize(), depthshade=True)

    # 3) add qubit‐index labels
    if qubit_positions is not None:
        for q_idx, node in enumerate(qubit_positions):
            if len(node) < 3:  # not idle
                x, y, z = pos3d[node]
            else:
                x, y, z = pos3d[node[:2]]
                z += idle_height
            # draw number just above the dot
            ax.text(
                x,
                y,
                z + label_offset,
                str(q_idx),
                fontsize=label_size,
                ha="center",
                va="bottom",
                color="black",
            )

    # final styling
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Idle Height")
    ax.legend(loc="upper left")
    ax.set_title(
        "Penning Trap Graph" + (f" – step with qubits" if qubit_positions else "")
    )
    plt.tight_layout()
    plt.show()


def plot_trap_graph(trap_graph, idle_height=1.5, figsize=(8, 8)):
    """
    Plot the Penning trap graph in 3D.

    Parameters
    ----------
    trap_graph : nx.Graph
        A graph with node attribute 'type' in {'standard','interaction','idle'}.
        Standard & interaction nodes should be keyed by (r,c),
        idle nodes by (r,c,'idle').
    idle_height : float, optional
        z‐coordinate at which to place all idle nodes (default=1.5).
    figsize : tuple, optional
        Figure size passed to plt.figure (default=(8,8)).
    """
    # build 3D positions
    pos = {}
    for n, data in trap_graph.nodes(data=True):
        t = data.get("type")
        if t in ("standard", "interaction"):
            r, c = n
            z = 0
        elif t == "idle":
            r, c, _ = n
            z = idle_height
        else:
            raise ValueError(f"Unknown node type {t!r}")
        pos[n] = (c, r, z)

    # start figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    # draw edges
    for u, v in trap_graph.edges():
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        ax.plot([x0, x1], [y0, y1], [z0, z1], color="lightgray", linewidth=1)

    # draw nodes by type
    specs = {
        "standard": ("blue", 50),
        "interaction": ("red", 80),
        "idle": ("green", 50),
    }
    for t, (color, size) in specs.items():
        ns = [n for n, d in trap_graph.nodes(data=True) if d["type"] == t]
        xs = [pos[n][0] for n in ns]
        ys = [pos[n][1] for n in ns]
        zs = [pos[n][2] for n in ns]
        ax.scatter(xs, ys, zs, c=color, s=size, label=t.capitalize(), depthshade=True)

    # labels & legend
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Idle Height")
    ax.legend(loc="upper left")
    ax.set_title("Penning Trap Graph")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    plt.tight_layout()
    plt.show()
    # plt.savefig("trap_graph.pdf")
