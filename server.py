from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from loguru import logger

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from cli import parse_args, resolve_default_model_name
from executor import LiteLLMAgentExecutor
from litellm_backend import LiteLLMAgent


def main() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    args = parse_args()

    server_url = args.card_url or f"http://{args.host}:{args.port}/"

    skill = AgentSkill(
        id="malt_purple_agent",
        name="MALT Purple Agent",
        description="No-helper MALT purple agent using LiteLLM.",
        tags=["llm", "litellm", "malt", "netarena"],
    )

    agent_card = AgentCard(
        name="MALT Purple Agent",
        description="A2A-compatible NetArena MALT purple agent using a no-helper safety/few-shot prompt.",
        url=server_url,
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    model_name = resolve_default_model_name(args)
    agent = LiteLLMAgent(
        model_name=model_name,
        api_key=args.api_key,
        api_base=args.api_base,
        api_version=args.api_version,
    )
    executor = LiteLLMAgentExecutor(agent)
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)

    logger.info(f"Starting A2A server on {args.host}:{args.port}")
    uvicorn.run(app.build(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
