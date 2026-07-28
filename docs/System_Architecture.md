# System Architecture

## Overview

The AI-Based Biomedical Waste Segregation Robotic Arm is an intelligent automation system designed to identify biomedical waste using computer vision and segregate it into the appropriate disposal bins using a 6-DOF robotic arm.

The system consists of three major subsystems:

- AI and Computer Vision
- Embedded Control System
- Mechanical Robotic Arm

Each subsystem communicates with the others to perform real-time waste detection, classification, and manipulation.

---

## System Workflow

1. The USB camera continuously captures images of biomedical waste.
2. The AI model processes each frame and identifies the waste category.
3. The detected object information is sent to the ESP32 controller.
4. The ESP32 calculates the required joint movements.
5. Servo motors move the robotic arm toward the object.
6. The robotic gripper picks the object.
7. The arm places the object into the appropriate waste bin.
8. The system returns to its home position and waits for the next object.

---

## Functional Architecture

Camera
    ↓
Computer Vision
    ↓
AI Object Detection
    ↓
ESP32 Controller
    ↓
Motion Planning
    ↓
Servo Driver
    ↓
Servo Motors
    ↓
6-DOF Robotic Arm
    ↓
Biomedical Waste Bin

---

## Major Subsystems

### Vision System

Responsible for acquiring images and detecting biomedical waste using AI-based object detection.

---

### Embedded Controller

Receives detection information, computes joint movements, and controls all servo motors.

---

### Motion Control

Generates smooth servo trajectories to move the robotic arm accurately.

---

### Robotic Manipulator

Performs pick-and-place operations based on commands received from the controller.

---

## Communication Flow

Camera
↓

Python AI Application
↓

ESP32 Serial Communication

↓

Servo Driver

↓

Servo Motors

---

## Future Enhancements

- IoT monitoring
- Cloud-based analytics
- Automatic calibration
- Conveyor belt integration
- Multi-object detection