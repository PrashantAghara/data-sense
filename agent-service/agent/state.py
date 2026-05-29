from typing import TypedDict, Optional


class AgentState(TypedDict):
    question: str
    conversation_history: list[dict]

    # Ambiguity Node
    is_ambiguous: bool
    clarifying_question: str

    # RAG - schema context
    schema_context: str

    # SQL Lifecycle
    generated_sql: str
    sql_explanation: str
    is_sql_safe: bool
    safety_error: str
    sql_result: Optional[list[dict]]
    sql_error: Optional[str]
    error_count: int

    # Output
    insight: str
    viz_code: str
    followup_questions: list[str]

    # Final Response
    response: str
