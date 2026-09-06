from app.services.storage import ALLOWED_EXTENSIONS


def test_allowed_video_extensions() -> None:
    assert ".mp4" in ALLOWED_EXTENSIONS
    assert ".mov" in ALLOWED_EXTENSIONS
    assert ".exe" not in ALLOWED_EXTENSIONS
