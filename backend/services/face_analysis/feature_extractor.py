import logging
from typing import Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

_IDX = {
    "jaw_left": 172,
    "jaw_right": 397,
    "forehead_left": 67,
    "forehead_right": 297,
    "cheek_left": 234,
    "cheek_right": 454,
    "face_top": 10,
    "face_bottom": 152,
}


def _pt(lms: list, key: str) -> np.ndarray:
    lm = lms[_IDX[key]]
    return np.array([lm["x"], lm["y"]])


def _dist(lms: list, a: str, b: str) -> float:
    return float(np.linalg.norm(_pt(lms, a) - _pt(lms, b)))


def _jawline_label(jaw_w: float, face_w: float) -> str:
    ratio = jaw_w / face_w if face_w > 0 else 0
    if ratio > 0.88:
        return "strong"
    if ratio > 0.75:
        return "moderate"
    return "soft"


def _forehead_label(fore_w: float, face_w: float) -> str:
    ratio = fore_w / face_w if face_w > 0 else 0
    if ratio > 0.92:
        return "wide"
    if ratio > 0.78:
        return "average"
    return "narrow"


def _cheekbone_label(cheek_w: float, jaw_w: float, fore_w: float) -> str:
    avg_other = (jaw_w + fore_w) / 2
    ratio = cheek_w / avg_other if avg_other > 0 else 1
    if ratio > 1.08:
        return "high"
    if ratio > 0.95:
        return "average"
    return "low"


def extract_features(landmarks_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Returns:
        {
            "jawline":    "strong" | "moderate" | "soft",
            "forehead":   "wide"   | "average"  | "narrow",
            "cheekbones": "high"   | "average"  | "low",
        }
    """
    lms = landmarks_data.get("front", [])
    if len(lms) < 468:
        logger.warning("Insufficient landmarks for feature extraction — using defaults")
        return {"jawline": "moderate", "forehead": "average", "cheekbones": "average"}

    try:
        jaw_w = _dist(lms, "jaw_left", "jaw_right")
        fore_w = _dist(lms, "forehead_left", "forehead_right")
        cheek_w = _dist(lms, "cheek_left", "cheek_right")
        face_w = cheek_w  # widest point as reference

        return {
            "jawline": _jawline_label(jaw_w, face_w),
            "forehead": _forehead_label(fore_w, face_w),
            "cheekbones": _cheekbone_label(cheek_w, jaw_w, fore_w),
        }
    except Exception as exc:
        logger.error(f"Feature extraction error: {exc}")
        return {"jawline": "moderate", "forehead": "average", "cheekbones": "average"}