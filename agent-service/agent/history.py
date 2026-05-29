def trim_history(history: list, max_turns: int = 3) -> list:
    """Keep only the last N turns (1 turn = 1 user + 1 assistant message)."""
    return history[-(max_turns * 2) :]


def format_history(history: list) -> str:
    """Format history list into a readable string for LLM prompts."""
    if not history:
        return "No previous conversation."
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history)


def update_history(history: list, question: str, insight: str) -> list:
    """Append the latest turn and trim to max_turns."""
    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": insight},
    ]
    return trim_history(history)
