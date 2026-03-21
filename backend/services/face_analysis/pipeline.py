import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from core.database import AsyncSessionLocal
from models.analysis import AnalysisSession, AnalysisStatus

from .feature_extractor import extract_features
from .mediapipe_mesh import extract_landmarks
from .shape_classifier import classify_face_shape
from .skin_analyzer import analyze_skin

logger = logging.getLogger(__name__)


async def run_analysis_pipeline(session_id: int) -> None:
    """
    Background task: runs the full 4-stage ML pipeline and persists results.
    Stages: landmark extraction → face shape → skin analysis → feature extraction
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if not session:
                logger.error(f"[{session_id}] Session not found, aborting pipeline")
                return

            session.status = AnalysisStatus.PROCESSING
            await db.commit()

            loop = asyncio.get_event_loop()

            # ── Stage 1: Landmark extraction ──────────────────────────────────
            logger.info(f"[{session_id}] Stage 1: Extracting landmarks")
            landmarks = await loop.run_in_executor(
                None,
                extract_landmarks,
                session.image_front,
                session.image_left,
                session.image_right,
            )
            if not landmarks.get("success"):
                raise ValueError(f"Landmark extraction failed: {landmarks.get('error')}")

            # ── Stage 2: Face shape ───────────────────────────────────────────
            logger.info(f"[{session_id}] Stage 2: Classifying face shape")
            face_shape = await loop.run_in_executor(
                None, classify_face_shape, landmarks
            )

            # ── Stage 3: Skin analysis ────────────────────────────────────────
            logger.info(f"[{session_id}] Stage 3: Analyzing skin")
            skin_analysis = await loop.run_in_executor(
                None, analyze_skin, session.image_front
            )

            # ── Stage 4: Feature extraction ───────────────────────────────────
            logger.info(f"[{session_id}] Stage 4: Extracting facial features")
            facial_features = await loop.run_in_executor(
                None, extract_features, landmarks
            )

            # ── Persist ───────────────────────────────────────────────────────
            session.face_shape = face_shape
            session.skin_analysis = skin_analysis
            session.facial_features = facial_features
            session.landmarks_data = {
                "front_count": len(landmarks.get("front", [])),
                "left_count": len(landmarks.get("left", [])),
                "right_count": len(landmarks.get("right", [])),
                "measurements": landmarks.get("measurements", {}),
            }
            session.status = AnalysisStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                f"[{session_id}] Pipeline complete — "
                f"shape={face_shape}, skin={skin_analysis.get('skin_type')}, "
                f"acne={skin_analysis.get('acne_severity')}"
            )

        except Exception as exc:
            logger.exception(f"[{session_id}] Pipeline failed: {exc}")
            try:
                result = await db.execute(
                    select(AnalysisSession).where(AnalysisSession.id == session_id)
                )
                session = result.scalar_one_or_none()
                if session:
                    session.status = AnalysisStatus.FAILED
                    session.error_message = str(exc)
                    await db.commit()
            except Exception as inner:
                logger.error(f"[{session_id}] Could not persist failure state: {inner}")