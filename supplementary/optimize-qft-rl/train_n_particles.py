# train_n_particles.py
import pathlib
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.callbacks import EvalCallback
from ion_n_particle_env import DummyNParticleEnv


def mask_fn(env: DummyNParticleEnv):
    return env._valid_actions()


# instantiate env with N=4 ions
train_env = ActionMasker(DummyNParticleEnv(N=4), mask_fn)
eval_env = ActionMasker(DummyNParticleEnv(N=4), mask_fn)

save_dir = pathlib.Path("best_n_particles")
save_dir.mkdir(exist_ok=True)

# every 5k steps, eval 10 episodes and save on improvement
eval_cb = EvalCallback(
    eval_env,
    best_model_save_path=str(save_dir),
    log_path=str(save_dir / "logs"),
    eval_freq=5_000,
    n_eval_episodes=10,
    deterministic=True,
)

model = MaskablePPO(
    policy="MultiInputPolicy",  # <— required for Dict obs
    env=train_env,
    verbose=1,
    n_steps=1024,
    ent_coef=0.01,
    learning_rate=3e-4,
)

model.learn(total_timesteps=100_000, callback=eval_cb)
