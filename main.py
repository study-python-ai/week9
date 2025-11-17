from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routers import post_router, user_router
from app.common.exception_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="Kakao TASK API", description="Kakao TASK API", version="1.0.0")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(user_router.router)
app.include_router(post_router.router)


@app.get("/", tags=["root"])
async def root():
    """
        루트 엔드포인트

    Returns:

        dict: 환영 메시지
    """
    return {"message": "Kakao TASK API ", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
