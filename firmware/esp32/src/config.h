/**
 * @file config.h
 * @brief Central configuration file for ESP32 Biomedical Waste Segregation Robotic Arm.
 *
 * @details
 * All hardware pin definitions, servo channel mappings, PWM parameters,
 * servo angle limits, communication settings, timing constants, and
 * command identifiers are defined here.
 *
 * Modifying this file is the ONLY place required to adapt firmware
 * to different hardware revisions.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef CONFIG_H
#define CONFIG_H

/* ===========================================================================
 * I2C Pin Configuration
 * =========================================================================*/

/** @brief GPIO pin number for I2C SDA line */
#define I2C_SDA_PIN          21

/** @brief GPIO pin number for I2C SCL line */
#define I2C_SCL_PIN          22

/** @brief I2C clock frequency in Hz for PCA9685 communication */
#define I2C_CLOCK_FREQ_HZ    400000UL

/* ===========================================================================
 * UART / Serial Configuration
 * =========================================================================*/

/** @brief UART baud rate for laptop ↔ ESP32 communication */
#define UART_BAUD_RATE       115200

/** @brief Maximum number of characters in a single UART command string */
#define UART_CMD_BUFFER_SIZE 64

/** @brief Command terminator character (newline) */
#define UART_CMD_TERMINATOR  '\n'

/* ===========================================================================
 * PCA9685 PWM Driver Configuration
 * =========================================================================*/

/** @brief I2C address of the PCA9685 PWM driver (default, A0-A5 = GND) */
#define PCA9685_I2C_ADDRESS  0x40

/** @brief PWM frequency in Hz for standard hobby servo control */
#define PWM_FREQUENCY_HZ     50

/* ===========================================================================
 * Servo Channel Assignments (PCA9685 Channels 0–15)
 * =========================================================================*/

/** @brief PCA9685 channel connected to the Base Rotation servo */
#define SERVO_CHANNEL_BASE       0

/** @brief PCA9685 channel connected to the Shoulder servo */
#define SERVO_CHANNEL_SHOULDER   1

/** @brief PCA9685 channel connected to the Elbow servo */
#define SERVO_CHANNEL_ELBOW      2

/** @brief PCA9685 channel connected to the Wrist servo */
#define SERVO_CHANNEL_WRIST      3

/** @brief PCA9685 channel connected to the Gripper servo */
#define SERVO_CHANNEL_GRIPPER    4

/** @brief Total number of servo joints on the robotic arm */
#define SERVO_JOINT_COUNT        5

/* ===========================================================================
 * Servo Angle Limits (degrees)
 * =========================================================================*/

/** @brief Minimum allowable servo angle in degrees */
#define SERVO_ANGLE_MIN_DEG     0

/** @brief Maximum allowable servo angle in degrees */
#define SERVO_ANGLE_MAX_DEG     180

/** @brief Minimum PWM pulse width in microseconds (0° position) */
#define SERVO_PULSE_MIN_US      500

/** @brief Maximum PWM pulse width in microseconds (180° position) */
#define SERVO_PULSE_MAX_US      2500

/* ===========================================================================
 * Home Position Angles (degrees)
 * =========================================================================*/

/** @brief Home angle for Base servo — centered */
#define HOME_ANGLE_BASE         90

/** @brief Home angle for Shoulder servo — upright */
#define HOME_ANGLE_SHOULDER     90

/** @brief Home angle for Elbow servo — upright */
#define HOME_ANGLE_ELBOW        90

/** @brief Home angle for Wrist servo — level */
#define HOME_ANGLE_WRIST        90

/** @brief Home angle for Gripper servo — open position */
#define HOME_ANGLE_GRIPPER      60

/* ===========================================================================
 * Gripper Angles (degrees)
 * =========================================================================*/

/** @brief Gripper servo angle for fully open position */
#define GRIPPER_ANGLE_OPEN      60

/** @brief Gripper servo angle for fully closed (gripping) position */
#define GRIPPER_ANGLE_CLOSED    120

/* ===========================================================================
 * Drop Zone Angles — Base Rotation (degrees)
 * =========================================================================*/

