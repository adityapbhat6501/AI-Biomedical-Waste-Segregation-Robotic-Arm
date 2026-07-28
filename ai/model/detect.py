"""
detect.py — Standalone Detection Script for Testing and Validation.

Runs inference on a single image file, a directory of images, or a
live camera stream without serial communication.

Useful for:
    - Verifying model accuracy before deployment
    - Debugging detections offline
    - Generating annotated output images

Usage:
    # Test on a single image
    python model/detect.py --source path/to/image.jpg

    # Test on a directory
    python model/detect.py --source dataset/images/val/

    # Test on ESP32-CAM stream
    python model/detect.py --source stream

    # Use a specific model
    python model/detect.py --source image.jpg --model model/best.pt

Author: [Author Placeholder]
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from inference.predictor import ModelPredictor
from utils.drawing import draw_all_detections, draw_fps_overlay, draw_category_legend
from utils.helpers import FPSCounter, get_timestamp_str
from utils.logger import get_logger
from camera.esp32cam import ESP32Camera
from camera.camera_utils import is_frame_valid

log = get_logger(__name__)


def detect_on_image(image_path: Path, predictor: ModelPredictor) -> None:
    """
    Run detection on a single image file and display / save the result.

    Args:
        image_path: Path to the input image file.
        predictor:  Loaded ModelPredictor instance.
    """
    import numpy as np
    frame = cv2.imread(str(image_path))
    if frame is None:
        log.error("Could not read image: %s", image_path)
        return

    detections = predictor.predict(frame)
    log.info("Detections on %s:", image_path.name)
    for det in detections:
        log.info("  %-25s  conf=%.2f  box=(%d,%d,%d,%d)",
                 det.label, det.confidence, det.x1, det.y1, det.x2, det.y2)

    annotated = draw_all_detections(frame.copy(), [d.to_dict() for d in detections])
    annotated = draw_category_legend(annotated)

    cv2.imshow(f"Detection — {image_path.name}", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save annotated image
    out_path = image_path.parent / f"{image_path.stem}_detected{image_path.suffix}"
    cv2.imwrite(str(out_path), annotated)
    log.info("Saved annotated image to: %s", out_path)


def detect_on_stream(predictor: ModelPredictor) -> None:
    """
    Run detection on the live ESP32-CAM stream (press Q to quit).

    Args:
        predictor: Loaded ModelPredictor instance.
    """
    camera = ESP32Camera()
    fps_counter = FPSCounter()

    try:
        camera.connect()
        log.info("Streaming — press Q to quit.")

        while True:
            ok, frame = camera.get_frame()
            if not ok or not is_frame_valid(frame):
                continue

            fps_counter.tick()
            detections = predictor.predict(frame)
            annotated = draw_all_detections(frame.copy(), [d.to_dict() for d in detections])
            annotated = draw_fps_overlay(annotated, fps_counter.fps)
            annotated = draw_category_legend(annotated)

            cv2.imshow("Detection Stream", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.disconnect()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Biomedical Waste YOLO Detection Test Script"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Image path, directory of images, or 'stream' for live camera.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=str(config.MODEL_PATH),
        help="Path to YOLO .pt weights file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    predictor = ModelPredictor(model_path=Path(args.model))
    predictor.load_model()

    if args.source.lower() == "stream":
        detect_on_stream(predictor)
    else:
        source_path = Path(args.source)
        if source_path.is_dir():
            for img_file in sorted(source_path.glob("*.[jp][pn]g")):
                detect_on_image(img_file, predictor)
        elif source_path.is_file():
            detect_on_image(source_path, predictor)
        else:
            print(f"Source not found: {args.source}")
            sys.exit(1)
