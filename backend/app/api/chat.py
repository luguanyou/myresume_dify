import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["chat"])


class ChatStreamRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation_id: str | None = ""
    visitor_id: str | None = "web-visitor"


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, separators=(',', ':'))}\n\n"


def parse_dify_data_line(line: str) -> dict | None:
    if not line.startswith("data:"):
        return None

    raw_data = line.removeprefix("data:").strip()
    if not raw_data or raw_data == "[DONE]":
        return None

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return None


def dify_chat_url() -> str:
    return f"{settings.dify_api_base_url.rstrip('/')}/chat-messages"


async def stream_dify_chat(payload: ChatStreamRequest) -> AsyncGenerator[str, None]:
    if not settings.dify_api_key:
        yield sse_event(
            "error",
            {"code": "DIFY_UPSTREAM_ERROR", "message": "Dify API key is not configured"},
        )
        return

    dify_payload = {
        "inputs": {},
        "query": payload.message,
        "response_mode": "streaming",
        "conversation_id": payload.conversation_id or "",
        "user": payload.visitor_id or "web-visitor",
    }
    headers = {
        "Authorization": f"Bearer {settings.dify_api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    last_conversation_id = payload.conversation_id or ""

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", dify_chat_url(), json=dify_payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    event_data = parse_dify_data_line(line)
                    if event_data is None:
                        continue

                    conversation_id = event_data.get("conversation_id") or last_conversation_id
                    if conversation_id:
                        last_conversation_id = conversation_id

                    dify_event = event_data.get("event")
                    if dify_event in {"agent_message", "message"}:
                        answer = event_data.get("answer") or ""
                        if answer:
                            yield sse_event(
                                "message",
                                {"answer": answer, "conversation_id": last_conversation_id},
                            )
                    elif dify_event in {"message_end", "workflow_finished"}:
                        yield sse_event("done", {"conversation_id": last_conversation_id})
                        return
                    elif dify_event == "error":
                        yield sse_event(
                            "error",
                            {
                                "code": event_data.get("code") or "DIFY_UPSTREAM_ERROR",
                                "message": event_data.get("message") or "Dify service returned an error",
                            },
                        )
                        return

        yield sse_event("done", {"conversation_id": last_conversation_id})
    except Exception:
        yield sse_event(
            "error",
            {"code": "DIFY_UPSTREAM_ERROR", "message": "Dify service is temporarily unavailable"},
        )


@router.post("/chat/stream")
async def chat_stream(payload: ChatStreamRequest):
    return StreamingResponse(
        stream_dify_chat(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
