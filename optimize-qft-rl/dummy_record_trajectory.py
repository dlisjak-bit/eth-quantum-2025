# inspect_best.py
import pandas as pd
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from ion_dummy_env import DummyIonEnv


def mask_fn(env):
    return env._valid_actions()


env = ActionMasker(DummyIonEnv(), mask_fn)
best_model = MaskablePPO.load("best_dummy_model/best_model.zip")

obs, _ = env.reset()
done, trunc = False, False
log = []  # holds (t, row, col, action, reward)

t = 0
while not (done or trunc):
    action, _ = best_model.predict(obs, deterministic=True)
    prev_pos = obs["pos"].copy()  # state before acting
    obs, reward, done, trunc, _ = env.step(action)
    log.append([t, int(prev_pos[0]), int(prev_pos[1]), int(action), reward])
    t += 1

traj = pd.DataFrame(log, columns=["t", "row", "col", "action", "reward"])
print(traj)

# If you want a CSV:
traj.to_csv("best_run.csv", index=False)
