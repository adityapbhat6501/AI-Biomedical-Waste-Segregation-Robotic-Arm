"""
export.py — YOLO Model Export Script.

Exports a trained best.pt model to deployment-optimised formats:
    - ONNX  (cross-platform, works on CPU/GPU)
    - TensorRT (NVIDIA GPU — maximum inference speed)
    - OpenVINO (Intel CPU/integrated GPU)
    - TFLite (edge devices, Raspberry Pi)

Usage:
    # Export to ONNX (recommended default)
    python model/export.py --format onnx

    # Export to TensorRT (requires NVIDIA GPU + TensorRT SDK)
    python model/export.py --format engine

    # Export with specific input size
    python model/export.py --format onnx --imgsz 320

Author: [Author Placeholder]
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO
import config
from utils.logger import get_logger

log = get_logger(__name__)

SUPPORTED_FORMATS = ("onnx", "engine", "openvino", "tflite", "coreml")


def export_model(
    model_path: Path,
    export_format: str,
    imgsz: int,
) -> Path:
    """
    Export a trained YOLO model to a specified deployment format.

    Args:
        model_path:    Path to the source .pt weights file.
        export_format: Target format string (e.g. "onnx", "engine").
        imgsz:         Square input image size for the exported model.

    Returns:
        Path to the exported model file.

    Raises:
        FileNotFoundError: If model_path does not exist.
        ValueError:        If export_format is not supported.
    """
    if not model_path.is_file():
        raise FileNotFoundError(f"Model weights not found: {model_path}")

    if export_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{export_format}'. "
            f"Choose from: {SUPPORTED_FORMATS}"
        )

    log.info("Exporting model: %s → format: %s", model_path, export_format)
    model = YOLO(str(model_path))

    exported_path = model.export(format=export_format, imgsz=imgsz)
    log.info("Export complete: %s", exported_path)
    return Path(exported_path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Export YOLO model to a deployment format."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=str(config.MODEL_PATH),
        help="Path to the trained .pt weights file.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="onnx",
        choices=SUPPORTED_FORMATS,
        help="Export format.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=config.MODEL_INPUT_SIZE,
        help="Input image size for the exported model.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        result_path = export_model(
            model_path=Path(args.model),
            export_format=args.format,
            imgsz=args.imgsz,
        )
        print(f"\n✓ Model exported to: {result_path}")
    except (FileNotFoundError, ValueError) as exc:
        print(f"\n✗ Error: {exc}")
        sys.exit(1)
