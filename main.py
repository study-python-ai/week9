import logging

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v2.routers import post_router as v2_post_router
from app.api.v2.routers import user_router as v2_user_router
from app.common.exception_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.common.exceptions import ForbiddenException
from app.middleware.logging_middleware import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Kakao TASK API",
    description="Kakao TASK API API v2",
    version="2.0.0",
    redirect_slashes=False,
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ForbiddenException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(v2_user_router.router)
app.include_router(v2_post_router.router)


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트

    Returns:
        dict: API 정보
    """
    return {
        "message": "Kakao TASK API API",
        "version": "v2",
        "base_url": "/api/v2",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
