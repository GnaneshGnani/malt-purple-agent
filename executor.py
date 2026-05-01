from loguru import logger
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from conversation import conversation_store
from litellm_backend import LiteLLMAgent


class LiteLLMAgentExecutor(AgentExecutor):
    def __init__(self, agent: LiteLLMAgent):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        input_text = context.get_user_input()

        context_id: str | None = None
        msg = getattr(context, "message", None)
        if msg is not None:
            context_id = getattr(msg, "context_id", None)
        if context_id is None:
            context_id = getattr(context, "context_id", None)
        if context_id is not None:
            context_id = str(context_id)

        history: list[dict[str, str]] = []
        if context_id:
            history = conversation_store.load(context_id)

        result = await self.agent.invoke(input_text, history)
        logger.info(f"LLM response length: {len(result)} chars")

        if context_id:
            new_hist = history + [
                {"role": "user", "content": input_text},
                {"role": "assistant", "content": result},
            ]
            conversation_store.save(context_id, new_hist)

        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")
