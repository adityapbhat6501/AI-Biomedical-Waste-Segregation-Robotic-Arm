/**
 * @file communication.c
 * @brief UART command reception, validation, and parsing implementation.
 *
 * @details
 * Implements the communication.h API. Reads line-delimited text commands
 * from Serial (USB UART), validates them, and returns a CommandId_t enum
 * value to the caller.
 *
 * Design decisions:
 *  - Uses a static internal buffer (UART_CMD_BUFFER_SIZE) to accumulate chars.
 *  - communication_available() is non-blocking — safe to poll in the main loop.
 *  - Commands are compared case-insensitively by converting to uppercase first.
 *  - Unknown commands are rejected with a STATUS:UNKNOWN_CMD response.
 *
 * Dependencies:
 *  - Arduino.h for Serial
 *  - string.h  for strcmp, strlen, toupper
 *  - config.h  for CMD_* strings and buffer size
 *  - utils.h   for utils_trim_trailing()
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include "communication.h"
#include "config.h"
#include "utils.h"

#include <Arduino.h>
#include <string.h>
#include <ctype.h>

/* ===========================================================================
 * Private State
 * =========================================================================*/

/** @brief Internal accumulation buffer for incoming UART characters */
static char s_rx_buffer[UART_CMD_BUFFER_SIZE];

/** @brief Current write index into s_rx_buffer */
static uint8_t s_rx_index = 0;

/** @brief Flag set when a complete line (terminated by '\n') is in the buffer */
static bool s_cmd_ready = false;

/* ===========================================================================
 * Private Helper Prototypes
 * =========================================================================*/

/**
 * @brief Convert all characters in a C-string to uppercase in place.
 *
 * @param str  Null-terminated string to convert.
 */
static void comm_to_uppercase(char *str);

/**
 * @brief Match a command string against all known CMD_* identifiers.
 *
 * @param cmd_str  Uppercase, whitespace-trimmed command string.
 * @return         Matching CommandId_t, or CMD_ID_UNKNOWN.
 */
static CommandId_t comm_parse_command(const char *cmd_str);

/**
 * @brief Accumulate incoming Serial bytes into the internal buffer.
 *
 * @details
 * Called internally by communication_available(). Reads all available
 * bytes, appending to s_rx_buffer until a newline or buffer-full condition.
 */
static void comm_accumulate_bytes(void);

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the Serial UART communication interface.
 */
void communication_init(void)
{
    Serial.begin(UART_BAUD_RATE);

    /* Wait briefly for USB-Serial to enumerate on the host side */
    utils_delay_ms(500);

    /* Clear buffer state */
    memset(s_rx_buffer, 0, sizeof(s_rx_buffer));
    s_rx_index = 0;
    s_cmd_ready = false;

    Serial.println(F("========================================"));
    Serial.println(F("  Biomedical Waste Segregation Arm v1.0"));
    Serial.println(F("  UART Ready — Awaiting Commands"));
    Serial.println(F("========================================"));
    Serial.println(STATUS_MSG_READY);
}

/* ===========================================================================
 * Command Reception
 * =========================================================================*/

/**
 * @brief Check whether a complete command line is available.
 */
bool communication_available(void)
{
    if (s_cmd_ready) {
        return true;
    }

    comm_accumulate_bytes();
    return s_cmd_ready;
}

/**
 * @brief Read and parse the next complete command from the UART buffer.
 */
CommandId_t communication_read(void)
{
    /* Reset the ready flag so the next command can be accumulated */
    s_cmd_ready = false;

    /* Trim trailing CR/LF/spaces */
    utils_trim_trailing(s_rx_buffer);

    /* Convert to uppercase for case-insensitive matching */
    comm_to_uppercase(s_rx_buffer);

    Serial.print(F("[comm] Received: \""));
    Serial.print(s_rx_buffer);
    Serial.println(F("\""));

    /* Parse to a command ID */
    CommandId_t cmd_id = comm_parse_command(s_rx_buffer);

    /* Clear buffer for next command */
    memset(s_rx_buffer, 0, sizeof(s_rx_buffer));
    s_rx_index = 0;

    if (cmd_id == CMD_ID_UNKNOWN) {
        communication_send_status(STATUS_MSG_UNKNOWN_CMD);
    }

    return cmd_id;
}

/**
 * @brief Send a status string back to the laptop over Serial.
 */
void communication_send_status(const char *message)
{
    if (message == NULL) {
        return;
    }
    Serial.println(message);
}

/* ===========================================================================
 * Private Helpers
 * =========================================================================*/

/**
 * @brief Accumulate incoming Serial bytes into the internal buffer.
 */
static void comm_accumulate_bytes(void)
{
    while (Serial.available() > 0) {
        char incoming_byte = (char)Serial.read();

        if (incoming_byte == UART_CMD_TERMINATOR) {
            /* Null-terminate and mark command as ready */
            s_rx_buffer[s_rx_index] = '\0';
            s_cmd_ready = true;
            return;
        }

        /* Ignore carriage return (Windows line endings) */
        if (incoming_byte == '\r') {
            continue;
        }

        /* Guard against buffer overflow — drop extra characters */
        if (s_rx_index < (UART_CMD_BUFFER_SIZE - 1)) {
            s_rx_buffer[s_rx_index] = incoming_byte;
            s_rx_index++;
        } else {
            Serial.println(F("[comm] WARNING: Command buffer overflow — flushing."));
            memset(s_rx_buffer, 0, sizeof(s_rx_buffer));
            s_rx_index = 0;
        }
    }
}

/**
 * @brief Convert all characters in a C-string to uppercase in place.
 */
static void comm_to_uppercase(char *str)
{
    if (str == NULL) {
        return;
    }
    for (uint32_t i = 0; str[i] != '\0'; i++) {
        str[i] = (char)toupper((unsigned char)str[i]);
    }
}

/**
 * @brief Match a command string against all known CMD_* identifiers.
 */
static CommandId_t comm_parse_command(const char *cmd_str)
{
    if (cmd_str == NULL) {
        return CMD_ID_UNKNOWN;
    }

    if (strcmp(cmd_str, CMD_HOME)        == 0) return CMD_ID_HOME;
    if (strcmp(cmd_str, CMD_PICK)        == 0) return CMD_ID_PICK;
    if (strcmp(cmd_str, CMD_DROP_RED)    == 0) return CMD_ID_DROP_RED;
    if (strcmp(cmd_str, CMD_DROP_YELLOW) == 0) return CMD_ID_DROP_YELLOW;
    if (strcmp(cmd_str, CMD_DROP_BLUE)   == 0) return CMD_ID_DROP_BLUE;
    if (strcmp(cmd_str, CMD_STOP)        == 0) return CMD_ID_STOP;
    if (strcmp(cmd_str, CMD_STATUS)      == 0) return CMD_ID_STATUS;
    if (strcmp(cmd_str, CMD_DEMO)        == 0) return CMD_ID_DEMO;

    return CMD_ID_UNKNOWN;
}
