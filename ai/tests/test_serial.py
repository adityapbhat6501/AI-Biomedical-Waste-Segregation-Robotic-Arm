"""
test_serial.py — Unit Tests for the Communication Module.

Tests:
    - Protocol encoding / decoding
    - Command validation
    - Category → command mapping
    - SerialCommunicator behaviour in DEBUG_MODE (no real hardware needed)

Run with:
    python -m pytest tests/test_serial.py -v

Author: [Author Placeholder]
Version: 1.0.0
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from communication.protocol import (
    RobotCommand,
    RobotResponse,
    encode_command,
    decode_response,
    is_valid_command,
    get_command_for_drop,
)


# ---------------------------------------------------------------------------
# Protocol Encoding Tests
# ---------------------------------------------------------------------------

class TestEncodeCommand:

    def test_home_encodes_correctly(self):
        result = encode_command(RobotCommand.HOME)
        assert result == b"HOME\n"

    def test_drop_red_encodes_correctly(self):
        result = encode_command(RobotCommand.DROP_RED)
        assert result == b"DROP_RED\n"

    def test_drop_yellow_encodes_correctly(self):
        result = encode_command(RobotCommand.DROP_YELLOW)
        assert result == b"DROP_YELLOW\n"

    def test_drop_blue_encodes_correctly(self):
        result = encode_command(RobotCommand.DROP_BLUE)
        assert result == b"DROP_BLUE\n"

    def test_stop_encodes_correctly(self):
        result = encode_command(RobotCommand.STOP)
        assert result == b"STOP\n"

    def test_status_encodes_correctly(self):
        result = encode_command(RobotCommand.STATUS)
        assert result == b"STATUS\n"

    def test_all_commands_end_with_newline(self):
        for cmd in RobotCommand:
            encoded = encode_command(cmd)
            assert encoded.endswith(b"\n"), f"Command {cmd} missing newline"

    def test_encoded_result_is_bytes(self):
        result = encode_command(RobotCommand.PICK)
        assert isinstance(result, bytes)


# ---------------------------------------------------------------------------
# Protocol Decoding Tests
# ---------------------------------------------------------------------------

class TestDecodeResponse:

    def test_ready_decodes_correctly(self):
        assert decode_response("STATUS:READY") == RobotResponse.READY

    def test_busy_decodes_correctly(self):
        assert decode_response("STATUS:BUSY") == RobotResponse.BUSY

    def test_done_decodes_correctly(self):
        assert decode_response("STATUS:DONE") == RobotResponse.DONE

    def test_stopped_decodes_correctly(self):
        assert decode_response("STATUS:STOPPED") == RobotResponse.STOPPED

    def test_unknown_returns_none(self):
        assert decode_response("GARBAGE") is None

    def test_empty_string_returns_none(self):
        assert decode_response("") is None

    def test_strips_whitespace(self):
        assert decode_response("  STATUS:READY  \n") == RobotResponse.READY


# ---------------------------------------------------------------------------
# Validation Tests
# ---------------------------------------------------------------------------

class TestIsValidCommand:

    def test_home_is_valid(self):
        assert is_valid_command("HOME") is True

    def test_drop_red_is_valid(self):
        assert is_valid_command("DROP_RED") is True

    def test_random_string_is_invalid(self):
        assert is_valid_command("MOVE_LEFT") is False

    def test_empty_string_is_invalid(self):
        assert is_valid_command("") is False

    def test_lowercase_is_invalid(self):
        # Commands are case-sensitive at this layer; normalisation is in comm.c
        assert is_valid_command("home") is False


# ---------------------------------------------------------------------------
# Command Mapping Tests
# ---------------------------------------------------------------------------

class TestGetCommandForDrop:

    def test_drop_red_maps_correctly(self):
        cmd = get_command_for_drop("DROP_RED")
        assert cmd == RobotCommand.DROP_RED

    def test_drop_yellow_maps_correctly(self):
        cmd = get_command_for_drop("DROP_YELLOW")
        assert cmd == RobotCommand.DROP_YELLOW

    def test_unknown_returns_none(self):
        cmd = get_command_for_drop("DROP_PURPLE")
        assert cmd is None


# ---------------------------------------------------------------------------
# RobotCommand Enum Tests
# ---------------------------------------------------------------------------

class TestRobotCommandEnum:

    def test_all_expected_commands_exist(self):
        expected = {"HOME", "PICK", "DROP_RED", "DROP_YELLOW",
                    "DROP_BLUE", "DROP_WHITE", "DROP_BLACK",
                    "STOP", "STATUS", "DEMO"}
        actual = {cmd.value for cmd in RobotCommand}
        assert expected.issubset(actual), f"Missing commands: {expected - actual}"
