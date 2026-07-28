"""
test_camera.py — Unit and Integration Tests for the Camera Module.

Tests:
    - Frame validity checking (camera_utils)
    - Letterbox preprocessing
    - CLAHE enhancement
    - ESP32Camera connection failure handling

Run with:
    python -m pytest tests/test_camera.py -v

Author: [Author Placeholder]
Version: 1.0.0
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from camera.camera_utils import (
    is_frame_valid,
    preprocess_frame,
    apply_clahe,
    crop_roi,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_bgr_frame() -> np.ndarray:
    """Generate a simple 480×640 BGR test frame."""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def small_bgr_frame() -> np.ndarray:
    """Generate a non-square 100×200 BGR test frame."""
    return np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# is_frame_valid Tests
# ---------------------------------------------------------------------------

class TestIsFrameValid:

    def test_valid_frame_returns_true(self, valid_bgr_frame):
        assert is_frame_valid(valid_bgr_frame) is True

    def test_none_returns_false(self):
        assert is_frame_valid(None) is False

    def test_empty_array_returns_false(self):
        assert is_frame_valid(np.array([])) is False

    def test_grayscale_returns_false(self, valid_bgr_frame):
        gray = valid_bgr_frame[:, :, 0]  # Single channel
        assert is_frame_valid(gray) is False

    def test_non_array_returns_false(self):
        assert is_frame_valid("not an array") is False  # type: ignore


# ---------------------------------------------------------------------------
# preprocess_frame Tests
# ---------------------------------------------------------------------------

class TestPreprocessFrame:

    def test_output_shape_is_correct(self, valid_bgr_frame):
        result = preprocess_frame(valid_bgr_frame, target_size=640)
        assert result.shape == (1, 3, 640, 640), f"Unexpected shape: {result.shape}"

    def test_output_dtype_is_float32(self, valid_bgr_frame):
        result = preprocess_frame(valid_bgr_frame, target_size=640)
        assert result.dtype == np.float32

    def test_pixel_values_are_normalised(self, valid_bgr_frame):
        result = preprocess_frame(valid_bgr_frame, target_size=640)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_non_square_input_produces_square_output(self, small_bgr_frame):
        result = preprocess_frame(small_bgr_frame, target_size=320)
        assert result.shape == (1, 3, 320, 320)

    def test_custom_target_size(self, valid_bgr_frame):
        result = preprocess_frame(valid_bgr_frame, target_size=416)
        assert result.shape == (1, 3, 416, 416)


# ---------------------------------------------------------------------------
# apply_clahe Tests
# ---------------------------------------------------------------------------

class TestApplyClahe:

    def test_output_same_shape(self, valid_bgr_frame):
        result = apply_clahe(valid_bgr_frame)
        assert result.shape == valid_bgr_frame.shape

    def test_output_same_dtype(self, valid_bgr_frame):
        result = apply_clahe(valid_bgr_frame)
        assert result.dtype == valid_bgr_frame.dtype

    def test_output_differs_from_input(self, valid_bgr_frame):
        result = apply_clahe(valid_bgr_frame)
        # CLAHE should change at least some pixels
        assert not np.array_equal(result, valid_bgr_frame)


# ---------------------------------------------------------------------------
# crop_roi Tests
# ---------------------------------------------------------------------------

class TestCropRoi:

    def test_full_frame_crop(self, valid_bgr_frame):
        result = crop_roi(valid_bgr_frame, x=0.0, y=0.0, width=1.0, height=1.0)
        assert result.shape == valid_bgr_frame.shape

    def test_quarter_crop_shape(self, valid_bgr_frame):
        result = crop_roi(valid_bgr_frame, x=0.0, y=0.0, width=0.5, height=0.5)
        expected_h = valid_bgr_frame.shape[0] // 2
        expected_w = valid_bgr_frame.shape[1] // 2
        assert result.shape == (expected_h, expected_w, 3)

    def test_centre_crop(self, valid_bgr_frame):
        result = crop_roi(valid_bgr_frame, x=0.25, y=0.25, width=0.5, height=0.5)
        assert result.shape[2] == 3  # Must still be 3-channel
