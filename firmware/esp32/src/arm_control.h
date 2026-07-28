/**
 * @file arm_control.h
 * @brief Public API for high-level robotic arm movement sequences.
 *
 * @details
 * Defines coordinated, multi-joint motion sequences for the biomedical
 * waste segregation robotic arm. All motion is performed through servo.h
 * and gripper.h — this module NEVER generates PWM directly.
 *
 * Responsibilities:
 *  - Orchestrate joint sequences for pick, drop, home, and demo operations
 *  - Dispatch incoming CommandId_t values to the correct motion function
 *  - Maintain a simple busy/stopped state flag
 *
 * Motion sequences follow this general pattern:
 *  1. Open gripper (safety)
 *  2. Move to target pre-position
 *  3. Lower to approach position
 *  4. Actuate gripper
 *  5. Retract to safe height
 *  6. Rotate to destination zone
 *  7. Release gripper
 *  8. Return to home
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef ARM_CONTROL_H
#define ARM_CONTROL_H

#include <stdbool.h>
#include "communication.h"  /* For CommandId_t */

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the arm control module state.
 *
 * @details
 * Resets the busy and stop flags. Does NOT move any servos.
 * Call after servo_init() during system startup.
 */
void arm_control_init(void);

/* ===========================================================================
 * Command Dispatcher
 * =========================================================================*/

/**
 * @brief Dispatch a CommandId_t to the corresponding arm motion function.
 *
 * @details
 * This is the primary entry point called by main.c. Selects and executes
 * the appropriate arm sequence based on the received command ID.
 * Prints STATUS:BUSY before motion and STATUS:DONE on completion.
 *
 * @param cmd  The command identifier returned by communication_read().
 */
void arm_control_dispatch(CommandId_t cmd);

/* ===========================================================================
 * Motion Sequences
 * =========================================================================*/

/**
 * @brief Move the arm to its home (safe resting) position.
 *
 * @details
 * Calls servo_set_home() and opens the gripper.
 * This is the default state after startup and between operations.
 */
void arm_home(void);

/**
 * @brief Execute a complete object pick-up sequence.
 *
 * @details
 * Steps:
 *  1. Open gripper
 *  2. Move to approach position above pick-up zone
 *  3. Lower to pick-up height
 *  4. Close gripper to grasp object
 *  5. Lift object to safe carry height
 *
 * After this sequence the arm holds the object and waits for a DROP command.
 */
void arm_pick_object(void);

/**
 * @brief Drop the held object into the red (infectious) waste bin.
 *
 * @details
 * Steps:
 *  1. Rotate base to DROP_ZONE_RED_BASE_DEG
 *  2. Lower arm to drop height
 *  3. Open gripper to release object
 *  4. Return to home position
 */
void arm_drop_red(void);

/**
 * @brief Drop the held object into the yellow (chemical) waste bin.
 *
 * @details
 * Same sequence as arm_drop_red() but rotates to DROP_ZONE_YELLOW_BASE_DEG.
 */
void arm_drop_yellow(void);

/**
 * @brief Drop the held object into the blue (sharps/recyclable) waste bin.
 *
 * @details
 * Same sequence as arm_drop_red() but rotates to DROP_ZONE_BLUE_BASE_DEG.
 */
void arm_drop_blue(void);

/**
 * @brief Execute a demonstration / calibration movement sequence.
 *
 * @details
 * Cycles through home, pick approach, and all three drop zones without
 * actually gripping an object. Useful for visual verification during setup
 * and to verify all joints move freely across their range.
 */
void arm_demo_sequence(void);

/* ===========================================================================
 * State Queries
 * =========================================================================*/

/**
 * @brief Query whether the arm is currently executing a motion sequence.
 *
 * @return true  if a motion is in progress.
 * @return false if the arm is idle.
 */
bool arm_is_busy(void);

/**
 * @brief Signal the arm to stop after the current motion step completes.
 *
 * @details
 * Sets an internal stop-requested flag. Full preemption is not implemented —
 * motion will halt at the next safe checkpoint.
 */
void arm_request_stop(void);

#endif /* ARM_CONTROL_H */
