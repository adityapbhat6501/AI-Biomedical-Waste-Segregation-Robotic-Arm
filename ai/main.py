"""
main.py — AI Biomedical Waste Segregation Application Entry Point.

Orchestrates all modules to run the live detection and control loop:
    1. Load YOLO model
    2. Connect to ESP32-CAM stream
    3. Connect to ESP32 serial controller
    4. Run inference loop per frame
    5. Display annotated detections
    6. Send robot commands on stable detections
    7. Gracefully shut down on exit

Exit: Press Q in the display window, or Ctrl+C in the terminal.

Author: [Author Placeholder]
Version: 1.0.0
"""

import signal
import sys
import time

import cv2

import config
from camera.esp32cam import ESP32Camera
from camera.camera_utils import is_frame_valid
from communication.serial_comm import SerialCommunicator
from communication.protocol import RobotCommand
from inference.predictor import ModelPredictor
from inference.postprocess import DetectionPostProcessor
from utils.drawing import (
    draw_all_detections,
    draw_fps_overlay,
    draw_status_overlay,
    draw_command_overlay,
    draw_no_detection_overlay,
    draw_category_legend,
)
from utils.helpers import FPSCounter, get_timestamp_str
from utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Application Class
# ---------------------------------------------------------------------------

class WasteSegregationApp:
    """
    Main application controller for the biomedical waste segregation system.

    Coordinates the camera, AI model, post-processor, and serial communicator
    into a single run loop.

    Usage:
        app = WasteSegregationApp()
        app.run()
    """

    def __init__(self) -> None:
        """Initialise all sub-systems (connections not opened yet)."""
        self._camera = ESP32Camera()
        self._predictor = ModelPredictor()
        self._post_processor = DetectionPostProcessor()
        self._serial = SerialCommunicator()
        self._fps_counter = FPSCounter(window_size=30)

        self._running = False
        self._last_command: str | None = None
        self._serial_available = True

        # Register clean shutdown on SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT,  self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    # ------------------------------------------------------------------
    # Public Run Interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Initialise all modules and enter the main detection loop.

        This method blocks until the user presses Q or signals exit.
        """
        log.info("=" * 60)
        log.info("  Biomedical Waste Segregation AI — Starting")
        log.info("  %s", get_timestamp_str())
        log.info("=" * 60)

        try:
            self._initialise()
            self._running = True
            self._main_loop()
        except KeyboardInterrupt:
            log.info("Keyboard interrupt received.")
        except Exception as exc:
            log.exception("Fatal error in main loop: %s", exc)
        finally:
            self._shutdown()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _initialise(self) -> None:
        """
        Load model, open camera and serial connections in order.
        """
        # Step 1: Load AI model
        log.info("Loading AI model...")
        self._predictor.load_model()
        log.info("Model loaded. Classes: %s", list(self._predictor.class_names.values()))

        # Step 2: Connect to ESP32-CAM
        log.info("Connecting to ESP32-CAM stream at: %s", config.CAMERA_URL)
        self._camera.connect()

        # Step 3: Connect to ESP32 serial controller
        if not config.DEBUG_MODE:
            log.info("Connecting to ESP32 controller on: %s", config.SERIAL_PORT)
            try:
                self._serial.connect()
                # Send HOME command at startup to ensure arm is in safe position
                self._serial.send_command(RobotCommand.HOME)
                log.info("ESP32 controller connected and homed.")
            except RuntimeError as exc:
                log.warning("Serial connection failed: %s", exc)
                log.warning("Continuing without serial — arm commands will be skipped.")
                self._serial_available = False
        else:
            log.info("[DEBUG] Serial communication disabled (DEBUG_MODE=True).")
            self._serial_available = False

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------

    def _main_loop(self) -> None:
        """
        Primary inference and display loop. Runs until self._running is False.
        """
        log.info("Entering main detection loop. Press Q to quit.")

        while self._running:
            # ── Capture Frame ──────────────────────────────────────────
            ok, frame = self._camera.get_frame()
            if not ok or not is_frame_valid(frame):
                self._handle_camera_failure()
                continue

            self._fps_counter.tick()

            # ── Run YOLO Inference ─────────────────────────────────────
            try:
                detections = self._predictor.predict(frame)
            except Exception as exc:
                log.error("Inference error: %s", exc)
                continue

            # ── Post-Process → Command ─────────────────────────────────
            command = self._post_processor.process(detections)
            if command is not None:
                self._send_command(command)

            # ── Render Overlay ─────────────────────────────────────────
            annotated = self._render_frame(frame, detections)

            # ── Display ────────────────────────────────────────────────
            if config.DISPLAY_SHOW_WINDOW:
                cv2.imshow(config.DISPLAY_WINDOW_TITLE, annotated)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # Q or Escape
                    log.info("User requested exit.")
                    self._running = False

            # Tiny yield to prevent 100% CPU on fast machines
            time.sleep(0.001)

    # ------------------------------------------------------------------
    # Frame Rendering
    # ------------------------------------------------------------------

    def _render_frame(self, frame, detections) -> "cv2.Mat":
        """
        Compose the annotated display frame with all overlays.

        Args:
            frame:      Raw BGR camera frame.
            detections: List of Detection objects from the predictor.

        Returns:
            Annotated BGR frame ready for display.
        """
        annotated = frame.copy()

        # Bounding boxes
        if detections:
            annotated = draw_all_detections(
                annotated, [d.to_dict() for d in detections]
            )
        else:
            annotated = draw_no_detection_overlay(annotated)

        # FPS
        if config.DISPLAY_SHOW_FPS:
            annotated = draw_fps_overlay(annotated, self._fps_counter.fps)

        # Last command
        annotated = draw_command_overlay(annotated, self._last_command)

        # Category legend
        annotated = draw_category_legend(annotated)

        # Serial status
        serial_status = "Serial: CONNECTED" if self._serial_available else "Serial: OFFLINE"
        annotated = draw_status_overlay(
            annotated, serial_status, is_error=not self._serial_available
        )

        return annotated

    # ------------------------------------------------------------------
    # Command Dispatch
    # ------------------------------------------------------------------

    def _send_command(self, command: RobotCommand) -> None:
        """
        Send a robot command over serial and update the last-command tracker.

        Args:
            command: RobotCommand to transmit.
        """
        self._last_command = command.value

        if self._serial_available:
            success = self._serial.send_command(command)
            if not success:
                log.warning("Failed to send command: %s", command.value)
        else:
            log.info("[DEBUG/OFFLINE] Command (not sent): %s", command.value)

    # ------------------------------------------------------------------
    # Error Recovery
    # ------------------------------------------------------------------

    def _handle_camera_failure(self) -> None:
        """Handle consecutive camera frame failures with a short back-off."""
        log.warning("Camera frame unavailable — waiting %.1fs...", config.CAMERA_RECONNECT_DELAY_S)
        time.sleep(config.CAMERA_RECONNECT_DELAY_S)

    def _signal_handler(self, signum, frame) -> None:
        """Handle OS signals for clean shutdown."""
        log.info("Received signal %d — shutting down.", signum)
        self._running = False

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def _shutdown(self) -> None:
        """
        Release all resources gracefully.
        """
        log.info("Shutting down...")

        # Send STOP to arm if connected
        if self._serial_available and self._serial.is_connected:
            try:
                self._serial.send_command(RobotCommand.STOP)
            except Exception:
                pass
            self._serial.close()

        self._camera.disconnect()
        cv2.destroyAllWindows()

        log.info("Shutdown complete. Goodbye.")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = WasteSegregationApp()
    app.run()
