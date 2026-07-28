# System Flowchart

The following flow represents the complete operation of the biomedical waste segregation system.

```

Start

↓

Initialize System

↓

Initialize Camera

↓

Initialize ESP32

↓

Initialize Servo Driver

↓

Move Robotic Arm to Home Position

↓

Capture Image

↓

Process Image using AI

↓

Object Detected?

├── No
│
└── Capture Next Frame

↓

Yes

↓

Classify Biomedical Waste

↓

Send Detection Data to ESP32

↓

Calculate Arm Movement

↓

Move Robotic Arm

↓

Close Gripper

↓

Pick Object

↓

Move to Target Bin

↓

Open Gripper

↓

Release Object

↓

Return to Home Position

↓

Repeat Process
