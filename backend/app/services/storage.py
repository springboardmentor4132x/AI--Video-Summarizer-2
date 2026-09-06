from pathlib import Path

from app.config import settings

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
    "video/x-matroska",
    "video/avi",
    "video/x-msvideo",
    "application/octet-stream",
}


def storage_root() -> Path:
    path = Path(settings.storage_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_storage_path(value: str) -> Path:
    """Resolve paths saved by older runs independently of the process cwd."""
    path = Path(value)
    if path.is_absolute() and path.exists():
        return path
    candidates = [path, Path(__file__).resolve().parents[3] / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


def video_dir(user_id: str, video_id: str) -> Path:
    path = storage_root() / "videos" / user_id / video_id
    path.mkdir(parents=True, exist_ok=True)
    return path
