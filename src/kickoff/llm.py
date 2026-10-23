"""One place that talks to Claude: structured output in, validated Pydantic model out."""

from __future__ import annotations

from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "high"

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Claude declined, ran out of room, or returned something that didn't fit the schema."""


class Claude:
    def __init__(self, client: anthropic.Anthropic | None = None, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT):
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.effort = effort

    def structured(self, system: str, prompt: str, schema: type[T], max_tokens: int = 64000) -> T:
        output_format = {"type": "json_schema", "schema": anthropic.transform_schema(schema.model_json_schema())}
        # Streaming keeps long contract extractions clear of HTTP timeouts.
        with self.client.beta.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": self.effort, "format": output_format},
            # If a safety classifier declines, retry server-side on Anthropic's recommended model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            message = stream.get_final_message()

        if message.stop_reason == "refusal":
            raise LLMError("Claude declined this request.")
        if message.stop_reason == "max_tokens":
            raise LLMError("The response hit the output limit. Try a shorter document or split it.")
        text = next((block.text for block in message.content if block.type == "text"), None)
        if text is None:
            raise LLMError("Claude returned no text.")
        try:
            return schema.model_validate_json(text)
        except ValidationError as e:
            raise LLMError(f"Claude's answer didn't match the expected structure: {e}") from e
