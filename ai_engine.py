"""
FlowMind AI — AI Engine
Gemini integration: intent classification, task extraction, NL responses.
All DB operations are executed by Python — Gemini only returns structured JSON.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL

# ─── Initialise Gemini ────────────────────────────────────────────────────────

_gemini_available = False
_model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(GEMINI_MODEL)
        _gemini_available = True
    except Exception as e:
        print(f"[AI Engine] Gemini init failed: {e}")


def is_ai_available() -> bool:
    return _gemini_available


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _parse_deadline(deadline_text: str) -> str:
    """Convert natural-language deadline to YYYY-MM-DD HH:MM:SS format."""
    if not deadline_text:
        return ""
    now = datetime.now()
    dl = deadline_text.strip().lower()

    if dl in ("today", "eod", "end of day"):
        return now.replace(hour=17, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    if dl in ("tomorrow", "tomorrow morning", "tomorrow am"):
        d = now + timedelta(days=1)
        hour = 9 if "morning" in dl else 17
        return d.replace(hour=hour, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    if dl in ("asap", "immediately", "now", "urgent"):
        return now.replace(hour=17, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    # "Friday at 3 PM" style
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if day in dl:
            current_weekday = now.weekday()
            target_weekday  = i
            diff = (target_weekday - current_weekday) % 7 or 7
            target = now + timedelta(days=diff)
            # Extract time if present
            hour = 17
            time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", dl)
            if time_match:
                h = int(time_match.group(1))
                meridiem = time_match.group(3)
                if meridiem == "pm" and h < 12:
                    h += 12
                elif meridiem == "am" and h == 12:
                    h = 0
                hour = h
            return target.replace(hour=hour, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    # Try direct ISO parse
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(deadline_text.strip(), fmt).replace(
                hour=17, minute=0, second=0
            ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # Fallback: return as-is if it already looks like a datetime
    if re.match(r"\d{4}-\d{2}-\d{2}", deadline_text):
        return deadline_text

    # Give up — return today EOD as safe fallback
    return now.replace(hour=17, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def _extract_json(text: str) -> Any:
    """Extract first JSON object/array from a text block."""
    # Try markdown code block first
    md_match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text, re.IGNORECASE)
    if md_match:
        text = md_match.group(1).strip()
    # Find balanced JSON
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == start_char:
                depth += 1
            elif ch == end_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break
    return None


def _call_gemini(prompt: str) -> str:
    """Raw Gemini call with error handling."""
    if not _gemini_available or _model is None:
        raise RuntimeError("Gemini is not available.")
    response = _model.generate_content(prompt)
    return response.text


# ─── Intent Classification ────────────────────────────────────────────────────

SYSTEM_CONTEXT = """
You are FlowMind AI, an intelligent operations assistant for small businesses.
Today's date: {today}
Employees in the system: {employees}

Your role is to classify user messages into structured intents and extract task information.
Always respond with valid JSON only — no markdown, no explanation outside the JSON.
""".strip()

TASK_EXTRACTION_PROMPT = """
{system}

Classify the following business message and extract tasks if applicable.

INTENT OPTIONS:
- CREATE_TASK      → user wants to create one or more tasks
- UPDATE_TASK      → user wants to update status/deadline/assignee/priority of a task
- DELETE_TASK      → user wants to delete a task
- QUERY_TASKS      → user wants to know about tasks (query, list, count)
- LIST_OVERDUE     → user wants overdue tasks
- LIST_HIGH_PRIORITY → user wants high/urgent priority tasks
- LIST_EMPLOYEE_TASKS → user wants tasks for a specific employee
- ASK_CLARIFICATION → critical info is missing (do NOT invent deadlines/assignees)
- GENERAL_QUERY    → general business question

RULES:
1. NEVER invent deadlines, priorities, or assignees.
2. If the message has tasks but is missing required info (assignee OR deadline), use ASK_CLARIFICATION.
3. Required for CREATE_TASK: title, assignee, priority, deadline.
4. For UPDATE_TASK: you need the task title and what to update.
5. Priority must be one of: LOW, MEDIUM, HIGH, URGENT
6. Status must be one of: TODO, IN_PROGRESS, COMPLETED
7. Return deadline as natural language ("today", "tomorrow morning", "Friday at 3 PM", "ASAP").

MESSAGE: "{message}"

Respond ONLY with this JSON structure:

