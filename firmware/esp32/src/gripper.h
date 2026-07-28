/**
 * @file gripper.h
 * @brief Public API for robotic gripper control.
 *
 * @details
 * Provides high-level open and close operations for the end-effector gripper.
 * Internally delegates to servo.c — does NOT generate PWM directly.
 *
 * Gripper angle constants (GRIPPER_ANGLE_OPEN, GRIPPER_ANGLE_CLOSED) are
 * defined in config.h and may be adjusted during calibration without
 * modifying this module.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef GRIPPER_H
#define GRIPPER_H

#include <stdbool.h>

/* ===========================================================================
 * Gripper Control
 * =========================================================================*/

/**
 * @brief Open the gripper to its maximum open angle.
 *
 * @details
 * Smoothly moves the gripper servo to GRIPPER_ANGLE_OPEN and waits
 * GRIPPER_ACTUATE_DELAY_MS to allow full mechanical travel.
 */
void gripper_open(void);

/**
 * @brief Close the gripper to its gripping angle.
 *
 * @details
 * Smoothly moves the gripper servo to GRIPPER_ANGLE_CLOSED and waits
 * GRIPPER_ACTUATE_DELAY_MS to allow full mechanical travel.
 */
void gripper_close(void);

/**
 * @brief Query whether the gripper is currently in the closed position.
 *
 * @return true  if the gripper servo is at GRIPPER_ANGLE_CLOSED.
 * @return false otherwise.
 */
bool gripper_is_closed(void);

#endif /* GRIPPER_H */
