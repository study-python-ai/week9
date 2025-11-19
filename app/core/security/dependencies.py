from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.db.dependencies import get_db, get_user_model
from app.core.exceptions.error_codes import ErrorCode
from app.core.exceptions.exceptions import UnauthorizedException
from app.core.security.security import verify_token
from app.models.user_model import User


def get_current_user(
    authorization: str = Header(None, description="Bearer 토큰"),
    db: Session = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 사용자 추출

    Args:
        authorization: Authorization 헤더 (Bearer {token})
        db: 데이터베이스 세션 (의존성 주입)

    Returns:
        인증된 User 객체

    Raises:
        UnauthorizedException: 토큰이 없거나 유효하지 않은 경우
    """
    if not authorization:
        raise UnauthorizedException(
            "인증 헤더가 없습니다.", error_code=ErrorCode.UNAUTHORIZED
        )

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(
            "유효하지 않은 인증 헤더 형식입니다.",
            error_code=ErrorCode.INVALID_AUTH_HEADER,
        )

    token = authorization.replace("Bearer ", "")

    payload = verify_token(token)
    if not payload:
        raise UnauthorizedException(
            "유효하지 않은 토큰입니다.", error_code=ErrorCode.TOKEN_INVALID
        )

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(
            "토큰에서 사용자 정보를 찾을 수 없습니다.",
            error_code=ErrorCode.TOKEN_INVALID,
        )

    user_model = get_user_model(db)
    user = user_model.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException(
            "사용자를 찾을 수 없습니다.", error_code=ErrorCode.TOKEN_USER_NOT_FOUND
        )

    return user


def get_optional_current_user(
    authorization: str = Header(None, description="Bearer 토큰"),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """JWT 토큰에서 현재 사용자 추출 (선택적)

    Args:
        authorization: Authorization 헤더 (Bearer {token})
        db: 데이터베이스 세션 (의존성 주입)

    Returns:
        인증된 User 객체 또는 None (토큰이 없는 경우)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_model = get_user_model(db)
    user = user_model.find_by_id(int(user_id))
    return user
