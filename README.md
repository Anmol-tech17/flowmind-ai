# ⚡ FlowMind AI

> **Turn messy business messages into organized work.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange?logo=google)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🧠 Overview

Small businesses run on WhatsApp, calls, and informal messages — not structured task systems.

**FlowMind AI** bridges that gap. A manager pastes a raw business conversation:

> *"Rahul please complete the ABC invoice today. Neha check the stock tomorrow morning. Amit call Sharma regarding the pending payment ASAP. Rahul has a client meeting Friday at 3 PM."*

FlowMind AI instantly extracts structured tasks:

| Task | Assignee | Priority | Deadline |
|------|----------|----------|----------|
| ABC Invoice | Rahul | HIGH | Today, 5 PM |
| Stock Check | Neha | MEDIUM | Tomorrow, 9 AM |
| Sharma Payment Call | Amit | HIGH | Today, 5 PM |
| Client Meeting | Rahul | HIGH | Friday, 3 PM |

No manual entry. No lost follow-ups. Just organized work.

---

## ✨ Key Features

- 🤖 **AI Task Extraction** — Paste any WhatsApp-style message; Gemini extracts tasks automatically
- 🔍 **Clarification Questions** — AI asks for missing info instead of inventing it
- 💬 **Natural Language Queries** — "What does Rahul have pending?" answered from live database
- ✅ **Task Confirmation Flow** — Review AI-extracted tasks before they're saved
- 🔄 **Natural Language Updates** — "Mark the ABC invoice as completed" → instant database update
- 📊 **Business Risk Radar** — Highlights overdue, urgent, and due-today tasks
- 👥 **Team Productivity Dashboard** — Per-employee workload and completion metrics
- 🗃️ **SQLite Storage** — Simple, portable, zero-config database
- 📋 **Task Board** — Kanban-style TO DO / IN PROGRESS / COMPLETED columns
- 🔒 **Safe Architecture** — Gemini returns structured intents; Python executes SQL (never Gemini directly)

---

## 🏗️ Architecture

```
User (Streamlit UI)
        ↓
    AI Assistant (Gemini 1.5 Flash)
        ↓
    Structured Intent (JSON)
        ↓
    Task Engine (Python Business Logic)
        ↓
    SQLite Database
        ↓
    Response rendered in Streamlit
```

Gemini **never** executes SQL directly. It only returns structured JSON intents that Python validates and executes.

**Supported Intents:**

| Intent | Description |
|--------|-------------|
| `CREATE_TASK` | Extract and create tasks from natural language |
| `UPDATE_TASK` | Update status, priority, deadline, or assignee |
| `DELETE_TASK` | Delete a task by title |
| `QUERY_TASKS` | Answer questions about tasks from live DB data |
| `LIST_OVERDUE` | List all overdue tasks |
| `LIST_HIGH_PRIORITY` | List high/urgent tasks |
| `LIST_EMPLOYEE_TASKS` | List tasks for a specific employee |
| `ASK_CLARIFICATION` | Request missing info (never invent it) |
| `GENERAL_QUERY` | Answer general business questions |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| Gemini 1.5 Flash | AI task extraction & NL understanding |
| SQLite | Local database |
| Pandas | Data manipulation |
| Plotly | Interactive charts |
| python-dotenv | Environment variable management |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/flowmind-ai.git
cd flowmind-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

> **Note:** Demo data is seeded automatically on first launch. No manual setup needed.

---

## 💡 Usage Examples

### Paste a business message

```
Rahul please complete the ABC invoice today.
Neha check the stock tomorrow morning.
Amit call Sharma regarding the pending payment ASAP.
Rahul has a client meeting Friday at 3 PM.
```

FlowMind AI extracts 4 structured tasks and shows a confirmation table before saving.

### Query your task database

```
What does Rahul have pending?
Show me overdue tasks.
What are today's urgent tasks?
How many tasks are assigned to Neha?
Which employee has the most pending tasks?
```

### Update tasks naturally

```
Mark the ABC invoice as completed.
Change the stock task to in progress.
Move Rahul's invoice deadline to tomorrow.
```

---

## 📁 Project Structure

```
flowmind-ai/
│
├── app.py            # Streamlit UI (Dashboard, AI Assistant, Task Board, Team)
├── database.py       # SQLite CRUD, schema, demo data seeding
├── ai_engine.py      # Gemini integration, intent classification, NL responses
├── task_engine.py    # Business logic: intent → database operations
├── config.py         # Configuration, constants, environment variables
│
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
├── .gitignore        # Ignores secrets, DB files, caches
├── README.md         # This file
│
└── data/
    └── .gitkeep      # Data directory (flowmind.db created at runtime)
```

---

## 🔮 Future Scope

- **Real WhatsApp Integration** — Connect to WhatsApp Business API for automatic message parsing
- **Email Integration** — Parse task-related emails automatically
- **Calendar Sync** — Sync deadlines to Google Calendar / Outlook
- **Team Notifications** — Slack/WhatsApp alerts for overdue and approaching tasks
- **Advanced Analytics** — Historical trends, completion rates, workload forecasting
- **Multi-Tenant** — Support multiple businesses with separate workspaces
- **Cloud Deployment** — Google Cloud Run for team-wide access
- **Mobile App** — React Native companion app
- **Voice Input** — Dictate business messages hands-free

---

## 🤝 Contributing

This is a hackathon MVP. PRs welcome for bug fixes and improvements.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ⚡ for hackathon season. FlowMind AI — Turn messy business messages into organized work.*
