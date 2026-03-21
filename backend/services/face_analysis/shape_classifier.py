import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# All possible face shape labels
FACE_SHAPES = ("oval", "round", "square", "heart", "oblong", "diamond")


def classify_face_shape(landmarks_data: Dict[str, Any]) -> str:
    """
    Classifies face shape from geometric ratios.

    Decision logic (in priority order):
    ─────────────────────────────────────────────────────────────────────────
    Oblong  : WHR < 0.65  (tall, narrow)
    Round   : WHR > 0.82  AND jaw ≈ cheeks      (wide + full)
    Heart   : forehead >> cheeks, jaw << cheeks  (broad top, narrow bottom)
    Diamond : forehead << cheeks AND jaw << cheeks (angular mid-face)
    Square  : jaw ≈ cheeks ≈ forehead, moderate WHR (uniform strong geometry)
    Oval    : default (balanced proportions)
    ─────────────────────────────────────────────────────────────────────────
    """
    m = landmarks_data.get("measurements", {})
    if not m:
        logger.warning("No measurements in landmark data — defaulting to oval")
        return "oval"

    whr = m.get("width_to_height_ratio", 0.75)
    jaw_cheek = m.get("jaw_to_cheek_ratio", 0.85)
    fore_cheek = m.get("forehead_to_cheek_ratio", 0.90)

    if whr < 0.65:
        return "oblong"

    if whr > 0.82 and jaw_cheek > 0.85:
        return "round"

    if fore_cheek > 0.95 and jaw_cheek < 0.75:
        return "heart"

    if fore_cheek < 0.80 and jaw_cheek < 0.80:
        return "diamond"

    if jaw_cheek > 0.88 and fore_cheek > 0.88 and 0.65 <= whr <= 0.82:
        return "square"

    return "oval"