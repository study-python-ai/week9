from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 예외 처리 핸들러

    커스텀 예외를 포함한 모든 HTTPException을 처리합니다.

    Args:

        request: FastAPI Request 객체
        exc: HTTPException 인스턴스

    Returns:
        JSONResponse: 에러 응답
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """요청 검증 예외 처리 핸들러

    Pydantic validation 에러를 처리하여 사용자 메시지를 응답합니다.


    Args:
        request: FastAPI Request 객체
        exc: RequestValidationError 인스턴스

    Returns:
        JSONResponse: 422 에러 응답

        TODO : 메시지, 메시지코드 추가
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """전역 예외 핸들러

    비지니스 로직 예외를 처리하고 에러로그를 남겨 디버깅에 활용합니다.

    Args:
        request: FastAPI Request 객체
        exc: Exception 인스턴스

    Returns:
        JSONResponse: 500 에러 응답

        TODO : 메시지, 메시지코드 추가

    """
    logger.error(
        f"예상치 못한 에러 발생: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "오류가 발생했습니다. 관리자에게 문의하여 주세요.",
            "error_type": type(exc).__name__,
        },
    )
