import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class InMemoryRateLimiter:
    """Simple fixed-window limiter suitable for one-process deployments and tests."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow_request(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window_seconds

        with self._lock:
            timestamps = self._requests[key]
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)
            return True


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit requests by client IP address."""

    def __init__(
        self,
        app,
        max_requests: int,
        window_seconds: int,
        excluded_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(max_requests, window_seconds)
        self.excluded_paths = excluded_paths or set()

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"

        if not self.limiter.allow_request(key):
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Rate limit exceeded. Please try again later.",
                },
            )

        return await call_next(request)
