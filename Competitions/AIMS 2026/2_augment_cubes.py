"""
Augmentation for the cube dataset.

Unlike the arrow-detection reference (which converted to grayscale,
since arrow shape was the only signal), this KEEPS COLOR throughout --
color is one of the most useful features for telling a 25mm cube from a
50mm cube, and stripping it would throw that signal away.

Hue jitter is kept intentionally small: a big hue shift risks pushing an
"unripe" color (blue/white/green/pink) into "ripe" hue territory (or vice
versa) in an augmented copy, which would train the model on a mislabeled
example. Rotation/affine/brightness/contrast jitter is more generous,
since those don't risk crossing a class boundary.
"""

import os

from PIL import Image
from torchvision import transforms

INPUT_ROOT = "dataset"
OUTPUT_ROOT = "augmented_dataset"
CLASSES = ["ripe", "unripe", "background"]

IMAGE_SIZE = (96, 96)
COPIES_PER_IMAGE = 6

base_transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
])

augmentation = transforms.Compose([
    transforms.RandomRotation(degrees=25),
    transforms.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.25, hue=0.03),
    transforms.RandomAffine(degrees=0, translate=(0.08, 0.08), scale=(0.85, 1.15)),
])


def main():
    for label in CLASSES:
        os.makedirs(os.path.join(OUTPUT_ROOT, label), exist_ok=True)

    for label in CLASSES:
        input_dir = os.path.join(INPUT_ROOT, label)
        output_dir = os.path.join(OUTPUT_ROOT, label)

        if not os.path.isdir(input_dir):
            print(f"Skipping missing folder: {input_dir}")
            continue

        files = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        print(f"{label}: {len(files)} source images -> {len(files) * (COPIES_PER_IMAGE + 1)} after augmentation")

        for fname in files:
            img_path = os.path.join(input_dir, fname)
            image = Image.open(img_path).convert("RGB")

            base_image = base_transform(image)
            base_name, ext = os.path.splitext(fname)
            base_image.save(os.path.join(output_dir, fname))

            for i in range(COPIES_PER_IMAGE):
                aug_image = augmentation(base_image)
                aug_image.save(os.path.join(output_dir, f"{base_name}_aug{i}{ext}"))

    print("Augmentation complete.")


if __name__ == "__main__":
    main()
