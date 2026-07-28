"""
config.py — Central Configuration for AI Biomedical Waste Segregation Module.

All runtime parameters are defined here.
No other module should hardcode any of these values.
Edit this file to adapt the system to different hardware or environments.

Author: [Author Placeholder]
Version: 1.0.0
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project Root
# ---------------------------------------------------------------------------

# Absolute path to the ai/ directory (this file's parent)
PROJECT_ROOT: Path = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Camera Configuration
# ---------------------------------------------------------------------------

# MJPEG stream URL of the ESP32-CAM module.
# Format: http://<ip-address>/stream  or  http://<ip-address>:81/stream
CAMERA_URL: str = "http://192.168.1.100:81/stream"

# Resolution to resize incoming frames before inference (width, height).
# Smaller values = faster inference, lower accuracy.
FRAME_WIDTH: int = 640
FRAME_HEIGHT: int = 480

# Number of seconds to wait before attempting camera reconnect.
CAMERA_RECONNECT_DELAY_S: float = 3.0

# Maximum number of consecutive reconnect attempts before aborting.
CAMERA_MAX_RECONNECT_ATTEMPTS: int = 10

# ---------------------------------------------------------------------------
# Serial / UART Communication Configuration
# ---------------------------------------------------------------------------

# Serial port connected to the ESP32 controller.
# Windows: "COM3", "COM4", etc.
# Linux/macOS: "/dev/ttyUSB0", "/dev/cu.usbserial-0001", etc.
SERIAL_PORT: str = "COM3"

# Baud rate — must match UART_BAUD_RATE in firmware config.h
SERIAL_BAUD_RATE: int = 115200

# Seconds to wait for a response from the ESP32 after sending a command.
SERIAL_TIMEOUT_S: float = 2.0

# Seconds between automatic serial reconnect attempts.
SERIAL_RECONNECT_DELAY_S: float = 3.0

# Maximum reconnect attempts before raising an error.
SERIAL_MAX_RECONNECT_ATTEMPTS: int = 10

# ---------------------------------------------------------------------------
# AI Model Configuration
# ---------------------------------------------------------------------------

# Path to the trained YOLO model weights file.
MODEL_PATH: Path = PROJECT_ROOT / "model" / "best.pt"

# Fallback pretrained base model (used if best.pt is not found).
MODEL_FALLBACK_PATH: Path = PROJECT_ROOT / "model" / "yolov8n.pt"

# Input image size fed to the YOLO model (square, pixels).
MODEL_INPUT_SIZE: int = 640

# Minimum confidence score [0.0–1.0] for a detection to be accepted.
CONFIDENCE_THRESHOLD: float = 0.50

# Intersection-over-Union (IoU) threshold for NMS duplicate suppression.
IOU_THRESHOLD: float = 0.45

# Maximum number of detections returned per frame.
MAX_DETECTIONS: int = 10

# ---------------------------------------------------------------------------
# Inference / Classification Configuration
# ---------------------------------------------------------------------------

# Minimum confidence required before sending a command to the ESP32.
# Can be set higher than CONFIDENCE_THRESHOLD to reduce false commands.
COMMAND_CONFIDENCE_THRESHOLD: float = 0.60

# Number of consecutive frames a class must appear before commanding ESP32.
# Prevents spurious commands from single-frame false positives.
COMMAND_STABILITY_FRAMES: int = 3

# Seconds to wait between sending repeated commands for the same detection.
COMMAND_COOLDOWN_S: float = 5.0

# ---------------------------------------------------------------------------
# Dataset Configuration
# ---------------------------------------------------------------------------

# Path to the YOLO dataset configuration file.
DATASET_YAML_PATH: Path = PROJECT_ROOT / "dataset" / "data.yaml"

# Path to the dataset images directory.
DATASET_IMAGES_PATH: Path = PROJECT_ROOT / "dataset" / "images"

# Path to the dataset labels directory.
DATASET_LABELS_PATH: Path = PROJECT_ROOT / "dataset" / "labels"

# ---------------------------------------------------------------------------
# Training Configuration
# ---------------------------------------------------------------------------

# Number of epochs for model training.
TRAIN_EPOCHS: int = 100

# Training batch size. Reduce if GPU memory is limited.
TRAIN_BATCH_SIZE: int = 16

# Input image size during training.
TRAIN_IMAGE_SIZE: int = 640

# Base model to fine-tune from ('yolov8n.pt', 'yolov8s.pt', etc.).
TRAIN_BASE_MODEL: str = "yolov8n.pt"

# Directory where training results (weights, metrics) are saved.
TRAIN_OUTPUT_DIR: Path = PROJECT_ROOT / "model" / "runs"

# ---------------------------------------------------------------------------
# Display Configuration
# ---------------------------------------------------------------------------

# Window title for the OpenCV display window.
DISPLAY_WINDOW_TITLE: str = "Biomedical Waste Segregation — AI Detection"

# Whether to show the detection overlay window.
DISPLAY_SHOW_WINDOW: bool = True

# Whether to show FPS counter on the display window.
DISPLAY_SHOW_FPS: bool = True

# Whether to show confidence scores on bounding box labels.
DISPLAY_SHOW_CONFIDENCE: bool = True

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

# Directory where log files are saved.
LOG_DIR: Path = PROJECT_ROOT / "logs"

# Log file name.
LOG_FILE_NAME: str = "detection.log"

# Full path to the log file.
LOG_FILE_PATH: Path = LOG_DIR / LOG_FILE_NAME

# Logging level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL: str = "INFO"

# Maximum log file size in bytes before rotation.
LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB

# Number of rotated log files to keep.
LOG_BACKUP_COUNT: int = 3

# ---------------------------------------------------------------------------
# Debug Mode
# ---------------------------------------------------------------------------

# When True: verbose console output, no serial commands sent to ESP32.
DEBUG_MODE: bool = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# When True: use a local webcam (index 0) instead of the ESP32-CAM stream.
DEBUG_USE_WEBCAM: bool = os.environ.get("DEBUG_USE_WEBCAM", "false").lower() == "true"

# Local webcam device index (used when DEBUG_USE_WEBCAM is True).
DEBUG_WEBCAM_INDEX: int = 0
