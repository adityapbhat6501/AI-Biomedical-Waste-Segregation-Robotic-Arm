"""
train.py — YOLO Model Training Script.

Trains a YOLOv8 model on the biomedical waste dataset using the
Ultralytics YOLO training API.

Usage:
    python model/train.py

Before running:
    1. Place annotated images in dataset/images/train/ and dataset/images/val/
    2. Place YOLO-format label files in dataset/labels/train/ and labels/val/
    3. Verify dataset/data.yaml matches your class list
    4. Adjust config.py training hyperparameters as needed

The trained weights (best.pt, last.pt) are saved to:
    model/runs/detect/train/weights/

Copy best.pt to model/best.pt for use with the inference system.

Author: [Author Placeholder]
Version: 1.0.0
"""

import shutil
import sys
from pathlib import Path

# Add parent directory to path so config.py is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO
import config
from utils.logger import get_logger
from utils.helpers import ensure_directory, get_timestamp_str

log = get_logger(__name__)


def train_model() -> Path:
    """
    Train a YOLOv8 model on the biomedical waste dataset.

    Steps:
        1. Validate that dataset/data.yaml exists.
        2. Load the base YOLO model (from config.TRAIN_BASE_MODEL).
        3. Run training with hyperparameters from config.py.
        4. Copy best.pt to model/best.pt for immediate use.

    Returns:
        Path to the best.pt weights file in the training output directory.

    Raises:
        FileNotFoundError: If data.yaml is not found.
    """
    log.info("=" * 60)
    log.info("  YOLO Training — Biomedical Waste Segregation")
    log.info("  Started at: %s", get_timestamp_str())
    log.info("=" * 60)

    # Validate dataset config
    if not config.DATASET_YAML_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset config not found: {config.DATASET_YAML_PATH}\n"
            "Ensure dataset/data.yaml exists and is correctly formatted."
        )

    log.info("Dataset config: %s", config.DATASET_YAML_PATH)
    log.info("Base model:     %s", config.TRAIN_BASE_MODEL)
    log.info("Epochs:         %d", config.TRAIN_EPOCHS)
    log.info("Batch size:     %d", config.TRAIN_BATCH_SIZE)
    log.info("Image size:     %d", config.TRAIN_IMAGE_SIZE)

    # Load base YOLO model
    model = YOLO(config.TRAIN_BASE_MODEL)

    # Run training
    ensure_directory(config.TRAIN_OUTPUT_DIR)
    results = model.train(
        data=str(config.DATASET_YAML_PATH),
        epochs=config.TRAIN_EPOCHS,
        batch=config.TRAIN_BATCH_SIZE,
        imgsz=config.TRAIN_IMAGE_SIZE,
        project=str(config.TRAIN_OUTPUT_DIR),
        name="train",
        exist_ok=True,
        verbose=True,
    )

    # Locate best.pt from training output
    best_weights_path = config.TRAIN_OUTPUT_DIR / "train" / "weights" / "best.pt"

    if not best_weights_path.is_file():
        log.error("Training completed but best.pt not found at: %s", best_weights_path)
        return best_weights_path

    # Copy best.pt to model/ for convenient access by the inference system
    dest_path = config.MODEL_PATH
    shutil.copy2(str(best_weights_path), str(dest_path))
    log.info("Best model saved to: %s", dest_path)
    log.info("Training complete. Finished at: %s", get_timestamp_str())

    return dest_path


if __name__ == "__main__":
    try:
        output_path = train_model()
        print(f"\n✓ Training complete. Model saved to: {output_path}")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        log.exception("Unexpected error during training: %s", e)
        sys.exit(1)
