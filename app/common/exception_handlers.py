import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.error_codes import ErrorCode
from app.common.exceptions import BaseCustomException

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 예외 처리 핸들러

    커스텀 예외를 포함한 모든 HTTPException을 표준 형식으로 처리합니다.

    Args:
        request: FastAPI Request 객체
        exc: HTTPException 인스턴스

    Returns:
        JSONResponse: 표준 에러 응답
    """
    log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR

    error_code = None
    if isinstance(exc, BaseCustomException) and hasattr(exc, "error_code"):
        error_code = exc.error_code

    if not error_code:
        if exc.status_code == 404:
            error_code = ErrorCode.POST_NOT_FOUND
        elif exc.status_code == 401:
            error_code = ErrorCode.UNAUTHORIZED
        elif exc.status_code == 403:
            error_code = ErrorCode.FORBIDDEN
        elif exc.status_code == 409:
            error_code = ErrorCode.USER_ALREADY_EXISTS
        elif exc.status_code == 400:
            error_code = ErrorCode.BAD_REQUEST
        else:
            error_code = ErrorCode.UNEXPECTED_ERROR

    logger.log(
        log_level,
        f"HTTP Exception: {exc.status_code} - {error_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": error_code,
            "client_ip": request.client.host if request.client else None,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": error_code, "message": exc.detail, "details": None},
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.url.path,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """요청 검증 예외 처리 핸들러

    Pydantic validation 에러를 표준 형식으로 처리합니다.

    Args:
        request: FastAPI Request 객체
        exc: RequestValidationError 인스턴스

    Returns:
        JSONResponse: 422 Validation 에러 응답
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]

        errors.append(
            {
                "field": field,
                "message": message,
                "type": error["type"],
                "input": error.get("input"),
            }
        )

    logger.warning(
        f"Validation Error: {len(errors)} errors",
        extra={"path": request.url.path, "method": request.method, "errors": errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "요청 데이터 검증에 실패했습니다.",
                "details": errors,
            },
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.url.path,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """전역 예외 핸들러

    예상하지 못한 모든 예외를 표준 형식으로 처리하고 500 에러를 반환합니다.

    Args:
        request: FastAPI Request 객체
        exc: Exception 인스턴스

    Returns:
        JSONResponse: 500 Internal Server Error 응답
    """
    logger.error(
        f"Unexpected Error: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "error_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
                "details": None,
            },
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.url.path,
        },
    )
