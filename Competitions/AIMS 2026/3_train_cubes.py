"""
Trains the cube classifier CNN.

Differences from the arrow-detection reference:
  - 3-channel (RGB) input instead of grayscale, since color is a useful
    feature here.
  - Held-out validation split, with accuracy printed each epoch -- your
    technical report needs a real accuracy number, and "trained on 100%
    of the data with no validation" doesn't give you one.
  - The class-to-index mapping is saved to cube_labels.json instead of
    being hardcoded at inference time. Retyping ['left','no_arrow','right']
    and hoping it matches ImageFolder's alphabetical ordering is a silent
    failure waiting to happen -- one folder rename and predictions swap
    without any error.
"""

import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

BATCH_SIZE = 32
EPOCHS = 15
LR = 0.001
VAL_FRACTION = 0.15
DATA_DIR = "augmented_dataset"
MODEL_OUT = "cube_model.pt"
LABELS_OUT = "cube_labels.json"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CubeCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # 96 -> 48
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 48 -> 24
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 24 -> 12
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 12 * 12, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            preds = model(imgs).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total if total else 0.0


def main():
    print(f"Training on: {device}")

    transform = transforms.Compose([
        transforms.Resize((96, 96)),
        transforms.ToTensor(),
    ])

    full_dataset = datasets.ImageFolder(root=DATA_DIR, transform=transform)
    print("Class mapping:", full_dataset.class_to_idx)

    with open(LABELS_OUT, "w") as f:
        json.dump(full_dataset.class_to_idx, f, indent=2)

    val_size = int(len(full_dataset) * VAL_FRACTION)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    num_classes = len(full_dataset.classes)
    model = CubeCNN(num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        val_acc = evaluate(model, val_loader, device)
        print(f"Epoch {epoch + 1}/{EPOCHS}  loss={total_loss:.4f}  val_acc={val_acc:.3f}")

    torch.save(model.state_dict(), MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")
    print(f"Label mapping saved to {LABELS_OUT}")


if __name__ == "__main__":
    main()
