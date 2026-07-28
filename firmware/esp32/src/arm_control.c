/**
 * @file arm_control.c
 * @brief High-level robotic arm motion sequence implementation.
 *
 * @details
 * Implements all coordinated arm movement sequences for biomedical waste
 * segregation. Each sequence performs multi-joint motion by calling
 * servo.h and gripper.h APIs exclusively — NO direct PCA9685/PWM access.
 *
 * Motion sequences reflect the physical robot behaviour:
 *  - Pick from a fixed pick-up zone in front of the robot
 *  - Drop to one of three colour-coded waste bins (red, yellow, blue)
 *  - Return to home between all operations
 *
 * Module state:
 *  - s_arm_busy:         set true during motion, false when idle
 *  - s_stop_requested:   set by arm_request_stop(), checked at waypoints
 *
 * Dependencies:
 *  - servo.h        — single and multi-joint servo motion
 *  - gripper.h      — gripper open / close
 *  - communication.h — CommandId_t enum
 *  - config.h       — all angle constants
 *  - utils.h        — delay helpers
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include "arm_control.h"
#include "servo.h"
#include "gripper.h"
#include "communication.h"
#include "config.h"
#include "utils.h"

#include <Arduino.h>

/* ===========================================================================
 * Private State
 * =========================================================================*/

/** @brief True when the arm is actively executing a motion sequence */
static bool s_arm_busy = false;

/** @brief True when an external STOP command has been requested */
static bool s_stop_requested = false;

/* ===========================================================================
 * Private Helper Prototypes
 * =========================================================================*/

/**
 * @brief Lift arm to a safe carry height after gripping an object.
 *
 * @details
 * Moves shoulder and elbow to a neutral carry pose so the arm can
 * rotate the base without the held object colliding with the workspace.
 */
static void arm_lift_to_carry_height(void);

/**
 * @brief Move arm to the generic drop pose over a bin (shoulder/elbow/wrist).
 *
 * @details
 * Positions the arm at drop height using DROP_ANGLE_* constants.
 * Called before opening the gripper in all drop sequences.
 */
static void arm_lower_to_drop_pose(void);

/**
 * @brief Check the stop flag and return to home if a stop was requested.
 *
 * @details
 * Insert this check at safe motion checkpoints within long sequences.
 *
 * @return true  if a stop was requested (caller should abort sequence).
 * @return false if execution should continue normally.
 */
static bool arm_check_stop_requested(void);

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the arm control module state.
 */
void arm_control_init(void)
{
    s_arm_busy = false;
    s_stop_requested = false;
    Serial.println(F("[arm_control] Module initialised."));
}

/* ===========================================================================
 * Command Dispatcher
 * =========================================================================*/

/**
 * @brief Dispatch a CommandId_t to the corresponding arm motion function.
 */
void arm_control_dispatch(CommandId_t cmd)
{
    switch (cmd) {
        case CMD_ID_HOME:
            communication_send_status(STATUS_MSG_BUSY);
            arm_home();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_PICK:
            communication_send_status(STATUS_MSG_BUSY);
            arm_pick_object();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_DROP_RED:
            communication_send_status(STATUS_MSG_BUSY);
            arm_drop_red();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_DROP_YELLOW:
            communication_send_status(STATUS_MSG_BUSY);
            arm_drop_yellow();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_DROP_BLUE:
            communication_send_status(STATUS_MSG_BUSY);
            arm_drop_blue();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_STOP:
            arm_request_stop();
            communication_send_status(STATUS_MSG_STOPPED);
            break;

        case CMD_ID_STATUS:
            if (s_arm_busy) {
                communication_send_status(STATUS_MSG_BUSY);
            } else {
                communication_send_status(STATUS_MSG_READY);
            }
            break;

        case CMD_ID_DEMO:
            communication_send_status(STATUS_MSG_BUSY);
            arm_demo_sequence();
            communication_send_status(STATUS_MSG_DONE);
            break;

        case CMD_ID_UNKNOWN:
            /* Unknown command — already handled in communication_read() */
            break;

        default:
            Serial.println(F("[arm_control] Unhandled command ID."));
            break;
    }
}

