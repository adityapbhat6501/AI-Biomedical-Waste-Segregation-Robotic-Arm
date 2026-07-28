"""
protocol.py — UART Command and Response Protocol Definitions.

Centralises all command strings and response tokens exchanged between
the Python AI module and the ESP32 firmware over Serial.

Must stay in sync with CMD_* and STATUS_MSG_* in firmware/esp32/src/config.h.

Author: [Author Placeholder]
Version: 1.0.0
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Outgoing Commands (Python → ESP32)
# ---------------------------------------------------------------------------

class RobotCommand(str, Enum):
    """
    Enumeration of all valid UART commands sent to the ESP32 controller.

    Each value is the exact ASCII string written to the serial port,
    followed by a newline character appended by :func:`encode_command`.
    """
    HOME        = "HOME"
    PICK        = "PICK"
    DROP_RED    = "DROP_RED"
    DROP_YELLOW = "DROP_YELLOW"
    DROP_BLUE   = "DROP_BLUE"
    DROP_WHITE  = "DROP_WHITE"
    DROP_BLACK  = "DROP_BLACK"
    STOP        = "STOP"
    STATUS      = "STATUS"
    DEMO        = "DEMO"


# ---------------------------------------------------------------------------
# Incoming Responses (ESP32 → Python)
# ---------------------------------------------------------------------------

class RobotResponse(str, Enum):
    """
    Enumeration of all status strings received from the ESP32 controller.
    """
    READY       = "STATUS:READY"
    BUSY        = "STATUS:BUSY"
    DONE        = "STATUS:DONE"
    STOPPED     = "STATUS:STOPPED"
    UNKNOWN_CMD = "STATUS:UNKNOWN_CMD"


# ---------------------------------------------------------------------------
# Encoding / Decoding Helpers
# ---------------------------------------------------------------------------

def encode_command(command: RobotCommand) -> bytes:
    """
    Encode a RobotCommand into bytes ready for serial transmission.

    Appends a newline character as the command terminator matching
    the firmware's UART_CMD_TERMINATOR definition.

    Args:
        command: A :class:`RobotCommand` enum value.

    Returns:
        UTF-8 encoded bytes with trailing newline.

    Example:
        >>> encode_command(RobotCommand.DROP_RED)
        b'DROP_RED\\n'
    """
    return (command.value + "\n").encode("utf-8")


def decode_response(raw: str) -> RobotResponse | None:
    """
    Decode a raw response string received from the ESP32 into a RobotResponse.

    Args:
        raw: Stripped response string from serial (e.g. "STATUS:DONE").

    Returns:
        Matching :class:`RobotResponse`, or ``None`` if unrecognised.
    """
    raw_stripped = raw.strip()
    for resp in RobotResponse:
        if resp.value == raw_stripped:
            return resp
    return None


def is_valid_command(command_str: str) -> bool:
    """
    Check whether a string is a valid RobotCommand value.

    Args:
        command_str: Command string to validate.

    Returns:
        True if the string matches any :class:`RobotCommand` value.
    """
    return command_str in {cmd.value for cmd in RobotCommand}


def get_command_for_drop(category_command: str) -> RobotCommand | None:
    """
    Map a waste category command string to a RobotCommand enum value.

    This bridges the ``WasteCategory.command`` strings in ``classes.py``
    to the typed :class:`RobotCommand` enum used by the serial module.

    Args:
        category_command: Command string from WasteCategory (e.g. "DROP_RED").

    Returns:
        Matching :class:`RobotCommand`, or ``None`` if not found.
    """
    for cmd in RobotCommand:
        if cmd.value == category_command:
            return cmd
    return None