For CREATE_TASK (all fields present):
{{
  "intent": "CREATE_TASK",
  "tasks": [
    {{
      "title": "...",
      "description": "...",
      "assignee": "...",
      "priority": "...",
      "deadline": "...",
      "status": "TODO"
    }}
  ]
}}

For ASK_CLARIFICATION:
{{
  "intent": "ASK_CLARIFICATION",
  "partial_tasks": [...],
  "clarification_question": "What specific info is needed?"
}}

For UPDATE_TASK:
{{
  "intent": "UPDATE_TASK",
  "updates": [
    {{
      "task_title": "...",
      "field": "status|priority|deadline|assignee",
      "value": "..."
    }}
  ]
}}

For QUERY_TASKS / LIST_OVERDUE / LIST_HIGH_PRIORITY / LIST_EMPLOYEE_TASKS:
{{
  "intent": "QUERY_TASKS",
  "query_type": "overdue|today|high_priority|employee|general|count",
  "employee": "Name or null",
  "filters": {{}}
}}

For GENERAL_QUERY:
{{
  "intent": "GENERAL_QUERY",
  "response": "Your helpful response here."
}}
""".strip()


def classify_message(message: str, employees: list[str]) -> dict:
    """
    Classify a user message and extract structured intent.
    Returns a dict with at minimum {"intent": "...", ...}.
    """
    if not _gemini_available:
        return {
            "intent": "GENERAL_QUERY",
            "response": "⚠️ AI is unavailable (no API key). Please use manual task creation."
        }

    today = _today_str()
    emp_list = ", ".join(employees)
    system = SYSTEM_CONTEXT.format(today=today, employees=emp_list)
    prompt = TASK_EXTRACTION_PROMPT.format(system=system, message=message)

    try:
        raw = _call_gemini(prompt)
        parsed = _extract_json(raw)
        if isinstance(parsed, dict):
            # Normalise deadlines in tasks
            if parsed.get("intent") == "CREATE_TASK":
                for task in parsed.get("tasks", []):
                    if "deadline" in task:
                        task["deadline"] = _parse_deadline(task["deadline"])
                    task["priority"] = task.get("priority", "MEDIUM").upper()
                    task["status"]   = task.get("status", "TODO").upper()
            return parsed
        return {"intent": "GENERAL_QUERY", "response": raw}
    except Exception as e:
        return {"intent": "ERROR", "response": f"AI error: {str(e)}"}


# ─── NL Query Response ────────────────────────────────────────────────────────

QUERY_RESPONSE_PROMPT = """
{system}

The user asked: "{question}"

Here is the ACTUAL data from the database:
{data}

Write a clear, concise, friendly answer using ONLY the data provided.
Do NOT invent any information not in the data.
Use bullet points if listing multiple items.
Keep it brief (under 200 words).
""".strip()


def answer_query(question: str, data: Any, employees: list[str]) -> str:
    """Generate a natural-language answer grounded in actual DB data."""
    if not _gemini_available:
        return "⚠️ AI unavailable. Here is the raw data:\n" + str(data)

    today = _today_str()
    emp_list = ", ".join(employees)
    system = SYSTEM_CONTEXT.format(today=today, employees=emp_list)

    data_str = json.dumps(data, indent=2, default=str) if not isinstance(data, str) else data
    prompt = QUERY_RESPONSE_PROMPT.format(system=system, question=question, data=data_str)

    try:
        return _call_gemini(prompt)
    except Exception as e:
        return f"⚠️ AI error generating response: {e}\n\nRaw data:\n{data_str}"


# ─── Update Intent Helpers ────────────────────────────────────────────────────

def resolve_status(value: str) -> str:
    """Normalise status strings from AI output."""
    mapping = {
        "completed": "COMPLETED",
        "complete": "COMPLETED",
        "done": "COMPLETED",
        "finish": "COMPLETED",
        "finished": "COMPLETED",
        "in progress": "IN_PROGRESS",
        "in_progress": "IN_PROGRESS",
        "progress": "IN_PROGRESS",
        "wip": "IN_PROGRESS",
        "working": "IN_PROGRESS",
        "todo": "TODO",
        "to do": "TODO",
        "pending": "TODO",
        "not started": "TODO",
    }
    return mapping.get(value.strip().lower(), value.upper())


def resolve_deadline(value: str) -> str:
    return _parse_deadline(value)
