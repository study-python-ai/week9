from fastapi import FastAPI
from app.api.v1.routers import user_router, post_router

app = FastAPI(title="Kakao TASK API", description="Kakao TASK API", version="1.0.0")

app.include_router(user_router.router)
app.include_router(post_router.router)


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {"message": "Kakao TASK API ", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
