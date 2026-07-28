/**
 * @file utils.c
 * @brief Implementation of general-purpose utility functions.
 *
 * @details
 * Provides mathematical helpers, value clamping, linear interpolation,
 * angle conversions, delay wrappers, and string helpers used across
 * all firmware modules. No hardware dependencies.
 *
 * @author   [Author Placeholder]
 * @version  1.0.0
 * @date     2026-07-28
 */

#include "utils.h"

#include <math.h>
#include <string.h>
#include <Arduino.h>  /* delay(), millis() */

/* ===========================================================================
 * Constants (private to this TU)
 * =========================================================================*/

/** @brief Pi constant used for degree/radian conversions */
static const float UTILS_PI = 3.14159265358979323846f;

/* ===========================================================================
 * Value Constraining
 * =========================================================================*/

/**
 * @brief Clamp an integer value between a minimum and maximum bound.
 */
int32_t utils_clamp_int(int32_t value, int32_t lo, int32_t hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

/**
 * @brief Clamp a floating-point value between a minimum and maximum bound.
 */
float utils_clamp_float(float value, float lo, float hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

/* ===========================================================================
 * Interpolation
 * =========================================================================*/

/**
 * @brief Linearly interpolate between two integer values.
 */
int32_t utils_lerp_int(int32_t start, int32_t end, float t)
{
    float t_clamped = utils_clamp_float(t, 0.0f, 1.0f);
    return (int32_t)((float)start + t_clamped * (float)(end - start));
}

/**
 * @brief Linearly interpolate between two floating-point values.
 */
float utils_lerp_float(float start, float end, float t)
{
    float t_clamped = utils_clamp_float(t, 0.0f, 1.0f);
    return start + t_clamped * (end - start);
}

/* ===========================================================================
 * Angle Conversion
 * =========================================================================*/

/**
 * @brief Convert degrees to radians.
 */
float utils_deg_to_rad(float degrees)
{
    return degrees * (UTILS_PI / 180.0f);
}

/**
 * @brief Convert radians to degrees.
 */
float utils_rad_to_deg(float radians)
{
    return radians * (180.0f / UTILS_PI);
}

/* ===========================================================================
 * Mapping
 * =========================================================================*/

/**
 * @brief Map a value from one numeric range to another.
 */
float utils_map_float(float value,
                      float in_min, float in_max,
                      float out_min, float out_max)
{
    /* Avoid division by zero if input range is degenerate */
    if ((in_max - in_min) == 0.0f) {
        return out_min;
    }
    return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min);
}

/* ===========================================================================
 * Delay Helpers
 * =========================================================================*/

/**
 * @brief Blocking delay for a given number of milliseconds.
 */
void utils_delay_ms(uint32_t ms)
{
    delay(ms);
}

/* ===========================================================================
 * String Helpers
 * =========================================================================*/

/**
 * @brief Strip trailing whitespace and line-ending characters from a C-string.
 */
void utils_trim_trailing(char *str)
{
    if (str == NULL) {
        return;
    }

    int32_t len = (int32_t)strlen(str);

    while (len > 0) {
        char last_char = str[len - 1];
        if (last_char == ' '  ||
            last_char == '\t' ||
            last_char == '\r' ||
            last_char == '\n') {
            str[len - 1] = '\0';
            len--;
        } else {
            break;
        }
    }
}
