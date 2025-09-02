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

"""
# Fake returns
rs = [1, 1, 1, 1]

# Compute raw discounted (no normalization)
gamma = 0.99
raw_returns = []
R = 0
for r in reversed(rs):
    R = r + gamma * R
    raw_returns.insert(0, R)

# Compute normalized returns (like in the real ai)
returns_tensor = torch.tensor(raw_returns, dtype=torch.float32)
normalized_returns = (returns_tensor - returns_tensor.mean()) / (returns_tensor.std() + 1e-9)

print("Toy rewards: ", rs)
print("Raw discounted returns: ", [round(x, 2) for x in raw_returns])
print("Normalized discounted returns: ", [round(x.item(), 2) for x in normalized_returns])
"""

# Training loop
def train_policy_gradient(num_episodes=500, print_interval=50):
    episode_rewards = []

    for episode in range(1, num_episodes + 1):
        state, _ = env.reset()
        log_probs = []
        rewards = []
        done = False

        while not done:
            action, log_prob = select_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            log_probs.append(log_prob)
            rewards.append(reward)
            state = next_state
        
        # Turn rewards into returns (credit over time)
        returns = compute_returns(rewards, gamma)

        # REINFORCE: encourage actions that lead to higher return
        loss_terms = []
        for log_prob, R in zip(log_probs, returns):
            loss_terms.append(-log_prob * R)
        loss = torch.stack(loss_terms).sum()

        # Standard pytorch update
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_reward = sum(rewards)
        episode_rewards.append(total_reward)

        # Periodic progress printouts
        if episode % print_interval == 0:
            avg_reward = sum(episode_rewards[-print_interval:]) / print_interval
            print(f"Episode {episode}\tAverage Reward: {avg_reward:.2f}")

    return episode_rewards

# Run training
# This may take a while depending on the computer
episode_rewards = train_policy_gradient(num_episodes=100, print_interval=10)

def plot_rewards(rewards):
    plt.figure(figsize=(10, 5))
    plt.plot(rewards)
    plt.xlabel('Episode')
    plt.ylabel("Total Reward")
    plt.title("Episode Reward over Time")
    plt.show()

plot_rewards(episode_rewards)