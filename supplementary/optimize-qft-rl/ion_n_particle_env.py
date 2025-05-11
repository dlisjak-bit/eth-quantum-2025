import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DummyNParticleEnv(gym.Env):
    """
    5×5 grid, N ions all starting at (0,0). Goal: get all to (2,2) and press 'gate'.
    Joint action is a vector of length N, each in {0:N,1:E,2:S,3:W,4:gate}.
    """

    metadata = {"render_modes": []}

    def __init__(self, N: int = 3, max_steps: int = 100):
        super().__init__()
        self.N = N
        self.grid_size = 5
        self.max_steps = max_steps

        # Joint action: one move per ion
        self.action_space = spaces.MultiDiscrete([5] * N)

        # Observation: positions + mask
        #  - "pos": a length-2N vector [r0, c0, r1, c1, …]
        #  - "action_mask": a flat binary mask of size N*5
        self.observation_space = spaces.Dict(
            {
                "pos": spaces.MultiDiscrete([self.grid_size] * 2 * self.N),
                "action_mask": spaces.MultiBinary(self.N * 5),
            }
        )

        # state
        self._pos = [(0, 0)] * N
        self._steps = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._pos = [(0, 0)] * self.N
        self._steps = 0
        return self._get_obs(), {}

    def step(self, action):
        """
        action: array-like of length N, each in {0,1,2,3,4}.
        """
        mask = self._valid_actions()  # flat length N*5
        # check legality
        for i, a in enumerate(action):
            if mask[i * 5 + a] == 0:
                # illegal, terminate early
                return self._get_obs(), -1.0, True, False, {}

        # apply moves
        new_pos = []
        for i, a in enumerate(action):
            r, c = self._pos[i]
            if a == 0 and r > 0:
                r -= 1
            elif a == 1 and c < self.grid_size - 1:
                c += 1
            elif a == 2 and r < self.grid_size - 1:
                r += 1
            elif a == 3 and c > 0:
                c -= 1
            # a==4 is gate: no move
            new_pos.append((r, c))
        self._pos = new_pos
        self._steps += 1

        # reward: +1 if *all* ions pressed gate on (2,2)
        # i.e. action[i]==4 and pos[i]==(2,2) ∀i
        if all(a == 4 and p == (2, 2) for a, p in zip(action, self._pos)):
            return self._get_obs(), +1.0, True, False, {}

        # else small step penalty
        done = self._steps >= self.max_steps
        return self._get_obs(), -0.01, done, False, {}

    def _get_obs(self):
        pos_flat = []
        for r, c in self._pos:
            pos_flat += [r, c]
        return {
            "pos": np.array(pos_flat, dtype=np.int64),
            "action_mask": self._valid_actions(),
        }

    def _valid_actions(self):
        """
        Build a binary mask of shape (N,5), flattened to (N*5,).
        For each ion i:
          - moves 0–3 legal only if on-grid
          - gate (4) legal only on centre square (2,2)
        """
        mask = np.zeros((self.N, 5), dtype=np.int8)
        for i, (r, c) in enumerate(self._pos):
            mask[i, 0] = 1 if r > 0 else 0
            mask[i, 1] = 1 if c < self.grid_size - 1 else 0
            mask[i, 2] = 1 if r < self.grid_size - 1 else 0
            mask[i, 3] = 1 if c > 0 else 0
            mask[i, 4] = 1 if (r == 2 and c == 2) else 0
        return mask.flatten()
