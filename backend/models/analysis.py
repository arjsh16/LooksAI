import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING
    )

    # Uploaded image paths
    image_front: Mapped[Optional[str]] = mapped_column(String(500))
    image_left: Mapped[Optional[str]] = mapped_column(String(500))
    image_right: Mapped[Optional[str]] = mapped_column(String(500))

    # Analysis results
    face_shape: Mapped[Optional[str]] = mapped_column(String(50))
    skin_analysis: Mapped[Optional[dict]] = mapped_column(JSON)     # acne_severity, dark_circles, skin_type
    facial_features: Mapped[Optional[dict]] = mapped_column(JSON)   # jawline, forehead, cheekbones
    landmarks_data: Mapped[Optional[dict]] = mapped_column(JSON)    # counts + key measurements

    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="analysis_sessions")
    recommendations = relationship(
        "Recommendation",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    chat_messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_sessions.id"), nullable=False, index=True
    )

    # User preferences captured mid-conversation
    maintenance_preference: Mapped[Optional[str]] = mapped_column(String(10))  # "high" | "low"
    length_preference: Mapped[Optional[str]] = mapped_column(String(10))       # "short" | "medium" | "long"

    # Filtered haircut objects from hashmap
    filtered_haircuts: Mapped[Optional[list]] = mapped_column(JSON)

    # Final LLM output (split for easy frontend rendering)
    narrative: Mapped[Optional[str]] = mapped_column(Text)
    haircut_table_md: Mapped[Optional[str]] = mapped_column(Text)
    skincare_tips: Mapped[Optional[str]] = mapped_column(Text)
    lifestyle_tips: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    session = relationship("AnalysisSession", back_populates="recommendations")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_sessions.id"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSON)  # e.g. {"stage": "ask_maintenance"}

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    session = relationship("AnalysisSession", back_populates="chat_messages")