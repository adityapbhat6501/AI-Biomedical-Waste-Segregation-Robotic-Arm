# Model — YOLO Weights and Training Scripts

This directory contains YOLO model weights and training/export utilities.

---

## Files

| File | Description |
|------|-------------|
| `best.pt` | Trained model weights (place here after training) |
| `yolov8n.pt` | Base pretrained weights (downloaded automatically by Ultralytics) |
| `train.py` | Training script |
| `detect.py` | Standalone detection test script |
| `export.py` | Model export to ONNX / TensorRT / etc. |
| `runs/` | Training output directory (auto-created) |

---

## Training

```bash
# 1. Prepare your dataset in dataset/images/ and dataset/labels/
# 2. Verify dataset/data.yaml class names match inference/classes.py

python model/train.py
```

The best weights are automatically copied to `model/best.pt`.

---

## Detection Test (No Serial Required)

```bash
# Single image
python model/detect.py --source path/to/image.jpg

# Folder of images
python model/detect.py --source dataset/images/val/

# Live ESP32-CAM stream
python model/detect.py --source stream
```

---

## Export

```bash
# ONNX (recommended for deployment)
python model/export.py --format onnx

# TensorRT (NVIDIA GPU)
python model/export.py --format engine

# TFLite (edge devices)
python model/export.py --format tflite
```

---

## Model Selection

Edit `config.py → MODEL_PATH` to switch between models.
The system automatically falls back to `yolov8n.pt` if `best.pt` is missing.

---

## Performance Targets

| Model    | mAP@50 Target | Inference (RTX 3060) |
|----------|---------------|----------------------|
| YOLOv8n  | 70%+          | ~8ms / frame         |
| YOLOv8s  | 75%+          | ~12ms / frame        |
| YOLOv8m  | 80%+          | ~20ms / frame        |
