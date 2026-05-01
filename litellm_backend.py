from __future__ import annotations

import os

import litellm
from litellm import acompletion
from litellm import (
    CustomStreamWrapper,
    ModelResponse,
    ModelResponseStream,
)

from output import validate_malt_output
from prompts import (
    MALT_FEW_SHOT_TURNS,
    MALT_RETRY_PROMPT,
    MALT_SYSTEM_PROMPT,
)


class LiteLLMAgent:
    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
        few_shot: bool = False,
    ):
        self.model_name = model_name
        self.few_shot = few_shot
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
        user_content: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": MALT_SYSTEM_PROMPT}]
        if self.few_shot:
            for ex in MALT_FEW_SHOT_TURNS:
                messages.append({"role": "user", "content": ex["user"]})
                messages.append({"role": "assistant", "content": ex["assistant"]})
        messages.append({"role": "user", "content": user_content})
        return messages

    async def invoke(
        self,
        input_text: str,
    ) -> str:
        messages = self._build_base_messages(input_text)
        result = await self._stream_to_text(messages)

        if validate_malt_output(result):
            return result
        retry_messages = messages + [
            {"role": "assistant", "content": result},
            {"role": "user", "content": MALT_RETRY_PROMPT},
        ]
        return await self._stream_to_text(retry_messages)
