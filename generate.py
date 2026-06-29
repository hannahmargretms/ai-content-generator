import logging

from fastapi import APIRouter, Depends, status

from app.models.content import GenerateRequest, GenerateResponse
from app.services.groq_service import GroqContentService, GroqServiceError, get_groq_service
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter(tags=["content-generation"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI content",
    response_description="Generated content from the configured Groq model.",
    responses={
        400: {"description": "Invalid request, including an empty prompt."},
        429: {"description": "Rate limit exceeded."},
        502: {"description": "Groq API request failed."},
    },
)
async def generate_content(
    request: GenerateRequest,
    service: GroqContentService = Depends(get_groq_service),
) -> GenerateResponse:
    """Generate text from a prompt using the service layer."""
    logger.info("Received generation request", extra={"prompt_length": len(request.prompt)})

    try:
        generated_text = await service.generate_text(request.prompt)
    except GroqServiceError as exc:
        logger.warning("Groq generation failed: %s", exc)
        raise AppException(status_code=502, message=str(exc)) from exc

    return GenerateResponse(generated_text=generated_text, status="success")
