"""
predictor.py — YOLO Model Loading and Inference.

Wraps the Ultralytics YOLO API to provide a simple predict() interface.
This module is the ONLY layer that loads weights and runs inference.
All higher-level modules receive structured Detection objects.

Supports:
    - YOLOv8 (all sizes: n, s, m, l, x)
    - Future model replacement via ModelPredictor subclassing

Author: [Author Placeholder]
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from ultralytics import YOLO

import config
from utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Detection Result Data Class
# ---------------------------------------------------------------------------

@dataclass
class Detection:
    """
    Represents a single detected object from YOLO inference.

    Attributes:
        label:      YOLO class label string (e.g. "syringe").
        confidence: Detection confidence score in [0.0, 1.0].
        x1:         Left pixel coordinate of the bounding box.
        y1:         Top pixel coordinate of the bounding box.
        x2:         Right pixel coordinate of the bounding box.
        y2:         Bottom pixel coordinate of the bounding box.
        class_id:   Integer class index from the YOLO model.
    """
    label: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    class_id: int

    def to_dict(self) -> dict:
        """Serialise the detection to a plain dictionary."""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "class_id": self.class_id,
        }

    @property
    def width(self) -> int:
        """Bounding box width in pixels."""
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        """Bounding box height in pixels."""
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        """Bounding box area in square pixels."""
        return self.width * self.height

    @property
    def centre(self) -> tuple[int, int]:
        """Bounding box centre (x, y) in pixels."""
        return (self.x1 + self.width // 2, self.y1 + self.height // 2)


# ---------------------------------------------------------------------------
# Model Predictor
# ---------------------------------------------------------------------------

class ModelPredictor:
    """
    Loads a YOLO model and provides a predict() API.

    To swap models:
        predictor = ModelPredictor(model_path=Path("model/yolov8s.pt"))

    Future extensions:
        - Subclass ModelPredictor and override predict() to support ONNX,
          TensorRT, or other inference backends.
    """

    def __init__(
        self,
        model_path: Path = config.MODEL_PATH,
        confidence_threshold: float = config.CONFIDENCE_THRESHOLD,
        iou_threshold: float = config.IOU_THRESHOLD,
        input_size: int = config.MODEL_INPUT_SIZE,
        max_detections: int = config.MAX_DETECTIONS,
    ) -> None:
        """
        Initialise the predictor (does NOT load weights yet).

        Args:
            model_path:           Path to YOLO .pt weights file.
            confidence_threshold: Minimum confidence to accept a detection.
            iou_threshold:        IoU threshold for NMS deduplication.
            input_size:           Square inference input size (pixels).
            max_detections:       Maximum detections returned per frame.
        """
        self._model_path = model_path
        self._confidence_threshold = confidence_threshold
        self._iou_threshold = iou_threshold
        self._input_size = input_size
        self._max_detections = max_detections

        self._model: Optional[YOLO] = None

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def load_model(self) -> None:
        """
        Load YOLO model weights from disk.

        Falls back to the pretrained base model if ``model_path`` is not found.

        Raises:
            FileNotFoundError: If neither best.pt nor the fallback model exists.
        """
        if self._model_path.is_file():
            weights_path = self._model_path
        elif config.MODEL_FALLBACK_PATH.is_file():
            log.warning(
                "Trained model not found at %s. Loading fallback: %s",
                self._model_path, config.MODEL_FALLBACK_PATH,
            )
            weights_path = config.MODEL_FALLBACK_PATH
        else:
            raise FileNotFoundError(
                f"No model weights found at '{self._model_path}' or "
                f"'{config.MODEL_FALLBACK_PATH}'. Train a model first or "
                f"place yolov8n.pt in the model/ directory."
            )

        log.info("Loading YOLO model from: %s", weights_path)
        self._model = YOLO(str(weights_path))
        log.info("Model loaded. Classes: %s", self._model.names)

    @property
    def is_loaded(self) -> bool:
        """Return True if the model weights have been loaded."""
        return self._model is not None

    @property
    def class_names(self) -> dict[int, str]:
        """
        Return the model's class name dictionary (id → label).

        Returns:
            Dict mapping class integer index to label string,
            or an empty dict if the model is not loaded.
        """
        if self._model is not None:
            return self._model.names
        return {}

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, frame: np.ndarray) -> list[Detection]:
        """
        Run YOLO inference on a single BGR frame.

        Args:
            frame: BGR numpy array from OpenCV.

        Returns:
            List of :class:`Detection` objects for all accepted detections,
            sorted by confidence descending.

        Raises:
            RuntimeError: If the model has not been loaded via load_model().
        """
        if self._model is None:
            raise RuntimeError(
                "Model not loaded. Call load_model() before predict()."
            )

        results = self._model.predict(
            source=frame,
            conf=self._confidence_threshold,
            iou=self._iou_threshold,
            imgsz=self._input_size,
            max_det=self._max_detections,
            verbose=False,
        )

        detections: list[Detection] = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                label = result.names.get(class_id, f"class_{class_id}")
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                detections.append(Detection(
                    label=label,
                    confidence=confidence,
                    x1=x1, y1=y1,
                    x2=x2, y2=y2,
                    class_id=class_id,
                ))

        # Sort by confidence descending
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections
