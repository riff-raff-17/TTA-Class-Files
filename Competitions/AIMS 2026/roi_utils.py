"""
Shared ROI (Region of Interest) definition for the cube classifier.

Keeping this in one place guarantees that the region of the frame you
train on (capture script) is exactly the region you run inference on
(test script) -- and, later, the region your main line-following code
will crop before classifying. A train/deploy mismatch in the crop is one
of the most common silent causes of a model that works great on your
laptop and falls apart on the actual field.

Tune ROI_WIDTH_FRAC / ROI_HEIGHT_FRAC / ROI_TOP_FRAC to match wherever
cubes actually appear in the camera frame when the robot is sitting at
its cube-approach / stop distance. Defaults assume cubes show up in a
centered band in the lower half of the frame -- check this against a
real frame from your robot before you start capturing data.
"""

# Fraction of frame width the ROI spans, centered horizontally
ROI_WIDTH_FRAC = 0.5
# Fraction of frame height the ROI spans
ROI_HEIGHT_FRAC = 0.65
# Where the *top* of the ROI starts, as a fraction of frame height
# (0 = top of frame, 1 = bottom of frame)
ROI_TOP_FRAC = 0.25


def get_roi_box(frame_width, frame_height):
    """Returns (x1, y1, x2, y2) pixel coordinates of the ROI for a frame
    of the given size."""
    roi_w = int(frame_width * ROI_WIDTH_FRAC)
    roi_h = int(frame_height * ROI_HEIGHT_FRAC)

    x1 = (frame_width - roi_w) // 2
    x2 = x1 + roi_w

    y1 = int(frame_height * ROI_TOP_FRAC)
    y2 = min(y1 + roi_h, frame_height)

    return x1, y1, x2, y2


def crop_roi(frame):
    """Crops the shared ROI out of a full BGR camera frame (numpy array)."""
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = get_roi_box(w, h)
    return frame[y1:y2, x1:x2]
