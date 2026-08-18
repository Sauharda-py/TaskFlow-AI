from dotenv import load_dotenv
load_dotenv()

import sqlite3
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain_ollama import ChatOllama  # noqa: F401  (kept for optional local-model swap)

DB_PATH = "my_tasks.db"

# ──────────────────────────────────────────────────────────────────────────
# Page config — must be the first Streamlit call
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tasks",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# Theme
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    :root {
        --bg: #0b0d12;
        --bg-2: #12151c;
        --surface: #171b24;
        --surface-2: #1d2230;
        --border: #262c3a;
        --text: #eceef3;
        --text-dim: #8b93a7;
        --accent: #7c9bff;
        --accent-2: #6ee7c0;
        --accent-3: #ff9d7c;
    }

    .stApp {
        background:
            radial-gradient(900px 480px at 12% -8%, rgba(124,155,255,0.16) 0%, transparent 60%),
            radial-gradient(900px 480px at 88% 0%, rgba(110,231,192,0.12) 0%, transparent 55%),
            var(--bg);
    }

    /* Keep the header (needed for the sidebar toggle) but make it blend in */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    #MainMenu, footer { visibility: hidden; }

    section[data-testid="stSidebarCollapsedControl"] button,
    header[data-testid="stHeader"] button {
        color: var(--text) !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    .block-container { padding-top: 1.2rem; max-width: 760px; }

    /* Hero */
    .hero { text-align: center; padding: 0.5rem 0 0.25rem 0; }
    .hero .badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--accent-2);
        background: rgba(110,231,192,0.10);
        border: 1px solid rgba(110,231,192,0.25);
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        margin-bottom: 0.7rem;
    }
    .hero h1 {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0 0 0.2rem 0;
        background: linear-gradient(100deg, #fff 10%, var(--accent) 55%, var(--accent-2) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p { color: var(--text-dim); font-size: 0.95rem; margin: 0; }

    /* Stat cards */
    .stat-row { display: flex; gap: 0.7rem; margin: 1.4rem 0 1.6rem 0; }
    .stat-card {
        flex: 1;
        background: linear-gradient(160deg, var(--surface) 0%, var(--surface-2) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        text-align: center;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .stat-card:hover { transform: translateY(-2px); border-color: var(--accent); }
    .stat-num { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; }
    .stat-label {
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
        text-transform: uppercase; color: var(--text-dim); margin-top: 0.15rem;
    }
    .stat-pending .stat-num { color: #ffcf7a; }
    .stat-progress .stat-num { color: #7aa9ff; }
    .stat-completed .stat-num { color: var(--accent-2); }

    /* Chat messages */
    div[data-testid="stChatMessage"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.95rem 1.15rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.22);
        animation: fadeUp 0.25s ease;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    div[data-testid="stChatMessage"] p { color: var(--text); margin-bottom: 0.4rem; }
    div[data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, var(--accent), #4f6fe0) !important;
    }
    div[data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, var(--accent-2), #2fb894) !important;
    }

    /* Chat input */
    div[data-testid="stChatInput"] {
        border-radius: 16px;
        border: 1px solid var(--border);
        background: var(--surface-2);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    div[data-testid="stChatInput"] textarea { color: var(--text) !important; }
    div[data-testid="stChatInput"]:focus-within { border-color: var(--accent); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg) 100%);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: var(--text); }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: var(--text-dim);
    }

    .sidebar-title {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 1.05rem; font-weight: 700; color: var(--text);
        margin-bottom: 0.9rem;
    }

    /* Example prompt buttons */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-dim);
        font-size: 0.85rem;
        padding: 0.55rem 0.8rem;
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: var(--accent);
        color: var(--text);
        background: var(--surface-2);
    }

    hr { border-color: var(--border); }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# Backend: database + agent
# ──────────────────────────────────────────────────────────────────────────
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

db.run("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN('Pending','In Progress','Completed')) DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

model = ChatGroq(
    model="qwen/qwen3.6-27b"
)

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

system_prompt = """
You are an SQL Agent for SQLite table `tasks`. 
Schema:
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('Pending','In Progress','Completed')) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

### ALLOWED SQL TEMPLATES
Only generate SQL matching these templates:
- CREATE: INSERT INTO tasks (title, description, status) VALUES ('<title>', '<description>', '<status>');
- READ ALL: SELECT id, title, description, status, created_at FROM tasks LIMIT 20;
- READ SEARCH: SELECT id, title, description, status, created_at FROM tasks WHERE title LIKE '%<term>%' OR description LIKE '%<term>%' LIMIT 20;
- READ FILTER: SELECT id, title, description, status, created_at FROM tasks WHERE status = '<status>' LIMIT 20;
- READ SINGLE: SELECT id, title, description, status, created_at FROM tasks WHERE id = <id>;
- UPDATE: UPDATE tasks SET status = '<status>' WHERE id = <id>;
- DELETE: DELETE FROM tasks WHERE id = <id>;

### RULES FOR DATABASE ACCURACY
1. Valid statuses ONLY: 'Pending', 'In Progress', 'Completed'. Default is 'Pending'.
2. NEVER invent, infer, or fabricate rows. Only report data directly returned by the tool.
3. If tool returns 0 rows, say: "No matching tasks found."
4. If tool returns N rows, report exactly N rows. Do not alter IDs, titles, descriptions, or timestamps.

### EXAMPLES

User: Show my pending tasks
SQL: SELECT id, title, description, status, created_at FROM tasks WHERE status = 'Pending' LIMIT 20;

User: Add task Buy Milk
SQL: INSERT INTO tasks (title, status) VALUES ('Buy Milk', 'Pending');

User: Mark task 3 as completed
SQL: UPDATE tasks SET status = 'Completed' WHERE id = 3;

User: Delete task 5
SQL: DELETE FROM tasks WHERE id = 5;

Dont ever display the SQL Querries, either display as bullet points , or as table.
Dont display in any other format, Strictly.
"""

if "memory" not in st.session_state:
    st.session_state.memory = InMemorySaver()
memory = st.session_state.memory

agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=memory,
    system_prompt=system_prompt
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def get_task_counts():
    """Read-only status counts straight from SQLite, purely for the dashboard cards."""
    counts = {"Pending": 0, "In Progress": 0, "Completed": 0}
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        for status, n in cur.fetchall():
            if status in counts:
                counts[status] = n
        conn.close()
    except Exception:
        pass
    return counts


def run_agent(question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user", avatar="🧑").markdown(question)
    with st.chat_message("assistant", avatar="⛃"):
        with st.spinner("Working on it…"):
            response = agent.invoke(
                {"messages": [{"role": "user", "content": question}]},
                {"configurable": {"thread_id": "1"}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
    st.session_state.messages.append({"role": "assistant", "content": result})


# ──────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">&nbsp; Tasks Assistant</div>', unsafe_allow_html=True)
    st.caption("A conversational front end for your SQLite task list.")
    st.markdown("---")

    st.markdown("**Try asking**")
    examples = [
        "Show my pending tasks",
        "Add task: Buy groceries",
        "Mark task 3 as completed",
        "Search tasks about report",
        "Delete task 5",
    ]
    for idx, example in enumerate(examples):
        if st.button(example, key=f"ex_{idx}", use_container_width=True):
            st.session_state.pending_question = example

    st.markdown("---")
    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = InMemorySaver()
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# Main area
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <span class="badge">SQL Agent</span>
        <h1>Task Manager</h1>
        <p>Talk to your task list in plain English.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

counts = get_task_counts()
st.markdown(
    f"""
    <div class="stat-row">
        <div class="stat-card stat-pending">
            <div class="stat-num">{counts['Pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card stat-progress">
            <div class="stat-num">{counts['In Progress']}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card stat-completed">
            <div class="stat-num">{counts['Completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

for i in st.session_state.messages:
    avatar = "🧑" if i["role"] == "user" else "✅"
    st.chat_message(i["role"], avatar=avatar).markdown(i["content"])

# Fire a queued example-prompt click
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    run_agent(q)
    st.rerun()

question = st.chat_input("Ask about your tasks…")
if question:
    run_agent(question)
    st.rerun()