/* ===========================================================================
 * Motion Sequences — Public
 * =========================================================================*/

/**
 * @brief Move the arm to its home (safe resting) position.
 */
void arm_home(void)
{
    Serial.println(F("[arm_control] Executing: HOME"));
    s_arm_busy = true;

    servo_set_home();
    gripper_open();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);
    s_arm_busy = false;
    Serial.println(F("[arm_control] HOME complete."));
}

/**
 * @brief Execute a complete object pick-up sequence.
 */
void arm_pick_object(void)
{
    Serial.println(F("[arm_control] Executing: PICK"));
    s_arm_busy = true;
    s_stop_requested = false;

    /* Step 1: Open gripper before approaching — safety first */
    gripper_open();

    if (arm_check_stop_requested()) { return; }

    /* Step 2: Move base to pick-up zone */
    servo_move_smooth(SERVO_CHANNEL_BASE, PICK_ANGLE_BASE);

    if (arm_check_stop_requested()) { return; }

    /* Step 3: Extend shoulder to approach angle */
    servo_move_smooth(SERVO_CHANNEL_SHOULDER, PICK_ANGLE_SHOULDER);

    /* Step 4: Lower elbow to reach down into pick-up zone */
    servo_move_smooth(SERVO_CHANNEL_ELBOW, PICK_ANGLE_ELBOW);

    /* Step 5: Adjust wrist for level grip */
    servo_move_smooth(SERVO_CHANNEL_WRIST, PICK_ANGLE_WRIST);

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    if (arm_check_stop_requested()) { return; }

    /* Step 6: Close gripper to grasp object */
    gripper_close();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 7: Lift to safe carry height */
    arm_lift_to_carry_height();

    s_arm_busy = false;
    Serial.println(F("[arm_control] PICK complete."));
}

/**
 * @brief Drop the held object into the red waste bin.
 */
void arm_drop_red(void)
{
    Serial.println(F("[arm_control] Executing: DROP_RED"));
    s_arm_busy = true;
    s_stop_requested = false;

    /* Step 1: Rotate base to red bin zone */
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_RED_BASE_DEG);

    if (arm_check_stop_requested()) { return; }

    /* Step 2: Lower arm into the drop pose */
    arm_lower_to_drop_pose();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 3: Release object */
    gripper_open();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 4: Return to home */
    arm_home();

    s_arm_busy = false;
    Serial.println(F("[arm_control] DROP_RED complete."));
}

/**
 * @brief Drop the held object into the yellow waste bin.
 */
void arm_drop_yellow(void)
{
    Serial.println(F("[arm_control] Executing: DROP_YELLOW"));
    s_arm_busy = true;
    s_stop_requested = false;

    /* Step 1: Rotate base to yellow bin zone */
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_YELLOW_BASE_DEG);

    if (arm_check_stop_requested()) { return; }

    /* Step 2: Lower arm into the drop pose */
    arm_lower_to_drop_pose();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 3: Release object */
    gripper_open();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 4: Return to home */
    arm_home();

    s_arm_busy = false;
    Serial.println(F("[arm_control] DROP_YELLOW complete."));
}

/**
 * @brief Drop the held object into the blue waste bin.
 */
void arm_drop_blue(void)
{
    Serial.println(F("[arm_control] Executing: DROP_BLUE"));
    s_arm_busy = true;
    s_stop_requested = false;

    /* Step 1: Rotate base to blue bin zone */
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_BLUE_BASE_DEG);

    if (arm_check_stop_requested()) { return; }

    /* Step 2: Lower arm into the drop pose */
    arm_lower_to_drop_pose();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 3: Release object */
    gripper_open();

    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Step 4: Return to home */
    arm_home();

    s_arm_busy = false;
    Serial.println(F("[arm_control] DROP_BLUE complete."));
}

