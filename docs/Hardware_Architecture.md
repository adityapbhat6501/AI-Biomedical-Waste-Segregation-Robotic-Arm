# Hardware Architecture

## Overview

The hardware architecture consists of the robotic manipulator, embedded controller, camera system, power distribution, and actuator control modules.

Each hardware component is selected to ensure reliable operation, modularity, and ease of maintenance.

---

## Hardware Components

### Microcontroller

ESP32

Responsibilities:

- Servo control
- Motion planning
- Communication with AI application
- Peripheral interfacing

---

### Camera

USB Camera

Responsibilities:

- Capture live images
- Send image stream to the AI model

---

### Servo Driver

PCA9685

Responsibilities:

- Generate PWM signals
- Drive multiple servo motors simultaneously

---

### Servo Motors

High torque servo motors are used to control all six degrees of freedom of the robotic arm.

Responsibilities:

- Base rotation
- Shoulder movement
- Elbow movement
- Wrist movement
- Wrist rotation
- Gripper control

---

### Power Supply

The robotic arm is powered using an external regulated DC power supply capable of supplying sufficient current for all servo motors.

The ESP32 is powered separately to ensure stable operation.

---

## Hardware Block Diagram

Power Supply
     │
     ├───────────────┐
     │               │
     ▼               ▼
ESP32          PCA9685 Driver
     │               │
     └──────┬────────┘
            │
            ▼
      Servo Motors
            │
            ▼
      Robotic Arm

USB Camera
      │
      ▼
Computer

---

## Design Considerations

- Modular hardware design
- Independent power supply for logic and actuators
- Expandable architecture
- Low-cost implementation
- Easy maintenance

---

## Future Improvements

- Custom PCB
- Current monitoring
- Emergency stop system
- Battery backup
- Wireless communication