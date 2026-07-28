# AI Module — Biomedical Waste Segregation Robotic Arm

Python-based AI application that captures live video from an ESP32-CAM,
detects and classifies biomedical waste objects using YOLOv8, and sends
classification commands to an ESP32 robotic arm controller over UART.

---

## System Architecture

```
ESP32-CAM → MJPEG Stream → Python AI App
                                │
                         YOLOv8 Inference
                                │
                         Post-Processing
                         (confidence + stability + cooldown)
                                │
                         UART Command (DROP_RED / DROP_YELLOW / DROP_BLUE ...)
                                │
                         ESP32 Controller → Robotic Arm
```

---

## Folder Structure

```
ai/
├── main.py                    ← Application entry point
├── config.py                  ← All configuration constants
├── requirements.txt
│
├── camera/
│   ├── esp32cam.py            ← ESP32-CAM MJPEG stream manager
│   └── camera_utils.py        ← Frame preprocessing utilities
│
├── communication/
│   ├── protocol.py            ← UART command/response enums
│   └── serial_comm.py         ← PySerial manager with auto-reconnect
│
├── inference/
│   ├── classes.py             ← Waste class registry & command mapping
│   ├── predictor.py           ← YOLO model loading & inference
│   └── postprocess.py         ← Confidence, stability & cooldown filtering
│
├── utils/
│   ├── drawing.py             ← OpenCV overlay rendering
│   ├── logger.py              ← Rotating file + coloured console logger
│   └── helpers.py             ← FPS counter, clamp, timestamp, debounce
│
├── model/
│   ├── train.py               ← YOLOv8 training script
│   ├── detect.py              ← Standalone detection test
│   ├── export.py              ← ONNX / TensorRT export
│   ├── best.pt                ← Trained weights (place here)
│   └── yolov8n.pt             ← Base pretrained weights
│
├── dataset/
│   ├── data.yaml              ← YOLO dataset config
│   ├── images/train/ val/     ← Training images
│   └── labels/train/ val/     ← YOLO label files
│
└── tests/
    ├── test_camera.py
    ├── test_serial.py
    └── test_model.py
```

---

## Installation

```bash
# 1. Clone the repository and navigate to the ai/ directory
cd ai/

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

### 1. Configure the System

Edit `config.py`:

```python
CAMERA_URL   = "http://192.168.1.100:81/stream"  # Your ESP32-CAM IP
SERIAL_PORT  = "COM3"                              # Your ESP32 serial port
```

Enable debug mode to run without hardware:

```bash
set DEBUG_MODE=true          # Windows
set DEBUG_USE_WEBCAM=true    # Use laptop webcam instead of ESP32-CAM
```

### 2. Place a Trained Model

Copy your trained `best.pt` to `model/best.pt`.
If no model exists, `yolov8n.pt` is used as a fallback (base pretrained).

### 3. Run the Application

```bash
python main.py
```

Press **Q** in the display window or **Ctrl+C** in the terminal to exit.

---

## UART Command Protocol

| Detected Category | UART Command   |
|-------------------|----------------|
| Red Waste         | `DROP_RED`     |
| Yellow Waste      | `DROP_YELLOW`  |
| Blue Waste        | `DROP_BLUE`    |
| White Waste       | `DROP_WHITE`   |
| Black Waste       | `DROP_BLACK`   |

The command is sent only after:
1. Detection confidence ≥ `COMMAND_CONFIDENCE_THRESHOLD` (default: 60%)
2. Same class detected for `COMMAND_STABILITY_FRAMES` consecutive frames (default: 3)
3. `COMMAND_COOLDOWN_S` seconds have elapsed since the last command (default: 5s)

---

## Training a Custom Model

```bash
# Place annotated images in dataset/images/train/ and /val/
# Place YOLO labels in dataset/labels/train/ and /val/
# Verify dataset/data.yaml class names

python model/train.py
```

See [`dataset/README.md`](dataset/README.md) and [`model/README.md`](model/README.md)
for detailed instructions.

---

## Testing

```bash
# Run all tests (no hardware required)
python -m pytest tests/ -v

# Test individual modules
python -m pytest tests/test_camera.py -v
python -m pytest tests/test_serial.py -v
python -m pytest tests/test_model.py -v
```

---

## Detection Test (Offline)

```bash
# Single image
python model/detect.py --source path/to/image.jpg

# Live ESP32-CAM stream (no serial, display only)
python model/detect.py --source stream
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera connection fails | Check ESP32-CAM IP in `config.py`; ensure camera is on same network |
| Serial port not found | Check `SERIAL_PORT` in `config.py`; verify drivers installed |
| Model not found | Place `best.pt` in `model/` or train first |
| Low FPS | Reduce `FRAME_WIDTH/HEIGHT` or `MODEL_INPUT_SIZE` in `config.py` |
| Spurious commands | Increase `COMMAND_STABILITY_FRAMES` or `COMMAND_CONFIDENCE_THRESHOLD` |

---

## Future Improvements

- **Pick command integration**: Send `PICK` before each `DROP_*` after detecting stable object.
- **Multi-object tracking**: Handle scenes with multiple waste items simultaneously.
- **TensorRT export**: Use `model/export.py` for 3–4× faster inference on NVIDIA GPUs.
- **REST API**: Expose detection results over HTTP for integration with dashboards.
- **Dataset expansion**: Collect 500+ images per class for production-grade accuracy.

---

## Author

[Author Placeholder]
Project: AI-Based Biomedical Waste Segregation Robotic Arm
AI Module Version: 1.0.0
