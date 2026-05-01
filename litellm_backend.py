from __future__ import annotations

import os

import litellm
from litellm import acompletion
from litellm import (
    CustomStreamWrapper,
    ModelResponse,
    ModelResponseStream,
)

from output import validate_malt_output, validate_route_output
from prompts import (
    MALT_FEW_SHOT_TURNS,
    MALT_RETRY_PROMPT,
    ROUTE_FEW_SHOT_TURNS,
    ROUTE_RETRY_PROMPT,
    SYSTEM_PROMPTS,
)


class LiteLLMAgent:
    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
    ):
        self.model_name = model_name
        if api_key is not None:
            self.api_key = api_key
        elif os.environ.get("NEBIUS_API_KEY"):
            self.api_key = os.environ["NEBIUS_API_KEY"]
        elif os.environ.get("AZURE_API_KEY"):
            self.api_key = os.environ["AZURE_API_KEY"]
        elif os.environ.get("OPENAI_API_KEY"):
            self.api_key = os.environ["OPENAI_API_KEY"]
        else:
            self.api_key = None

        if api_base is not None:
            self.api_base = api_base
        elif self.api_key and self.api_key == os.environ.get("NEBIUS_API_KEY"):
            self.api_base = os.environ.get("NEBIUS_API_BASE") or "https://api.studio.nebius.ai/v1/"
        else:
            self.api_base = os.environ.get("AZURE_API_BASE")

        self.api_version = api_version or os.environ.get("AZURE_API_VERSION", "2024-12-01-preview")

    async def _stream_to_text(self, messages: list[dict[str, str]]) -> str:
        response = await acompletion(
            self.model_name,
            messages,
            stream=True,
            api_key=self.api_key,
            base_url=self.api_base,
            api_version=self.api_version,
        )
        if isinstance(response, CustomStreamWrapper):
            chunks = [chunk async for chunk in response]
            response = litellm.stream_chunk_builder(chunks, messages=messages)
        if isinstance(response, ModelResponseStream):
            return response.choices[0].delta.content or ""
        if isinstance(response, ModelResponse):
            return response.choices[0].message.content or ""
        return ""

    def _build_base_messages(
        self,
        benchmark: str | None,
        history: list[dict[str, str]],
        user_content: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if benchmark and benchmark in SYSTEM_PROMPTS:
            messages.append({"role": "system", "content": SYSTEM_PROMPTS[benchmark]})
        if benchmark == "route":
            for ex in ROUTE_FEW_SHOT_TURNS:
                messages.append({"role": "user", "content": ex["user"]})
                messages.append({"role": "assistant", "content": ex["assistant"]})
        if benchmark == "malt":
            for ex in MALT_FEW_SHOT_TURNS:
                messages.append({"role": "user", "content": ex["user"]})
                messages.append({"role": "assistant", "content": ex["assistant"]})
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})
        return messages

    async def invoke(
        self,
        input_text: str,
        benchmark: str | None,
        history: list[dict[str, str]],
    ) -> str:
        messages = self._build_base_messages(benchmark, history, input_text)
        result = await self._stream_to_text(messages)

        if benchmark == "route":
            ok, cleaned = validate_route_output(result)
            if ok and cleaned is not None:
                return cleaned
            retry_messages = messages + [
                {"role": "assistant", "content": result},
                {"role": "user", "content": ROUTE_RETRY_PROMPT},
            ]
            result2 = await self._stream_to_text(retry_messages)
            ok2, cleaned2 = validate_route_output(result2)
            if ok2 and cleaned2 is not None:
                return cleaned2
            return result2

        if benchmark == "malt":
            if validate_malt_output(result):
                return result
            retry_messages = messages + [
                {"role": "assistant", "content": result},
                {"role": "user", "content": MALT_RETRY_PROMPT},
            ]
            result2 = await self._stream_to_text(retry_messages)
            return result2

        return result
