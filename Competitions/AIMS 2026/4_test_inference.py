"""
Standalone test harness for the trained cube classifier.

Runs live on the UGOT robot's camera feed and displays the predicted
class + confidence for whatever is in the shared ROI. Deliberately does
NOT drive the robot or trigger any collect/avoid behavior -- this is
just for validating the model in isolation before it gets wired into
your line-following/actuation code.
"""

import json
import queue
import threading

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from ugot import ugot

from roi_utils import crop_roi, get_roi_box

UGOT_IP = "192.168.1.53"
MODEL_PATH = "cube_model.pt"
LABELS_PATH = "cube_labels.json"
CONFIDENCE_THRESHOLD = 0.75

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CubeCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 12 * 12, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def main():
    with open(LABELS_PATH) as f:
        class_to_idx = json.load(f)
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    model = CubeCNN(len(class_to_idx)).to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((96, 96)),
        transforms.ToTensor(),
    ])

    got = ugot.UGOT()
    got.initialize(UGOT_IP)
    got.open_camera()

    frame_q = queue.Queue(maxsize=1)

    def grab_frames():
        while True:
            raw = got.read_camera_data()
            if not raw:
                break
            if not frame_q.full():
                frame_q.put(raw)

    threading.Thread(target=grab_frames, daemon=True).start()

    print("Press 'q' to quit.")

    while True:
        try:
            raw = frame_q.get(timeout=0.1)
        except queue.Empty:
            continue

        nparr = np.frombuffer(raw, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = get_roi_box(w, h)
        roi_bgr = crop_roi(frame)
        roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)

        input_tensor = transform(roi_rgb).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
            conf = conf.item()
            pred_label = idx_to_class[pred_idx.item()]

        if conf >= CONFIDENCE_THRESHOLD:
            text = f"{pred_label} ({conf:.2f})"
            color = (0, 255, 0)
        else:
            text = f"Uncertain ({pred_label} {conf:.2f})"
            color = (0, 165, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        cv2.imshow("Cube Classifier Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
