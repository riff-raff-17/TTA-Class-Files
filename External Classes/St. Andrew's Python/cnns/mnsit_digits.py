# mnist_draw_gui.py
# pip install torch torchvision pillow

import tkinter as tk
from tkinter import ttk
import threading
import io
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import torch, torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import time
import os
import sys
import math
import traceback

# -------- Harden runtime for stability --------
# Force single-threaded compute to avoid OpenMP/MKL thrash
torch.set_num_threads(1)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

# ---------------------------
# Model
# ---------------------------
class MNISTCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                 # 14x14
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                 # 7x7
            nn.Flatten(),
            nn.Linear(64*7*7, 128), nn.ReLU(),
            nn.Linear(128, 10)
        )
    def forward(self, x): return self.net(x)

# ---------------------------
# Training (quick & robust)
# ---------------------------
def train_mnist_quick(
    epochs=2,
    batch_size=128,
    device="cpu",
    status_cb=None,
    progress_cb=None,
    use_subset=True,
    subset_size=10000,
    num_workers=0,
    cancel_flag=lambda: False
):
    """
    Trains a small CNN on MNIST with defensive defaults.
    - CPU by default (flip to CUDA later)
    - num_workers=0 (safe inside threads)
    - optional subset for fast epochs
    - progress callbacks
    """
    def say(msg):
        if status_cb: status_cb(msg)

    say("Preparing data ...")
    tfm_train = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    tfm_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    # Download can sometimes be the slow part on first run
    train_ds = datasets.MNIST("data", train=True, download=True, transform=tfm_train)
    test_ds  = datasets.MNIST("data", train=False, download=True, transform=tfm_test)

    if use_subset:
        # Use a fixed subset for speed & determinism
        indices = list(range(min(subset_size, len(train_ds))))
        train_ds = Subset(train_ds, indices)

    pin = (device == "cuda")
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=pin)
    test_loader  = DataLoader(test_ds, batch_size=256,
                              num_workers=num_workers, pin_memory=pin)

    model = MNISTCNN().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-2)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(1, epochs+1):
        if cancel_flag(): 
            say("Training cancelled.")
            return None
        say(f"Training (epoch {epoch}/{epochs}) ...")
        model.train()
        n_batches = math.ceil(len(train_loader.dataset) / batch_size)
        b = 0
        t0 = time.time()
        for xb, yb in train_loader:
            if cancel_flag():
                say("Training cancelled.")
                return None
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()

            b += 1
            # Update progress every ~10 batches
            if progress_cb and (b % 10 == 0 or b == n_batches):
                elapsed = time.time() - t0
                progress_cb(epoch, epochs, b, n_batches, float(loss.item()), elapsed)

    # quick eval
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for xb, yb in test_loader:
            pred = model(xb.to(device)).argmax(1).cpu()
            correct += (pred == yb).sum().item()
            total += yb.size(0)
    acc = correct / total
    say(f"Done. Test accuracy ~ {acc:.3f}. Draw a digit!")
    return model

# ---------------------------
# Preprocess for inference
# ---------------------------
MNIST_MEAN, MNIST_STD = 0.1307, 0.3081

def preprocess_pil_to_tensor(img28: Image.Image, device="cpu"):
    tfm = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((MNIST_MEAN,), (MNIST_STD,))
    ])
    x = tfm(img28).unsqueeze(0).to(device)  # (1,1,28,28)
    return x

def prepare_from_canvas(pil_canvas_image: Image.Image):
    img = pil_canvas_image.convert("L")
    # If background is light (mean>127), invert (we want white digit on black)
    if np.asarray(img).mean() > 127:
        img = ImageOps.invert(img)

    # Tight crop to content
    bbox = ImageOps.invert(img).getbbox()
    if bbox:
        img = img.crop(bbox)

    # Fit to 28x28, centered (keep aspect)
    # Pillow>=9 uses Image.Resampling; older Pillow: Image.LANCZOS
    resample = getattr(Image, "Resampling", Image).LANCZOS
    img = ImageOps.pad(img, (28, 28), method=resample, color=0, centering=(0.5, 0.5))
    return img

