# Project Overview

## Introduction

Biomedical waste generated in hospitals and healthcare facilities must be handled carefully to prevent the spread of infections and protect both healthcare workers and the environment. Traditional manual segregation methods expose personnel to hazardous materials and increase the possibility of incorrect waste disposal.

This project proposes an intelligent robotic system capable of automatically identifying, classifying, and segregating biomedical waste using Artificial Intelligence, Computer Vision, and Embedded Systems.

The system integrates a 6-DOF robotic arm with an AI-based object detection model to perform automated pick-and-place operations. Once an object is detected, the embedded controller computes the required arm movement and places the waste into the appropriate disposal container.

---

## Problem Statement

Manual biomedical waste segregation is time-consuming, inconsistent, and potentially hazardous. Human intervention increases the risk of contamination, infection, and improper waste disposal.

An automated segregation system can improve workplace safety, increase sorting accuracy, and reduce direct human exposure to hazardous waste.

---

## Proposed Solution

The proposed solution combines Artificial Intelligence, Computer Vision, Robotics, and Embedded Systems to automate the biomedical waste segregation process.

The system captures live images using a USB camera, identifies biomedical waste using an AI model, and controls a 6-DOF robotic arm through an ESP32 microcontroller to perform accurate pick-and-place operations.

---

## Objectives

- Automate biomedical waste segregation.
- Reduce human exposure to hazardous materials.
- Improve waste classification accuracy.
- Develop a reliable robotic manipulation system.
- Integrate AI with embedded hardware.
- Build a scalable and modular automation platform.

---

## Technologies Used

### Software

- Embedded C
- Python
- OpenCV
- Arduino IDE
- Visual Studio Code
- Git & GitHub

### Hardware

- ESP32
- PCA9685 Servo Driver
- Servo Motors
- USB Camera
- External Power Supply

### Design Tools

- KiCad
- Fusion 360

---

## Expected Outcome

The final system will automatically detect biomedical waste, classify it using Artificial Intelligence, and accurately place it into the appropriate disposal container using a robotic arm with minimal human intervention.

The project aims to demonstrate the practical integration of AI, Robotics, and Embedded Systems for real-world healthcare automation.