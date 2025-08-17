import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import matplotlib.pyplot as plt


# The Playground
env = gym.make('CartPole-v1')

# Optional
# Reproducability
# torch.manual_seed(0)
# env.reset(seed=0)

# Policy Network (Decision maker)
# Given a state (4 numbers), output an action (2 actions)
class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, action_dim)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return self.softmax(x)

# Hyperparameters
state_dim = env.observation_space.shape[0] # 4
hidden_dim = 128
action_dim = env.action_space.n # 2
gamma = 0.99
learning_rate = 1e-2

policy_net = PolicyNetwork(state_dim, hidden_dim, action_dim)
optimizer = optim.Adam(policy_net.parameters(), lr=learning_rate)

# Peek at policy output for one state
# s, _ = env.reset(seed=0)
# with torch.no_grad():
#     p = policy_net(torch.from_numpy(s).float())

# print("Action probabilities: ", p.numpy(), "sum: ", float(p.sum()))

# Select an action by sampling from the policy
def select_action(state):
    state = torch.from_numpy(state).float()
    probs = policy_net(state)
    dist = Categorical(probs)
    action = dist.sample()
    return action.item(), dist.log_prob(action)

# s, _ = env.reset(seed=0)
# with torch.no_grad():
#     for t in range(3):
#         a, lp = select_action(s)
#         s, r, term, trunc, _ = env.step(a)
#         print(f"step {t}: action={a}, reward={r}")
#         if term or trunc:
#             print('ended early')
#             break

def compute_returns(rewards, gamma):
    returns = []
    R = 0
    for r in reversed(rewards):
        R = r + gamma * R # Accumulate from the end
        returns.insert(0, R)
    returns = torch.tensor(returns)
    # Normalize
    returns = (returns - returns.mean()) / (returns.std() + 1e-9)
    return returns