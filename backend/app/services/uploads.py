from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.api.responses import api_error
from app.core.config import settings


ALLOWED_UPLOADS = {
    "image": {
        "extensions": {"jpg", "jpeg", "png", "webp"},
        "mime_types": {"image/jpeg", "image/png", "image/webp"},
        "max_size": 10 * 1024 * 1024,
        "folder": "projects",
    },
    "video": {
        "extensions": {"mp4", "webm"},
        "mime_types": {"video/mp4", "video/webm"},
        "max_size": 50 * 1024 * 1024,
        "folder": "projects",
    },
    "document": {
        "extensions": {"pdf"},
        "mime_types": {"application/pdf"},
        "max_size": 20 * 1024 * 1024,
        "folder": "documents",
    },
}


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    stored_filename: str
    storage_path: str
    public_url: str
    mime_type: str
    file_ext: str
    file_size: int


def normalize_ext(filename: str) -> str:
    return Path(filename or "").suffix.lower().lstrip(".")


def safe_subfolder(media_type: str, purpose: str | None = None) -> str:
    if media_type == "document" and purpose == "resume":
        return "resume"
    return ALLOWED_UPLOADS[media_type]["folder"]


async def save_upload_file(file: UploadFile, media_type: str, purpose: str | None = None) -> StoredUpload:
    rules = ALLOWED_UPLOADS.get(media_type)
    if rules is None:
        raise api_error(415, "UNSUPPORTED_MEDIA_TYPE", "Unsupported media type")

    original_filename = Path(file.filename or "upload").name
    file_ext = normalize_ext(original_filename)
    mime_type = file.content_type or "application/octet-stream"
    if file_ext not in rules["extensions"] or mime_type not in rules["mime_types"]:
        raise api_error(415, "UNSUPPORTED_MEDIA_TYPE", "Unsupported file type")

    content = await file.read()
    file_size = len(content)
    if file_size > rules["max_size"]:
        raise api_error(413, "PAYLOAD_TOO_LARGE", "Uploaded file is too large")

    subfolder = safe_subfolder(media_type, purpose)
    upload_root = Path(settings.upload_dir)
    target_dir = upload_root / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}.{file_ext}"
    storage_path = target_dir / stored_filename
    storage_path.write_bytes(content)

    public_base = settings.public_upload_base_url.rstrip("/")
    public_url = f"{public_base}/{subfolder}/{stored_filename}"
    return StoredUpload(
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=str(storage_path),
        public_url=public_url,
        mime_type=mime_type,
        file_ext=file_ext,
        file_size=file_size,
    )
