# extract_trajectory.py
import pandas as pd
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from ion_n_particle_env import DummyNParticleEnv


def mask_fn(env):
    return env._valid_actions()


env = ActionMasker(DummyNParticleEnv(N=4), mask_fn)
best_model = MaskablePPO.load("best_n_particles/best_model.zip")

obs, _ = env.reset()
done = False
trajectory = []

t = 0
while not done:
    action, _ = best_model.predict(obs, deterministic=True)
    state = obs["pos"].tolist()  # [r0,c0, r1,c1, …]
    trajectory.append([t, state, action.tolist()])
    obs, reward, done, _, _ = env.step(action)
    t += 1

df = pd.DataFrame(trajectory, columns=["t", "state", "action_vector"])
print(df)
df.to_csv("best_n_trajectory.csv", index=False)
