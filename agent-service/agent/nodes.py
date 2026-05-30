import re
import pandas as pd
from core.llm import llm
from agent.state import AgentState
from agent.history import format_history
from agent.prompts import (
    AMBIGUITY_PROMPT,
    SQL_PROMPT,
    SQL_EXPLAINER_PROMPT,
    SQL_REWRITER_PROMPT,
    INSIGHT_WRITER_PROMPT,
    VIZ_CODE_PROMPT,
    FOLLOWUP_PROMPT,
)
from agent.rag.retriever import retrieve_relevant_schema, get_all_tables
from agent.db.execute import execute_sql

MAX_RETRIES = 3
BLOCKED_KEYWORDS = ["insert", "update", "delete", "drop", "truncate", "alter", "create"]


# --- Node Functions
def ambiguity_detector(state: AgentState) -> AgentState:
    tables = get_all_tables()
    result = (
        (AMBIGUITY_PROMPT | llm)
        .invoke(
            {
                "question": state["question"],
                "tables": ", ".join(tables),
                "conversation_history": format_history(
                    state.get("conversation_history", [])
                ),
            }
        )
        .content.strip()
    )

    if result.upper().startswith("AMBIGUOUS"):
        clarifying = (
            result.split(":", 1)[-1].strip()
            if ":" in result
            else "Could you clarify your question?"
        )
        print(f"[Ambiguity] Clarification needed: {clarifying}")
        return {**state, "is_ambiguous": True, "clarifying_question": clarifying}

    print("[Ambiguity] CLEAR")
    return {**state, "is_ambiguous": False, "clarifying_question": ""}


def retrieve_schema(state: AgentState) -> AgentState:
    context = retrieve_relevant_schema(state["question"])
    print(f"[RAG] Retrieved {len(context)} chars")
    return {**state, "schema_context": context}


def generate_sql(state: AgentState) -> AgentState:
    sql_chain = SQL_PROMPT | llm
    sql = sql_chain.invoke(
        {
            "question": state["question"],
            "schema_context": state["schema_context"],
            "conversation_history": format_history(
                state.get("conversation_history", [])
            ),
        }
    ).content.strip()
    print(f"[SQL]\n{sql}")
    return {**state, "generated_sql": sql}


def validate_sql(state: AgentState) -> AgentState:
    lower = state["generated_sql"].lower()
    for keyword in BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lower):
            print(f"[Validator] BLOCKED — found keyword: {keyword}")
            return {
                **state,
                "is_sql_safe": False,
                "safety_error": f"Blocked keyword: {keyword}",
            }
    print("[Validator] SQL is safe.")
    return {**state, "is_sql_safe": True, "safety_error": ""}


def execute_sql_node(state: AgentState) -> AgentState:
    rows, error = execute_sql(state["generated_sql"])
    if error:
        print(f"[Execute] Error: {error}")
        return {
            **state,
            "sql_result": None,
            "sql_error": error,
            "error_count": state.get("error_count", 0) + 1,
        }
    if not rows:
        print("[Execute] Query returned 0 rows.")
        return {**state, "sql_result": [], "sql_error": None}
    print(f"[Execute] {len(rows)} rows returned.")
    return {**state, "sql_result": rows, "sql_error": None}


def rewrite_sql(state: AgentState) -> AgentState:
    print(f"[Rewrite] Attempt {state['error_count']}...")
    rewriter_chain = SQL_REWRITER_PROMPT | llm
    sql = rewriter_chain.invoke(
        {
            "schema_context": state["schema_context"],
            "failed_sql": state["generated_sql"],
            "db_error": state["sql_error"],
            "question": state["question"],
        }
    ).content.strip()
    print(f"[Rewrite] New SQL:\n{sql}")
    return {**state, "generated_sql": sql, "sql_error": None}


def explain_sql(state: AgentState) -> AgentState:
    if not state.get("generated_sql"):
        return {**state, "sql_explanation": "No SQL was generated."}
    explanation = (
        (SQL_EXPLAINER_PROMPT | llm)
        .invoke({"sql": state["generated_sql"]})
        .content.strip()
    )
    print(f"[Explain] {explanation}")
    return {**state, "sql_explanation": explanation}


def generate_insight(state: AgentState) -> AgentState:
    if not state.get("sql_result"):
        return {**state, "insight": "No results to analyse."}
    insight_text = (
        (INSIGHT_WRITER_PROMPT | llm)
        .invoke(
            {
                "question": state["question"],
                "sql_results": str(state["sql_result"][:20]),
            }
        )
        .content.strip()
    )
    print(f"[Insight] {insight_text}")
    return {**state, "insight": insight_text}


def generate_viz(state: AgentState) -> AgentState:
    rows = state.get("sql_result") or []
    if not rows:
        return {**state, "viz_code": ""}

    columns = list(rows[0].keys()) if rows else []

    chain = VIZ_CODE_PROMPT | llm
    result = chain.invoke(
        {
            "question": state["question"],
            "columns": ", ".join(columns),
        }
    )
    return {**state, "viz_code": result.content.strip()}


def suggest_followups(state: AgentState) -> AgentState:
    if not state.get("sql_result"):
        return {**state, "followup_questions": []}
    df = pd.DataFrame(state["sql_result"])
    raw = (
        (FOLLOWUP_PROMPT | llm)
        .invoke(
            {
                "question": state["question"],
                "insight": state["insight"],
                "columns": list(df.columns),
            }
        )
        .content.strip()
    )
    try:
        followups = eval(raw)
    except Exception:
        followups = [raw]
    print(f"[Follow-ups] {followups}")
    return {**state, "followup_questions": followups}
