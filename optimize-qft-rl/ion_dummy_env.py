# ion_dummy_env.py
import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DummyIonEnv(gym.Env):
    """
    5×5 grid, one ion that must reach centre (2,2) and press 'gate'.
    """

    metadata = {"render_modes": []}

    def __init__(self, max_steps: int = 50):
        super().__init__()
        self.grid_size = 5
        self.max_steps = max_steps
        self.action_space = spaces.Discrete(5)  # 0:N,1:E,2:S,3:W,4:gate
        # observation = {"pos": (row,col), "action_mask": 5‑bool}
        self.observation_space = spaces.Dict(
            {
                "pos": spaces.MultiDiscrete([self.grid_size, self.grid_size]),
                "action_mask": spaces.MultiBinary(5),
            }
        )
        self._pos = (0, 0)
        self._steps = 0

    # ───── helper ────────────────────────────────────────────────────────────
    def _valid_actions(self):
        r, c = self._pos
        mask = np.zeros(5, dtype=np.int8)
        # moves
        mask[0] = r > 0  # N
        mask[1] = c < self.grid_size - 1  # E
        mask[2] = r < self.grid_size - 1 and c < 2  # S
        mask[3] = c > 0  # W
        # gate only on centre square
        mask[4] = r == 2 and c == 2
        return mask

    def _get_obs(self):
        return {
            "pos": np.array(self._pos, dtype=np.int64),
            "action_mask": self._valid_actions(),
        }

    # ───── Gym API ───────────────────────────────────────────────────────────
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._pos = (0, 0)
        self._steps = 0
        return self._get_obs(), {}

    def step(self, action: int):
        if not self._valid_actions()[action]:
            # shouldn’t happen with a masked agent, but keep env robust
            reward = -1.0
            terminated = True
            return self._get_obs(), reward, terminated, False, {}

        r, c = self._pos
        if action == 0:
            r -= 1
        elif action == 1:
            c += 1
        elif action == 2:
            r += 1
        elif action == 3:
            c -= 1
        elif action == 4:
            pass  # gate (no move)

        self._pos = (r, c)
        self._steps += 1

        terminated = action == 4  # succeed when gate pressed
        truncated = self._steps >= self.max_steps
        reward = 1.0 if terminated else -0.01  # tiny step penalty
        return self._get_obs(), reward, terminated, truncated, {}
