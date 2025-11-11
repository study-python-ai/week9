from fastapi import HTTPException, status


class BaseCustomException(HTTPException):
    """기본 커스텀 예외"""
    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code, detail=detail)


class NotFoundException(BaseCustomException):
    """404 Not Found"""
    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedException(BaseCustomException):
    """401 Unauthorized"""
    status_code = status.HTTP_401_UNAUTHORIZED


class DuplicateException(BaseCustomException):
    """409 Conflict"""
    status_code = status.HTTP_409_CONFLICT


class BadRequestException(BaseCustomException):
    """400 Bad Request"""
    status_code = status.HTTP_400_BAD_REQUEST
