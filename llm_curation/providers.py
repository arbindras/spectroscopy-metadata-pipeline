from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any


DEFAULT_MODELS = {
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-5.5",
}


class CurationError(RuntimeError):
    pass


@dataclass
class Completion:
    data: dict[str, Any]
    model: str
    input_tokens: int | None
    output_tokens: int | None
    stop_reason: str | None


def load_dotenv_if_present(*directories) -> None:
    """Pick up ANTHROPIC_API_KEY / OPENAI_API_KEY from a .env file."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for directory in directories:
        path = os.path.join(str(directory), ".env")
        if os.path.isfile(path):
            load_dotenv(path, override=False)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, model: str | None = None, effort: str = "high", max_output_tokens: int = 32000):
        import anthropic

        self._anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=4)
        self.model = model or DEFAULT_MODELS["anthropic"]
        self.effort = effort
        self.max_output_tokens = max_output_tokens

    def complete(self, system: str, user: str, schema: dict[str, Any]) -> Completion:
        anthropic = self._anthropic
        try:
            # Streaming avoids HTTP timeouts on long packs; the stable system
            # prompt + examples is cached across records of a batch.
            # "fallbacks": a safety-classifier decline is retried server-side
            # on a fallback model instead of returning an empty record.
            with self.client.beta.messages.stream(
                model=self.model,
                max_tokens=self.max_output_tokens,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                thinking={"type": "adaptive"},
                output_config={
                    "effort": self.effort,
                    "format": {"type": "json_schema", "schema": schema},
                },
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user}],
            ) as stream:
                message = stream.get_final_message()
        except anthropic.BadRequestError as exc:
            raise CurationError(f"Claude rejected the request: {exc.message}") from exc
        except anthropic.AuthenticationError as exc:
            raise CurationError("Invalid ANTHROPIC_API_KEY") from exc
        except anthropic.APIStatusError as exc:
            raise CurationError(f"Claude API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise CurationError(f"Network error talking to Claude: {exc}") from exc

        if message.stop_reason == "refusal":
            raise CurationError("Claude declined the request (stop_reason=refusal)")
        if message.stop_reason == "max_tokens":
            raise CurationError("Output hit max_output_tokens; raise llm.max_output_tokens")
        text = next((block.text for block in message.content if block.type == "text"), "")
        return Completion(
            data=json.loads(text),
            model=message.model,
            input_tokens=getattr(message.usage, "input_tokens", None),
            output_tokens=getattr(message.usage, "output_tokens", None),
            stop_reason=message.stop_reason,
        )


class OpenAIProvider:
    name = "openai"

    def __init__(self, model: str | None = None, effort: str = "high", max_output_tokens: int = 32000):
        import openai

        self._openai = openai
        self.client = openai.OpenAI(max_retries=4, timeout=900)
        self.model = model or DEFAULT_MODELS["openai"]
        self.effort = effort
        self.max_output_tokens = max_output_tokens

    def complete(self, system: str, user: str, schema: dict[str, Any]) -> Completion:
        openai = self._openai
        request = dict(
            model=self.model,
            instructions=system,
            input=user,
            max_output_tokens=self.max_output_tokens,
            text={"format": {"type": "json_schema", "name": "curated_record", "schema": schema, "strict": True}},
        )
        if self.effort:
            request["reasoning"] = {"effort": self.effort}
        try:
            try:
                response = self.client.responses.create(**request)
            except openai.BadRequestError as exc:
                # Non-reasoning models reject the reasoning parameter.
                if "reasoning" not in str(exc).lower():
                    raise
                request.pop("reasoning", None)
                response = self.client.responses.create(**request)
        except openai.AuthenticationError as exc:
            raise CurationError("Invalid OPENAI_API_KEY") from exc
        except openai.APIStatusError as exc:
            raise CurationError(f"OpenAI API error {exc.status_code}: {exc.message}") from exc
        except openai.APIConnectionError as exc:
            raise CurationError(f"Network error talking to OpenAI: {exc}") from exc

        if getattr(response, "status", None) == "incomplete":
            reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
            raise CurationError(f"OpenAI response incomplete ({reason}); raise llm.max_output_tokens")
        usage = getattr(response, "usage", None)
        return Completion(
            data=json.loads(response.output_text),
            model=response.model,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            stop_reason=getattr(response, "status", None),
        )


def make_provider(name: str, model: str | None = None, effort: str = "high", max_output_tokens: int = 32000):
    name = (name or "").lower()
    if name in {"anthropic", "claude"}:
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise CurationError("Set ANTHROPIC_API_KEY (environment or .env) to use Claude")
        return AnthropicProvider(model, effort, max_output_tokens)
    if name in {"openai", "gpt"}:
        if not os.environ.get("OPENAI_API_KEY"):
            raise CurationError("Set OPENAI_API_KEY (environment or .env) to use OpenAI")
        return OpenAIProvider(model, effort, max_output_tokens)
    raise CurationError(f"Unknown provider {name!r}; use 'anthropic' or 'openai'")


def complete_with_retry(provider, system: str, user: str, schema: dict[str, Any], attempts: int = 3) -> Completion:
    """Retry malformed JSON / transient failures (SDK already retries 429/5xx)."""
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return provider.complete(system, user, schema)
        except json.JSONDecodeError as exc:
            last = exc
        except CurationError as exc:
            last = exc
            if "Invalid" in str(exc) or "rejected" in str(exc) or "max_output_tokens" in str(exc):
                raise
        time.sleep(5 * (attempt + 1))
    raise CurationError(f"Failed after {attempts} attempts: {last}")
