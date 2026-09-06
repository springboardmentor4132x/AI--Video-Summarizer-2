from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.rbac import ensure_role
from app.models.user import UserRole


def test_ensure_role_allows_matching_role() -> None:
    user = SimpleNamespace(role=UserRole.EDUCATOR)
    ensure_role(user, UserRole.EDUCATOR, UserRole.ADMINISTRATOR)


def test_ensure_role_rejects_other_role() -> None:
    user = SimpleNamespace(role=UserRole.LEARNER)
    with pytest.raises(HTTPException) as exc:
        ensure_role(user, UserRole.CONTENT_CREATOR)
    assert exc.value.status_code == 403
