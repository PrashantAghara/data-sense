from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    MAX_RETRIES,
    ambiguity_detector,
    retrieve_schema,
    generate_sql,
    validate_sql,
    execute_sql_node,
    rewrite_sql,
    explain_sql,
    generate_insight,
    generate_viz,
    suggest_followups,
)


# -- Conditional Edges
def route_ambiguity(state: AgentState) -> str:
    return "end_ambiguous" if state["is_ambiguous"] else "retrieve_schema"


def route_validation(state: AgentState) -> str:
    return "end_blocked" if not state["is_sql_safe"] else "execute_sql"


def route_execution(state: AgentState) -> str:
    if state.get("sql_error"):
        return (
            "rewrite_sql" if state.get("error_count", 0) < MAX_RETRIES else "end_error"
        )
    return "explain_sql"


# -- Graphs
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("ambiguity_detector", ambiguity_detector)
    graph.add_node("retrieve_schema", retrieve_schema)
    graph.add_node("generate_sql", generate_sql)
    graph.add_node("validate_sql", validate_sql)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("rewrite_sql", rewrite_sql)
    graph.add_node("explain_sql", explain_sql)
    graph.add_node("generate_insight", generate_insight)
    graph.add_node("generate_viz", generate_viz)
    graph.add_node("suggest_followups", suggest_followups)

    graph.set_entry_point("ambiguity_detector")

    graph.add_conditional_edges(
        "ambiguity_detector",
        route_ambiguity,
        {"end_ambiguous": END, "retrieve_schema": "retrieve_schema"},
    )

    graph.add_edge("retrieve_schema", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")

    graph.add_conditional_edges(
        "validate_sql",
        route_validation,
        {"end_blocked": END, "execute_sql": "execute_sql"},
    )

    graph.add_conditional_edges(
        "execute_sql",
        route_execution,
        {"rewrite_sql": "rewrite_sql", "end_error": END, "explain_sql": "explain_sql"},
    )

    graph.add_edge("rewrite_sql", "execute_sql")
    graph.add_edge("explain_sql", "generate_insight")
    graph.add_edge("generate_insight", "generate_viz")
    graph.add_edge("generate_viz", "suggest_followups")
    graph.add_edge("suggest_followups", END)

    return graph.compile()


agent = build_graph()
