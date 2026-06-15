import json

from starlette.testclient import TestClient

from app.core.config import settings
from app.main import app


class FakeDifyStream:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("Dify failed")

    async def aiter_lines(self):
        yield 'data: {"event":"agent_message","answer":"Hello ","conversation_id":"conv-123"}'
        yield 'data: {"event":"agent_message","answer":"world","conversation_id":"conv-123"}'
        yield 'data: {"event":"message_end","conversation_id":"conv-123"}'


class FakeAsyncClient:
    calls = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def stream(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        return FakeDifyStream()


def test_chat_stream_proxies_dify_stream_as_standard_sse(monkeypatch):
    FakeAsyncClient.calls = []
    monkeypatch.setattr(settings, "dify_api_key", "test-dify-key")
    monkeypatch.setattr(settings, "dify_api_base_url", "https://dify.example/v1")
    monkeypatch.setattr("httpx.AsyncClient", FakeAsyncClient)

    client = TestClient(app)
    with client.stream(
        "POST",
        "/api/chat/stream",
        json={
            "message": "Tell me about your backend work",
            "conversation_id": "",
            "visitor_id": "visitor-1",
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: message" in body
    assert 'data: {"answer":"Hello ","conversation_id":"conv-123"}' in body
    assert 'data: {"answer":"world","conversation_id":"conv-123"}' in body
    assert "event: done" in body
    assert 'data: {"conversation_id":"conv-123"}' in body

    assert len(FakeAsyncClient.calls) == 1
    dify_call = FakeAsyncClient.calls[0]
    assert dify_call["method"] == "POST"
    assert dify_call["url"] == "https://dify.example/v1/chat-messages"
    assert dify_call["headers"]["Authorization"] == "Bearer test-dify-key"
    assert dify_call["json"]["query"] == "Tell me about your backend work"
    assert dify_call["json"]["response_mode"] == "streaming"
    assert dify_call["json"]["conversation_id"] == ""
    assert dify_call["json"]["user"] == "visitor-1"


def test_chat_stream_returns_sse_error_when_dify_key_is_missing(monkeypatch):
    monkeypatch.setattr(settings, "dify_api_key", "")

    client = TestClient(app)
    response = client.post("/api/chat/stream", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: error" in response.text
    data_line = next(line for line in response.text.splitlines() if line.startswith("data: "))
    error_payload = json.loads(data_line.removeprefix("data: "))
    assert error_payload["code"] == "DIFY_UPSTREAM_ERROR"
