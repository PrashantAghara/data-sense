import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.getenv("FAST_API_URL", "http://localhost:8000")
MAX_HISTORY_TURNS = 3
HISTORY_FILE = Path("chat_history.json")

st.set_page_config(
    page_title="DataSense AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

    :root {
        --bg-primary: #0d1117;
        --bg-card: #161b22;
        --bg-elevated: #1c2128;
        --accent: #58a6ff;
        --accent-green: #3fb950;
        --accent-orange: #d29922;
        --accent-red: #f85149;
        --accent-purple: #bc8cff;
        --text-primary: #e6edf3;
        --text-muted: #7d8590;
        --border: #30363d;
        --font-mono: 'JetBrains Mono', monospace;
        --font-body: 'Sora', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--font-body);
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    [data-testid="stSidebar"] {
        background-color: var(--bg-card);
        border-right: 1px solid var(--border);
    }

    [data-testid="stChatMessage"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 8px;
    }

    hr { border-color: var(--border); }

    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: var(--font-mono);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-green  { background: #1a3a1f; color: var(--accent-green);  border: 1px solid var(--accent-green); }
    .badge-orange { background: #2d2208; color: var(--accent-orange); border: 1px solid var(--accent-orange); }
    .badge-red    { background: #2d1117; color: var(--accent-red);    border: 1px solid var(--accent-red); }
    .badge-blue   { background: #0d2340; color: var(--accent);        border: 1px solid var(--accent); }
    .badge-purple { background: #1e1040; color: var(--accent-purple); border: 1px solid var(--accent-purple); }

    .insight-block {
        background: linear-gradient(135deg, #0d2340 0%, #161b22 100%);
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .explanation-block {
        background: #161b22;
        border-left: 3px solid var(--accent-purple);
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        font-size: 0.86rem;
        line-height: 1.6;
        color: var(--text-muted);
    }

    .clarify-block {
        background: #2d2208;
        border-left: 3px solid var(--accent-orange);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #e3b341;
    }

    .safety-block {
        background: #2d1117;
        border-left: 3px solid var(--accent-red);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0;
        font-size: 0.88rem;
        font-family: var(--font-mono);
        color: var(--accent-red);
    }

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

    .followup-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
        margin-top: 1rem;
        margin-bottom: 0.4rem;
    }

    .metric-card {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.65rem 1rem;
        margin-bottom: 0.4rem;
        font-family: var(--font-mono);
        font-size: 0.76rem;
        color: var(--text-muted);
    }
    .metric-card span { color: var(--accent); font-weight: 600; }

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


# ── Node metadata ──────────────────────────────────────────────────────────────
NODE_META = {
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

# What to show inside each st.status step as a detail line
NODE_DETAIL = {
    "ambiguity_detector": "Analysing question intent and checking if clarification is needed…",
    "retrieve_schema": "Running RAG over pgvector to pull relevant table schemas…",
    "generate_sql": "Prompting Groq llama-3.3-70b to write the SQL query…",
    "validate_sql": "Scanning for destructive keywords (INSERT / DROP / DELETE…)",
    "execute_sql": "Running query against PostgreSQL…",
    "rewrite_sql": "SQL failed — asking LLM to self-correct and retry…",
    "explain_sql": "Generating a plain-English explanation of the SQL…",
    "generate_insight": "Summarising result rows into a key business insight…",
    "generate_viz": "Writing Plotly visualisation code for the result set…",
    "suggest_followups": "Generating 3 follow-up questions based on the insight…",
}


# ── Persist chat history ───────────────────────────────────────────────────────
def save_messages():
    try:
        HISTORY_FILE.write_text(
            json.dumps(st.session_state.messages, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def load_messages():
    try:
        if HISTORY_FILE.exists():
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


# ── Session state init ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": load_messages(),
        "history": [],
        "query_count": 0,
        "total_retries": 0,
        "last_query_meta": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ── SSE streaming call with st.status() steps ─────────────────────────────────
def call_agent_streaming(question: str) -> dict:
    """
    Streams /query/stream and renders each node as a live st.status() block —
    exactly like Claude's tool-use UI: spinning while active, ticked when done.
    Returns the final result dict.
    """
    payload = {
        "question": question,
        "conversation_history": st.session_state.history,
        "user_email": "demo@datasense.ai",
    }

    start = datetime.now()
    data = {}

    # One st.status container per node that actually fires.
    # We open it when the node starts, close it (complete) when the next starts.
    active_status = None  # the currently open st.status context
    active_node = None  # key of the currently running node

    with httpx.Client(timeout=120) as client:
        with client.stream("POST", f"{FASTAPI_URL}/query/stream", json=payload) as resp:
            resp.raise_for_status()

            buffer = ""
            for raw_chunk in resp.iter_text():
                buffer += raw_chunk

                while "\n\n" in buffer:
                    event_str, buffer = buffer.split("\n\n", 1)
                    if not event_str.strip():
                        continue

                    event_type = ""
                    event_data = ""
                    for line in event_str.splitlines():
                        if line.startswith("event: "):
                            event_type = line[7:].strip()
                        elif line.startswith("data: "):
                            event_data = line[6:].strip()

                    if not event_data:
                        continue

                    parsed = json.loads(event_data)

                    # ── node_update: a new node just started ───────────────
                    if event_type == "node_update":
                        node_key = parsed.get("node", "")

                        # Close the previous st.status as complete
                        if active_status is not None:
                            active_status.update(state="complete", expanded=False)

                        icon, label = NODE_META.get(node_key, ("▸", node_key))
                        detail = NODE_DETAIL.get(node_key, "")

                        # Open a new st.status — starts spinning automatically
                        active_status = st.status(f"{icon} {label}", expanded=True)
                        active_status.markdown(
                            f"<span style='font-size:0.82rem;color:#7d8590;'>{detail}</span>",
                            unsafe_allow_html=True,
                        )
                        active_node = node_key

                    # ── result: stream finished, final payload arrived ──────
                    elif event_type == "result":
                        if active_status is not None:
                            active_status.update(state="complete", expanded=False)
                        data = parsed

    data["_duration_ms"] = int((datetime.now() - start).total_seconds() * 1000)
    return data


# ── Fallback: plain POST (if /query/stream not yet deployed) ──────────────────
def call_agent_plain(question: str) -> dict:
    payload = {
        "question": question,
        "conversation_history": st.session_state.history,
        "user_email": "demo@datasense.ai",
    }
    start = datetime.now()
    resp = httpx.post(f"{FASTAPI_URL}/query", json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    data["_duration_ms"] = int((datetime.now() - start).total_seconds() * 1000)
    return data


# ── Helper: render chart ──────────────────────────────────────────────────────
def render_chart(viz_code: str, rows: list):
    if not viz_code or not rows:
        return
    try:
        df = pd.DataFrame(rows)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        local_vars = {"df": df, "px": px, "pd": pd}
        exec(viz_code, local_vars)  # noqa: S102
        if "fig" in local_vars:
            fig = local_vars["fig"]
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e6edf3",
                font_family="Sora, sans-serif",
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"⚠️ Chart render failed: {exc}")


# ── Helper: render final assistant response ────────────────────────────────────
def render_assistant_response(data: dict):
    if data.get("error"):
        st.markdown(
            f'<div class="error-block">❌ {data["error"]}</div>',
            unsafe_allow_html=True,
        )
        return

    if not data.get("is_sql_safe", True):
        st.markdown(
            f'<div class="safety-block">🚫 Query blocked — {data.get("safety_error", "unsafe SQL detected")}</div>',
            unsafe_allow_html=True,
        )
        return

    if data.get("is_ambiguous") and data.get("clarifying_question"):
        st.markdown(
            f'<div class="clarify-block">🤔 {data["clarifying_question"]}</div>',
            unsafe_allow_html=True,
        )
        return

    rows = data.get("rows") or []
    sql = data.get("sql", "")
    sql_exp = data.get("sql_explanation", "")
    insight = data.get("insight", "")
    viz_code = data.get("viz_code", "")
    retries = data.get("retries", 0)
    duration = data.get("_duration_ms", 0)
    followups = data.get("followup_questions") or []

    badges = []
    if retries == 0:
        badges.append('<span class="badge badge-green">✓ First try</span>')
    else:
        badges.append(
            f'<span class="badge badge-orange">⟳ {retries} self-correction(s)</span>'
        )
    if rows:
        badges.append(f'<span class="badge badge-blue">{len(rows)} rows</span>')
    badges.append(f'<span class="badge badge-blue">{duration} ms</span>')
    badges.append('<span class="badge badge-green">✓ SQL safe</span>')
    st.markdown(" ".join(badges), unsafe_allow_html=True)

    if insight:
        st.markdown(
            f'<div class="insight-block">💡 {insight}</div>', unsafe_allow_html=True
        )

    if viz_code and rows:
        render_chart(viz_code, rows)

    if rows:
        df = pd.DataFrame(rows)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        st.dataframe(df, use_container_width=True, hide_index=True)

    if sql:
        with st.expander("🔍 View generated SQL"):
            st.code(sql, language="sql")
            if sql_exp:
                st.markdown(
                    f'<div class="explanation-block">📖 {sql_exp}</div>',
                    unsafe_allow_html=True,
                )

    if followups:
        st.markdown(
            '<div class="followup-label">💬 You might also ask:</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(len(followups))
        for i, fq in enumerate(followups):
            with cols[i]:
                if st.button(fq, key=f"fq_{hash(fq)}_{data.get('_duration_ms', 0)}"):
                    st.session_state["_pending_question"] = fq
                    st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">⬡ DataSense AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="logo-sub">Natural Language → SQL → Insight</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    try:
        health = httpx.get(f"{FASTAPI_URL}/health", timeout=3)
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
        f'<div class="metric-card">Queries this session: <span>{st.session_state.query_count}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="metric-card">Self-corrections total: <span>{st.session_state.total_retries}</span></div>',
        unsafe_allow_html=True,
    )
    if st.session_state.last_query_meta:
        m = st.session_state.last_query_meta
        st.markdown(
            f'<div class="metric-card">Last query: <span>{m["duration_ms"]} ms</span> · <span>{m["rows"]} rows</span></div>',
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
        save_messages()
        st.rerun()

    st.divider()
    st.markdown(
        "<span style=\"font-size:0.7rem;color:#7d8590;font-family:'JetBrains Mono',monospace;\">"
        "LangGraph · Groq · pgvector<br>FastAPI · Streamlit · PostgreSQL</span>",
        unsafe_allow_html=True,
    )


# ── Main area ─────────────────────────────────────────────────────────────────
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
    st.chat_input("e.g. What is the total revenue generated by each seller?") or pending
)

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        try:
            # ── Streaming path: each node appears as a live st.status() step
            data = call_agent_streaming(question)

        except httpx.ConnectError:
            # /query/stream not reachable — fall back to plain spinner
            try:
                with st.spinner("Agent thinking..."):
                    data = call_agent_plain(question)
            except httpx.ConnectError:
                data = {"error": "Cannot reach agent service. Is FastAPI running?"}
            except httpx.TimeoutException:
                data = {"error": "Agent timed out after 90 seconds."}
            except Exception as exc:
                data = {"error": str(exc)}

        except httpx.TimeoutException:
            data = {"error": "Agent timed out after 120 seconds."}
        except Exception as exc:
            data = {"error": str(exc)}

        # ── Final response renders below all the status steps ─────────────
        render_assistant_response(data)

    st.session_state.messages.append({"role": "assistant", "data": data})
    save_messages()

    if data.get("updated_history"):
        st.session_state.history = data["updated_history"][-(MAX_HISTORY_TURNS * 2) :]
    else:
        st.session_state.history.append({"role": "user", "content": question})
        st.session_state.history.append(
            {"role": "assistant", "content": data.get("insight", "")}
        )
        st.session_state.history = st.session_state.history[-(MAX_HISTORY_TURNS * 2) :]

    if not data.get("error") and data.get("is_sql_safe", True):
        st.session_state.query_count += 1
        st.session_state.total_retries += data.get("retries", 0)
        st.session_state.last_query_meta = {
            "duration_ms": data.get("_duration_ms", 0),
            "rows": len(data.get("rows") or []),
        }
