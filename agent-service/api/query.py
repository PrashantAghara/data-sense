from fastapi import APIRouter
from agent.graph import agent
from agent.history import update_history
from api.dto.request import QueryRequest
from api.dto.response import QueryResponse

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
