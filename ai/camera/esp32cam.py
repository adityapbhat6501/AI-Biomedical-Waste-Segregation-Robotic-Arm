"""
esp32cam.py — ESP32-CAM MJPEG Stream Capture.

Connects to the ESP32-CAM's MJPEG stream URL and provides a clean
frame-by-frame API with automatic reconnection on stream loss.

The stream is opened as a standard HTTP MJPEG source via OpenCV's
VideoCapture. Falls back to a local webcam when DEBUG_USE_WEBCAM is True.

Author: [Author Placeholder]
Version: 1.0.0
"""

import time
from typing import Optional, Tuple

import cv2
import numpy as np

import config
from utils.logger import get_logger

log = get_logger(__name__)


class ESP32Camera:
    """
    Manages a connection to the ESP32-CAM MJPEG stream.

    Provides:
        - connect / disconnect lifecycle
        - get_frame() for single frame retrieval
        - Automatic reconnect on stream failure
        - Optional local webcam fallback (debug mode)

    Usage:
        cam = ESP32Camera()
        cam.connect()
        ok, frame = cam.get_frame()
        cam.disconnect()
    """

    def __init__(
        self,
        stream_url: str = config.CAMERA_URL,
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
        reconnect_delay: float = config.CAMERA_RECONNECT_DELAY_S,
        max_reconnect_attempts: int = config.CAMERA_MAX_RECONNECT_ATTEMPTS,
        use_webcam: bool = config.DEBUG_USE_WEBCAM,
        webcam_index: int = config.DEBUG_WEBCAM_INDEX,
    ) -> None:
        """
        Initialise the camera manager (does NOT open the stream yet).

        Args:
            stream_url:             MJPEG stream URL of the ESP32-CAM.
            frame_width:            Target frame width after resize.
            frame_height:           Target frame height after resize.
            reconnect_delay:        Seconds to wait between reconnect attempts.
            max_reconnect_attempts: Max reconnects before raising an error.
            use_webcam:             If True, open a local webcam instead.
            webcam_index:           Local webcam device index.
        """
        self._stream_url = stream_url
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._reconnect_delay = reconnect_delay
        self._max_reconnect_attempts = max_reconnect_attempts
        self._use_webcam = use_webcam
        self._webcam_index = webcam_index

        self._capture: Optional[cv2.VideoCapture] = None
        self._is_connected = False
        self._consecutive_failures = 0

    # ------------------------------------------------------------------
    # Connection Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """
        Open the camera stream (MJPEG URL or local webcam).

        Attempts connection up to ``max_reconnect_attempts`` times before
        raising a RuntimeError.

        Returns:
            True on successful connection.

        Raises:
            RuntimeError: If all connection attempts fail.
        """
        source = self._webcam_index if self._use_webcam else self._stream_url
        source_label = f"webcam:{self._webcam_index}" if self._use_webcam else self._stream_url

        for attempt in range(1, self._max_reconnect_attempts + 1):
            log.info(
                "Connecting to camera [%s] (attempt %d/%d)...",
                source_label, attempt, self._max_reconnect_attempts,
            )
            cap = cv2.VideoCapture(source)

            if cap.isOpened():
                self._capture = cap
                self._is_connected = True
                self._consecutive_failures = 0
                log.info("Camera connected: %s", source_label)
                return True

            cap.release()
            log.warning("Camera connection attempt %d failed.", attempt)
            if attempt < self._max_reconnect_attempts:
                time.sleep(self._reconnect_delay)

        raise RuntimeError(
            f"Failed to connect to camera [{source_label}] after "
            f"{self._max_reconnect_attempts} attempts."
        )

    def disconnect(self) -> None:
        """
        Release the camera stream and free resources.
        """
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._is_connected = False
        log.info("Camera disconnected.")

    @property
    def is_connected(self) -> bool:
        """Return True if the camera stream is currently open."""
        return (
            self._is_connected
            and self._capture is not None
            and self._capture.isOpened()
        )

    # ------------------------------------------------------------------
    # Frame Retrieval
    # ------------------------------------------------------------------

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture and return a single frame from the camera stream.

        If the capture fails, an automatic reconnect is attempted.

        Returns:
            Tuple of (success: bool, frame: np.ndarray or None).
            If ``success`` is False, ``frame`` is None.
        """
        if not self.is_connected:
            log.warning("get_frame() called while camera is not connected.")
            self._reconnect()
            if not self.is_connected:
                return False, None

        ret, raw_frame = self._capture.read()

        if not ret or raw_frame is None:
            self._consecutive_failures += 1
            log.warning(
                "Frame read failed (consecutive failures: %d).",
                self._consecutive_failures,
            )
            if self._consecutive_failures >= 5:
                log.error("Too many consecutive frame failures — reconnecting...")
                self._reconnect()
            return False, None

        self._consecutive_failures = 0
        resized_frame = self._resize_frame(raw_frame)
        return True, resized_frame

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize a frame to the configured target resolution.

        Args:
            frame: Raw BGR frame from VideoCapture.

        Returns:
            Resized BGR frame.
        """
        if frame.shape[1] != self._frame_width or frame.shape[0] != self._frame_height:
            return cv2.resize(
                frame,
                (self._frame_width, self._frame_height),
                interpolation=cv2.INTER_LINEAR,
            )
        return frame

    def _reconnect(self) -> None:
        """
        Silently attempt to reconnect to the camera after a failure.
        """
        log.warning("Attempting camera reconnect...")
        self.disconnect()
        time.sleep(self._reconnect_delay)
        try:
            self.connect()
        except RuntimeError as exc:
            log.error("Camera reconnect failed: %s", exc)
