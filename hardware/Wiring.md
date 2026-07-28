# Hardware Wiring

## Overview

This document describes the electrical connections between the ESP32, PCA9685 Servo Driver, USB Camera, Power Supply, and Servo Motors used in the AI-Based Biomedical Waste Segregation Robotic Arm.

---

# System Connections

The USB camera is connected directly to the host computer where the AI model performs object detection.

The ESP32 communicates with the computer through serial communication and receives the detected object information.

The ESP32 controls the PCA9685 servo driver using the I2C communication protocol.

The PCA9685 generates PWM signals to control all six servo motors.

---

# ESP32 to PCA9685 Connections

| ESP32 Pin | PCA9685 Pin | Description |
|-----------|-------------|-------------|
| 3.3V | VCC | Logic Power |
| GND | GND | Common Ground |
| GPIO 21 | SDA | I2C Data |
| GPIO 22 | SCL | I2C Clock |

---

# PCA9685 to Servo Motors

Each servo motor is connected to one PWM output channel.

| PWM Channel | Function |
|------------|----------|
| Channel 0 | Base Servo |
| Channel 1 | Shoulder Servo |
| Channel 2 | Elbow Servo |
| Channel 3 | Wrist Pitch |
| Channel 4 | Wrist Rotation |
| Channel 5 | Gripper Servo |

---

# Power Connections

### Servo Power

- External regulated DC power supply
- Connected directly to the PCA9685 servo power input

### ESP32 Power

- Powered independently through USB or regulated DC supply

### Common Ground

The ground of the ESP32, PCA9685, and external power supply must be connected together to ensure reliable communication.

---

# Camera Connection

The USB camera is connected directly to the host computer using a standard USB cable.

The AI application running on the computer continuously captures frames from the camera for object detection.

---

# Communication

| From | To | Protocol |
|------|----|----------|
| USB Camera | Computer | USB |
| Computer | ESP32 | Serial UART (USB) |
| ESP32 | PCA9685 | I2C |
| PCA9685 | Servo Motors | PWM |

---

# Safety Considerations

- Do not power servo motors directly from the ESP32.
- Ensure all grounds are connected together.
- Verify power supply polarity before powering the system.
- Use a regulated power supply capable of handling the total servo current.
- Secure all wiring before operating the robotic arm.

---

# Future Improvements

- Custom PCB for improved reliability
- Cable management system
- Power protection circuitry
- Emergency stop switch
- Current monitoring for each servo