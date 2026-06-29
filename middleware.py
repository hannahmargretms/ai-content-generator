import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ResponseTimingMiddleware(BaseHTTPMiddleware):
    """Adds response timing metrics to headers and request logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Process-Time-MS"] = f"{duration_ms:.2f}"
        logger.info(
            "%s %s completed in %.2fms with status %s",
            request.method,
            request.url.path,
            duration_ms,
            response.status_code,
        )
        return response
