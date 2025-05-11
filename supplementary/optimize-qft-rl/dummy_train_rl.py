# train_and_save_best.py
import os, pathlib
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.callbacks import EvalCallback
from ion_dummy_env import DummyIonEnv  # ← your minimal env from previous step


# ---------- helper to expose the mask -----------------
def mask_fn(env: DummyIonEnv):
    return env._valid_actions()


train_env = ActionMasker(DummyIonEnv(), mask_fn)

# ---------- separate eval env so scores are unbiased --
eval_env = ActionMasker(DummyIonEnv(), mask_fn)

save_dir = pathlib.Path("best_dummy_model")
save_dir.mkdir(exist_ok=True)

# EvalCallback: evaluates every eval_freq steps and saves model if reward ↑
eval_cb = EvalCallback(
    eval_env,
    best_model_save_path=str(save_dir),
    log_path=str(save_dir / "logs"),
    eval_freq=2_000,  # evaluate every 2 000 env steps
    n_eval_episodes=20,  # take the mean reward over 20 episodes
    deterministic=True,
    render=False,
)

model = MaskablePPO(
    "MultiInputPolicy",
    train_env,
    verbose=1,
    tensorboard_log=str(save_dir / "tb"),
    n_steps=512,
    ent_coef=0.01,
    learning_rate=3e-4,
)

model.learn(total_timesteps=50_000, callback=eval_cb)  # ~30 s on CPU
