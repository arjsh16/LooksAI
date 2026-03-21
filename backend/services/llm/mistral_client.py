import json
import logging
from typing import AsyncIterator, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

_API_URL = "https://api.mistral.ai/v1/chat/completions"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }


# ── Streaming ─────────────────────────────────────────────────────────────────

async def stream_completion(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> AsyncIterator[str]:
    """
    Yields text chunks from a streaming Mistral call (SSE).
    Use this inside a WebSocket handler for real-time token delivery.
    """
    payload = {
        "model": settings.MISTRAL_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            "POST",
            _API_URL,
            json=payload,
            headers={**_headers(), "Accept": "text/event-stream"},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        chunk = data["choices"][0].get("delta", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


# ── Non-streaming ─────────────────────────────────────────────────────────────

async def complete(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> str:
    """
    Blocking Mistral call. Returns the full response string.
    Raises httpx.HTTPStatusError on API errors.
    """
    payload = {
        "model": settings.MISTRAL_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(_API_URL, json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_recommendation_prompt(
    analysis: dict,
    filtered_haircuts: list[dict],
    maintenance: str,
    length: str,
) -> list[dict]:
    """
    Constructs the message list for the recommendation call.
    The system prompt enforces a strict 3-part output structure:
      1. Narrative
      2. ## Haircut Instructions to the Barber  (markdown table)
      3. ## Skincare & Lifestyle Tips           (bullet list)
    """
    system = (
        "You are LooksAI — a professional hairstylist and dermatology-informed skincare advisor.\n"
        "Always structure your response in exactly this order:\n"
        "1. A warm, confident 2–3 sentences narrative explaining WHY these cuts work for this person.\n"
        "2. A markdown section titled '## Haircut Instructions to the Barber' containing a table "
        "with columns: Haircut | Length | Maintenance | Barber Instructions | Key Products\n"
        "3. A markdown section titled '## Skincare & Lifestyle Tips' with targeted bullet points "
        "addressing detected skin/lifestyle gaps (acne → routine, dark circles → sleep/hydration, etc.).\n"
        "Be specific and actionable. Never use filler phrases."
    )

    skin = analysis.get("skin_analysis", {})
    features = analysis.get("facial_features", {})

    user_msg = f"""Facial analysis results:
- Face shape:   {analysis.get("face_shape", "unknown")}
- Jawline:      {features.get("jawline", "unknown")}
- Forehead:     {features.get("forehead", "unknown")}
- Cheekbones:   {features.get("cheekbones", "unknown")}
- Skin type:    {skin.get("skin_type", "unknown")}
- Acne:         {skin.get("acne_severity", "unknown")}
- Dark circles: {skin.get("dark_circles", "unknown")}
- Maintenance preference: {maintenance}
- Length preference:      {length}

Pre-filtered haircut options (from recommendation engine):
```json
{json.dumps(filtered_haircuts, indent=2)}
```

Please deliver your full recommendation."""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


def build_analysis_summary_prompt(analysis: dict) -> list[dict]:
    """
    Prompt for the first chat message: telling the user what was detected.
    The bot narrates the findings in a friendly, conversational way before
    asking about maintenance preference.
    """
    skin = analysis.get("skin_analysis", {})
    features = analysis.get("facial_features", {})

    system = (
        "You are FaceForm AI. You've just finished analyzing a user's face. "
        "Summarize the findings warmly and naturally — like a professional stylist in a consultation. "
        "Keep it to 3–5 sentences. End by asking whether they prefer high or low maintenance styling."
    )
    user_msg = f"""Analysis complete:
Face shape: {analysis.get("face_shape")}
Jawline: {features.get("jawline")}, Forehead: {features.get("forehead")}, Cheekbones: {features.get("cheekbones")}
Skin: {skin.get("skin_type")}, Acne: {skin.get("acne_severity")}, Dark circles: {skin.get("dark_circles")}"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]

# ── Convenience wrapper used by chat router ───────────────────────────────────

async def stream_recommendation_narrative(
    filtered_haircuts: list[dict],
    analysis_context: dict,
) -> "AsyncIterator[str]":
    """
    Wrapper that builds the prompt and streams the LLM response.
    Called from the WebSocket chat handler.
    """
    messages = build_recommendation_prompt(
        analysis=analysis_context,
        filtered_haircuts=filtered_haircuts,
        maintenance=analysis_context.get("maintenance_preference", "low"),
        length=analysis_context.get("length_preference", "medium"),
    )
    async for chunk in stream_completion(messages):
        yield chunk