/** @brief Base rotation angle for dropping in the Red zone (infectious waste) */
#define DROP_ZONE_RED_BASE_DEG        45

/** @brief Base rotation angle for dropping in the Yellow zone (chemical waste) */
#define DROP_ZONE_YELLOW_BASE_DEG     135

/** @brief Base rotation angle for dropping in the Blue zone (sharps / recyclable) */
#define DROP_ZONE_BLUE_BASE_DEG       0

/* ===========================================================================
 * Pick-Up Pose Angles (degrees)
 * =========================================================================*/

/** @brief Base angle when moving to pick-up position */
#define PICK_ANGLE_BASE         90

/** @brief Shoulder angle when moving to pick-up position */
#define PICK_ANGLE_SHOULDER     60

/** @brief Elbow angle when moving to pick-up position */
#define PICK_ANGLE_ELBOW        110

/** @brief Wrist angle when moving to pick-up position */
#define PICK_ANGLE_WRIST        70

/* ===========================================================================
 * Drop Pose Common Angles (degrees) — shared by all drop zones
 * =========================================================================*/

/** @brief Shoulder angle used for all drop operations */
#define DROP_ANGLE_SHOULDER     80

/** @brief Elbow angle used for all drop operations */
#define DROP_ANGLE_ELBOW        90

/** @brief Wrist angle used for all drop operations */
#define DROP_ANGLE_WRIST        90

/* ===========================================================================
 * Smooth Motion Configuration
 * =========================================================================*/

/** @brief Number of interpolation steps for smooth servo movement */
#define SMOOTH_MOTION_STEPS         50

/** @brief Delay in milliseconds between each interpolation step */
#define SMOOTH_MOTION_STEP_DELAY_MS 15

/** @brief Delay in milliseconds after completing a full motion sequence */
#define MOTION_SETTLE_DELAY_MS      300

/* ===========================================================================
 * Timing Constants
 * =========================================================================*/

/** @brief Delay in milliseconds after PCA9685 initialisation */
#define PCA9685_INIT_DELAY_MS       100

/** @brief Delay in milliseconds between home position joint moves */
#define HOME_SEQUENCE_DELAY_MS      200

/** @brief Delay in milliseconds for the gripper to physically open/close */
#define GRIPPER_ACTUATE_DELAY_MS    400

/** @brief Main loop polling interval in milliseconds */
#define MAIN_LOOP_DELAY_MS          10

/* ===========================================================================
 * Command String Definitions
 * =========================================================================*/

/** @brief UART command string to return arm to home position */
#define CMD_HOME        "HOME"

/** @brief UART command string to execute pick-up sequence */
#define CMD_PICK        "PICK"

/** @brief UART command string to drop object into red waste bin */
#define CMD_DROP_RED    "DROP_RED"

/** @brief UART command string to drop object into yellow waste bin */
#define CMD_DROP_YELLOW "DROP_YELLOW"

/** @brief UART command string to drop object into blue waste bin */
#define CMD_DROP_BLUE   "DROP_BLUE"

/** @brief UART command string to emergency-stop all motion */
#define CMD_STOP        "STOP"

/** @brief UART command string to report current arm status */
#define CMD_STATUS      "STATUS"

/** @brief UART command string to run a demo/calibration sequence */
#define CMD_DEMO        "DEMO"

/* ===========================================================================
 * Serial Status Messages
 * =========================================================================*/

/** @brief Printed when firmware is ready and waiting for commands */
#define STATUS_MSG_READY        "STATUS:READY"

/** @brief Printed when the arm is executing a motion */
#define STATUS_MSG_BUSY         "STATUS:BUSY"

/** @brief Printed when an unrecognised command is received */
#define STATUS_MSG_UNKNOWN_CMD  "STATUS:UNKNOWN_CMD"

/** @brief Printed after a successful motion completes */
#define STATUS_MSG_DONE         "STATUS:DONE"

/** @brief Printed when a STOP command is received */
#define STATUS_MSG_STOPPED      "STATUS:STOPPED"

#endif /* CONFIG_H */
