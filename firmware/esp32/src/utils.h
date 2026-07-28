/**
 * @file utils.h
 * @brief Public API for general-purpose utility functions.
 *
 * @details
 * Provides mathematical helpers, value clamping, linear interpolation,
 * angle conversions, and delay wrappers used across all firmware modules.
 * No hardware dependencies — compiles and tests independently.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>

/* ===========================================================================
 * Value Constraining
 * =========================================================================*/

/**
 * @brief Clamp an integer value between a minimum and maximum bound.
 *
 * @param value  The input value to constrain.
 * @param lo     The lower bound (inclusive).
 * @param hi     The upper bound (inclusive).
 * @return       value clamped to [lo, hi].
 */
int32_t utils_clamp_int(int32_t value, int32_t lo, int32_t hi);

/**
 * @brief Clamp a floating-point value between a minimum and maximum bound.
 *
 * @param value  The input value to constrain.
 * @param lo     The lower bound (inclusive).
 * @param hi     The upper bound (inclusive).
 * @return       value clamped to [lo, hi].
 */
float utils_clamp_float(float value, float lo, float hi);

/* ===========================================================================
 * Interpolation
 * =========================================================================*/

/**
 * @brief Linearly interpolate between two integer values.
 *
 * @details
 * Returns the value at fractional position t between start and end,
 * where t = 0.0 returns start and t = 1.0 returns end.
 *
 * @param start  Starting value (t = 0.0).
 * @param end    Ending value   (t = 1.0).
 * @param t      Interpolation fraction in [0.0, 1.0].
 * @return       Interpolated integer value.
 */
int32_t utils_lerp_int(int32_t start, int32_t end, float t);

/**
 * @brief Linearly interpolate between two floating-point values.
 *
 * @param start  Starting value.
 * @param end    Ending value.
 * @param t      Interpolation fraction in [0.0, 1.0].
 * @return       Interpolated float value.
 */
float utils_lerp_float(float start, float end, float t);

/* ===========================================================================
 * Angle Conversion
 * =========================================================================*/

/**
 * @brief Convert an angle in degrees to radians.
 *
 * @param degrees  Angle in degrees.
 * @return         Equivalent angle in radians.
 */
float utils_deg_to_rad(float degrees);

/**
 * @brief Convert an angle in radians to degrees.
 *
 * @param radians  Angle in radians.
 * @return         Equivalent angle in degrees.
 */
float utils_rad_to_deg(float radians);

/* ===========================================================================
 * Mapping
 * =========================================================================*/

/**
 * @brief Map a value from one numeric range to another.
 *
 * @details
 * Equivalent to Arduino's map() but using floating-point arithmetic for
 * accuracy. The output is NOT clamped — call utils_clamp_float() if needed.
 *
 * @param value     Input value within [in_min, in_max].
 * @param in_min    Minimum of the input range.
 * @param in_max    Maximum of the input range.
 * @param out_min   Minimum of the output range.
 * @param out_max   Maximum of the output range.
 * @return          Mapped value in the output range.
 */
float utils_map_float(float value,
                      float in_min, float in_max,
                      float out_min, float out_max);

/* ===========================================================================
 * Delay Helpers
 * =========================================================================*/

/**
 * @brief Blocking delay for a given number of milliseconds.
 *
 * @details
 * Wraps Arduino delay() to centralise timing calls and simplify
 * future porting to an RTOS (vTaskDelay) or bare-metal timer.
 *
 * @param ms  Number of milliseconds to delay.
 */
void utils_delay_ms(uint32_t ms);

/* ===========================================================================
 * String Helpers
 * =========================================================================*/

/**
 * @brief Strip trailing whitespace (spaces, \\r, \\n) from a C-string in place.
 *
 * @param str  Pointer to the null-terminated string to trim.
 */
void utils_trim_trailing(char *str);

#endif /* UTILS_H */