/**
 * @brief Execute a demonstration / calibration movement sequence.
 */
void arm_demo_sequence(void)
{
    Serial.println(F("[arm_control] Executing: DEMO SEQUENCE"));
    s_arm_busy = true;
    s_stop_requested = false;

    /* Start at home */
    arm_home();
    if (arm_check_stop_requested()) { return; }

    /* Sweep to pick position */
    Serial.println(F("[demo] Approaching pick zone..."));
    servo_move_smooth(SERVO_CHANNEL_BASE,     PICK_ANGLE_BASE);
    servo_move_smooth(SERVO_CHANNEL_SHOULDER, PICK_ANGLE_SHOULDER);
    servo_move_smooth(SERVO_CHANNEL_ELBOW,    PICK_ANGLE_ELBOW);
    servo_move_smooth(SERVO_CHANNEL_WRIST,    PICK_ANGLE_WRIST);
    utils_delay_ms(MOTION_SETTLE_DELAY_MS);
    if (arm_check_stop_requested()) { return; }

    /* Demo gripper */
    gripper_close();
    utils_delay_ms(MOTION_SETTLE_DELAY_MS);
    gripper_open();

    /* Visit red bin */
    Serial.println(F("[demo] Visiting RED bin zone..."));
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_RED_BASE_DEG);
    arm_lower_to_drop_pose();
    utils_delay_ms(MOTION_SETTLE_DELAY_MS);
    if (arm_check_stop_requested()) { return; }

    /* Visit yellow bin */
    Serial.println(F("[demo] Visiting YELLOW bin zone..."));
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_YELLOW_BASE_DEG);
    utils_delay_ms(MOTION_SETTLE_DELAY_MS);
    if (arm_check_stop_requested()) { return; }

    /* Visit blue bin */
    Serial.println(F("[demo] Visiting BLUE bin zone..."));
    servo_move_smooth(SERVO_CHANNEL_BASE, DROP_ZONE_BLUE_BASE_DEG);
    utils_delay_ms(MOTION_SETTLE_DELAY_MS);

    /* Return to home */
    arm_home();

    s_arm_busy = false;
    Serial.println(F("[arm_control] DEMO SEQUENCE complete."));
}

/* ===========================================================================
 * State Queries
 * =========================================================================*/

/**
 * @brief Query whether the arm is currently executing a motion sequence.
 */
bool arm_is_busy(void)
{
    return s_arm_busy;
}

/**
 * @brief Signal the arm to stop after the current motion step completes.
 */
void arm_request_stop(void)
{
    Serial.println(F("[arm_control] STOP requested."));
    s_stop_requested = true;
}

/* ===========================================================================
 * Private Helpers
 * =========================================================================*/

/**
 * @brief Lift arm to a safe carry height after gripping an object.
 */
static void arm_lift_to_carry_height(void)
{
    servo_move_smooth(SERVO_CHANNEL_SHOULDER, HOME_ANGLE_SHOULDER);
    servo_move_smooth(SERVO_CHANNEL_ELBOW,    HOME_ANGLE_ELBOW);
    servo_move_smooth(SERVO_CHANNEL_WRIST,    HOME_ANGLE_WRIST);
}

/**
 * @brief Move arm to the generic drop pose over a bin.
 */
static void arm_lower_to_drop_pose(void)
{
    servo_move_smooth(SERVO_CHANNEL_SHOULDER, DROP_ANGLE_SHOULDER);
    servo_move_smooth(SERVO_CHANNEL_ELBOW,    DROP_ANGLE_ELBOW);
    servo_move_smooth(SERVO_CHANNEL_WRIST,    DROP_ANGLE_WRIST);
}

/**
 * @brief Check the stop flag and abort sequence with a home return if set.
 */
static bool arm_check_stop_requested(void)
{
    if (s_stop_requested) {
        Serial.println(F("[arm_control] Stop flag detected — aborting sequence."));
        s_stop_requested = false;
        s_arm_busy = false;
        arm_home();
        return true;
    }
    return false;
}
