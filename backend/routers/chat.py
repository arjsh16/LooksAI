from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
import json
import logging

from core.database import AsyncSessionLocal
from models.analysis import AnalysisSession, ChatMessage
from services.recommendation.engine import get_haircut_recommendations
from services.llm.mistral_client import stream_recommendation_narrative

router = APIRouter()
logger = logging.getLogger(__name__)

# Conversation state machine stages
STAGE_GREET = "greet"
STAGE_ASK_MAINTENANCE = "ask_maintenance"
STAGE_ASK_LENGTH = "ask_length"
STAGE_GENERATING = "generating"
STAGE_DONE = "done"


async def send_json(ws: WebSocket, data: dict):
    await ws.send_text(json.dumps(data))


@router.websocket("/stream/{session_id}")
async def chat_stream(
    websocket: WebSocket,
    session_id: int,
    token: str = Query(...),  # JWT passed as query param for WS auth
):
    """
    WebSocket endpoint that drives the multi-turn conversation:
    1. Greet + summarise analysis
    2. Ask maintenance preference
    3. Ask length preference
    4. Stream LLM recommendation
    """
    from jose import jwt, JWTError
    from core.config import settings

    await websocket.accept()

    # Authenticate via token query param
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await send_json(websocket, {"type": "error", "message": "Unauthorized"})
        await websocket.close(code=1008)
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AnalysisSession).where(
                AnalysisSession.id == session_id,
                AnalysisSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()

    if not session:
        await send_json(websocket, {"type": "error", "message": "Session not found"})
        await websocket.close(code=1008)
        return

    if session.status != "complete":
        await send_json(websocket, {"type": "error", "message": "Analysis not complete yet"})
        await websocket.close()
        return

    stage = STAGE_GREET
    maintenance = None
    length = None

    try:
        # Stage 1: Greet with analysis summary
        greeting = _build_greeting(session)
        await send_json(websocket, {"type": "message", "role": "assistant", "content": greeting, "stage": stage})
        await _save_message(session_id, "assistant", greeting, "analysis_summary")

        stage = STAGE_ASK_MAINTENANCE
        maint_prompt = "Would you prefer a **high maintenance** or **low maintenance** haircut?"
        await send_json(websocket, {
            "type": "message", "role": "assistant", "content": maint_prompt,
            "stage": stage, "options": ["high", "low"],
        })

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_msg = data.get("message", "").strip().lower()

            await _save_message(session_id, "user", user_msg, "text")

            if stage == STAGE_ASK_MAINTENANCE:
                if user_msg in ("high", "low"):
                    maintenance = user_msg
                    stage = STAGE_ASK_LENGTH
                    length_prompt = "Great! And what length are you going for — **short**, **medium**, or **long**?"
                    await send_json(websocket, {
                        "type": "message", "role": "assistant", "content": length_prompt,
                        "stage": stage, "options": ["short", "medium", "long"],
                    })
                else:
                    await send_json(websocket, {
                        "type": "message", "role": "assistant",
                        "content": "Please reply with **high** or **low**.",
                        "stage": stage, "options": ["high", "low"],
                    })

            elif stage == STAGE_ASK_LENGTH:
                if user_msg in ("short", "medium", "long"):
                    length = user_msg
                    stage = STAGE_GENERATING

                    # Filter haircuts and stream narrative
                    haircuts = get_haircut_recommendations(
                        face_shape=session.face_shape,
                        facial_features=session.facial_features,
                        skin_type=session.skin_type,
                        maintenance=maintenance,
                        length=length,
                    )
                    analysis_context = {
                        "face_shape": session.face_shape,
                        "skin_type": session.skin_type,
                        "acne_severity": session.acne_severity,
                        "dark_circles": session.dark_circles,
                        "facial_features": session.facial_features,
                        "maintenance_preference": maintenance,
                        "length_preference": length,
                    }

                    await send_json(websocket, {"type": "stream_start", "stage": stage})

                    full_response = ""
                    async for chunk in stream_recommendation_narrative(haircuts, analysis_context):
                        full_response += chunk
                        await send_json(websocket, {"type": "stream_chunk", "content": chunk})

                    await send_json(websocket, {"type": "stream_end", "stage": STAGE_DONE})
                    await _save_message(session_id, "assistant", full_response, "recommendation")
                    stage = STAGE_DONE
                    break
                else:
                    await send_json(websocket, {
                        "type": "message", "role": "assistant",
                        "content": "Please reply with **short**, **medium**, or **long**.",
                        "stage": stage, "options": ["short", "medium", "long"],
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.exception(f"WebSocket error for session {session_id}: {e}")
        await send_json(websocket, {"type": "error", "message": "An internal error occurred"})
        await websocket.close()


def _build_greeting(session: AnalysisSession) -> str:
    feats = session.facial_features or {}
    lines = [
        f"Analysis complete! Here's what I found:",
        f"- **Face shape**: {session.face_shape or 'unknown'}",
        f"- **Skin type**: {session.skin_type or 'unknown'}",
        f"- **Acne severity**: {session.acne_severity or 'none'}",
        f"- **Dark circles**: {session.dark_circles or 'none'}",
    ] 
    if feats:
        lines.append(f"- **Jawline**: {feats.get('jawline', 'n/a')}, "
                     f"**Forehead**: {feats.get('forehead', 'n/a')}, "
                     f"**Cheekbones**: {feats.get('cheekbones', 'n/a')}")
    lines.append("\nLet's find the perfect haircut for you! I have a couple of quick questions.")
    return "\n".join(lines)


async def _save_message(session_id: int, role: str, content: str, message_type: str):
    async with AsyncSessionLocal() as db:
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_type=message_type,
        )
        db.add(msg)
        await db.commit()