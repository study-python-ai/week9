from typing import Optional, TypeVar

from app.core.exceptions.exceptions import (
    DuplicateException,
    NotFoundException,
    UnauthorizedException,
)

T = TypeVar("T")


def get_or_raise(
    entity: Optional[T],
    error_message: str = "리소스를 찾을 수 없습니다.",
    error_code: Optional[str] = None,
) -> T:
    """엔티티가 None이면 NotFoundException 발생

    Args:
        entity: 검증할 엔티티 객체
        error_message: 예외 발생 시 메시지
        error_code: 에러 코드 (선택)

    Returns:
        T: 검증된 엔티티 객체

    Raises:
        NotFoundException: 엔티티가 None인 경우
    """
    if entity is None:
        raise NotFoundException(error_message, error_code=error_code)

    return entity


def verify_ownership(
    owner_id: int,
    requester_id: int,
    error_message: str = "권한이 없습니다.",
    error_code: Optional[str] = None,
) -> None:
    """소유권 검증 - 다르면 UnauthorizedException 발생

    Args:
        owner_id: 리소스 소유자 ID
        requester_id: 요청자 ID
        error_message: 예외 발생 시 메시지
        error_code: 에러 코드 (선택)

    Raises:
        UnauthorizedException: 소유자와 요청자가 다른 경우
    """
    if owner_id != requester_id:
        raise UnauthorizedException(error_message, error_code=error_code)


def ensure_unique(
    exists: bool,
    error_message: str = "이미 존재합니다.",
    error_code: Optional[str] = None,
) -> None:
    """중복 검증 - 존재하면 DuplicateException 발생

    Args:
        exists: 존재 여부
        error_message: 예외 발생 시 메시지
        error_code: 에러 코드 (선택)

    Raises:
        DuplicateException: 이미 존재하는 경우
    """
    if exists:
        raise DuplicateException(error_message, error_code=error_code)
