import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status

from app.utils.dependencies import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_instructor,
    require_admin,
)
from app.models.user import User, UserRole


@pytest.fixture
def fake_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.is_active = True
    user.role = UserRole.STUDENT
    return user


@pytest.fixture
def fake_db(fake_user):
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value.first.return_value = fake_user
    return db


@pytest.fixture
def fake_credentials():
    creds = MagicMock()
    creds.credentials = "fake.jwt.token"
    return creds


# ---- get_current_user ----
@patch("app.utils.dependencies.decode_token", return_value={"sub": 1})
def test_get_current_user_valid(mock_decode, fake_db, fake_credentials, fake_user):
    user = get_current_user(fake_credentials, fake_db)
    assert user == fake_user
    mock_decode.assert_called_once()


@patch("app.utils.dependencies.decode_token", return_value=None)
def test_get_current_user_invalid_token(mock_decode, fake_db, fake_credentials):
    with pytest.raises(HTTPException) as exc:
        get_current_user(fake_credentials, fake_db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.utils.dependencies.decode_token", return_value={})
def test_get_current_user_missing_sub(mock_decode, fake_db, fake_credentials):
    with pytest.raises(HTTPException) as exc:
        get_current_user(fake_credentials, fake_db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.utils.dependencies.decode_token", return_value={"sub": 99})
def test_get_current_user_not_found(mock_decode, fake_db, fake_credentials):
    fake_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_current_user(fake_credentials, fake_db)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@patch("app.utils.dependencies.decode_token", return_value={"sub": 1})
def test_get_current_user_inactive(mock_decode, fake_db, fake_credentials, fake_user):
    fake_user.is_active = False
    with pytest.raises(HTTPException) as exc:
        get_current_user(fake_credentials, fake_db)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


# ---- get_current_active_user ----
def test_get_current_active_user_valid(fake_user):
    assert get_current_active_user(fake_user) == fake_user


def test_get_current_active_user_inactive(fake_user):
    fake_user.is_active = False
    with pytest.raises(HTTPException) as exc:
        get_current_active_user(fake_user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


# ---- require_role ----
def test_require_role_correct(fake_user):
    fake_user.role = UserRole.INSTRUCTOR
    dep = require_role(UserRole.INSTRUCTOR)
    assert dep(fake_user) == fake_user


def test_require_role_admin_bypass(fake_user):
    fake_user.role = UserRole.ADMIN
    dep = require_role(UserRole.INSTRUCTOR)
    assert dep(fake_user) == fake_user


def test_require_role_forbidden(fake_user):
    fake_user.role = UserRole.STUDENT
    dep = require_role(UserRole.INSTRUCTOR)
    with pytest.raises(HTTPException) as exc:
        dep(fake_user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


# ---- require_instructor ----
def test_require_instructor_valid(fake_user):
    fake_user.role = UserRole.INSTRUCTOR
    assert require_instructor(fake_user) == fake_user


def test_require_instructor_admin(fake_user):
    fake_user.role = UserRole.ADMIN
    assert require_instructor(fake_user) == fake_user


def test_require_instructor_forbidden(fake_user):
    fake_user.role = UserRole.STUDENT
    with pytest.raises(HTTPException) as exc:
        require_instructor(fake_user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


# ---- require_admin ----
def test_require_admin_valid(fake_user):
    fake_user.role = UserRole.ADMIN
    assert require_admin(fake_user) == fake_user


def test_require_admin_forbidden(fake_user):
    fake_user.role = UserRole.INSTRUCTOR
    with pytest.raises(HTTPException) as exc:
        require_admin(fake_user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
