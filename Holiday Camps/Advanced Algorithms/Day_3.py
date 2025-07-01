import gymnasium as gym
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.atari_wrappers import AtariWrapper
from stable_baselines3.common.vec_env import DummyVecEnv
from torchviz import make_dot
import numpy as np
import ale_py

gym.register_envs(ale_py)

# Create Breakout environment
def make_env():
    env = gym.make("ALE/Breakout-v5", render_mode="rgb_array")
    env = AtariWrapper(env)
    return env

env = DummyVecEnv([make_env])

# Create PPO model with CNN policy
model = PPO("CnnPolicy", env, verbose=0)

# Reset env and extract obs
obs = env.reset()[0] # shape: [H, W, C]

# Converts to [C, H, W] if needed
if obs.shape[-1] in [1,3]: # Check if it's HWC
    obs = np.transpose(obs, (2, 0, 1)) # Convert to CHW

# Add batch dimension and convert to tensor
obs_tensor = torch.tensor(np.array([obs]), dtype=torch.float32)

# Forward pass through policy
dist = model.policy.get_distribution(obs_tensor)

# Visualize graph
dot = make_dot(dist.distribution.logits, params=dict(model.policy.named_parameters()))
dot.format = "png"
dot.render("breakout_policy")

print("Saved Breakout policy graph to breakout_policy.png")
print("any awesome austin")