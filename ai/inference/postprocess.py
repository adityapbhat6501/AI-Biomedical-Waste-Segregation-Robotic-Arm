"""
postprocess.py — Detection Post-Processing and Command Generation.

Transforms raw YOLO Detection objects into actionable robot commands:
    1. Filter detections below the command confidence threshold.
    2. Select the single highest-confidence detection.
    3. Map the detected label to a waste category.
    4. Apply a stability filter (N consecutive frames).
    5. Apply a cooldown to prevent command flooding.
    6. Return the appropriate RobotCommand.

Author: [Author Placeholder]
Version: 1.0.0
"""

import time
from typing import Optional

import config
from inference.predictor import Detection
from inference.classes import get_command_for_label, get_category_name_for_label
from communication.protocol import RobotCommand, get_command_for_drop
from utils.helpers import StabilityCounter, elapsed_since
from utils.logger import get_logger

log = get_logger(__name__)


class DetectionPostProcessor:
    """
    Converts a stream of Detection lists into discrete RobotCommands.

    Applies three layers of filtering to prevent spurious commands:
        1. **Confidence gate**: Drops detections below COMMAND_CONFIDENCE_THRESHOLD.
        2. **Stability filter**: Requires the same class for N consecutive frames.
        3. **Cooldown**: Suppresses repeated commands within COMMAND_COOLDOWN_S seconds.

    Usage:
        processor = DetectionPostProcessor()
        while True:
            detections = predictor.predict(frame)
            command = processor.process(detections)
            if command is not None:
                serial.send_command(command)
    """

    def __init__(
        self,
        confidence_threshold: float = config.COMMAND_CONFIDENCE_THRESHOLD,
        stability_frames: int = config.COMMAND_STABILITY_FRAMES,
        cooldown_s: float = config.COMMAND_COOLDOWN_S,
    ) -> None:
        """
        Initialise the post-processor.

        Args:
            confidence_threshold: Minimum confidence to consider a detection.
            stability_frames:     Consecutive frames required to confirm a class.
            cooldown_s:           Minimum seconds between successive commands.
        """
        self._confidence_threshold = confidence_threshold
        self._stability_counter = StabilityCounter(required_count=stability_frames)
        self._cooldown_s = cooldown_s
        self._last_command_time: float = 0.0
        self._last_command: Optional[RobotCommand] = None

    # ------------------------------------------------------------------
    # Primary Processing API
    # ------------------------------------------------------------------

    def process(
        self, detections: list[Detection]
    ) -> Optional[RobotCommand]:
        """
        Process a list of detections and return a command if appropriate.

        Args:
            detections: Raw Detection list from ModelPredictor.predict().

        Returns:
            A :class:`RobotCommand` if a stable, confident, non-cooldown
            detection was found, otherwise ``None``.
        """
        # Step 1: Select best candidate above confidence threshold
        best = self._select_best_detection(detections)

        if best is None:
            self._stability_counter.reset()
            log.debug("No detection above confidence threshold.")
            return None

        # Step 2: Apply stability filter
        if not self._stability_counter.update(best.label):
            log.debug(
                "Stability: %d/%d for '%s'",
                self._stability_counter.count,
                config.COMMAND_STABILITY_FRAMES,
                best.label,
            )
            return None

        # Step 3: Map label → RobotCommand
        command = self._label_to_command(best.label)
        if command is None:
            log.warning("No command mapping found for label: '%s'", best.label)
            return None

        # Step 4: Apply cooldown
        if self._is_in_cooldown(command):
            return None

        # Step 5: Emit command
        self._last_command = command
        self._last_command_time = time.monotonic()

        log.info(
            "Commanding: %s | Label: '%s' | Category: '%s' | Confidence: %.2f",
            command.value,
            best.label,
            get_category_name_for_label(best.label),
            best.confidence,
        )
        return command

    def reset(self) -> None:
        """
        Reset all internal state (stability counter and cooldown timer).
        """
        self._stability_counter.reset()
        self._last_command_time = 0.0
        self._last_command = None

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def last_command(self) -> Optional[RobotCommand]:
        """The most recently emitted RobotCommand, or None."""
        return self._last_command

    @property
    def cooldown_remaining(self) -> float:
        """
        Seconds remaining in the current cooldown period.

        Returns:
            Remaining cooldown seconds, or 0.0 if not in cooldown.
        """
        elapsed = elapsed_since(self._last_command_time)
        remaining = self._cooldown_s - elapsed
        return max(0.0, remaining)

    # ------------------------------------------------------------------
    # Static / Frame Analysis Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_primary_detection(
        detections: list[Detection],
    ) -> Optional[Detection]:
        """
        Return the single highest-confidence detection from a list.

        Args:
            detections: List of Detection objects.

        Returns:
            Detection with the highest confidence, or None if the list is empty.
        """
        if not detections:
            return None
        return max(detections, key=lambda d: d.confidence)

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _select_best_detection(
        self, detections: list[Detection]
    ) -> Optional[Detection]:
        """
        Filter detections by confidence threshold and return the best.

        Args:
            detections: Raw detection list.

        Returns:
            Best Detection above threshold, or None.
        """
        candidates = [
            d for d in detections
            if d.confidence >= self._confidence_threshold
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda d: d.confidence)

    def _label_to_command(self, label: str) -> Optional[RobotCommand]:
        """
        Map a YOLO label to a RobotCommand via the waste class registry.

        Args:
            label: YOLO class label string.

        Returns:
            Matching RobotCommand, or None if not mapped.
        """
        category_command = get_command_for_label(label)
        if category_command is None:
            return None
        return get_command_for_drop(category_command)

    def _is_in_cooldown(self, command: RobotCommand) -> bool:
        """
        Check whether the cooldown period has elapsed since the last command.

        Returns:
            True if still in cooldown (command should NOT be sent).
        """
        if self._last_command is None:
            return False
        elapsed = elapsed_since(self._last_command_time)
        if elapsed < self._cooldown_s:
            log.debug(
                "Cooldown active: %.1fs remaining for %s.",
                self._cooldown_s - elapsed,
                command.value,
            )
            return True
        return False
