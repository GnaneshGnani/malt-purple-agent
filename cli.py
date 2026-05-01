import argparse
import os
from dataclasses import dataclass


@dataclass
class Args:
    model_name: str
    api_key: str | None
    api_base: str | None
    api_version: str | None
    host: str
    port: int
    card_url: str | None
    few_shot: bool


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Expose an LLM as an A2A-compatible purple agent for AgentBeats."
    )
    parser.add_argument("--model-name", type=str, default=None, help="LiteLLM model name")
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--api-base", type=str, default=None)
    parser.add_argument("--api-version", type=str, default=None)
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind")
    parser.add_argument("--card-url", type=str, default=None, help="Public URL for agent card")
    parser.add_argument(
        "--few-shot",
        action="store_true",
        help="Prepend the static MALT few-shot examples before the current query.",
    )
    args = parser.parse_args()
    return Args(**vars(args))


def resolve_default_model_name(args: Args) -> str:
    nebius_default = "openai/meta-llama/Llama-3.3-70B-Instruct"
    if args.model_name:
        return args.model_name
    env_model = os.environ.get("MODEL_NAME")
    if env_model:
        return env_model
    if os.environ.get("NEBIUS_API_KEY"):
        return nebius_default
    return "gpt-4o"
