/**
 * @file main.c
 * @brief Entry point and system coordinator for the ESP32 Robotic Arm Firmware.
 *
 * @details
 * This file contains only high-level system initialisation and the main
 * control loop. It contains NO robotic logic, PWM generation, or
 * communication parsing — those responsibilities belong to the respective
 * modules.
 *
 * Startup Sequence:
 *  1. Initialize Serial (UART)
 *  2. Initialize I2C (Wire)
 *  3. Initialize PCA9685 via servo_init()
 *  4. Initialize arm_control module
 *  5. Initialize communication module
 *  6. Move arm to Home Position
 *  7. Enter main control loop
 *
 * Main Loop:
 *  - Poll communication_available() for incoming UART commands
 *  - On receipt, call arm_control_dispatch() to execute the sequence
 *  - Short delay between polls to yield CPU
 *
 * Hardware Configuration:
 *  - All pin and peripheral settings are in config.h
 *  - No magic numbers in this file
 *
 * Required Libraries (install via Arduino Library Manager):
 *  - Adafruit PWM Servo Driver Library (Adafruit PCA9685)
 *  - Wire (built-in ESP32 Arduino core)
 *
 * Board:
 *  - Arduino IDE: Tools → Board → ESP32 Dev Module
 *  - Upload Speed: 115200 or 921600
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include <Arduino.h>
#include <Wire.h>

#include "config.h"
#include "communication.h"
#include "servo.h"
#include "arm_control.h"
#include "utils.h"

/* ===========================================================================
 * Arduino setup() — Runs Once at Power-On / Reset
 * =========================================================================*/

/**
 * @brief System initialisation — called once by the Arduino runtime.
 *
 * @details
 * Brings up all hardware peripherals and firmware modules in dependency order:
 *  Serial → I2C → PCA9685 → Modules → Home Position.
 */
void setup(void)
{
    /* -----------------------------------------------------------------------
     * Step 1: Initialise UART communication
     * Serial.begin() is called inside communication_init(), which also
     * prints the firmware banner and STATUS:READY.
     * --------------------------------------------------------------------- */
    communication_init();

    /* -----------------------------------------------------------------------
     * Step 2: Initialise I2C bus for PCA9685
     * SDA and SCL pin numbers are defined in config.h.
     * --------------------------------------------------------------------- */
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    Serial.println(F("[main] I2C initialised."));

    /* -----------------------------------------------------------------------
     * Step 3: Initialise PCA9685 servo driver
     * --------------------------------------------------------------------- */
    bool servo_ok = servo_init();
    if (!servo_ok) {
        /* PCA9685 not found — indicate hardware fault and halt */
        Serial.println(F("[main] FATAL: PCA9685 not found. Check I2C wiring."));
        Serial.println(F("[main] Halting."));
        while (true) {
            utils_delay_ms(1000);
        }
    }
    Serial.println(F("[main] Servo driver initialised."));

    /* -----------------------------------------------------------------------
     * Step 4: Initialise arm control module state
     * --------------------------------------------------------------------- */
    arm_control_init();
    Serial.println(F("[main] Arm control module initialised."));

    /* -----------------------------------------------------------------------
     * Step 5: Move robotic arm to home (safe resting) position
     * --------------------------------------------------------------------- */
    Serial.println(F("[main] Moving arm to home position..."));
    arm_home();
    Serial.println(F("[main] System ready. Awaiting commands."));
}

/* ===========================================================================
 * Arduino loop() — Main Control Loop (runs continuously)
 * =========================================================================*/

/**
 * @brief Main control loop — polls for UART commands and dispatches motion.
 *
 * @details
 * Each iteration:
 *  1. Check if a complete UART command has been received.
 *  2. If so, read and parse the command via communication_read().
 *  3. Dispatch the parsed CommandId_t to arm_control_dispatch().
 *  4. Delay MAIN_LOOP_DELAY_MS to yield CPU between polls.
 *
 * The loop intentionally contains no motion logic.
 */
void loop(void)
{
    /* Check for a complete incoming UART command (non-blocking) */
    if (communication_available()) {
        CommandId_t received_command = communication_read();
        arm_control_dispatch(received_command);
    }

    /* Short yield delay between UART polls */
    utils_delay_ms(MAIN_LOOP_DELAY_MS);
}
