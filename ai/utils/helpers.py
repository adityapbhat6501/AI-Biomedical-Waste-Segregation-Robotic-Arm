"""
helpers.py — General-Purpose Utility Functions.

Provides cross-cutting helpers used by multiple modules:
    - FPS computation
    - Timestamp generation
    - Directory creation
    - Value clamping
    - Confidence formatting

Author: [Author Placeholder]
Version: 1.0.0
"""

import time
from collections import deque
from pathlib import Path
from typing import Deque


# ---------------------------------------------------------------------------
# FPS Counter
# ---------------------------------------------------------------------------

class FPSCounter:
    """
    Rolling-average FPS counter based on a sliding window of frame timestamps.

    Usage:
        fps_counter = FPSCounter(window_size=30)
        while True:
            fps_counter.tick()
            print(fps_counter.fps)
    """

    def __init__(self, window_size: int = 30) -> None:
        """
        Initialise the FPS counter.

        Args:
            window_size: Number of recent frame timestamps to average over.
        """
        self._timestamps: Deque[float] = deque(maxlen=window_size)

    def tick(self) -> None:
        """Record a new frame timestamp (call once per processed frame)."""
        self._timestamps.append(time.monotonic())

    @property
    def fps(self) -> float:
        """
        Compute the current rolling-average frames per second.

        Returns:
            FPS as a float, or 0.0 if fewer than 2 frames have been recorded.
        """
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0.0:
            return 0.0
        return (len(self._timestamps) - 1) / elapsed

    def reset(self) -> None:
        """Clear all recorded timestamps."""
        self._timestamps.clear()


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

def get_timestamp_str() -> str:
    """
    Return the current local time as a human-readable string.

    Returns:
        Timestamp string in ``YYYY-MM-DD HH:MM:SS`` format.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def elapsed_since(start_time: float) -> float:
    """
    Compute seconds elapsed since a reference monotonic time.

    Args:
        start_time: Reference time from :func:`time.monotonic`.

    Returns:
        Elapsed seconds as a float.
    """
    return time.monotonic() - start_time


# ---------------------------------------------------------------------------
# Value Helpers
# ---------------------------------------------------------------------------

def clamp(value: float, lo: float, hi: float) -> float:
    """
    Clamp a numeric value between a lower and upper bound.

    Args:
        value: Input value.
        lo:    Lower bound (inclusive).
        hi:    Upper bound (inclusive).

    Returns:
        Value constrained to [lo, hi].
    """
    return max(lo, min(hi, value))


def format_confidence(confidence: float) -> str:
    """
    Format a confidence score as a percentage string.

    Args:
        confidence: Float in [0.0, 1.0].

    Returns:
        String like ``"87.4%"``.
    """
    return f"{confidence * 100:.1f}%"


# ---------------------------------------------------------------------------
# File System Helpers
# ---------------------------------------------------------------------------

def ensure_directory(path: Path) -> None:
    """
    Create a directory (and all parents) if it does not already exist.

    Args:
        path: Directory path to create.
    """
    path.mkdir(parents=True, exist_ok=True)


def file_exists_and_nonempty(path: Path) -> bool:
    """
    Check whether a file exists and has non-zero size.

    Args:
        path: File path to check.

    Returns:
        True if the file exists and has size > 0, otherwise False.
    """
    return path.is_file() and path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Stability / Debounce Counter
# ---------------------------------------------------------------------------

class StabilityCounter:
    """
    Counts consecutive occurrences of the same value.

    Used to debounce YOLO detections before sending UART commands —
    a class must appear for ``required_count`` consecutive frames
    before it is considered stable enough to act on.

    Usage:
        counter = StabilityCounter(required_count=3)
        for label in stream_of_labels:
            if counter.update(label):
                send_command(label)
    """

    def __init__(self, required_count: int = 3) -> None:
        """
        Initialise the stability counter.

        Args:
            required_count: Consecutive detections required to confirm stability.
        """
        self._required_count: int = required_count
        self._current_value: str = ""
        self._count: int = 0

    def update(self, value: str) -> bool:
        """
        Update the counter with a new observation.

        Args:
            value: The latest detected class label.

        Returns:
            True if the value has been stable for ``required_count`` frames.
        """
        if value == self._current_value:
            self._count += 1
        else:
            self._current_value = value
            self._count = 1

        return self._count >= self._required_count

    def reset(self) -> None:
        """Reset the counter state."""
        self._current_value = ""
        self._count = 0

    @property
    def current_value(self) -> str:
        """The most recently observed value."""
        return self._current_value

    @property
    def count(self) -> int:
        """Number of consecutive occurrences of the current value."""
        return self._count
