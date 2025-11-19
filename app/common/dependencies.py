from fastapi import Depends, Header

from app.common.error_codes import ErrorCode
from app.common.exceptions import UnauthorizedException
from app.core.security import verify_token
from app.dependencies import get_user_model
from app.models.user_model import User, UserModel


def get_current_user(
    authorization: str = Header(None, description="Bearer 토큰"),
    user_model: UserModel = Depends(get_user_model),
) -> User:
    """JWT 토큰에서 현재 사용자 추출

    Args:
        authorization: Authorization 헤더 (Bearer {token})
        user_model: 사용자 모델 (의존성 주입)

    Returns:
        인증된 User 객체

    Raises:
        UnauthorizedException: 토큰이 없거나 유효하지 않은 경우
    """
    if not authorization:
        raise UnauthorizedException(
            "인증 헤더가 없습니다.",
            error_code=ErrorCode.UNAUTHORIZED,
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

    user = user_model.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException(
            "사용자를 찾을 수 없습니다.", error_code=ErrorCode.TOKEN_USER_NOT_FOUND
        )

    return user
