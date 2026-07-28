/**
 * @file servo.c
 * @brief PCA9685-backed servo motor control implementation.
 *
 * @details
 * Implements the servo.h API by wrapping the Adafruit PCA9685 Arduino library.
 * All PWM generation is encapsulated here. Higher-level modules never touch
 * PCA9685 registers directly.
 *
 * Responsibilities:
 *  - Initialise PCA9685 over I2C
 *  - Convert degree angles to PWM tick counts
 *  - Write angles immediately or with smooth interpolation
 *  - Cache current servo positions for interpolation start points
 *
 * Dependencies:
 *  - Adafruit_PWMServoDriver (Adafruit PCA9685 library)
 *  - Wire (ESP32 Arduino I2C)
 *  - config.h for all hardware constants
 *  - utils.h for clamping and interpolation
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include "servo.h"
#include "config.h"
#include "utils.h"

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

/* ===========================================================================
 * Private Constants
 * =========================================================================*/

/** @brief Number of PWM ticks in one PCA9685 period (12-bit resolution) */
static const uint16_t PCA9685_TICK_RESOLUTION = 4096;

/** @brief Tick count representing the start of the PWM pulse (always 0) */
static const uint16_t PWM_PULSE_START_TICK = 0;

/* ===========================================================================
 * Private State
 * =========================================================================*/

/** @brief Adafruit PCA9685 driver object, initialised with I2C address */
static Adafruit_PWMServoDriver s_pwm_driver =
    Adafruit_PWMServoDriver(PCA9685_I2C_ADDRESS);

/**
 * @brief Cached angle (degrees) for each PCA9685 channel.
 *
 * Initialised to home positions during servo_init().
 * Updated on every servo_write_angle() call.
 */
static uint8_t s_current_angles[16] = {0};

/* ===========================================================================
 * Private Helper Prototypes
 * =========================================================================*/

/**
 * @brief Convert a servo angle in degrees to a PCA9685 tick count.
 *
 * @details
 * Maps [SERVO_ANGLE_MIN_DEG, SERVO_ANGLE_MAX_DEG] →
 *       [SERVO_PULSE_MIN_US, SERVO_PULSE_MAX_US] →
 *       [0, PCA9685_TICK_RESOLUTION - 1]
 *
 * The conversion uses PWM_FREQUENCY_HZ to derive the period duration in µs.
 *
 * @param angle_deg  Servo angle in degrees (pre-clamped).
 * @return           PCA9685 off-tick value for setPin().
 */
static uint16_t servo_angle_to_ticks(uint8_t angle_deg);

/* ===========================================================================
 * Initialisation
 * =========================================================================*/

/**
 * @brief Initialise the PCA9685 driver and set PWM frequency.
 */
bool servo_init(void)
{
    s_pwm_driver.begin();

    /* Allow PCA9685 oscillator to stabilise */
    utils_delay_ms(PCA9685_INIT_DELAY_MS);

    s_pwm_driver.setPWMFreq(PWM_FREQUENCY_HZ);

    Serial.println(F("[servo] PCA9685 initialised at "
                     "address 0x" ));
    Serial.println(PCA9685_I2C_ADDRESS, HEX);

    /* Set all tracked channels to home angle as initial cache state */
    for (uint8_t ch = 0; ch < 16; ch++) {
        s_current_angles[ch] = HOME_ANGLE_BASE; /* safe default */
    }

    return true; /* Adafruit library does not return an error code */
}

/* ===========================================================================
 * Single Servo Control
 * =========================================================================*/

/**
 * @brief Write an angle to a single servo channel immediately.
 */
void servo_write_angle(uint8_t channel, uint8_t angle)
{
    /* Clamp to configured limits */
    uint8_t safe_angle = (uint8_t)utils_clamp_int(
        (int32_t)angle,
        (int32_t)SERVO_ANGLE_MIN_DEG,
        (int32_t)SERVO_ANGLE_MAX_DEG
    );

    uint16_t ticks = servo_angle_to_ticks(safe_angle);

    s_pwm_driver.setPWM(channel, PWM_PULSE_START_TICK, ticks);

    /* Update cache */
    s_current_angles[channel] = safe_angle;
}

/**
 * @brief Read the last-written angle for a servo channel.
 */
