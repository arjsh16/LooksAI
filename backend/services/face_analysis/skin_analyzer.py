import logging
from typing import Any, Dict, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ── Optional deep model import ────────────────────────────────────────────────

try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as T
    from torchvision.models import efficientnet_b0

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available — heuristic-only skin analysis active")

from core.config import settings

_model_cache = None  # module-level singleton


# ── Heuristic helpers ─────────────────────────────────────────────────────────

def _crop_face(img_rgb: np.ndarray) -> np.ndarray:
    h, w = img_rgb.shape[:2]
    roi = img_rgb[int(h * 0.10) : int(h * 0.90), int(w * 0.15) : int(w * 0.85)]
    return cv2.resize(roi, (224, 224))


def _crop_under_eye(img_rgb: np.ndarray) -> np.ndarray:
    h, w = img_rgb.shape[:2]
    roi = img_rgb[int(h * 0.35) : int(h * 0.55), int(w * 0.20) : int(w * 0.80)]
    if roi.size == 0:
        return img_rgb[:56, :112]
    return cv2.resize(roi, (112, 56))


def _acne_heuristic(face_roi: np.ndarray) -> Dict[str, Any]:
    """Estimates acne severity by red-blotch density in HSV space."""
    hsv = cv2.cvtColor(face_roi, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255])) | \
           cv2.inRange(hsv, np.array([160, 50, 50]), np.array([180, 255, 255]))
    ratio = cv2.countNonZero(mask) / (face_roi.shape[0] * face_roi.shape[1])
    severity = (
        "none" if ratio < 0.01 else
        "mild" if ratio < 0.03 else
        "moderate" if ratio < 0.07 else
        "severe"
    )
    return {"acne_severity": severity, "red_ratio": float(ratio)}


def _dark_circles_heuristic(eye_roi: np.ndarray) -> Dict[str, Any]:
    """Estimates dark circles via mean brightness under the eyes."""
    brightness = float(np.mean(cv2.cvtColor(eye_roi, cv2.COLOR_RGB2GRAY)))
    severity = (
        "none" if brightness > 160 else
        "mild" if brightness > 130 else
        "moderate" if brightness > 100 else
        "severe"
    )
    return {"dark_circles": severity, "mean_brightness": brightness}


def _skin_type_heuristic(face_roi: np.ndarray) -> str:
    """Estimates skin type via T-zone luminance and variance."""
    gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
    _, w = gray.shape
    t_zone = gray[:, w // 3 : 2 * w // 3]
    t_mean = float(np.mean(t_zone))
    t_std = float(np.std(t_zone))
    if t_mean > 170 and t_std > 25:
        return "oily"
    if t_mean < 130 and t_std < 15:
        return "dry"
    return "combination"


# ── EfficientNet model ────────────────────────────────────────────────────────

def _load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    if not TORCH_AVAILABLE:
        return None
    try:
        import os

        model = efficientnet_b0(weights=None)
        # 5 outputs: acne×4 classes + 1 skin_type logit
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)

        if os.path.exists(settings.EFFICIENTNET_MODEL_PATH):
            state = torch.load(settings.EFFICIENTNET_MODEL_PATH, map_location="cpu")
            model.load_state_dict(state)
            logger.info("EfficientNet weights loaded")
        else:
            logger.warning(
                f"No checkpoint at {settings.EFFICIENTNET_MODEL_PATH} — "
                "EfficientNet disabled, using heuristics"
            )
            return None

        model.eval()
        _model_cache = model
        return model
    except Exception as exc:
        logger.error(f"EfficientNet load failed: {exc}")
        return None


def _efficientnet_predict(face_roi_rgb: np.ndarray) -> Optional[Dict[str, Any]]:
    model = _load_model()
    if model is None:
        return None

    transform = T.Compose([
        T.ToPILImage(),
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    tensor = transform(face_roi_rgb).unsqueeze(0)

    with torch.no_grad():
        logits = model(tensor)[0]
        acne_probs = torch.softmax(logits[:4], dim=0).tolist()
        skin_logit = logits[4].item()

    acne_labels = ["none", "mild", "moderate", "severe"]
    acne_idx = int(torch.tensor(acne_probs).argmax())
    skin_type = (
        "oily" if skin_logit > 0.3 else
        "dry" if skin_logit < -0.3 else
        "combination"
    )
    return {
        "acne_severity": acne_labels[acne_idx],
        "acne_confidence": round(acne_probs[acne_idx], 3),
        "skin_type": skin_type,
    }


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_skin(image_path: str) -> Dict[str, Any]:
    """
    Returns:
        {
            acne_severity:  "none" | "mild" | "moderate" | "severe",
            dark_circles:   "none" | "mild" | "moderate" | "severe",
            skin_type:      "oily" | "dry" | "combination",
            source:         "efficientnet+heuristic" | "heuristic",
        }
    """
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Could not load: {image_path}")
        return {
            "acne_severity": "unknown",
            "dark_circles": "unknown",
            "skin_type": "combination",
            "source": "error",
        }

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_roi = _crop_face(img_rgb)
    eye_roi = _crop_under_eye(img_rgb)

    dark = _dark_circles_heuristic(eye_roi)
    deep = _efficientnet_predict(face_roi)

    if deep:
        return {
            "acne_severity": deep["acne_severity"],
            "dark_circles": dark["dark_circles"],
            "skin_type": deep["skin_type"],
            "source": "efficientnet+heuristic",
            "debug": {
                "acne_confidence": deep.get("acne_confidence"),
                "eye_brightness": dark["mean_brightness"],
            },
        }

    acne = _acne_heuristic(face_roi)
    skin_type = _skin_type_heuristic(face_roi)
    return {
        "acne_severity": acne["acne_severity"],
        "dark_circles": dark["dark_circles"],
        "skin_type": skin_type,
        "source": "heuristic",
        "debug": {
            "red_ratio": acne["red_ratio"],
            "eye_brightness": dark["mean_brightness"],
        },
    }