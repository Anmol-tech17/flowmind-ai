"""
FlowMind AI — Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import database as db
import task_engine as engine
import ai_engine as ai
from config import (
    APP_NAME, APP_TAGLINE, PRIORITY_COLORS, STATUS_COLORS,
    PRIORITY_VALUES, STATUS_VALUES
)

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="FlowMind AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1226 0%, #111827 100%);
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    padding: 6px 0;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #e2e8f0 !important;
}

/* Cards */
.metric-card {
    background: linear-gradient(135deg, #1a2234 0%, #1e293b 100%);
    border: 1px solid #2d3748;
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    height: 100%;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #4f6ef7;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    margin: 0;
    line-height: 1;
}
.metric-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 6px;
}

/* Task card */
.task-card {
    background: #1a2234;
    border: 1px solid #2d3748;
    border-left: 4px solid #4f6ef7;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.task-card.urgent  { border-left-color: #dc3545; }
.task-card.high    { border-left-color: #fd7e14; }
.task-card.medium  { border-left-color: #0d6efd; }
.task-card.low     { border-left-color: #6c757d; }
.task-card.overdue { background: #1e0f0f; border-left-color: #dc3545; }

/* Priority badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.badge-urgent   { background: #dc354520; color: #fc8181; border: 1px solid #dc354540; }
.badge-high     { background: #fd7e1420; color: #fbd38d; border: 1px solid #fd7e1440; }
.badge-medium   { background: #0d6efd20; color: #90cdf4; border: 1px solid #0d6efd40; }
.badge-low      { background: #6c757d20; color: #a0aec0; border: 1px solid #6c757d40; }
.badge-todo     { background: #6c757d20; color: #a0aec0; border: 1px solid #6c757d40; }
.badge-inprog   { background: #0d6efd20; color: #90cdf4; border: 1px solid #0d6efd40; }
.badge-done     { background: #19875420; color: #9ae6b4; border: 1px solid #19875440; }
.badge-overdue  { background: #dc354520; color: #fc8181; border: 1px solid #dc354540; }

/* Section header */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #c7d2fe;
    border-bottom: 1px solid #2d3748;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Chat */
.chat-user {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 8px 0 8px 40px;
    color: #e2e8f0;
}
.chat-ai {
    background: #0f1f3d;
    border: 1px solid #1e3a5f;
    border-radius: 12px 12px 12px 4px;
    padding: 12px 16px;
    margin: 8px 40px 8px 0;
    color: #bfdbfe;
}
.chat-label-user { font-size: 0.72rem; color: #64748b; text-align: right; margin-bottom: 2px; }
.chat-label-ai   { font-size: 0.72rem; color: #64748b; margin-bottom: 2px; }

/* Risk radar */
.risk-item {
    background: #1a0e0e;
    border: 1px solid #dc354530;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.87rem;
}

/* Team card */
.team-card {
    background: #1a2234;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}
.team-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f6ef7, #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0 auto 10px;
    color: white;
}
.ai-banner {
    background: linear-gradient(135deg, #0f1f3d, #1a0a2e);
    border: 1px solid #3730a3;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #a5b4fc;
    margin-bottom: 16px;
}
.warn-banner {
    background: #1a1000;
    border: 1px solid #92400e;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #fbbf24;
    margin-bottom: 16px;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; border: none; }

div[data-testid="stHorizontalBlock"] > div { gap: 12px; }

.stTextArea textarea {
    background: #1a2234;
    border: 1px solid #334155;
    color: #e2e8f0;
    border-radius: 8px;
}
.stTextInput input {
    background: #1a2234;
    border: 1px solid #334155;
    color: #e2e8f0;
    border-radius: 8px;
}
.stSelectbox select, .stSelectbox > div {
    background: #1a2234 !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
}
.stDataFrame { background: #1a2234; }

/* Plotly transparent */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─── Init DB ──────────────────────────────────────────────────────────────────

db.init_db()

# ─── Session State ────────────────────────────────────────────────────────────

if "chat_history"         not in st.session_state: st.session_state.chat_history = []
if "pending_tasks"        not in st.session_state: st.session_state.pending_tasks = []
if "show_task_preview"    not in st.session_state: st.session_state.show_task_preview = False
if "success_message"      not in st.session_state: st.session_state.success_message = ""
if "page"                 not in st.session_state: st.session_state.page = "Dashboard"

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 12px 0 24px;">
        <div style="font-size:1.6rem;font-weight:700;background:linear-gradient(90deg,#4f6ef7,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2px;">
            ⚡ {APP_NAME}
        </div>
        <div style="font-size:0.75rem;color:#64748b;">{APP_TAGLINE}</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["Dashboard", "AI Assistant", "Task Board", "Team"],
        index=["Dashboard", "AI Assistant", "Task Board", "Team"].index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.session_state.page = page

    st.markdown("---")
    ai_status = "🟢 AI Online" if ai.is_ai_available() else "🔴 AI Offline"
    st.markdown(f"<small style='color:#64748b;'>{ai_status}</small>", unsafe_allow_html=True)
    st.markdown(f"<small style='color:#334155;'>v1.0.0 · {datetime.now().strftime('%d %b %Y')}</small>", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def priority_badge(priority: str) -> str:
    cls = {"URGENT": "urgent", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}.get(priority, "low")
    return f'<span class="badge badge-{cls}">{priority}</span>'

def status_badge(status: str) -> str:
    cls = {"TODO": "todo", "IN_PROGRESS": "inprog", "COMPLETED": "done"}.get(status, "todo")
    label = {"TODO": "TO DO", "IN_PROGRESS": "IN PROGRESS", "COMPLETED": "DONE"}.get(status, status)
    return f'<span class="badge badge-{cls}">{label}</span>'

def is_overdue(task: dict) -> bool:
    if not task.get("deadline") or task["status"] == "COMPLETED":
        return False
    return task["deadline"] < datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fmt_deadline(dl: str) -> str:
    if not dl:
        return "No deadline"
    try:
        dt = datetime.strptime(dl, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return dl


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def page_dashboard():
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:700;margin-bottom:4px;color:#e2e8f0;">
        📊 Dashboard
    </h1>
    <p style="color:#64748b;margin-bottom:24px;">Real-time overview of your business operations</p>
    """, unsafe_allow_html=True)

    stats = db.get_task_stats()

    # Metric cards
    cols = st.columns(7)
    metrics = [
        ("Total Tasks",   stats["total"],         "#4f6ef7", "📋"),
        ("Pending",       stats["pending"],        "#64748b", "📌"),
        ("In Progress",   stats["in_progress"],    "#0d6efd", "⚙️"),
        ("Completed",     stats["completed"],      "#198754", "✅"),
        ("Overdue",       stats["overdue"],        "#dc3545", "⚠️"),
        ("High Priority", stats["high_priority"],  "#fd7e14", "🔥"),
        ("Due Today",     stats["due_today"],      "#7c3aed", "📅"),
    ]
    for col, (label, value, color, icon) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.4rem;margin-bottom:4px;">{icon}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-header">Task Status Breakdown</div>', unsafe_allow_html=True)
        all_tasks = db.get_all_tasks()
        if all_tasks:
            df = pd.DataFrame(all_tasks)
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            status_counts["Status"] = status_counts["Status"].map(
                {"TODO": "To Do", "IN_PROGRESS": "In Progress", "COMPLETED": "Completed"}
            )
            fig = px.pie(
                status_counts, names="Status", values="Count",
                color="Status",
                color_discrete_map={"To Do": "#6c757d", "In Progress": "#0d6efd", "Completed": "#198754"},
                hole=0.55,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                showlegend=True,
            )
            fig.update_traces(textinfo="value+percent", textfont_size=12)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Tasks by Employee</div>', unsafe_allow_html=True)
        emp_stats = db.get_employee_stats()
        if emp_stats:
            df_emp = pd.DataFrame(emp_stats)
            fig2 = go.Figure(data=[
                go.Bar(name="Pending",     x=df_emp["name"], y=df_emp["pending"],     marker_color="#64748b"),
                go.Bar(name="In Progress", x=df_emp["name"], y=df_emp["in_progress"], marker_color="#0d6efd"),
                go.Bar(name="Completed",   x=df_emp["name"], y=df_emp["completed"],   marker_color="#198754"),
                go.Bar(name="Overdue",     x=df_emp["name"], y=df_emp["overdue"],     marker_color="#dc3545"),
            ])
            fig2.update_layout(
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=10, b=30, l=10, r=10),
                height=280,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e2a3a"),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Priority breakdown
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown('<div class="section-header">Priority Distribution</div>', unsafe_allow_html=True)
        if all_tasks:
            df_p = pd.DataFrame(all_tasks)
            prio_counts = df_p[df_p["status"] != "COMPLETED"]["priority"].value_counts().reset_index()
            prio_counts.columns = ["Priority", "Count"]
            fig3 = px.bar(
                prio_counts, x="Priority", y="Count",
                color="Priority",
                color_discrete_map={
                    "URGENT": "#dc3545", "HIGH": "#fd7e14",
                    "MEDIUM": "#0d6efd", "LOW": "#6c757d"
                },
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                showlegend=False,
                margin=dict(t=10, b=30, l=10, r=10),
                height=220,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e2a3a"),
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">🚨 Business Risk Radar</div>', unsafe_allow_html=True)
        overdue_tasks   = db.get_overdue_tasks()
        today_tasks     = db.get_tasks_due_today()
        high_tasks      = db.get_high_priority_tasks()
        all_t           = db.get_all_tasks()
        unassigned      = [t for t in all_t if not t.get("assignee", "").strip()]

        radar_items = []
        for t in overdue_tasks[:3]:
            radar_items.append(f"🔴 OVERDUE · {t['title']} ({t['assignee'] or 'Unassigned'})")
        for t in today_tasks[:2]:
            radar_items.append(f"🟡 DUE TODAY · {t['title']} ({t['assignee'] or 'Unassigned'})")
        for t in unassigned[:2]:
            radar_items.append(f"⚪ UNASSIGNED · {t['title']}")
        # Approaching deadline (tomorrow)
        from datetime import timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        approaching = [
            t for t in all_t
            if t.get("deadline", "")[:10] == tomorrow and t["status"] != "COMPLETED"
        ]
        for t in approaching[:2]:
            radar_items.append(f"🟠 DUE TOMORROW · {t['title']} ({t['assignee'] or 'Unassigned'})")

        if not radar_items:
            st.markdown('<div style="color:#198754;padding:10px;">✅ No critical risks detected!</div>', unsafe_allow_html=True)
        else:
            for item in radar_items[:8]:
                st.markdown(f'<div class="risk-item">{item}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════

def page_ai_assistant():
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:700;margin-bottom:4px;color:#e2e8f0;">
        🤖 AI Assistant
    </h1>
    <p style="color:#64748b;margin-bottom:16px;">
        Paste business messages to extract tasks, or ask anything about your operations.
    </p>
    """, unsafe_allow_html=True)

    if ai.is_ai_available():
        st.markdown("""
        <div class="ai-banner">
            ⚡ <strong>AI Active</strong> — Powered by Gemini. 
            Paste WhatsApp-style messages or ask questions like "What does Rahul have pending?"
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warn-banner">
            ⚠️ <strong>AI Offline</strong> — Add your <code>GEMINI_API_KEY</code> to a <code>.env</code> file to enable AI features.
            Manual task management still works on the Task Board.
        </div>""", unsafe_allow_html=True)

    # ── Task Preview / Confirmation ──────────────────────────────────────────
    if st.session_state.show_task_preview and st.session_state.pending_tasks:
        st.markdown("---")
        st.markdown("#### ✅ Review Extracted Tasks")
        tasks = st.session_state.pending_tasks
        df_preview = pd.DataFrame([{
            "Task":     t.get("title", ""),
            "Assignee": t.get("assignee", ""),
            "Priority": t.get("priority", ""),
            "Deadline": fmt_deadline(t.get("deadline", "")),
            "Status":   t.get("status", "TODO"),
        } for t in tasks])

        st.dataframe(
            df_preview,
            use_container_width=True,
            hide_index=True,
        )

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
        with btn_col1:
            if st.button("✅ Add All Tasks", key="add_all_tasks"):
                ids = engine.insert_tasks_from_preview(tasks)
                st.session_state.show_task_preview = False
                st.session_state.pending_tasks = []
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"✅ **{len(ids)} task(s) added to the database!** You can view them on the Task Board."
                })
                st.rerun()
        with btn_col2:
            if st.button("❌ Discard", key="discard_tasks"):
                st.session_state.show_task_preview = False
                st.session_state.pending_tasks = []
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "Tasks discarded. Let me know if you'd like to try again."
                })
                st.rerun()

        # Add individual task buttons
        if len(tasks) > 1:
            st.markdown("**Or add individual tasks:**")
            for i, t in enumerate(tasks):
                col_t, col_b = st.columns([4, 1])
                with col_t:
                    st.markdown(f"`{t.get('title', '')}` → {t.get('assignee', '')} | {t.get('priority', '')} | {fmt_deadline(t.get('deadline', ''))}")
                with col_b:
                    if st.button(f"Add", key=f"add_single_{i}"):
                        engine.insert_tasks_from_preview([t])
                        st.session_state.pending_tasks = [
                            x for j, x in enumerate(tasks) if j != i
                        ]
                        if not st.session_state.pending_tasks:
                            st.session_state.show_task_preview = False
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"✅ Task **{t.get('title','')}** added."
                        })
                        st.rerun()
        st.markdown("---")

    # ── Chat History ────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-label-user">You</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-label-ai">⚡ FlowMind AI</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    # ── Input ────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            placeholder=(
                "Paste a business message (e.g. 'Rahul please complete the ABC invoice today. Neha check stock tomorrow morning.')\n"
                "Or ask a question: 'What does Rahul have pending?' / 'Show me overdue tasks.'"
            ),
            height=120,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send ➤", use_container_width=False)

    if submitted and user_input.strip():
        user_msg = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        with st.spinner("FlowMind AI is thinking..."):
            response = engine.handle_message(user_msg, st.session_state.chat_history)

        if response["type"] == "task_preview":
            st.session_state.pending_tasks = response["tasks"]
            st.session_state.show_task_preview = True
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["content"]
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["content"]
            })

        st.rerun()

    # ── Quick Examples ───────────────────────────────────────────────────────
    with st.expander("💡 Try these examples", expanded=False):
        st.markdown("""
**Task Creation:**
```
Rahul please complete the ABC invoice today. Neha check the stock tomorrow morning. Amit call Sharma regarding the pending payment ASAP. Rahul has a client meeting Friday at 3 PM.
```

**Queries:**
- `What does Rahul have pending?`
- `Show me overdue tasks`
- `What are today's urgent tasks?`
- `How many tasks are assigned to Neha?`
- `Which employee has the most pending tasks?`

**Updates:**
- `Mark the ABC invoice as completed`
- `Change the stock task to in progress`
- `Move Rahul's invoice deadline to tomorrow`
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TASK BOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_task_card(task: dict, show_actions: bool = True):
    overdue   = is_overdue(task)
    prio      = task.get("priority", "MEDIUM")
    prio_cls  = prio.lower()
    card_cls  = "task-card overdue" if overdue else f"task-card {prio_cls}"
    overdue_tag = '<span class="badge badge-overdue">OVERDUE</span>' if overdue else ""

    st.markdown(f"""
    <div class="{card_cls}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
            <span style="font-weight:600;font-size:0.95rem;color:#e2e8f0;">{task['title']}</span>
            <span>{priority_badge(prio)} {overdue_tag}</span>
        </div>
        <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:4px;">
            👤 {task.get('assignee','Unassigned')} &nbsp;|&nbsp;
            📅 {fmt_deadline(task.get('deadline',''))}
        </div>
        {f'<div style="font-size:0.8rem;color:#64748b;">{task["description"]}</div>' if task.get("description") else ""}
    </div>
    """, unsafe_allow_html=True)

    if show_actions:
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            new_status = st.selectbox(
                "Status",
                STATUS_VALUES,
                index=STATUS_VALUES.index(task.get("status", "TODO")),
                key=f"status_{task['id']}",
                label_visibility="collapsed",
            )
            if new_status != task.get("status"):
                db.update_task(task["id"], status=new_status)
                st.rerun()
        with c3:
            if st.button("🗑️", key=f"del_{task['id']}", help="Delete task"):
                db.delete_task(task["id"])
                st.rerun()


def page_task_board():
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:700;margin-bottom:4px;color:#e2e8f0;">
        📋 Task Board
    </h1>
    <p style="color:#64748b;margin-bottom:16px;">Manage all tasks across the team</p>
    """, unsafe_allow_html=True)

    # Quick add form
    with st.expander("➕ Add Task Manually", expanded=False):
        with st.form("manual_task_form"):
            fc1, fc2 = st.columns([3, 1])
            with fc1:
                m_title = st.text_input("Task Title *", placeholder="e.g. Send monthly report")
            with fc2:
                m_priority = st.selectbox("Priority", PRIORITY_VALUES, index=2)

            fc3, fc4, fc5 = st.columns(3)
            with fc3:
                m_assignee = st.selectbox("Assignee", [""] + db.get_employee_names())
            with fc4:
                m_deadline = st.date_input("Deadline", value=None)
            with fc5:
                m_status = st.selectbox("Status", STATUS_VALUES)

            m_desc = st.text_area("Description", height=68, placeholder="Optional details...")
            submit_manual = st.form_submit_button("Add Task")

            if submit_manual and m_title.strip():
                dl_str = ""
                if m_deadline:
                    dl_str = datetime.combine(m_deadline, datetime.min.time().replace(hour=17)).strftime("%Y-%m-%d %H:%M:%S")
                db.create_task(
                    title=m_title.strip(),
                    description=m_desc,
                    assignee=m_assignee,
                    priority=m_priority,
                    deadline=dl_str,
                    status=m_status,
                )
                st.success(f"Task **{m_title}** added!")
                st.rerun()

    # Filters
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        filter_assignee = st.selectbox("Filter by Assignee", ["All"] + db.get_employee_names(), key="filter_assignee")
    with f2:
        filter_priority = st.selectbox("Filter by Priority", ["All"] + PRIORITY_VALUES, key="filter_prio")
    with f3:
        filter_overdue  = st.checkbox("Show only overdue", key="filter_overdue")

    all_tasks = db.get_all_tasks()

    if filter_assignee != "All":
        all_tasks = [t for t in all_tasks if t.get("assignee","").lower() == filter_assignee.lower()]
    if filter_priority != "All":
        all_tasks = [t for t in all_tasks if t.get("priority","") == filter_priority]
    if filter_overdue:
        all_tasks = [t for t in all_tasks if is_overdue(t)]

    st.markdown("<br>", unsafe_allow_html=True)
    col_todo, col_prog, col_done = st.columns(3)

    todo_tasks      = [t for t in all_tasks if t["status"] == "TODO"]
    inprog_tasks    = [t for t in all_tasks if t["status"] == "IN_PROGRESS"]
    completed_tasks = [t for t in all_tasks if t["status"] == "COMPLETED"]

    with col_todo:
        st.markdown(f'<div class="section-header">📌 TO DO &nbsp;<span style="color:#64748b;font-size:0.85rem;">({len(todo_tasks)})</span></div>', unsafe_allow_html=True)
        for t in todo_tasks:
            render_task_card(t)
        if not todo_tasks:
            st.markdown('<div style="color:#334155;font-size:0.85rem;text-align:center;padding:20px 0;">No tasks</div>', unsafe_allow_html=True)

    with col_prog:
        st.markdown(f'<div class="section-header">⚙️ IN PROGRESS &nbsp;<span style="color:#64748b;font-size:0.85rem;">({len(inprog_tasks)})</span></div>', unsafe_allow_html=True)
        for t in inprog_tasks:
            render_task_card(t)
        if not inprog_tasks:
            st.markdown('<div style="color:#334155;font-size:0.85rem;text-align:center;padding:20px 0;">No tasks</div>', unsafe_allow_html=True)

    with col_done:
        st.markdown(f'<div class="section-header">✅ COMPLETED &nbsp;<span style="color:#64748b;font-size:0.85rem;">({len(completed_tasks)})</span></div>', unsafe_allow_html=True)
        for t in completed_tasks:
            render_task_card(t)
        if not completed_tasks:
            st.markdown('<div style="color:#334155;font-size:0.85rem;text-align:center;padding:20px 0;">No tasks</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TEAM
# ═══════════════════════════════════════════════════════════════════════════════

AVATAR_COLORS = [
    "linear-gradient(135deg,#4f6ef7,#7c3aed)",
    "linear-gradient(135deg,#059669,#0d6efd)",
    "linear-gradient(135deg,#dc3545,#fd7e14)",
    "linear-gradient(135deg,#7c3aed,#db2777)",
]

def page_team():
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:700;margin-bottom:4px;color:#e2e8f0;">
        👥 Team
    </h1>
    <p style="color:#64748b;margin-bottom:24px;">Productivity overview per team member</p>
    """, unsafe_allow_html=True)

    emp_stats = db.get_employee_stats()

    # Top row: summary cards
    cols = st.columns(len(emp_stats))
    for i, (col, emp) in enumerate(zip(cols, emp_stats)):
        initials = "".join(w[0] for w in emp["name"].split())[:2].upper()
        color    = AVATAR_COLORS[i % len(AVATAR_COLORS)]
        with col:
            st.markdown(f"""
            <div class="team-card">
                <div class="team-avatar" style="background:{color};">{initials}</div>
                <div style="font-weight:700;font-size:1rem;color:#e2e8f0;margin-bottom:2px;">{emp['name']}</div>
                <div style="font-size:0.75rem;color:#64748b;margin-bottom:14px;">{emp['role']}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div style="background:#0d1226;border-radius:8px;padding:8px;text-align:center;">
                        <div style="font-size:1.4rem;font-weight:700;color:#4f6ef7;">{emp['total']}</div>
                        <div style="font-size:0.7rem;color:#64748b;">Total</div>
                    </div>
                    <div style="background:#0d1226;border-radius:8px;padding:8px;text-align:center;">
                        <div style="font-size:1.4rem;font-weight:700;color:#64748b;">{emp['pending']}</div>
                        <div style="font-size:0.7rem;color:#64748b;">Pending</div>
                    </div>
                    <div style="background:#0d1226;border-radius:8px;padding:8px;text-align:center;">
                        <div style="font-size:1.4rem;font-weight:700;color:#198754;">{emp['completed']}</div>
                        <div style="font-size:0.7rem;color:#64748b;">Done</div>
                    </div>
                    <div style="background:#0d1226;border-radius:8px;padding:8px;text-align:center;">
                        <div style="font-size:1.4rem;font-weight:700;color:#dc3545;">{emp['overdue']}</div>
                        <div style="font-size:0.7rem;color:#64748b;">Overdue</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed table per employee
    for emp in emp_stats:
        with st.expander(f"📋 {emp['name']} — Task Details ({emp['total']} total)", expanded=False):
            tasks = db.get_tasks_by_assignee(emp["name"])
            if tasks:
                df = pd.DataFrame([{
                    "Title":    t["title"],
                    "Priority": t["priority"],
                    "Deadline": fmt_deadline(t.get("deadline", "")),
                    "Status":   t["status"],
                    "Overdue":  "⚠️ Yes" if is_overdue(t) else "—",
                } for t in tasks])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No tasks assigned yet.")

    # Team comparison chart
    st.markdown("<br>")
    st.markdown('<div class="section-header">Team Workload Comparison</div>', unsafe_allow_html=True)
    df_emp = pd.DataFrame(emp_stats)
    fig = go.Figure(data=[
        go.Bar(name="Pending",     x=df_emp["name"], y=df_emp["pending"],     marker_color="#64748b"),
        go.Bar(name="In Progress", x=df_emp["name"], y=df_emp["in_progress"], marker_color="#0d6efd"),
        go.Bar(name="Completed",   x=df_emp["name"], y=df_emp["completed"],   marker_color="#198754"),
        go.Bar(name="Overdue",     x=df_emp["name"], y=df_emp["overdue"],     marker_color="#dc3545"),
    ])
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=10, b=30, l=10, r=10),
        height=300,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e2a3a"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── Router ───────────────────────────────────────────────────────────────────

if   page == "Dashboard":    page_dashboard()
elif page == "AI Assistant": page_ai_assistant()
elif page == "Task Board":   page_task_board()
elif page == "Team":         page_team()
