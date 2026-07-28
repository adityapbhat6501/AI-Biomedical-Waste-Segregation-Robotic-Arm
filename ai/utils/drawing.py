"""
drawing.py — OpenCV Bounding Box and Overlay Rendering.

Provides functions for drawing detection results on frames:
    - Labelled bounding boxes with category colours
    - FPS and status overlays
    - Waste category legend panel

All drawing functions accept and return OpenCV BGR frames (numpy arrays).

Author: [Author Placeholder]
Version: 1.0.0
"""

import cv2
import numpy as np
from typing import Optional

import config
from inference.classes import get_color_for_label, get_category_name_for_label, get_all_categories
from utils.helpers import format_confidence


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_FONT_SCALE_LABEL = 0.55
_FONT_SCALE_OVERLAY = 0.65
_FONT_SCALE_LEGEND = 0.5
_THICKNESS_BOX = 2
_THICKNESS_TEXT = 1
_PADDING = 6          # pixels of padding around text backgrounds
_LEGEND_MARGIN = 10   # pixels from window edge for legend panel


# ---------------------------------------------------------------------------
# Bounding Box Drawing
# ---------------------------------------------------------------------------

def draw_detection(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    label: str,
    confidence: float,
    show_confidence: bool = True,
) -> np.ndarray:
    """
    Draw a single detection bounding box with a labelled header on a frame.

    Args:
        frame:           BGR image array to draw on (modified in place).
        x1, y1:         Top-left corner of the bounding box.
        x2, y2:         Bottom-right corner of the bounding box.
        label:           Detected class label string.
        confidence:      Detection confidence in [0.0, 1.0].
        show_confidence: If True, append confidence percentage to the label.

    Returns:
        The frame with the detection drawn on it.
    """
    colour = get_color_for_label(label)
    category_name = get_category_name_for_label(label)

    # Build display text
    if show_confidence:
        display_text = f"{label} ({format_confidence(confidence)}) — {category_name}"
    else:
        display_text = f"{label} — {category_name}"

    # Draw bounding box rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, _THICKNESS_BOX)

    # Compute label background dimensions
    (text_w, text_h), baseline = cv2.getTextSize(
        display_text, _FONT, _FONT_SCALE_LABEL, _THICKNESS_TEXT
    )
    label_bg_y1 = max(y1 - text_h - 2 * _PADDING, 0)
    label_bg_y2 = y1

    # Draw filled label background
    cv2.rectangle(
        frame,
        (x1, label_bg_y1),
        (x1 + text_w + 2 * _PADDING, label_bg_y2),
        colour,
        cv2.FILLED,
    )

    # Draw label text (white for contrast)
    cv2.putText(
        frame,
        display_text,
        (x1 + _PADDING, label_bg_y2 - _PADDING // 2),
        _FONT,
        _FONT_SCALE_LABEL,
        (255, 255, 255),
        _THICKNESS_TEXT,
        cv2.LINE_AA,
    )

    return frame


def draw_all_detections(
    frame: np.ndarray,
    detections: list[dict],
) -> np.ndarray:
    """
    Draw all detections on a frame.

    Args:
        frame:      BGR image array.
        detections: List of detection dicts with keys:
                    ``label``, ``confidence``, ``x1``, ``y1``, ``x2``, ``y2``.

    Returns:
        Annotated frame.
    """
    for det in detections:
        frame = draw_detection(
            frame=frame,
            x1=det["x1"],
            y1=det["y1"],
            x2=det["x2"],
            y2=det["y2"],
            label=det["label"],
            confidence=det["confidence"],
            show_confidence=config.DISPLAY_SHOW_CONFIDENCE,
        )
    return frame


# ---------------------------------------------------------------------------
# Overlay Panels
# ---------------------------------------------------------------------------

def draw_fps_overlay(frame: np.ndarray, fps: float) -> np.ndarray:
    """
    Draw an FPS counter in the top-left corner of the frame.

    Args:
        frame: BGR image array.
        fps:   Current frames-per-second value.

    Returns:
        Frame with FPS text drawn.
    """
    fps_text = f"FPS: {fps:.1f}"
    _draw_text_with_background(
        frame=frame,
        text=fps_text,
        origin=(10, 30),
        font_scale=_FONT_SCALE_OVERLAY,
        text_colour=(0, 255, 0),
        bg_colour=(0, 0, 0),
        alpha=0.5,
    )
    return frame


def draw_status_overlay(
    frame: np.ndarray,
    status_text: str,
    is_error: bool = False,
) -> np.ndarray:
    """
    Draw a status message in the bottom-left corner of the frame.

    Args:
        frame:       BGR image array.
        status_text: Status string to display.
        is_error:    If True, render text in red; otherwise green.

    Returns:
        Frame with status text drawn.
    """
    height = frame.shape[0]
    text_colour = (0, 0, 220) if is_error else (0, 220, 0)
    _draw_text_with_background(
        frame=frame,
        text=status_text,
        origin=(10, height - 15),
        font_scale=_FONT_SCALE_OVERLAY,
        text_colour=text_colour,
        bg_colour=(0, 0, 0),
        alpha=0.5,
    )
    return frame


def draw_command_overlay(frame: np.ndarray, command: Optional[str]) -> np.ndarray:
    """
    Draw the last sent UART command in the top-right corner of the frame.

    Args:
        frame:   BGR image array.
        command: Last command string, or None if no command has been sent.

    Returns:
        Frame with command text drawn.
    """
    if command is None:
        return frame

    text = f"CMD: {command}"
    (text_w, _), _ = cv2.getTextSize(text, _FONT, _FONT_SCALE_OVERLAY, _THICKNESS_TEXT)
    width = frame.shape[1]
    _draw_text_with_background(
        frame=frame,
        text=text,
        origin=(width - text_w - 15, 30),
        font_scale=_FONT_SCALE_OVERLAY,
        text_colour=(255, 200, 0),
        bg_colour=(0, 0, 0),
        alpha=0.5,
    )
    return frame


def draw_no_detection_overlay(frame: np.ndarray) -> np.ndarray:
    """
    Draw a "No detection" message when the frame has no detections.

    Args:
        frame: BGR image array.

    Returns:
        Frame with no-detection text.
    """
    return draw_status_overlay(frame, "No waste detected", is_error=False)


def draw_category_legend(frame: np.ndarray) -> np.ndarray:
    """
    Draw a colour-coded waste category legend panel in the bottom-right corner.

    Args:
        frame: BGR image array.

    Returns:
        Frame with legend drawn.
    """
    categories = get_all_categories()
    height, width = frame.shape[:2]

    line_height = 22
    legend_h = len(categories) * line_height + 2 * _LEGEND_MARGIN
    legend_w = 220

    x_start = width - legend_w - _LEGEND_MARGIN
    y_start = height - legend_h - _LEGEND_MARGIN

    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x_start, y_start),
        (width - _LEGEND_MARGIN, height - _LEGEND_MARGIN),
        (20, 20, 20),
        cv2.FILLED,
    )
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    for i, cat in enumerate(categories):
        y = y_start + _LEGEND_MARGIN + i * line_height + line_height // 2
        # Colour swatch
        cv2.rectangle(
            frame,
            (x_start + 8, y - 7),
            (x_start + 22, y + 7),
            cat.color_bgr,
            cv2.FILLED,
        )
        # Category name
        cv2.putText(
            frame,
            cat.name,
            (x_start + 30, y + 4),
            _FONT,
            _FONT_SCALE_LEGEND,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

    return frame


# ---------------------------------------------------------------------------
# Private Helpers
# ---------------------------------------------------------------------------

def _draw_text_with_background(
    frame: np.ndarray,
    text: str,
    origin: tuple[int, int],
    font_scale: float,
    text_colour: tuple[int, int, int],
    bg_colour: tuple[int, int, int],
    alpha: float = 0.5,
) -> None:
    """
    Draw text with a semi-transparent rectangular background.

    Args:
        frame:        BGR image array (modified in place).
        text:         String to render.
        origin:       Bottom-left corner (x, y) of the text.
        font_scale:   OpenCV font scale factor.
        text_colour:  BGR text colour.
        bg_colour:    BGR background rectangle colour.
        alpha:        Opacity of the background (0 = transparent, 1 = opaque).
    """
    (text_w, text_h), _ = cv2.getTextSize(text, _FONT, font_scale, _THICKNESS_TEXT)
    x, y = origin
    bg_x1 = x - _PADDING
    bg_y1 = y - text_h - _PADDING
    bg_x2 = x + text_w + _PADDING
    bg_y2 = y + _PADDING

    # Clip to frame bounds
    h, w = frame.shape[:2]
    bg_x1 = max(bg_x1, 0)
    bg_y1 = max(bg_y1, 0)
    bg_x2 = min(bg_x2, w - 1)
    bg_y2 = min(bg_y2, h - 1)

    overlay = frame.copy()
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_colour, cv2.FILLED)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    cv2.putText(
        frame, text, (x, y), _FONT, font_scale, text_colour, _THICKNESS_TEXT, cv2.LINE_AA
    )
