# ⚡ FlowMind AI

> **Turn messy business messages into organized work.**

FlowMind AI is an AI-powered workflow management platform designed for small businesses. It converts unstructured business messages into organized tasks with assignees, priorities, deadlines, and statuses.

Instead of managing work across WhatsApp messages, notebooks, phone calls, and spreadsheets, businesses can use FlowMind AI to organize their daily operations in one simple interface.

---

## 📌 Project Overview

Small businesses often communicate their daily work through informal messages such as:

> "Rahul complete the ABC invoice today. Neha check the stock tomorrow. Amit call Sharma regarding the pending payment."

Important tasks can easily be missed or forgotten in these conversations.

FlowMind AI solves this problem by allowing users to paste natural-language business messages into an AI assistant. Gemini analyzes the message and converts it into structured tasks.

The user can review the extracted tasks before saving them to the database.

### Example

| Task                 | Assignee | Priority | Deadline |
| -------------------- | -------- | -------- | -------- |
| Complete ABC Invoice | Rahul    | HIGH     | Today    |
| Check Stock          | Neha     | MEDIUM   | Tomorrow |
| Call Sharma          | Amit     | HIGH     | Today    |

---

## 🎯 Objective

The objective of FlowMind AI is to provide small businesses with a simple digital workflow system for:

* Creating tasks
* Assigning responsibilities
* Setting priorities
* Managing deadlines
* Updating task status
* Monitoring pending and completed work
* Managing team members
* Identifying overdue and high-priority tasks

---

## ✨ Key Features

### 🤖 AI Task Extraction

Paste WhatsApp-style business messages and Gemini automatically extracts structured tasks.

### 🔍 AI Clarification

If important information is missing, the AI asks for clarification instead of inventing details.

### 📋 Task Creation

Create and manage tasks with:

* Task title
* Assignee
* Priority
* Deadline
* Status

### 👤 Task Assignment

Assign tasks to members of the business team.

### 🚦 Priority Management

Tasks support:

* LOW
* MEDIUM
* HIGH
* URGENT

### 🔄 Task Status

Tasks can move through:

* TODO
* IN PROGRESS
* COMPLETED

### ⏰ Deadline Tracking

Track upcoming and overdue tasks.

### ⚠️ Business Risk Radar

The dashboard highlights important work such as:

* Overdue tasks
* Urgent tasks
* High-priority tasks
* Tasks due today
* Unassigned tasks

### 📊 Dashboard

Provides an overview of business workload and task progress.

### 👥 Team Management

View team members and their assigned workload.

### 💬 Natural Language AI Assistant

Users can ask questions such as:

```text
What does Rahul have pending?

Show me overdue tasks.

What are today's urgent tasks?

How many tasks are assigned to Neha?
```

### 🔄 Natural Language Task Updates

Users can interact with tasks naturally:

```text
Mark the ABC invoice as completed.

Change the stock task to in progress.

Move Rahul's invoice deadline to tomorrow.
```

### 🔒 Safe AI Architecture

Gemini does **not** directly execute database queries.

The architecture follows:

```text
User
  ↓
Gemini AI
  ↓
Structured Intent / JSON
  ↓
Python Validation & Business Logic
  ↓
SQLite Database
  ↓
Response
```

This keeps database operations under Python application control.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     User / Manager  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit Web UI  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Gemini 2.5 Flash   │
                    │    AI Assistant     │
                    └──────────┬──────────┘
                               │
                         Structured JSON
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Python Task Engine  │
                    │ Validation & Logic  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQLite Database   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Dashboard / Tasks   │
                    │ Team / AI Response  │
                    └─────────────────────┘
```

---

## 🛠️ Technologies Used

| Technology           | Purpose                                               |
| -------------------- | ----------------------------------------------------- |
| **Python 3.10+**     | Core application                                      |
| **Streamlit**        | Web application interface                             |
| **Gemini 2.5 Flash** | AI task extraction and natural-language understanding |
| **SQLite**           | Task and team data storage                            |
| **Pandas**           | Data manipulation                                     |
| **Plotly**           | Dashboard visualizations                              |
| **python-dotenv**    | Environment variable management                       |
| **Git & GitHub**     | Version control and source code hosting               |

---

## 📁 Project Structure

```text
flowmind-ai/
│
├── app.py
├── ai_engine.py
├── database.py
├── task_engine.py
├── config.py
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── data/
    └── .gitkeep
```

### Main Files

| File               | Purpose                             |
| ------------------ | ----------------------------------- |
| `app.py`           | Streamlit application and UI        |
| `ai_engine.py`     | Gemini AI integration               |
| `database.py`      | SQLite database and CRUD operations |
| `task_engine.py`   | Task processing and business logic  |
| `config.py`        | Application configuration           |
| `requirements.txt` | Python dependencies                 |
| `.env.example`     | Environment variable template       |

---

## 🚀 Setup and Run Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Anmol-tech17/flowmind-ai.git
cd flowmind-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API Key

Create a `.env` file from the provided example:

```bash
cp .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

A Gemini API key can be obtained from Google AI Studio.

### 4. Run the Application

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

## 🌐 Live Application

**FlowMind AI — Live Demo**

https://flowmind-ai-jqbsqx4th2twmbrfbtzdqr.streamlit.app/

---

## 🔗 GitHub Repository

**Public Source Code**

https://github.com/Anmol-tech17/flowmind-ai

---

## 💡 Example Workflow

### Step 1 — Enter a Business Message

```text
Rahul complete the ABC invoice today.

Neha check the stock tomorrow morning.

Amit call Sharma regarding the pending payment.

Rahul has a client meeting Friday at 3 PM.
```

### Step 2 — AI Extraction

Gemini identifies the individual tasks, responsibilities, priorities, and deadlines.

### Step 3 — Review

The extracted tasks are displayed for user confirmation.

### Step 4 — Save

Confirmed tasks are stored in the SQLite database.

### Step 5 — Manage

Users can:

* View tasks
* Update status
* Change priority
* Change deadlines
* Reassign tasks
* Ask the AI about pending work

### Step 6 — Monitor

The dashboard provides an overview of business workload and identifies important or overdue work.

---

## 🔮 Future Scope

Possible future improvements include:

* Real WhatsApp Business API integration
* Email integration
* Google Calendar / Outlook synchronization
* Automated team notifications
* Advanced productivity analytics
* Multi-tenant business workspaces
* Mobile application
* Voice-based task creation

---

## 🏆 Hackathon Project

**FlowMind AI** was developed as a software-based workflow management solution for small businesses.

The project focuses on transforming scattered, informal business communication into structured and actionable work.

> **FlowMind AI — Turn messy business messages into organized work.**

---

## 📄 License

This project is licensed under the MIT License.
