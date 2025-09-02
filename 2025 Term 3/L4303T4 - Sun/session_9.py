import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import gymnasium as gym
from gymnasium.wrappers import RecordVideo
import pickle
from numpy.core.multiarray import scalar as np_scalar

# Hyperparamters and directories
ENV_NAME = "CartPole-v1"
NUM_EPISODES = 500
SAVE_INTERVAL = 50
HIDDEN_DIM = 128
LEARNING_RATE = 1e-2
GAMMA = 0.99

CKPT_DIR = "checkpoints"
VIDEO_DIR = "videos_post"

os.makedirs(CKPT_DIR, exit_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Policy Network
class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.state_dim = int(state_dim)
        self.action_dim = int(action_dim)

        self.net = nn.Sequential(
            nn.Linear(self.state_dim, HIDDEN_DIM),
            nn.ReLU(),
            nn.Linear(HIDDEN_DIM, self.action_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.net(x)
    
# Utilities

def select_action(state, policy_net):
    state = torch.from_numpy(state).float()
    probs = policy_net(state)
    dist = Categorical(probs)
    action = dist.sample()
    return action.item(), dist.log_prob(action)

def compute_returns(rewards):
    R = 0.0
    returns = []
    for r in reversed(rewards):
        R = r + GAMMA * R
        returns.insert(0, R)
    returns = torch.tensor(returns, dtype=torch.float32)
    return (returns - returns.mean()) / (returns.std() + 1e-9)

def save_checkpoints(model, episode):
    filename = os.path.join(CKPT_DIR, f"policy_ep{episode:04d}.pth")
    payload = {
        "state_dict": model.state_dict(),
        "state_dim": int(model.state_dim),
        "action_dim": int(model.action_dim)
    }
    torch.save(payload, filename)
    return filename

def _infer_dims(state_dict):
    linear_weight_keys = [
        k for k in state_dict.keys()
        if k.startswith("net.") and k.endswith(".weight")
    ]
    if not linear_weight_keys:
        raise ValueError("Could not find linear weights for dims")
    
    def layer_index(k):
        try:
            return int(k.split(".")[1])
        except:
            return 1_000_000
        
    linear_weight_keys.sort(key=layer_index)
    first_w = state_dict[linear_weight_keys[0]] # shape [hidden, state_dim]
    last_w = state_dict[linear_weight_keys[-1]] # shape [action_dim, hidden]

    if first_w.ndim != 2 or last_w.ndim != 2:
        raise ValueError("Not linear")
    
    state_dim = int(first_w.shape[1])
    action_dim = int(last_w.shape[0])
    return state_dim, action_dim

def load_checkpoint(path, map_location='cpu'):
    try:
        with torch.serialization.safe_globals([np_scalar]):
            ckpt = torch.load(path, weights_only=True, map_location=map_location)
    except pickle.UnpicklingError as e:
            raise RuntimeError(
                "failed :( let mr rafa know you have a pickling error"
            ) from e
    
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        state_dict = ckpt["state_dict"]
        state_dim = int(ckpt["state_dim"])
        action_dim = int(ckpt["action_dim"])
        