"""
test_model.py — Unit Tests for Inference Module.

Tests:
    - WasteClass registry lookup functions
    - Detection dataclass properties
    - DetectionPostProcessor filtering logic
    - StabilityCounter debounce behaviour
    - Confidence formatting helpers

Run with:
    python -m pytest tests/test_model.py -v

Author: [Author Placeholder]
Version: 1.0.0
"""

import sys
import time
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inference.classes import (
    get_waste_class,
    get_command_for_label,
    get_color_for_label,
    get_category_name_for_label,
    get_all_categories,
    CLASS_NAMES,
)
from inference.predictor import Detection
from inference.postprocess import DetectionPostProcessor
from utils.helpers import StabilityCounter, FPSCounter, format_confidence, clamp


# ---------------------------------------------------------------------------
# Waste Class Registry Tests
# ---------------------------------------------------------------------------

class TestWasteClassRegistry:

    def test_syringe_maps_to_blue_category(self):
        wc = get_waste_class("syringe")
        assert wc is not None
        assert wc.category.name == "Blue Waste"

    def test_used_glove_maps_to_red_category(self):
        wc = get_waste_class("used_glove")
        assert wc is not None
        assert wc.category.name == "Red Waste"

    def test_chemical_container_maps_to_yellow_category(self):
        wc = get_waste_class("chemical_container")
        assert wc is not None
        assert wc.category.name == "Yellow Waste"

    def test_unknown_label_returns_none(self):
        assert get_waste_class("unknown_item") is None

    def test_get_command_for_syringe(self):
        cmd = get_command_for_label("syringe")
        assert cmd == "DROP_BLUE"

    def test_get_command_for_glove(self):
        cmd = get_command_for_label("used_glove")
        assert cmd == "DROP_RED"

    def test_get_command_for_unknown_returns_none(self):
        assert get_command_for_label("banana") is None

    def test_color_for_syringe_is_blue_category_color(self):
        from inference.classes import CATEGORY_BLUE
        assert get_color_for_label("syringe") == CATEGORY_BLUE.color_bgr

    def test_color_for_unknown_is_white(self):
        assert get_color_for_label("unknown") == (255, 255, 255)

    def test_category_name_for_syringe(self):
        assert get_category_name_for_label("syringe") == "Blue Waste"

    def test_category_name_for_unknown(self):
        assert get_category_name_for_label("xyz") == "Unknown"

    def test_all_categories_returns_unique_list(self):
        categories = get_all_categories()
        names = [c.name for c in categories]
        assert len(names) == len(set(names))

    def test_class_names_is_non_empty(self):
        assert len(CLASS_NAMES) > 0


# ---------------------------------------------------------------------------
# Detection Dataclass Tests
# ---------------------------------------------------------------------------

class TestDetection:

    def make_detection(self, label="syringe", conf=0.85,
                       x1=10, y1=20, x2=110, y2=120) -> Detection:
        return Detection(
            label=label, confidence=conf,
            x1=x1, y1=y1, x2=x2, y2=y2, class_id=7,
        )

    def test_width_is_correct(self):
        det = self.make_detection(x1=10, x2=110)
        assert det.width == 100

    def test_height_is_correct(self):
        det = self.make_detection(y1=20, y2=120)
        assert det.height == 100

    def test_area_is_correct(self):
        det = self.make_detection(x1=0, y1=0, x2=100, y2=50)
        assert det.area == 5000

    def test_centre_is_correct(self):
        det = self.make_detection(x1=0, y1=0, x2=100, y2=100)
        assert det.centre == (50, 50)

    def test_to_dict_contains_expected_keys(self):
        det = self.make_detection()
        d = det.to_dict()
        for key in ("label", "confidence", "x1", "y1", "x2", "y2", "class_id"):
            assert key in d


# ---------------------------------------------------------------------------
# DetectionPostProcessor Tests
# ---------------------------------------------------------------------------

class TestDetectionPostProcessor:

    def make_detection(self, label: str, conf: float) -> Detection:
        return Detection(
            label=label, confidence=conf,
            x1=10, y1=10, x2=100, y2=100, class_id=0,
        )

    def test_no_detections_returns_none(self):
        proc = DetectionPostProcessor(confidence_threshold=0.5, stability_frames=1, cooldown_s=0)
        assert proc.process([]) is None

    def test_low_confidence_returns_none(self):
        proc = DetectionPostProcessor(confidence_threshold=0.8, stability_frames=1, cooldown_s=0)
        det = self.make_detection("syringe", conf=0.4)
        assert proc.process([det]) is None

    def test_stable_high_confidence_returns_command(self):
        proc = DetectionPostProcessor(confidence_threshold=0.5, stability_frames=3, cooldown_s=0)
        det = self.make_detection("syringe", conf=0.9)
        # First two frames: stability not met
        assert proc.process([det]) is None
        assert proc.process([det]) is None
        # Third frame: stability met
        from communication.protocol import RobotCommand
        result = proc.process([det])
        assert result == RobotCommand.DROP_BLUE

    def test_cooldown_prevents_repeat_command(self):
        proc = DetectionPostProcessor(confidence_threshold=0.5, stability_frames=1, cooldown_s=60)
        det = self.make_detection("syringe", conf=0.9)
        first = proc.process([det])
        assert first is not None
        second = proc.process([det])
        assert second is None

    def test_unknown_label_returns_none(self):
        proc = DetectionPostProcessor(confidence_threshold=0.5, stability_frames=1, cooldown_s=0)
        det = self.make_detection("unknown_item", conf=0.95)
        assert proc.process([det]) is None

    def test_reset_clears_state(self):
        proc = DetectionPostProcessor(confidence_threshold=0.5, stability_frames=1, cooldown_s=60)
        det = self.make_detection("syringe", conf=0.9)
        proc.process([det])  # Sends a command
        proc.reset()
        result = proc.process([det])
        assert result is not None  # Cooldown cleared


# ---------------------------------------------------------------------------
# StabilityCounter Tests
# ---------------------------------------------------------------------------

class TestStabilityCounter:

    def test_resets_on_value_change(self):
        counter = StabilityCounter(required_count=3)
        counter.update("a")
        counter.update("a")
        counter.update("b")  # Resets count
        assert counter.count == 1

    def test_returns_true_at_required_count(self):
        counter = StabilityCounter(required_count=3)
        assert counter.update("x") is False
        assert counter.update("x") is False
        assert counter.update("x") is True

    def test_continues_true_after_threshold(self):
        counter = StabilityCounter(required_count=2)
        counter.update("x")
        assert counter.update("x") is True
        assert counter.update("x") is True  # Still True

    def test_reset_clears_state(self):
        counter = StabilityCounter(required_count=2)
        counter.update("x")
        counter.update("x")
        counter.reset()
        assert counter.count == 0
        assert counter.current_value == ""


# ---------------------------------------------------------------------------
# Helper Function Tests
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_clamp_within_range(self):
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_clamp_below_minimum(self):
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_clamp_above_maximum(self):
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_format_confidence_50_percent(self):
        assert format_confidence(0.5) == "50.0%"

    def test_format_confidence_100_percent(self):
        assert format_confidence(1.0) == "100.0%"

    def test_format_confidence_zero(self):
        assert format_confidence(0.0) == "0.0%"

    def test_fps_counter_initialises_at_zero(self):
        counter = FPSCounter()
        assert counter.fps == 0.0

    def test_fps_counter_non_zero_after_ticks(self):
        counter = FPSCounter(window_size=5)
        for _ in range(5):
            counter.tick()
            time.sleep(0.01)
        assert counter.fps > 0.0
