/**
 * @file servo.h
 * @brief Public API for PCA9685-backed servo motor control.
 *
 * @details
 * Abstracts the PCA9685 16-channel PWM driver to provide a clean,
 * angle-based interface for controlling up to 16 hobby servos.
 *
 * Features:
 *  - One-call angle writes (0–180°) with automatic clamping
 *  - Smooth interpolated movement between angles
 *  - Bulk home position reset
 *  - PWM pulse width calculated from config.h constants
 *
 * This module is the ONLY layer that generates PWM signals.
 * All higher-level modules (arm_control, gripper) must use these APIs.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef SERVO_H
#define SERVO_H

#include <stdint.h>
#include <stdbool.h>

/* ===========================================================================
 * Data Types
 * =========================================================================*/

/**
 * @brief Snapshot of all servo joint angles at a single point in time.
 *
 * @details
 * Used to describe a target pose for smooth multi-joint motion.
 * Array indices correspond to PCA9685 channel numbers.
 */
typedef struct {
    uint8_t angles[16]; /**< Angle (°) for each PCA9685 channel (0–15) */
} ServoPose_t;

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the PCA9685 driver and set PWM frequency.
 *
 * @details
 * Must be called once during system startup, after Wire.begin().
 * Sets all servo channels to their home positions defined in config.h.
 *
 * @return true  if PCA9685 was found and initialised successfully.
 * @return false if the I2C device was not found.
 */
bool servo_init(void);

/* ===========================================================================
 * Single Servo Control
 * =========================================================================*/

/**
 * @brief Write an angle to a single servo channel immediately.
 *
 * @details
 * The angle is automatically clamped to [SERVO_ANGLE_MIN_DEG, SERVO_ANGLE_MAX_DEG].
 * The corresponding PWM pulse width is computed from SERVO_PULSE_MIN_US and
 * SERVO_PULSE_MAX_US constants in config.h.
 *
 * @param channel  PCA9685 channel number (0–15).
 * @param angle    Target angle in degrees (0–180).
 */
void servo_write_angle(uint8_t channel, uint8_t angle);

/**
 * @brief Read the last-written angle for a servo channel.
 *
 * @details
 * Returns the cached angle from an internal state array.
 * Does NOT read back from PCA9685 hardware.
 *
 * @param channel  PCA9685 channel number (0–15).
 * @return         Last written angle in degrees, or 0 if never written.
 */
uint8_t servo_read_angle(uint8_t channel);

/* ===========================================================================
 * Smooth Motion
 * =========================================================================*/

/**
 * @brief Smoothly move a single servo from its current angle to a target angle.
 *
 * @details
 * Performs linear interpolation over SMOOTH_MOTION_STEPS steps,
 * pausing SMOOTH_MOTION_STEP_DELAY_MS between each step.
 * Blocks until the motion is complete.
 *
 * @param channel      PCA9685 channel number (0–15).
 * @param target_angle Target angle in degrees (0–180).
 */
void servo_move_smooth(uint8_t channel, uint8_t target_angle);

/**
 * @brief Smoothly move all specified joints in parallel to a target pose.
 *
 * @details
 * Interpolates every joint simultaneously over SMOOTH_MOTION_STEPS steps,
 * which produces coordinated, natural-looking arm motion.
 * Blocks until all joints reach their target angles.
 *
 * @param target_pose  Pointer to a ServoPose_t describing target angles per channel.
 * @param joint_count  Number of channels to move (use SERVO_JOINT_COUNT typically).
 */
void servo_move_pose_smooth(const ServoPose_t *target_pose, uint8_t joint_count);

/* ===========================================================================
 * Home Position
 * =========================================================================*/

/**
 * @brief Move all arm servos to their home positions defined in config.h.
 *
 * @details
 * Moves each joint independently with a short delay between joints
 * (HOME_SEQUENCE_DELAY_MS) to reduce peak current draw.
 */
void servo_set_home(void);

#endif /* SERVO_H */
