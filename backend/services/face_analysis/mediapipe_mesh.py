import logging
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

logger = logging.getLogger(__name__)

mp_face_mesh = mp.solutions.face_mesh

# Landmark indices for key geometric points
LANDMARK_IDX = {
    "jaw_left": 172,
    "jaw_right": 397,
    "chin": 152,
    "forehead_top": 10,
    "forehead_left": 67,
    "forehead_right": 297,
    "cheek_left": 234,
    "cheek_right": 454,
    "face_top": 10,
    "face_bottom": 152,
}


def _load_rgb(path: str) -> Optional[np.ndarray]:
    img = cv2.imread(path)
    if img is None:
        logger.warning(f"Could not load image: {path}")
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _run_mesh(image_rgb: np.ndarray, label: str) -> Optional[list]:
    h, w = image_rgb.shape[:2]
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as mesh:
        results = mesh.process(image_rgb)
        if not results.multi_face_landmarks:
            logger.warning(f"No face detected in {label} image")
            return None
        lms = results.multi_face_landmarks[0].landmark
        # Denormalize to pixel coords, keep Z for depth cues
        return [{"x": lm.x * w, "y": lm.y * h, "z": lm.z} for lm in lms]


def _compute_measurements(lms: list) -> dict:
    """Derives key facial ratios from front-view landmarks."""

    def pt(key: str) -> np.ndarray:
        lm = lms[LANDMARK_IDX[key]]
        return np.array([lm["x"], lm["y"]])

    def dist(a: str, b: str) -> float:
        return float(np.linalg.norm(pt(a) - pt(b)))

    face_width = dist("cheek_left", "cheek_right")
    face_height = dist("face_top", "face_bottom")
    jaw_width = dist("jaw_left", "jaw_right")
    forehead_width = dist("forehead_left", "forehead_right")
    cheek_width = face_width  # alias for clarity

    return {
        "face_width": face_width,
        "face_height": face_height,
        "jaw_width": jaw_width,
        "forehead_width": forehead_width,
        "cheek_width": cheek_width,
        "width_to_height_ratio": face_width / face_height if face_height > 0 else 0.0,
        "jaw_to_cheek_ratio": jaw_width / cheek_width if cheek_width > 0 else 0.0,
        "forehead_to_cheek_ratio": forehead_width / cheek_width if cheek_width > 0 else 0.0,
    }


def extract_landmarks(front_path: str, left_path: str, right_path: str) -> dict:
    """
    Runs MediaPipe Face Mesh on all 3 angles.
    Returns a result dict with landmark arrays and computed measurements.
    Front image is required; side images degrade gracefully if detection fails.
    """
    front_img = _load_rgb(front_path)
    if front_img is None:
        return {"success": False, "error": "Front image could not be loaded"}

    front_lms = _run_mesh(front_img, "front")
    if not front_lms:
        return {"success": False, "error": "No face detected in front image"}

    left_img = _load_rgb(left_path)
    right_img = _load_rgb(right_path)

    left_lms = _run_mesh(left_img, "left") if left_img is not None else None
    right_lms = _run_mesh(right_img, "right") if right_img is not None else None

    return {
        "success": True,
        "front": front_lms,
        "left": left_lms or [],
        "right": right_lms or [],
        "measurements": _compute_measurements(front_lms),
    }