/**
 * @file gripper.c
 * @brief Robotic gripper control implementation.
 *
 * @details
 * Implements open/close operations for the servo-driven end-effector.
 * All PWM generation is performed via servo.c APIs — this module
 * contains NO direct PCA9685 access.
 *
 * Dependencies:
 *  - servo.h  for servo_move_smooth() and servo_read_angle()
 *  - config.h for GRIPPER_ANGLE_OPEN, GRIPPER_ANGLE_CLOSED,
 *              SERVO_CHANNEL_GRIPPER, GRIPPER_ACTUATE_DELAY_MS
 *  - utils.h  for utils_delay_ms()
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include "gripper.h"
#include "servo.h"
#include "config.h"
#include "utils.h"

#include <Arduino.h>

/* ===========================================================================
 * Gripper Control Implementation
 * =========================================================================*/

/**
 * @brief Open the gripper to its maximum open angle.
 */
void gripper_open(void)
{
    Serial.println(F("[gripper] Opening..."));
    servo_move_smooth(SERVO_CHANNEL_GRIPPER, GRIPPER_ANGLE_OPEN);
    utils_delay_ms(GRIPPER_ACTUATE_DELAY_MS);
    Serial.println(F("[gripper] Open."));
}

/**
 * @brief Close the gripper to its gripping angle.
 */
void gripper_close(void)
{
    Serial.println(F("[gripper] Closing..."));
    servo_move_smooth(SERVO_CHANNEL_GRIPPER, GRIPPER_ANGLE_CLOSED);
    utils_delay_ms(GRIPPER_ACTUATE_DELAY_MS);
    Serial.println(F("[gripper] Closed."));
}

/**
 * @brief Query whether the gripper is currently in the closed position.
 */
bool gripper_is_closed(void)
{
    return (servo_read_angle(SERVO_CHANNEL_GRIPPER) == GRIPPER_ANGLE_CLOSED);
}
