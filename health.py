from fastapi import APIRouter

from app.models.content import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    response_description="Service health status.",
)
async def health_check() -> HealthResponse:
    """Return a lightweight health signal for load balancers and uptime checks."""
    return HealthResponse(status="healthy")
