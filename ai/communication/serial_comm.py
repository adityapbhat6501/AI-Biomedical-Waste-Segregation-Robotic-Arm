"""
serial_comm.py — PySerial-based Serial Communication Manager.

Manages the UART connection to the ESP32 robotic arm controller:
    - Open / close the serial port
    - Send typed RobotCommand instances
    - Read and decode ESP32 status responses
    - Automatic reconnection on connection loss

Usage:
    comm = SerialCommunicator(port="COM3", baud_rate=115200)
    comm.connect()
    comm.send_command(RobotCommand.PICK)
    response = comm.read_response()
    comm.close()

Author: [Author Placeholder]
Version: 1.0.0
"""

import time
import threading
from typing import Optional

import serial
import serial.serialutil

import config
from communication.protocol import RobotCommand, RobotResponse, encode_command, decode_response
from utils.logger import get_logger

log = get_logger(__name__)


class SerialCommunicator:
    """
    Thread-safe serial communicator for the ESP32 robotic arm controller.

    Attributes:
        port:            Serial port name (e.g. "COM3", "/dev/ttyUSB0").
        baud_rate:       UART baud rate (must match ESP32 firmware).
        timeout:         Read timeout in seconds.
        reconnect_delay: Seconds to wait between reconnect attempts.
        max_reconnects:  Maximum number of reconnect attempts before giving up.
    """

    def __init__(
        self,
        port: str = config.SERIAL_PORT,
        baud_rate: int = config.SERIAL_BAUD_RATE,
        timeout: float = config.SERIAL_TIMEOUT_S,
        reconnect_delay: float = config.SERIAL_RECONNECT_DELAY_S,
        max_reconnects: int = config.SERIAL_MAX_RECONNECT_ATTEMPTS,
    ) -> None:
        """
        Initialise the serial communicator (does NOT open the port yet).

        Args:
            port:            Serial port identifier.
            baud_rate:       UART baud rate.
            timeout:         Read timeout in seconds.
            reconnect_delay: Delay between reconnect attempts.
            max_reconnects:  Maximum reconnect attempts.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.max_reconnects = max_reconnects

        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._is_connected = False

    # ------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """
        Open the serial port and establish connection to the ESP32.

        Returns:
            True if the connection was established successfully.

        Raises:
            RuntimeError: If all reconnect attempts fail.
        """
        for attempt in range(1, self.max_reconnects + 1):
            try:
                log.info(
                    "Connecting to ESP32 on %s at %d baud (attempt %d/%d)...",
                    self.port, self.baud_rate, attempt, self.max_reconnects,
                )
                self._serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=self.timeout,
                )
                time.sleep(2.0)  # Allow ESP32 to complete reset after DTR toggle
                self._is_connected = True
                log.info("Serial connection established on %s.", self.port)
                return True

            except serial.SerialException as exc:
                log.warning("Connection attempt %d failed: %s", attempt, exc)
                if attempt < self.max_reconnects:
                    log.info("Retrying in %.1f s...", self.reconnect_delay)
                    time.sleep(self.reconnect_delay)

        raise RuntimeError(
            f"Failed to connect to ESP32 on {self.port} after "
            f"{self.max_reconnects} attempts."
        )

    def close(self) -> None:
        """
        Close the serial port gracefully.
        """
        with self._lock:
            if self._serial and self._serial.is_open:
                try:
                    self._serial.close()
                    log.info("Serial port %s closed.", self.port)
                except serial.SerialException as exc:
                    log.warning("Error closing serial port: %s", exc)
            self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Return True if the serial port is currently open."""
        return self._is_connected and self._serial is not None and self._serial.is_open

    # ------------------------------------------------------------------
    # Command Transmission
    # ------------------------------------------------------------------

    def send_command(self, command: RobotCommand) -> bool:
        """
        Send a RobotCommand to the ESP32 over serial.

        In debug mode (config.DEBUG_MODE), the command is logged but NOT sent.

        Args:
            command: The :class:`RobotCommand` to transmit.

        Returns:
            True if the command was sent successfully, False otherwise.
        """
        if config.DEBUG_MODE:
            log.debug("[DEBUG] Would send command: %s", command.value)
            return True

        if not self.is_connected:
            log.warning("Cannot send command — serial port not connected.")
            self._attempt_reconnect()
            if not self.is_connected:
                return False

        payload = encode_command(command)
        try:
            with self._lock:
                self._serial.write(payload)
                self._serial.flush()
            log.info("Sent command: %s", command.value)
            return True

        except (serial.SerialException, OSError) as exc:
            log.error("Failed to send command '%s': %s", command.value, exc)
            self._is_connected = False
            self._attempt_reconnect()
            return False

    # ------------------------------------------------------------------
    # Response Reading
    # ------------------------------------------------------------------

    def read_response(self) -> Optional[RobotResponse]:
        """
        Read one line from the ESP32 and decode it as a RobotResponse.

        Blocks up to ``self.timeout`` seconds waiting for data.

        Returns:
            Decoded :class:`RobotResponse`, or ``None`` if no valid response
            was received within the timeout.
        """
        if not self.is_connected:
            return None

        try:
            with self._lock:
                raw_bytes = self._serial.readline()

            if not raw_bytes:
                return None

            raw_str = raw_bytes.decode("utf-8", errors="replace").strip()
            log.debug("ESP32 response: %s", raw_str)

            response = decode_response(raw_str)
            if response is None:
                log.debug("Unrecognised response from ESP32: '%s'", raw_str)
            return response

        except (serial.SerialException, OSError) as exc:
            log.error("Error reading from serial: %s", exc)
            self._is_connected = False
            return None

    def flush_input(self) -> None:
        """
        Discard all buffered incoming serial data.

        Useful to clear stale responses before sending a new command.
        """
        if self.is_connected:
            try:
                with self._lock:
                    self._serial.reset_input_buffer()
            except serial.SerialException:
                pass

    # ------------------------------------------------------------------
    # Status Query
    # ------------------------------------------------------------------

    def query_status(self) -> Optional[RobotResponse]:
        """
        Send a STATUS command and return the ESP32's current state.

        Returns:
            :class:`RobotResponse` from the ESP32, or ``None`` on failure.
        """
        self.flush_input()
        if self.send_command(RobotCommand.STATUS):
            return self.read_response()
        return None

    # ------------------------------------------------------------------
    # Internal Reconnect Logic
    # ------------------------------------------------------------------

    def _attempt_reconnect(self) -> None:
        """
        Attempt to silently reconnect to the serial port.

        Called automatically when a send or read operation fails.
        """
        log.warning("Serial connection lost. Attempting to reconnect...")
        try:
            self.connect()
        except RuntimeError as exc:
            log.error("Reconnect failed: %s", exc)
