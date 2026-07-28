# Software Architecture

## Overview

The software architecture follows a modular design to simplify development, testing, debugging, and future expansion.

Each module performs a specific task while communicating with other modules through well-defined interfaces.

---

## Software Modules

### AI Detection Module

Responsibilities:

- Capture camera frames
- Detect biomedical waste
- Classify waste category
- Send detection results to ESP32

---

### Communication Module

Responsibilities:

- Serial communication
- Data validation
- Error handling

---

### Motion Planning Module

Responsibilities:

- Calculate joint angles
- Generate movement sequence
- Avoid unnecessary motion

---

### Servo Control Module

Responsibilities:

- Generate PWM signals
- Move each joint
- Control gripper

---

### System Controller

Coordinates all software modules.

Responsibilities:

- Receive commands
- Execute pick-and-place sequence
- Monitor system state
- Handle errors

---

## Software Flow

Camera Input
↓

AI Detection

↓

Object Classification

↓

ESP32 Communication

↓

Motion Planning

↓

Servo Control

↓

Pick Object

↓

Place Object

↓

Return Home

---

## Programming Languages

Embedded Firmware

- Embedded C

AI Application

- Python

---

## Development Tools

- Visual Studio Code
- Arduino IDE
- Git
- GitHub

---

## Design Principles

- Modular programming
- Readable code
- Reusable functions
- Low coupling
- High cohesion
- Easy debugging