uint8_t servo_read_angle(uint8_t channel)
{
    if (channel >= 16) {
        return 0;
    }
    return s_current_angles[channel];
}

/* ===========================================================================
 * Smooth Motion
 * =========================================================================*/

/**
 * @brief Smoothly move a single servo from its current angle to a target angle.
 */
void servo_move_smooth(uint8_t channel, uint8_t target_angle)
{
    uint8_t start_angle = s_current_angles[channel];

    for (uint8_t step = 0; step <= SMOOTH_MOTION_STEPS; step++) {
        float t = (float)step / (float)SMOOTH_MOTION_STEPS;
        int32_t interpolated = utils_lerp_int((int32_t)start_angle,
                                              (int32_t)target_angle,
                                              t);
        servo_write_angle(channel, (uint8_t)interpolated);
        utils_delay_ms(SMOOTH_MOTION_STEP_DELAY_MS);
    }
}

/**
 * @brief Smoothly move all specified joints in parallel to a target pose.
 */
void servo_move_pose_smooth(const ServoPose_t *target_pose, uint8_t joint_count)
{
    if (target_pose == NULL || joint_count == 0) {
        return;
    }

    /* Capture start angles for all joints */
    uint8_t start_angles[16];
    for (uint8_t ch = 0; ch < joint_count; ch++) {
        start_angles[ch] = s_current_angles[ch];
    }

    /* Interpolate all joints simultaneously step by step */
    for (uint8_t step = 0; step <= SMOOTH_MOTION_STEPS; step++) {
        float t = (float)step / (float)SMOOTH_MOTION_STEPS;

        for (uint8_t ch = 0; ch < joint_count; ch++) {
            int32_t interpolated = utils_lerp_int((int32_t)start_angles[ch],
                                                  (int32_t)target_pose->angles[ch],
                                                  t);
            servo_write_angle(ch, (uint8_t)interpolated);
        }

        utils_delay_ms(SMOOTH_MOTION_STEP_DELAY_MS);
    }
}

/* ===========================================================================
 * Home Position
 * =========================================================================*/

/**
 * @brief Move all arm servos to their home positions defined in config.h.
 */
void servo_set_home(void)
{
    Serial.println(F("[servo] Moving to home position..."));

    servo_write_angle(SERVO_CHANNEL_BASE,     HOME_ANGLE_BASE);
    utils_delay_ms(HOME_SEQUENCE_DELAY_MS);

    servo_write_angle(SERVO_CHANNEL_SHOULDER, HOME_ANGLE_SHOULDER);
    utils_delay_ms(HOME_SEQUENCE_DELAY_MS);

    servo_write_angle(SERVO_CHANNEL_ELBOW,    HOME_ANGLE_ELBOW);
    utils_delay_ms(HOME_SEQUENCE_DELAY_MS);

    servo_write_angle(SERVO_CHANNEL_WRIST,    HOME_ANGLE_WRIST);
    utils_delay_ms(HOME_SEQUENCE_DELAY_MS);

    servo_write_angle(SERVO_CHANNEL_GRIPPER,  HOME_ANGLE_GRIPPER);
    utils_delay_ms(HOME_SEQUENCE_DELAY_MS);

    Serial.println(F("[servo] Home position reached."));
}

/* ===========================================================================
 * Private Helpers
 * =========================================================================*/

/**
 * @brief Convert a servo angle in degrees to a PCA9685 tick count.
 */
static uint16_t servo_angle_to_ticks(uint8_t angle_deg)
{
    /* Period in microseconds = 1,000,000 / frequency */
    float period_us = 1000000.0f / (float)PWM_FREQUENCY_HZ;

    /* Map angle → pulse width in µs */
    float pulse_us = utils_map_float((float)angle_deg,
                                     (float)SERVO_ANGLE_MIN_DEG,
                                     (float)SERVO_ANGLE_MAX_DEG,
                                     (float)SERVO_PULSE_MIN_US,
                                     (float)SERVO_PULSE_MAX_US);

    /* Map pulse width → tick count in the 4096-tick period */
    float ticks_f = (pulse_us / period_us) * (float)PCA9685_TICK_RESOLUTION;

    return (uint16_t)utils_clamp_float(ticks_f,
                                       0.0f,
                                       (float)(PCA9685_TICK_RESOLUTION - 1));
}
