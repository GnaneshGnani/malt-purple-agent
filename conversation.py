MAX_HISTORY_MESSAGES = 20


class ConversationStore:
    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, str]]] = {}

    def load(self, context_id: str) -> list[dict[str, str]]:
        return list(self._store.get(context_id, []))

    def save(self, context_id: str, messages: list[dict[str, str]]) -> None:
        self._store[context_id] = messages[-MAX_HISTORY_MESSAGES:]


conversation_store = ConversationStore()
