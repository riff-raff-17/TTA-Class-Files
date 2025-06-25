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