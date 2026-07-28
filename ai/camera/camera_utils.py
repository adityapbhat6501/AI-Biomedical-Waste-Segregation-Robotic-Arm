"""
camera_utils.py — Frame Preprocessing Utilities for YOLO Inference.

Provides helper functions that transform raw camera frames into a
format suitable for YOLO inference, plus diagnostic utilities.

Author: [Author Placeholder]
Version: 1.0.0
"""

import cv2
import numpy as np


def preprocess_frame(
    frame: np.ndarray,
    target_size: int = 640,
) -> np.ndarray:
    """
    Preprocess a raw BGR camera frame for YOLO inference.

    Operations applied:
        1. Resize to a square ``target_size × target_size`` with letterboxing
           to preserve aspect ratio (remaining area filled with grey).
        2. Convert from BGR to RGB colour space.
        3. Normalise pixel values to [0.0, 1.0].
        4. Add a batch dimension: shape becomes (1, C, H, W).

    Note:
        The Ultralytics YOLO API internally performs its own preprocessing,
        so passing a raw BGR frame directly to ``model.predict()`` is also
        valid. This function is provided for use with custom inference
        pipelines or manual PyTorch calls.

    Args:
        frame:       Raw BGR numpy array from OpenCV VideoCapture.
        target_size: Square input size expected by the model.

    Returns:
        Pre-processed numpy array with shape (1, 3, H, W), float32.
    """
    letterboxed = _letterbox(frame, target_size)
    rgb = cv2.cvtColor(letterboxed, cv2.COLOR_BGR2RGB)
    normalised = rgb.astype(np.float32) / 255.0
    transposed = np.transpose(normalised, (2, 0, 1))  # HWC → CHW
    batched = np.expand_dims(transposed, axis=0)       # CHW → BCHW
    return batched


def apply_clahe(frame: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalisation) to a frame.

    Improves detection quality under uneven or low lighting conditions
    by locally equalising contrast in the LAB colour space.

    Args:
        frame: BGR numpy array.

    Returns:
        Contrast-enhanced BGR numpy array.
    """
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_equalised = clahe.apply(l_channel)

    enhanced_lab = cv2.merge([l_equalised, a_channel, b_channel])
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def is_frame_valid(frame: np.ndarray | None) -> bool:
    """
    Check whether a frame is a valid, non-empty BGR image.

    Args:
        frame: Frame to validate.

    Returns:
        True if the frame is a non-None, non-empty numpy array with 3 channels.
    """
    if frame is None:
        return False
    if not isinstance(frame, np.ndarray):
        return False
    if frame.ndim != 3 or frame.shape[2] != 3:
        return False
    if frame.size == 0:
        return False
    return True


def crop_roi(
    frame: np.ndarray,
    x: float,
    y: float,
    width: float,
    height: float,
) -> np.ndarray:
    """
    Crop a region of interest from a frame using normalised coordinates.

    Args:
        frame:  BGR numpy array.
        x:      Normalised x position of top-left corner [0.0, 1.0].
        y:      Normalised y position of top-left corner [0.0, 1.0].
        width:  Normalised width of the ROI [0.0, 1.0].
        height: Normalised height of the ROI [0.0, 1.0].

    Returns:
        Cropped BGR numpy array.
    """
    h, w = frame.shape[:2]
    x1 = int(x * w)
    y1 = int(y * h)
    x2 = int((x + width) * w)
    y2 = int((y + height) * h)
    return frame[y1:y2, x1:x2]


# ---------------------------------------------------------------------------
# Private Helpers
# ---------------------------------------------------------------------------

def _letterbox(
    frame: np.ndarray,
    target_size: int,
    pad_colour: tuple[int, int, int] = (114, 114, 114),
) -> np.ndarray:
    """
    Resize a frame to a square with letterbox padding.

    Preserves the original aspect ratio by padding the shorter dimension
    with grey bars rather than distorting the image.

    Args:
        frame:       Input BGR frame.
        target_size: Target square dimension (pixels).
        pad_colour:  BGR colour used for padding bars.

    Returns:
        Letterboxed frame of shape (target_size, target_size, 3).
    """
    h, w = frame.shape[:2]
    scale = target_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((target_size, target_size, 3), pad_colour, dtype=np.uint8)
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    return canvas
