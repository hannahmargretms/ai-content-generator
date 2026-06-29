import asyncio
import logging
from functools import lru_cache

from groq import APIConnectionError, APIStatusError, Groq, RateLimitError

from app.utils.config import Settings, get_settings

logger = logging.getLogger(__name__)


class GroqServiceError(RuntimeError):
    """Raised when content generation fails in the Groq service layer."""


class GroqContentService:
    """Encapsulates all Groq SDK interactions for easier testing and maintenance."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Groq | None = None

    @property
    def client(self) -> Groq:
        if not self.settings.groq_api_key:
            raise GroqServiceError("Groq API key is not configured. Set GROQ_API_KEY in your .env file.")

        if self._client is None:
            self._client = Groq(api_key=self.settings.groq_api_key)

        return self._client

    async def generate_text(self, prompt: str) -> str:
        """Generate text using Groq chat completions without blocking the event loop."""
        try:
            completion = await asyncio.to_thread(self._create_completion, prompt)
        except RateLimitError as exc:
            raise GroqServiceError("Groq API rate limit exceeded. Please try again later.") from exc
        except APIConnectionError as exc:
            raise GroqServiceError("Unable to connect to the Groq API.") from exc
        except APIStatusError as exc:
            raise GroqServiceError(f"Groq API returned an error: {exc.status_code}") from exc
        except Exception as exc:
            logger.exception("Unexpected Groq SDK error")
            raise GroqServiceError("Unexpected error while generating content.") from exc

        generated_text = completion.choices[0].message.content
        if not generated_text:
            raise GroqServiceError("Groq returned an empty response.")

        return generated_text.strip()

    def _create_completion(self, prompt: str):
        return self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI content generator. Produce clear, useful, and concise text.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.settings.groq_temperature,
            max_tokens=self.settings.groq_max_tokens,
        )


@lru_cache
def get_groq_service() -> GroqContentService:
    return GroqContentService(get_settings())
