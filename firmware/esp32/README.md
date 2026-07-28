# AI-Based Biomedical Waste Segregation — ESP32 Robotic Arm Firmware

Modular Embedded C firmware for an ESP32-controlled 5-DOF robotic arm that
segregates biomedical waste into colour-coded bins based on commands received
from a laptop AI system over UART.

---

## System Architecture

```
ESP32-CAM  →  Laptop (Python + OpenCV + AI Model)  →  USB Serial (UART)
           →  ESP32 Controller  →  PCA9685 Servo Driver  →  5 Servo Motors
```

The ESP32 controller performs **no AI inference**. It is a pure motion
controller that executes pre-defined coordinated arm sequences in response
to plain-text commands.

---

## Hardware Requirements

| Component          | Details                                      |
|--------------------|----------------------------------------------|
| Microcontroller    | ESP32 Dev Module                             |
| Camera             | ESP32-CAM (separate module, image streaming) |
| Servo Driver       | PCA9685 16-channel PWM driver (I2C)          |
| Servos             | 5× standard hobby servo (SG90 / MG996R)      |
| Communication      | USB Serial / UART at 115200 baud             |

### Pin Connections

| Signal | GPIO |
|--------|------|
| I2C SDA | GPIO 21 |
| I2C SCL | GPIO 22 |

### Servo Channel Map (PCA9685)

| Channel | Joint           |
|---------|-----------------|
| 0       | Base Rotation   |
| 1       | Shoulder        |
| 2       | Elbow           |
| 3       | Wrist           |
| 4       | Gripper         |

---

## Required Libraries

Install via **Arduino IDE → Library Manager**:

1. **Adafruit PWM Servo Driver Library** (search: `Adafruit PCA9685`)
2. **Wire** (built-in with ESP32 Arduino core)

### Arduino IDE Board Setup

- Board: `ESP32 Dev Module`
- Upload Speed: `115200` or `921600`
- Flash Frequency: `80 MHz`

---

## Folder Structure

```
firmware/
└── esp32/
    ├── src/
    │   ├── main.c            ← Entry point, system coordinator
    │   ├── config.h          ← ALL hardware constants (edit here for calibration)
    │   ├── communication.c   ← UART command reception & parsing
    │   ├── communication.h
    │   ├── servo.c           ← PCA9685 PWM driver abstraction
    │   ├── servo.h
    │   ├── arm_control.c     ← High-level motion sequences
    │   ├── arm_control.h
    │   ├── gripper.c         ← Gripper open/close operations
    │   ├── gripper.h
    │   ├── kinematics.c      ← FK/IK placeholder (future implementation)
    │   ├── kinematics.h
    │   ├── utils.c           ← Math helpers, clamp, lerp, angle conversion
    │   └── utils.h
    ├── include/              ← Third-party / shared headers
    └── lib/                  ← Private project libraries (PlatformIO-compatible)
```

---

## UART Command Protocol

The laptop sends plain-text commands terminated with a newline (`\n`).

| Command       | Action                                      |
|---------------|---------------------------------------------|
| `HOME`        | Return arm to home (resting) position       |
| `PICK`        | Execute pick-up sequence at pick zone       |
| `DROP_RED`    | Drop object into red (infectious) bin       |
| `DROP_YELLOW` | Drop object into yellow (chemical) bin      |
| `DROP_BLUE`   | Drop object into blue (sharps/recycl.) bin  |
| `STOP`        | Abort current motion, return to home        |
| `STATUS`      | Report current arm state over Serial        |
| `DEMO`        | Run full demonstration / calibration sweep  |

### Status Responses

The firmware replies with one of:

| Response               | Meaning                     |
|------------------------|-----------------------------|
| `STATUS:READY`         | Idle, waiting for commands  |
| `STATUS:BUSY`          | Motion in progress          |
| `STATUS:DONE`          | Motion completed            |
| `STATUS:STOPPED`       | Arm halted by STOP command  |
| `STATUS:UNKNOWN_CMD`   | Unrecognised command        |

---

## Typical Operation Sequence

```
Boot → HOME → Wait for UART
→ PICK              (arm picks up waste item)
→ DROP_RED          (drops into red bin)
→ [arm auto-returns to HOME]
→ Wait for next command
```

---

## Calibration

All angles are defined in [`src/config.h`](src/config.h). Adjust the following
constants to match your physical hardware:

| Constant                  | Purpose                                   |
|---------------------------|-------------------------------------------|
| `HOME_ANGLE_*`            | Resting position for each joint           |
| `PICK_ANGLE_*`            | Approach angles for pick-up zone          |
| `DROP_ZONE_*_BASE_DEG`    | Base rotation angles for each waste bin   |
| `GRIPPER_ANGLE_OPEN/CLOSED` | Gripper servo angles for open/close     |
| `SERVO_PULSE_MIN/MAX_US`  | Pulse widths — adjust for your servos     |
| `SMOOTH_MOTION_STEPS`     | Higher = smoother but slower movement     |
| `SMOOTH_MOTION_STEP_DELAY_MS` | Delay between interpolation steps    |

---

## Module Architecture

```
main.c
  │
  ├── communication.c   (UART RX, command parsing)
  ├── arm_control.c     (motion sequences)
  │     ├── servo.c     (PCA9685 angle → PWM)
  │     │     └── utils.c (math helpers)
  │     └── gripper.c   (open/close)
  └── kinematics.c      (FK/IK — placeholder)
```

**Strict dependency rule:** Higher layers must not bypass lower layers.
`arm_control` → `servo` → `PCA9685`. Never directly.

---

## Future Work

- **Inverse Kinematics**: Implement geometric IK in `kinematics.c` using
  DH parameters and `atan2()` / law of cosines for the 5-DOF chain.
- **RTOS Integration**: Replace `delay()` calls with `vTaskDelay()` for
  preemptive multitasking and concurrent UART monitoring during motion.
- **Velocity Profiling**: Replace linear interpolation with trapezoidal or
  S-curve velocity profiles in `servo_move_smooth()` for smoother acceleration.
- **Torque Feedback**: Add current sensing on servo power rails to detect
  collisions and overloads.

---

## Author

[Author Placeholder]  
Project: AI-Based Biomedical Waste Segregation Robotic Arm  
Firmware Version: 1.0.0
