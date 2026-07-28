# Dataset — Biomedical Waste Segregation

This directory contains the YOLO-format dataset for training the
biomedical waste object detection model.

---

## Directory Structure

```
dataset/
├── data.yaml              ← YOLO dataset configuration
├── images/
│   ├── train/             ← Training images (.jpg / .png)
│   └── val/               ← Validation images
└── labels/
    ├── train/             ← YOLO label files (.txt)
    └── val/               ← Validation labels
```

---

## Label File Format (YOLO)

Each `.txt` file corresponds to one image file and contains one detection per line:

```
<class_id> <x_center> <y_center> <width> <height>
```

- All coordinates are **normalised** to [0.0, 1.0] relative to image dimensions.
- `class_id` is the integer index from `data.yaml → names`.

**Example** (syringe detected in an image):
```
7 0.512 0.438 0.124 0.213
```

---

## Waste Classes

| ID | Label                 | Category       |
|----|-----------------------|----------------|
|  0 | used_glove            | Red Waste      |
|  1 | blood_soaked_bandage  | Red Waste      |
|  2 | culture_dish          | Red Waste      |
|  3 | contaminated_swab     | Red Waste      |
|  4 | chemical_container    | Yellow Waste   |
|  5 | pathological_sample   | Yellow Waste   |
|  6 | expired_medicine      | Yellow Waste   |
|  7 | syringe               | Blue Waste     |
|  8 | needle                | Blue Waste     |
|  9 | scalpel               | Blue Waste     |
| 10 | broken_glass          | Blue Waste     |
| 11 | ampoule               | Blue Waste     |
| 12 | plastic_wrapper       | White Waste    |
| 13 | sterile_packaging     | White Waste    |
| 14 | iv_bag_empty          | White Waste    |
| 15 | paper_waste           | Black Waste    |
| 16 | food_wrapper          | Black Waste    |

---

## Recommended Data Collection

- Minimum **200 images per class** for reasonable accuracy.
- Vary **lighting conditions**, **backgrounds**, and **orientations**.
- Use **Roboflow** or **LabelImg** for annotation.
- Apply **augmentation** (flip, rotate, brightness) to expand dataset size.

---

## Annotation Tools

- [Roboflow](https://roboflow.com) — cloud-based, exports YOLO format directly
- [LabelImg](https://github.com/heartexlabs/labelImg) — desktop, YOLO format
- [CVAT](https://www.cvat.ai) — advanced annotation platform

---

## Adding New Classes

1. Add the new class to `data.yaml` under `names`.
2. Add a corresponding `WasteClass` entry in `inference/classes.py`.
3. Re-annotate dataset images with the new class.
4. Retrain the model: `python model/train.py`
