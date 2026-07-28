"""
classes.py — Waste Category Class Definitions and Command Mapping.

Defines all detectable waste object classes, their parent waste categories,
and the corresponding UART command sent to the ESP32 robotic arm controller.

To add a new waste class:
    1. Add an entry to WASTE_CLASS_MAP below.
    2. Ensure the class name matches the YOLO label in data.yaml.
    3. The correct DROP command will be sent automatically.

Author: [Author Placeholder]
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WasteCategory:
    """
    Represents a high-level waste disposal category.

    Attributes:
        name:        Human-readable category name (e.g. "Red Waste").
        command:     UART command string sent to the ESP32 (e.g. "DROP_RED").
        color_bgr:   BGR colour tuple used for bounding box rendering.
        description: Short description of what this category contains.
    """
    name: str
    command: str
    color_bgr: Tuple[int, int, int]
    description: str


@dataclass(frozen=True)
class WasteClass:
    """
    Represents an individual detectable waste object class.

    Attributes:
        label:    YOLO class label string (must match data.yaml exactly).
        category: The parent WasteCategory this object belongs to.
    """
    label: str
    category: WasteCategory


# ---------------------------------------------------------------------------
# Waste Category Definitions
# ---------------------------------------------------------------------------

CATEGORY_RED = WasteCategory(
    name="Red Waste",
    command="DROP_RED",
    color_bgr=(0, 0, 220),
    description="Infectious waste — used gloves, blood-soaked items, culture dishes.",
)

CATEGORY_YELLOW = WasteCategory(
    name="Yellow Waste",
    command="DROP_YELLOW",
    color_bgr=(0, 200, 255),
    description="Chemical / pathological waste — anatomical parts, chemical containers.",
)

CATEGORY_BLUE = WasteCategory(
    name="Blue Waste",
    command="DROP_BLUE",
    color_bgr=(220, 80, 0),
    description="Sharps / glass — syringes, needles, scalpel blades, broken glass.",
)

CATEGORY_WHITE = WasteCategory(
    name="White Waste",
    command="DROP_WHITE",
    color_bgr=(220, 220, 220),
    description="Recyclable / general — uncontaminated plastic wrappers, packaging.",
)

CATEGORY_BLACK = WasteCategory(
    name="Black Waste",
    command="DROP_BLACK",
    color_bgr=(40, 40, 40),
    description="General waste — non-infectious, non-recyclable municipal waste.",
)

# ---------------------------------------------------------------------------
# Waste Class Registry
# ---------------------------------------------------------------------------
# Maps YOLO label strings → WasteClass instances.
# Add or remove entries to match the classes in your dataset/data.yaml.

WASTE_CLASS_MAP: Dict[str, WasteClass] = {
    # ── Red Waste ──────────────────────────────────────────────────────────
    "used_glove":          WasteClass(label="used_glove",          category=CATEGORY_RED),
    "blood_soaked_bandage":WasteClass(label="blood_soaked_bandage",category=CATEGORY_RED),
    "culture_dish":        WasteClass(label="culture_dish",        category=CATEGORY_RED),
    "contaminated_swab":   WasteClass(label="contaminated_swab",   category=CATEGORY_RED),

    # ── Yellow Waste ───────────────────────────────────────────────────────
    "chemical_container":  WasteClass(label="chemical_container",  category=CATEGORY_YELLOW),
    "pathological_sample": WasteClass(label="pathological_sample", category=CATEGORY_YELLOW),
    "expired_medicine":    WasteClass(label="expired_medicine",    category=CATEGORY_YELLOW),

    # ── Blue Waste (Sharps) ────────────────────────────────────────────────
    "syringe":             WasteClass(label="syringe",             category=CATEGORY_BLUE),
    "needle":              WasteClass(label="needle",              category=CATEGORY_BLUE),
    "scalpel":             WasteClass(label="scalpel",             category=CATEGORY_BLUE),
    "broken_glass":        WasteClass(label="broken_glass",        category=CATEGORY_BLUE),
    "ampoule":             WasteClass(label="ampoule",             category=CATEGORY_BLUE),

    # ── White Waste (Recyclable) ───────────────────────────────────────────
    "plastic_wrapper":     WasteClass(label="plastic_wrapper",     category=CATEGORY_WHITE),
    "sterile_packaging":   WasteClass(label="sterile_packaging",   category=CATEGORY_WHITE),
    "iv_bag_empty":        WasteClass(label="iv_bag_empty",        category=CATEGORY_WHITE),

    # ── Black Waste (General) ──────────────────────────────────────────────
    "paper_waste":         WasteClass(label="paper_waste",         category=CATEGORY_BLACK),
    "food_wrapper":        WasteClass(label="food_wrapper",        category=CATEGORY_BLACK),
    "general_trash":       WasteClass(label="general_trash",       category=CATEGORY_BLACK),
}

# Ordered list of class labels matching the integer index in data.yaml.
# The position in this list must match the class id in YOLO labels.
CLASS_NAMES: list[str] = list(WASTE_CLASS_MAP.keys())


# ---------------------------------------------------------------------------
# Lookup Helpers
# ---------------------------------------------------------------------------

def get_waste_class(label: str) -> Optional[WasteClass]:
    """
    Retrieve a WasteClass by its YOLO label string.

    Args:
        label: The YOLO class label (e.g. "syringe").

    Returns:
        Matching WasteClass, or None if the label is not registered.
    """
    return WASTE_CLASS_MAP.get(label)


def get_command_for_label(label: str) -> Optional[str]:
    """
    Get the UART command string for a detected object label.

    Args:
        label: The YOLO class label string.

    Returns:
        Command string (e.g. "DROP_BLUE"), or None if not found.
    """
    waste_class = get_waste_class(label)
    if waste_class is not None:
        return waste_class.category.command
    return None


def get_color_for_label(label: str) -> Tuple[int, int, int]:
    """
    Get the BGR bounding-box colour for a detected object label.

    Args:
        label: The YOLO class label string.

    Returns:
        BGR colour tuple, or white (255, 255, 255) if label is unknown.
    """
    waste_class = get_waste_class(label)
    if waste_class is not None:
        return waste_class.category.color_bgr
    return (255, 255, 255)


def get_category_name_for_label(label: str) -> str:
    """
    Get the human-readable waste category name for a label.

    Args:
        label: The YOLO class label string.

    Returns:
        Category name string, or "Unknown" if the label is not registered.
    """
    waste_class = get_waste_class(label)
    if waste_class is not None:
        return waste_class.category.name
    return "Unknown"


def get_all_categories() -> list[WasteCategory]:
    """
    Return a deduplicated list of all registered WasteCategory objects.

    Returns:
        List of unique WasteCategory instances.
    """
    seen: set[str] = set()
    categories: list[WasteCategory] = []
    for wc in WASTE_CLASS_MAP.values():
        if wc.category.name not in seen:
            seen.add(wc.category.name)
            categories.append(wc.category)
    return categories
