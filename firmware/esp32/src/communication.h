/**
 * @file communication.h
 * @brief Public API for UART command reception and parsing.
 *
 * @details
 * Handles all Serial communication between the laptop AI system and
 * the ESP32 controller. Provides a non-blocking polling API to check
 * for, read, and validate incoming text commands.
 *
 * Supported Commands (defined as CMD_* in config.h):
 *  - HOME        — Return arm to home position
 *  - PICK        — Execute pick-up sequence
 *  - DROP_RED    — Drop object in red waste bin
 *  - DROP_YELLOW — Drop object in yellow waste bin
 *  - DROP_BLUE   — Drop object in blue/sharps bin
 *  - STOP        — Emergency stop
 *  - STATUS      — Report current arm status
 *  - DEMO        — Run demonstration sequence
 *
 * Adding new commands: define CMD_* in config.h and add a case to the
 * command dispatcher in arm_control.c. No changes to communication.c needed.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <stdbool.h>
#include "config.h"

/* ===========================================================================
 * Data Types
 * =========================================================================*/

/**
 * @brief Enumeration of all recognised UART commands.
 *
 * @details
 * CMD_UNKNOWN is returned when the received string does not match any
 * defined command. This allows the caller to handle invalid inputs cleanly.
 */
typedef enum {
    CMD_ID_HOME        = 0, /**< Return arm to home position              */
    CMD_ID_PICK        = 1, /**< Execute pick-up sequence                 */
    CMD_ID_DROP_RED    = 2, /**< Drop in red (infectious) waste bin       */
    CMD_ID_DROP_YELLOW = 3, /**< Drop in yellow (chemical) waste bin      */
    CMD_ID_DROP_BLUE   = 4, /**< Drop in blue (sharps/recyclable) bin     */
    CMD_ID_STOP        = 5, /**< Emergency stop all motion                */
    CMD_ID_STATUS      = 6, /**< Report current firmware status           */
    CMD_ID_DEMO        = 7, /**< Run demo / calibration sequence          */
    CMD_ID_UNKNOWN     = 8  /**< Unrecognised or malformed command         */
} CommandId_t;

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the Serial (UART) communication interface.
 *
 * @details
 * Must be called once in setup() before any communication functions are used.
 * Starts Serial at UART_BAUD_RATE and prints a ready banner to the console.
 */
void communication_init(void);

/* ===========================================================================
 * Command Reception
 * =========================================================================*/

/**
 * @brief Check whether a complete command line is available in the UART buffer.
 *
 * @details
 * Non-blocking poll. A command is considered available when a newline
 * character (UART_CMD_TERMINATOR) has been received. Safe to call every
 * loop iteration.
 *
 * @return true  if a complete command string is ready to be read.
 * @return false if no complete command has arrived yet.
 */
bool communication_available(void);

/**
 * @brief Read and parse the next complete command from the UART buffer.
 *
 * @details
 * Reads characters from Serial into an internal buffer until a newline
 * is found or the buffer is full. Strips trailing whitespace, converts
 * to uppercase, and matches against known CMD_* strings.
 *
 * Must only be called after communication_available() returns true.
 *
 * @return CommandId_t  The parsed command identifier, or CMD_ID_UNKNOWN
 *                      if the string did not match any known command.
 */
CommandId_t communication_read(void);

/**
 * @brief Send a status string back to the laptop over Serial.
 *
 * @details
 * Appends a newline to the message before transmitting.
 * Use STATUS_MSG_* constants from config.h for standard responses.
 *
 * @param message  Null-terminated ASCII string to transmit.
 */
void communication_send_status(const char *message);

#endif /* COMMUNICATION_H */