# ---------------------------
# Tkinter App
# ---------------------------
class DrawAndPredictApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MNIST: Draw a digit (0–9), then Predict")

        # Force CPU first for reliability (flip to CUDA later if desired)
        self.device = "cpu"  # "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._cancel_training = False

        # UI Layout
        self.status = tk.StringVar(value="Training model (subset for speed)...")
        ttk.Label(self.root, textvariable=self.status).pack(pady=6)

        # Progress bar + label
        pframe = ttk.Frame(self.root)
        pframe.pack(pady=4, fill="x", padx=8)
        self.pbar = ttk.Progressbar(pframe, mode="determinate", maximum=100)
        self.pbar.pack(side="left", fill="x", expand=True)
        self.ptext = tk.StringVar(value="")
        ttk.Label(pframe, textvariable=self.ptext, width=24).pack(side="left", padx=6)

        # Canvas area
        self.W = self.H = 280  # 10x MNIST size for easier drawing
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="black", cursor="cross")
        self.canvas.pack(padx=8, pady=8)

        # Mirror PIL image (we draw here too for clean capture)
        self.pil_img = Image.new("RGB", (self.W, self.H), "black")
        self.pil_draw = ImageDraw.Draw(self.pil_img)
        self.last_x, self.last_y = None, None
        self.brush_size = 20  # thickness of strokes

        self.canvas.bind("<ButtonPress-1>", self.on_pen_down)
        self.canvas.bind("<B1-Motion>", self.on_pen_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_pen_up)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Predict", command=self.predict).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.clear_canvas).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Cancel Training", command=self.cancel_training).grid(row=0, column=2, padx=4)

        # Prediction label
        self.pred_var = tk.StringVar(value="Prediction: —")
        ttk.Label(self.root, textvariable=self.pred_var, font=("Arial", 14, "bold")).pack(pady=4)

        # Start training in a background thread so UI stays responsive
        threading.Thread(target=self._train_background, daemon=True).start()

    # ----- thread-safe UI helpers -----
    def _set_status(self, msg: str):
        self.root.after(0, self.status.set, msg)

    def _set_pred(self, msg: str):
        self.root.after(0, self.pred_var.set, msg)

    def _set_progress(self, epoch, epochs, batch_idx, total_batches, loss, elapsed):
        pct_epoch = int(100 * batch_idx / max(1, total_batches))
        self.root.after(0, self.pbar.configure, {"value": pct_epoch})
        self.root.after(0, self.ptext.set,
                        f"ep {epoch}/{epochs} | {batch_idx}/{total_batches} | loss {loss:.3f}")

    # Drawing handlers
    def on_pen_down(self, event):
        self.last_x, self.last_y = event.x, event.y

    def on_pen_move(self, event):
        x, y = event.x, event.y
        if self.last_x is not None:
            # draw on Tk canvas
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                    width=self.brush_size, fill="white",
                                    capstyle=tk.ROUND, smooth=True)
            # mirror draw on PIL image
            self.pil_draw.line((self.last_x, self.last_y, x, y),
                               width=self.brush_size, fill="white", joint="curve")
        self.last_x, self.last_y = x, y

    def on_pen_up(self, _):
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.pil_img.paste("black", [0, 0, self.W, self.H])
        self._set_pred("Prediction: —")

    def cancel_training(self):
        self._cancel_training = True
        self._set_status("Cancelling training...")

    # Training in background
    def _train_background(self):
        try:
            model = train_mnist_quick(
                epochs=2,
                batch_size=128,
                device=self.device,           # start with CPU for reliability
                status_cb=self._set_status,
                progress_cb=self._set_progress,
                use_subset=True,              # fast first pass
                subset_size=10000,
                num_workers=0,                # critical inside threads
                cancel_flag=lambda: self._cancel_training
            )
            if model is None:
                return
            self.model = model
        except Exception:
            tb = traceback.format_exc()
            self._set_status(f"Training failed:\n{tb}")
            return
        self._set_status("Model ready. Draw a digit and click Predict.")
        # Reset progress bar
        self.root.after(0, self.pbar.configure, {"value": 0})
        self.root.after(0, self.ptext.set, "")

    # Prediction
    @torch.no_grad()
    def predict(self):
        if self.model is None:
            self._set_pred("Model not ready yet...")
            return
        img28 = prepare_from_canvas(self.pil_img)
        x = preprocess_pil_to_tensor(img28, device=self.device)
        self.model.eval()
        logits = self.model(x)
        probs = logits.softmax(dim=1).squeeze(0).cpu().numpy()
        top = int(probs.argmax())
        conf = float(probs[top])
        top3_idx = probs.argsort()[-3:][::-1]
        top3_str = ", ".join([f"{i}:{probs[i]:.2f}" for i in top3_idx])
        self._set_pred(f"Prediction: {top}  (p={conf:.2f})  | top-3: {top3_str}")

    def run(self):
        self.root.mainloop()

# ---------------------------
# Entry
# ---------------------------
if __name__ == "__main__":
    app = DrawAndPredictApp()
    app.run()
