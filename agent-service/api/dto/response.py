from pydantic import BaseModel


class QueryResponse(BaseModel):
    sql: str = ""
    sql_explanation: str = ""
    rows: list[dict] = []
    insight: str = ""
    viz_code: str = ""
    followup_questions: list[str] = []
    retries: int = 0
    queried_by: str = ""
    is_ambiguous: bool = False
    clarifying_question: str = ""
    is_sql_safe: bool = True
    safety_error: str = ""
    updated_history: list[dict] = []
