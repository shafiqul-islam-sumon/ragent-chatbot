from typing import Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class MemoryManager:
    def __init__(self):
        self.sessions: Dict[str, List[BaseMessage]] = {}

    def get(self, session_id: str = "default") -> List[BaseMessage]:
        """Returns message history for a given session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add(self, session_id: str, message: BaseMessage):
        """Appends a message to the session memory."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)

    def clear(self, session_id: str = "default"):
        """Clears memory for a given session."""
        if session_id in self.sessions:
            self.sessions[session_id] = []

    def list_sessions(self) -> List[str]:
        """Lists all active session IDs."""
        return list(self.sessions.keys())


if __name__ == "__main__":
    memory = MemoryManager()

    # Add messages to session "test1"
    memory.add("test1", HumanMessage(content="What's the weather today?"))
    memory.add("test1", AIMessage(content="It's sunny in Tokyo."))

    # Retrieve and print messages
    print("\n--- Chat history for 'test1' ---")
    for msg in memory.get("test1"):
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        print(f"{role}: {msg.content}")

    # List sessions
    print("\n--- Active Sessions ---")
    print(memory.list_sessions())

    # Clear session
    memory.clear("test1")
    print("\n--- Chat history after clearing ---")
    print(memory.get("test1"))
