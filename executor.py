from loguru import logger
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

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
        result = await self.agent.invoke(input_text)
        logger.info(f"LLM response length: {len(result)} chars")

        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")
