import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """AOP 스타일 HTTP 요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]

        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Client: {client_host}"
        )

        start_time = time.time()

        try:
            response = await call_next(request)

            process_time = (time.time() - start_time) * 1000

            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            response.headers["X-Request-ID"] = request_id

            log_level = self._get_log_level(response.status_code)
            logger.log(
                log_level,
                f"[{request_id}] {request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.2f}ms"
            )

            return response

        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"ERROR: {str(e)} - {process_time:.2f}ms",
                exc_info=True
            )
            raise

    def _get_log_level(self, status_code: int) -> int:
        """상태 코드에 따른 로그 레벨 결정"""
        if status_code < 400:
            return logging.INFO
        elif status_code < 500:
            return logging.WARNING
        else:
            return logging.ERROR
