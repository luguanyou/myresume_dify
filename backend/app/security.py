import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings


PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
TOKEN_ALGORITHM = "HS256"


def _urlsafe_b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS)
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != PASSWORD_ALGORITHM:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    expires_in = expires_delta or timedelta(seconds=settings.admin_token_expire_seconds)
    expires_at = datetime.now(timezone.utc) + expires_in
    header = {"alg": TOKEN_ALGORITHM, "typ": "JWT"}
    payload = {"sub": str(subject), "exp": int(expires_at.timestamp())}
    signing_input = ".".join(
        [
            _urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(settings.token_secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_urlsafe_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
        signing_input = f"{encoded_header}.{encoded_payload}"
        expected_signature = hmac.new(
            settings.token_secret.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        actual_signature = _urlsafe_b64decode(encoded_signature)
        if not hmac.compare_digest(expected_signature, actual_signature):
            return None

        header = json.loads(_urlsafe_b64decode(encoded_header))
        if header.get("alg") != TOKEN_ALGORITHM:
            return None

        payload = json.loads(_urlsafe_b64decode(encoded_payload))
        expires_at = int(payload.get("exp", 0))
        if expires_at < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except (ValueError, json.JSONDecodeError, TypeError):
        return None
