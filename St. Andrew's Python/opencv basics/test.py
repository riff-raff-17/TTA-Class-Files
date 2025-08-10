import cv2
import numpy as np

# Create a blank image (white background)
frame = np.ones((500, 500, 3), dtype=np.uint8) * 255

# 1️⃣ Basic shapes
cv2.rectangle(frame, (50, 50), (200, 200), (0, 0, 255), 2)       # Red rectangle
cv2.circle(frame, (350, 150), 50, (255, 0, 0), 2)                 # Blue circle
cv2.line(frame, (50, 300), (200, 450), (0, 255, 0), 3)            # Green line

# 2️⃣ Filled shapes
cv2.circle(frame, (350, 350), 40, (0, 255, 255), -1)              # Filled yellow circle

# 3️⃣ Overlay with transparency
overlay = frame.copy()
cv2.rectangle(overlay, (100, 100), (400, 400), (128, 0, 128), -1) # Filled purple rectangle
alpha = 0.4  # transparency factor
cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

# Show the final image
cv2.imshow("Shapes & Overlay Demo", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
