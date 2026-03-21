import os
import uuid
from datetime import datetime
from typing import Optional

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.security import get_current_user
from models.analysis import AnalysisSession, AnalysisStatus
from models.user import User
from services.face_analysis.pipeline import run_analysis_pipeline

router = APIRouter(tags=["analysis"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


# ── Schemas ────────────────────────────────────────────────────────────────────

class AnalysisSessionResponse(BaseModel):
    id: int
    status: str
    face_shape: Optional[str]
    skin_analysis: Optional[dict]
    facial_features: Optional[dict]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _save_upload(file: UploadFile, session_dir: str, label: str) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            400, f"Invalid file type for '{label}'. Use JPEG, PNG, or WebP."
        )
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(400, f"'{label}' image exceeds the 10 MB limit.")

    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    path = os.path.join(session_dir, f"{label}.{ext}")
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)
    return path


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post(
    "/upload",
    response_model=AnalysisSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_photos(
    background_tasks: BackgroundTasks,
    front: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Create isolated directory per session
    session_uuid = str(uuid.uuid4())
    session_dir = os.path.join(settings.UPLOAD_DIR, session_uuid)
    os.makedirs(session_dir, exist_ok=True)

    front_path = await _save_upload(front, session_dir, "front")
    left_path = await _save_upload(left, session_dir, "left")
    right_path = await _save_upload(right, session_dir, "right")

    session = AnalysisSession(
        user_id=current_user.id,
        status=AnalysisStatus.PENDING,
        image_front=front_path,
        image_left=left_path,
        image_right=right_path,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    background_tasks.add_task(run_analysis_pipeline, session.id)
    return session


@router.get("/{session_id}", response_model=AnalysisSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AnalysisSession).where(
            AnalysisSession.id == session_id,
            AnalysisSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Analysis session not found")
    return session


@router.get("/", response_model=list[AnalysisSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.user_id == current_user.id)
        .order_by(AnalysisSession.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()