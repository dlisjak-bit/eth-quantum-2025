# cp_n_ions.py
from ortools.sat.python import cp_model


def solve_n_ions(N: int, T: int, time_limit_s: int = 30):
    """Solves for N ions on a 5×5 grid over T timesteps."""
    model = cp_model.CpModel()

    # --- 1. Grid & position encoding ---
    grid_size = 5
    # List of (r,c) pairs
    positions = [(r, c) for r in range(grid_size) for c in range(grid_size)]
    num_pos = len(positions)  # =25
    pos_to_id = {pos: i for i, pos in enumerate(positions)}
    start_id = pos_to_id[(0, 0)]
    goal_id = pos_to_id[(2, 2)]

    # --- 2. State variables x[p,t] ∈ {0…24} ---
    x = {}
    for p in range(N):
        for t in range(T):
            x[p, t] = model.NewIntVar(
                0, num_pos - 1, f"x_{p}_{t}"
            )  # :contentReference[oaicite:0]{index=0}

    # --- 3. Initial and final constraints ---
    for p in range(N):
        model.Add(x[p, 0] == start_id)  # all start at (0,0)
        model.Add(x[p, T - 1] == goal_id)  # all end at (2,2)

    # --- 4. Legal transitions via AddAllowedAssignments ---
    # Precompute allowed (from→to) tuples for one ion
    allowed_moves = []
    for s_id, (r, c) in enumerate(positions):
        # neighbors + stay
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid_size and 0 <= nc < grid_size:
                allowed_moves.append((s_id, pos_to_id[(nr, nc)]))

    for p in range(N):
        for t in range(T - 1):
            model.AddAllowedAssignments(
                [x[p, t], x[p, t + 1]], allowed_moves
            )  # :contentReference[oaicite:1]{index=1}

    # --- 5. Movement indicator vars & objective ---
    move_vars = []
    for p in range(N):
        for t in range(T - 1):
            m = model.NewBoolVar(
                f"move_{p}_{t}"
            )  # :contentReference[oaicite:2]{index=2}
            # m = 1 ↔ x[p,t] ≠ x[p,t+1]
            model.Add(x[p, t] != x[p, t + 1]).OnlyEnforceIf(m)
            model.Add(x[p, t] == x[p, t + 1]).OnlyEnforceIf(m.Not())
            move_vars.append(m)
    model.Minimize(sum(move_vars))

    # --- 6. Solve ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Extract positions_history[t][p]
        positions_history = []
        for t in range(T):
            positions_history.append([solver.Value(x[p, t]) for p in range(N)])
        # Map back to (r,c)
        pos_hist_rc = [[positions[id] for id in step] for step in positions_history]
        print(f"Found solution with total moves = {solver.ObjectiveValue()}")
        for t, step in enumerate(pos_hist_rc):
            print(f" t={t}: {step}")
    else:
        print("No solution found within time limit.")


if __name__ == "__main__":
    # Example: 3 ions over 10 timesteps
    solve_n_ions(N=3, T=10)
