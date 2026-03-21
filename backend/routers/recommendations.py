from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from core.security import get_current_user
from models.analysis import AnalysisSession, AnalysisStatus, Recommendation
from models.user import User

router = APIRouter(tags=["recommendations"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: int
    session_id: int
    maintenance_preference: Optional[str]
    length_preference: Optional[str]
    filtered_haircuts: Optional[list]
    narrative: Optional[str]
    haircut_table_md: Optional[str]
    skincare_tips: Optional[str]
    lifestyle_tips: Optional[str]

    class Config:
        from_attributes = True


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/{session_id}", response_model=list[RecommendationResponse])
async def get_recommendations(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify session ownership
    session_result = await db.execute(
        select(AnalysisSession).where(
            AnalysisSession.id == session_id,
            AnalysisSession.user_id == current_user.id,
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            400, f"Analysis not complete. Current status: {session.status}"
        )

    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.session_id == session_id)
        .order_by(Recommendation.created_at.desc())
    )
    return result.scalars().all()