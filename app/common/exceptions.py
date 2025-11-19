from typing import Optional

from fastapi import HTTPException, status


class BaseCustomException(HTTPException):
    """기본 커스텀 예외

    에러 코드를 포함한 커스텀 예외 클래스
    """

    def __init__(self, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=self.status_code, detail=detail)
        self.error_code = error_code


class NotFoundException(BaseCustomException):
    """404 Not Found"""

    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedException(BaseCustomException):
    """401 Unauthorized"""

    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(BaseCustomException):
    """403 Forbidden"""

    status_code = status.HTTP_403_FORBIDDEN


class DuplicateException(BaseCustomException):
    """409 Conflict"""

    status_code = status.HTTP_409_CONFLICT


class BadRequestException(BaseCustomException):
    """400 Bad Request"""

    status_code = status.HTTP_400_BAD_REQUEST
