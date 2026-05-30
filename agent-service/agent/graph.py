import agent.nodes as _nodes
from langgraph.graph import StateGraph, END
from agent.state import AgentState


def _ambiguity_detector(state):
    return _nodes.ambiguity_detector(state)


def _retrieve_schema(state):
    return _nodes.retrieve_schema(state)


def _generate_sql(state):
    return _nodes.generate_sql(state)


def _validate_sql(state):
    return _nodes.validate_sql(state)


def _execute_sql_node(state):
    return _nodes.execute_sql_node(state)


def _rewrite_sql(state):
    return _nodes.rewrite_sql(state)


def _explain_sql(state):
    return _nodes.explain_sql(state)


def _generate_insight(state):
    return _nodes.generate_insight(state)


def _generate_viz(state):
    return _nodes.generate_viz(state)


def _suggest_followups(state):
    return _nodes.suggest_followups(state)


# ── Conditional Edge Functions ────────────────────────────────────────────────


def route_ambiguity(state: AgentState) -> str:
    return "end_ambiguous" if state["is_ambiguous"] else "retrieve_schema"


def route_validation(state: AgentState) -> str:
    return "end_blocked" if not state["is_sql_safe"] else "execute_sql"


def route_execution(state: AgentState) -> str:
    if state.get("sql_error"):
        return (
            "rewrite_sql"
            if state.get("error_count", 0) < _nodes.MAX_RETRIES
            else "end_error"
        )
    return "explain_sql"


# ── Graph Assembly ────────────────────────────────────────────────────────────


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("ambiguity_detector", _ambiguity_detector)
    graph.add_node("retrieve_schema", _retrieve_schema)
    graph.add_node("generate_sql", _generate_sql)
    graph.add_node("validate_sql", _validate_sql)
    graph.add_node("execute_sql", _execute_sql_node)
    graph.add_node("rewrite_sql", _rewrite_sql)
    graph.add_node("explain_sql", _explain_sql)
    graph.add_node("generate_insight", _generate_insight)
    graph.add_node("generate_viz", _generate_viz)
    graph.add_node("suggest_followups", _suggest_followups)

    graph.set_entry_point("ambiguity_detector")

    graph.add_conditional_edges(
        "ambiguity_detector",
        route_ambiguity,
        {
            "end_ambiguous": END,
            "retrieve_schema": "retrieve_schema",
        },
    )
    graph.add_edge("retrieve_schema", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")

    graph.add_conditional_edges(
        "validate_sql",
        route_validation,
        {
            "end_blocked": END,
            "execute_sql": "execute_sql",
        },
    )
    graph.add_conditional_edges(
        "execute_sql",
        route_execution,
        {
            "rewrite_sql": "rewrite_sql",
            "end_error": END,
            "explain_sql": "explain_sql",
        },
    )
    graph.add_edge("rewrite_sql", "execute_sql")
    graph.add_edge("explain_sql", "generate_insight")
    graph.add_edge("generate_insight", "generate_viz")
    graph.add_edge("generate_viz", "suggest_followups")
    graph.add_edge("suggest_followups", END)

    return graph.compile()


# Compiled singleton — import this everywhere, never call build_graph() twice
agent = build_graph()
