import logging

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """HTTP 예외 처리 핸들러

    커스텀 예외를 포함한 모든 HTTPException을 처리합니다.

    Args:

        request: FastAPI Request 객체
        exc: HTTPException 인스턴스

    Returns:
        JSONResponse: 에러 응답
    """

    # HTTPException이 아닌 경우 500 에러로 처리
    logger.error(f"예외 발생: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "오류가 발생했습니다. 관리자에게 문의하여 주세요."},
    )


async def validation_exception_handler(
    request: Request, exc: Exception
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
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=500, content={"message": "오류가 발생했습니다."}
        )

    errors = []
    for error in exc.errors():
        error_dict = {
            "type": error["type"],
            "loc": error["loc"],
            "msg": error["msg"],
            "input": error.get("input"),
        }
        errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": errors}
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
            "message": "오류가 발생했습니다. 관리자에게 문의하여 주세요.",
            "error_type": type(exc).__name__,
        },
    )
