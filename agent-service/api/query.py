import json
from fastapi import APIRouter
from agent.graph import agent
from agent.history import update_history
from api.dto.request import QueryRequest
from api.dto.response import QueryResponse
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def run_query(req: QueryRequest):
    result = agent.invoke(
        {
            "question": req.question,
            "conversation_history": req.conversation_history,
            "error_count": 0,
            "is_ambiguous": False,
            "is_sql_safe": True,
        }
    )

    updated_history = req.conversation_history
    if not result.get("is_ambiguous") and result.get("sql_result"):
        updated_history = update_history(
            req.conversation_history, req.question, result.get("insight", "")
        )

    return QueryResponse(
        sql=result.get("generated_sql", ""),
        sql_explanation=result.get("sql_explanation", ""),
        rows=result.get("sql_result") or [],
        insight=result.get("insight", ""),
        viz_code=result.get("viz_code", ""),
        followup_questions=result.get("followup_questions", []),
        retries=result.get("error_count", 0),
        queried_by=req.user_email,
        is_ambiguous=result.get("is_ambiguous", False),
        clarifying_question=result.get("clarifying_question", ""),
        is_sql_safe=result.get("is_sql_safe", True),
        safety_error=result.get("safety_error", ""),
        updated_history=updated_history,
    )


# ---- Streaming response ----

NODE_LABELS = {
    "ambiguity_detector": ("🤔", "Checking question clarity"),
    "retrieve_schema": ("🗄️", "Fetching database schema"),
    "generate_sql": ("⚙️", "Generating SQL query"),
    "validate_sql": ("🛡️", "Validating SQL safety"),
    "execute_sql": ("⚡", "Executing SQL query"),
    "rewrite_sql": ("✏️", "Rewriting SQL (retry)"),
    "explain_sql": ("💬", "Explaining the query"),
    "generate_insight": ("💡", "Generating insights"),
    "generate_viz": ("📊", "Building visualization"),
    "suggest_followups": ("📋", "Suggesting follow-ups"),
}


async def _stream_query(req: QueryRequest):
    """Generator that yields SSE events while the graph runs node-by-node."""
    initial_state = {
        "question": req.question,
        "conversation_history": req.conversation_history,
        "error_count": 0,
        "is_ambiguous": False,
        "is_sql_safe": True,
    }

    final_state = {}
    for chunk in agent.stream(initial_state, stream_mode="updates"):
        for node_name, node_output in chunk.items():
            icon, label = NODE_LABELS.get(
                node_name, ("▸", node_name.replace("_", " ").title())
            )
            event = {
                "type": "node_update",
                "node": node_name,
                "icon": icon,
                "label": label,
            }
            yield f"event: node_update\ndata: {json.dumps(event)}\n\n"
            final_state.update(node_output)

    updated_history = req.conversation_history
    if not final_state.get("is_ambiguous") and final_state.get("sql_result"):
        updated_history = update_history(
            req.conversation_history,
            req.question,
            final_state.get("insight", ""),
        )

    response = QueryResponse(
        sql=final_state.get("generated_sql", ""),
        sql_explanation=final_state.get("sql_explanation", ""),
        rows=final_state.get("sql_result") or [],
        insight=final_state.get("insight", ""),
        viz_code=final_state.get("viz_code", ""),
        followup_questions=final_state.get("followup_questions", []),
        retries=final_state.get("error_count", 0),
        queried_by=req.user_email,
        is_ambiguous=final_state.get("is_ambiguous", False),
        clarifying_question=final_state.get("clarifying_question", ""),
        is_sql_safe=final_state.get("is_sql_safe", True),
        safety_error=final_state.get("safety_error", ""),
        updated_history=updated_history,
    )

    yield f"event: result\ndata: {response.model_dump_json()}\n\n"


@router.post("/stream")
async def stream_query(req: QueryRequest):
    return StreamingResponse(
        _stream_query(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
