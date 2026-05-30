import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URI = os.getenv("FAST_API_URL")
MAX_HISTORY_TURNS = 3

st.set_page_config(
    page_title="Datasense AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
 
    /* Root theme */
    :root {
        --bg-primary: #0d1117;
        --bg-card: #161b22;
        --bg-elevated: #1c2128;
        --accent: #58a6ff;
        --accent-green: #3fb950;
        --accent-orange: #d29922;
        --accent-red: #f85149;
        --text-primary: #e6edf3;
        --text-muted: #7d8590;
        --border: #30363d;
        --font-mono: 'JetBrains Mono', monospace;
        --font-body: 'Sora', sans-serif;
    }
 
    /* Global */
    html, body, [class*="css"] {
        font-family: var(--font-body);
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
 
    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
 
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary);
    }
 
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
 
    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-primary);
    }
 
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }
 
    /* Metric cards */
    .metric-card {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        font-family: var(--font-mono);
        font-size: 0.78rem;
        color: var(--text-muted);
    }
    .metric-card span {
        color: var(--accent);
        font-weight: 600;
    }
 
    /* Status badge */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: var(--font-mono);
        margin-right: 6px;
    }
    .badge-green { background: #1a3a1f; color: var(--accent-green); border: 1px solid var(--accent-green); }
    .badge-orange { background: #2d2208; color: var(--accent-orange); border: 1px solid var(--accent-orange); }
    .badge-red { background: #2d1117; color: var(--accent-red); border: 1px solid var(--accent-red); }
    .badge-blue { background: #0d2340; color: var(--accent); border: 1px solid var(--accent); }
 
    /* Logo area */
    .logo-text {
        font-family: var(--font-mono);
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--accent);
        letter-spacing: -0.5px;
    }
    .logo-sub {
        font-size: 0.72rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
        margin-top: -4px;
    }
 
    /* Expander */
    [data-testid="stExpander"] {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
 
    /* Divider */
    hr { border-color: var(--border); }
 
    /* Insight block */
    .insight-block {
        background: linear-gradient(135deg, #0d2340 0%, #161b22 100%);
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0;
        font-size: 0.92rem;
        line-height: 1.6;
    }
 
    /* Error block */
    .error-block {
        background: #2d1117;
        border-left: 3px solid var(--accent-red);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0;
        font-size: 0.88rem;
        font-family: var(--font-mono);
        color: var(--accent-red);
    }
 
    /* Suggestion chips */
    .stButton > button {
        background-color: var(--bg-elevated);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 20px;
        font-size: 0.78rem;
        font-family: var(--font-body);
        padding: 0.3rem 0.9rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
        background-color: #0d2340;
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "messages": [],  # full chat display history
        "history": [],  # last N turns sent to agent (context)
        "query_count": 0,
        "total_retries": 0,
        "last_query_meta": None,  # {rows, retries, duration_ms}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def call_agent(question: str) -> dict:
    """POST /query — returns raw response dict or raises."""
    payload = {
        "question": question,
        "conversation_history": st.session_state.history,
        "user_email": "demo@datasense.ai",
    }
    start = datetime.now()
    resp = httpx.post(
        f"{FASTAPI_URI}/query",
        json=payload,
        timeout=90,
    )
    resp.raise_for_status()
    data = resp.json()
    data["_duration_ms"] = int((datetime.now() - start).total_seconds() * 1000)
    return data


def render_chart(viz_code: str, rows: list):
    """Safely exec the Plotly Express string returned by the agent."""
    if not viz_code or not rows:
        return
    try:
        df = pd.DataFrame(rows)
        local_vars = {"df": df, "px": px, "pd": pd}
        exec(viz_code, local_vars)
        if "fig" in local_vars:
            fig = local_vars["fig"]
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e6edf3",
                font_family="Sora, sans-serif",
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"⚠️ Chart render failed: {exc}")


def render_assistant_response(data: dict):
    """Render insight, SQL expander, dataframe, chart, and meta badges."""
    rows = data.get("rows") or []
    sql = data.get("sql", "")
    insight = data.get("insight", "")
    viz_code = data.get("viz_code", "")
    retries = data.get("retries", 0)
    duration = data.get("_duration_ms", 0)
    error = data.get("error")

    if error:
        st.markdown(
            f'<div class="error-block">❌ Agent error: {error}</div>',
            unsafe_allow_html=True,
        )
        return

    badge_parts = []
    if retries == 0:
        badge_parts.append('<span class="badge badge-green">✓ First try</span>')
    else:
        badge_parts.append(
            f'<span class="badge badge-orange">⟳ {retries} correction(s)</span>'
        )

    if rows:
        badge_parts.append(f'<span class="badge badge-blue">{len(rows)} rows</span>')

    badge_parts.append(f'<span class="badge badge-blue">{duration}ms</span>')

    st.markdown(" ".join(badge_parts), unsafe_allow_html=True)

    if insight:
        st.markdown(
            f'<div class="insight-block">{insight}</div>',
            unsafe_allow_html=True,
        )

    if viz_code and rows:
        render_chart(viz_code, rows)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    if sql:
        with st.expander("🔍 View generated SQL"):
            st.code(sql, language="sql")


with st.sidebar:
    st.markdown('<div class="logo-text">⬡ DataSense AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="logo-sub">Natural Language → SQL → Insight</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    try:
        health = httpx.get(f"{FASTAPI_URI}/health", timeout=3)
        if health.status_code == 200:
            st.markdown(
                '<span class="badge badge-green">● Agent Online</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge badge-red">● Agent Error</span>',
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(
            '<span class="badge badge-red">● Agent Offline</span>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("**Session Stats**")
    st.markdown(
        f'<div class="metric-card">Queries: <span>{st.session_state.query_count}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="metric-card">Self-corrections: <span>{st.session_state.total_retries}</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.last_query_meta:
        meta = st.session_state.last_query_meta
        st.markdown(
            f'<div class="metric-card">Last query: <span>{meta["duration_ms"]}ms</span> · '
            f"<span>{meta['rows']} rows</span></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("**Try these**")
    suggestions = [
        "Top 10 customers by revenue",
        "Monthly revenue trend for 2024",
        "Orders by status breakdown",
        "Best selling products this quarter",
        "Average order value by category",
    ]
    for s in suggestions:
        if st.button(s, key=f"sugg_{s}"):
            st.session_state["_pending_question"] = s
            st.rerun()

    st.divider()

    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.query_count = 0
        st.session_state.total_retries = 0
        st.session_state.last_query_meta = None
        st.rerun()

    st.divider()
    st.markdown(
        "<span style=\"font-size:0.7rem;color:#7d8590;font-family:'JetBrains Mono',monospace;\">"
        "LangGraph · Groq · pgvector<br>FastAPI · Streamlit · PostgreSQL</span>",
        unsafe_allow_html=True,
    )

st.markdown("### Ask anything about your data")
st.caption("Powered by LangGraph · RAG · Groq llama-3.3-70b · pgvector")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_assistant_response(msg["data"])

pending = st.session_state.pop("_pending_question", None)
question = (
    st.chat_input("e.g. Top 5 customers by total orders this quarter...") or pending
)

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Querying agent..."):
            try:
                data = call_agent(question)
            except httpx.ConnectError:
                data = {
                    "error": "Cannot connect to agent service at localhost:8000. Is FastAPI running?"
                }
            except httpx.TimeoutException:
                data = {"error": "Agent timed out after 90 seconds."}
            except Exception as exc:
                data = {"error": str(exc)}

        render_assistant_response(data)

    st.session_state.messages.append({"role": "assistant", "data": data})
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append(
        {
            "role": "assistant",
            "content": data.get("insight", ""),
        }
    )
    st.session_state.history = st.session_state.history[-(MAX_HISTORY_TURNS * 2) :]

    if not data.get("error"):
        st.session_state.query_count += 1
        retries = data.get("retries", 0)
        st.session_state.total_retries += retries
        st.session_state.last_query_meta = {
            "duration_ms": data.get("_duration_ms", 0),
            "rows": len(data.get("rows") or []),
        }
