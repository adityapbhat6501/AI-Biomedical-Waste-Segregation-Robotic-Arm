# Hardware Components

## Overview

This document provides an overview of all major hardware components used in the AI-Based Biomedical Waste Segregation Robotic Arm. Each component has been selected based on performance, compatibility, reliability, and ease of integration.

---

# Main Controller

## ESP32 Development Board

### Purpose

Acts as the primary embedded controller responsible for coordinating the robotic arm, processing commands received from the AI application, and controlling all servo motors.

### Features

- Dual-core microcontroller
- Wi-Fi and Bluetooth support
- Multiple GPIO pins
- PWM support
- UART, SPI and I2C communication

---

# Vision System

## USB Camera

### Purpose

Captures real-time images of biomedical waste for AI-based object detection and classification.

### Features

- Live video streaming
- High-resolution image capture
- USB interface
- Compatible with OpenCV

---

# Servo Driver

## PCA9685 16-Channel PWM Driver

### Purpose

Generates accurate PWM signals required to control multiple servo motors simultaneously.

### Features

- 16 independent PWM channels
- I2C communication
- 12-bit PWM resolution
- Reduces processing load on the ESP32

---

# Servo Motors

The robotic arm uses six servo motors to provide six degrees of freedom.

| Joint | Purpose |
|--------|---------|
| Base | Rotates the robotic arm |
| Shoulder | Lifts the arm |
| Elbow | Extends and retracts the arm |
| Wrist Pitch | Controls wrist angle |
| Wrist Rotation | Rotates the end effector |
| Gripper | Opens and closes the gripper |

---

# Mechanical Structure

The robotic arm structure is designed using Fusion 360 and fabricated using lightweight materials to achieve stability while minimizing overall weight.

---

# Power Supply

The robotic arm is powered using an external regulated DC power supply capable of delivering sufficient current for all servo motors.

The ESP32 receives a dedicated regulated supply to ensure stable operation during high-current servo movements.

---

# Software Tools

- Arduino IDE
- Visual Studio Code
- Git
- GitHub

---

# CAD and PCB Design Tools

- Fusion 360
- KiCad

---

# Future Hardware Upgrades

- Custom PCB
- Higher precision servo motors
- Force feedback sensors
- Battery backup
- Emergency stop circuit
- Wireless monitoring