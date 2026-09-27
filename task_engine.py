"""
FlowMind AI — Task Engine
Business logic layer between AI intents and the database.
Gemini → structured intent → task_engine → database.
"""

from datetime import datetime

import database as db
import ai_engine as ai


def _format_task_list(tasks: list[dict]) -> str:
    """Format a list of tasks for AI context / display."""
    if not tasks:
        return "No tasks found."
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for t in tasks:
        overdue = (
            " [OVERDUE]" if t.get("deadline") and t["deadline"] < now and t["status"] != "COMPLETED"
            else ""
        )
        lines.append(
            f"• [{t['id']}] {t['title']} | {t['assignee']} | {t['priority']} | "
            f"Deadline: {t.get('deadline','N/A')} | Status: {t['status']}{overdue}"
        )
    return "\n".join(lines)


def handle_message(message: str, chat_history: list[dict]) -> dict:
    """
    Main entry point for AI assistant messages.
    Returns a response dict consumed by the Streamlit UI.
    """
    employees = db.get_employee_names()
    intent_data = ai.classify_message(message, employees)
    intent = intent_data.get("intent", "GENERAL_QUERY")

    # ── CREATE_TASK ──────────────────────────────────────────────────────────
    if intent == "CREATE_TASK":
        tasks = intent_data.get("tasks", [])
        if not tasks:
            return {
                "type": "text",
                "content": "I understood you want to create a task but couldn't extract details. Please try again with more information."
            }
        return {
            "type": "task_preview",
            "tasks": tasks,
            "content": f"I extracted **{len(tasks)} task(s)** from your message. Please review before adding:"
        }

    # ── ASK_CLARIFICATION ────────────────────────────────────────────────────
    if intent == "ASK_CLARIFICATION":
        question = intent_data.get("clarification_question", "Could you provide more details?")
        partial  = intent_data.get("partial_tasks", [])
        resp_text = f"🤔 **Need a bit more info:**\n\n{question}"
        if partial:
            resp_text += "\n\n*Partial tasks detected:*\n"
            for pt in partial:
                resp_text += f"• **{pt.get('title','?')}** — assignee: {pt.get('assignee','?')}, priority: {pt.get('priority','?')}, deadline: {pt.get('deadline','?')}\n"
        return {"type": "text", "content": resp_text}

    # ── UPDATE_TASK ──────────────────────────────────────────────────────────
    if intent == "UPDATE_TASK":
        updates = intent_data.get("updates", [])
        results = []
        for upd in updates:
            task_title = upd.get("task_title", "")
            field      = upd.get("field", "")
            value      = upd.get("value", "")

            matched = db.find_task_by_title(task_title)
            if not matched:
                results.append(f"❌ Could not find task matching **\"{task_title}\"**.")
                continue

            task = matched[0]
            update_kwargs = {}

            if field == "status":
                update_kwargs["status"] = ai.resolve_status(value)
            elif field == "priority":
                update_kwargs["priority"] = value.upper()
            elif field == "deadline":
                update_kwargs["deadline"] = ai.resolve_deadline(value)
            elif field == "assignee":
                update_kwargs["assignee"] = value
            else:
                results.append(f"⚠️ Unknown field **{field}** for task \"{task_title}\".")
                continue

            db.update_task(task["id"], **update_kwargs)
            results.append(
                f"✅ Updated **{task['title']}** — set `{field}` to `{list(update_kwargs.values())[0]}`."
            )

        return {"type": "text", "content": "\n".join(results) if results else "No updates applied."}

    # ── QUERY: LIST_OVERDUE / LIST_HIGH_PRIORITY / LIST_EMPLOYEE_TASKS / QUERY ─
    if intent in ("QUERY_TASKS", "LIST_OVERDUE", "LIST_HIGH_PRIORITY", "LIST_EMPLOYEE_TASKS"):
        query_type = intent_data.get("query_type", "general")
        employee   = intent_data.get("employee")

        if intent == "LIST_OVERDUE" or query_type == "overdue":
            tasks = db.get_overdue_tasks()
            data  = _format_task_list(tasks)
            label = "overdue tasks"
        elif query_type == "today":
            tasks = db.get_tasks_due_today()
            data  = _format_task_list(tasks)
            label = "tasks due today"
        elif intent == "LIST_HIGH_PRIORITY" or query_type == "high_priority":
            tasks = db.get_high_priority_tasks()
            data  = _format_task_list(tasks)
            label = "high-priority tasks"
        elif intent == "LIST_EMPLOYEE_TASKS" or (query_type == "employee" and employee):
            tasks = db.get_tasks_by_assignee(employee)
            data  = _format_task_list(tasks)
            label = f"{employee}'s tasks"
        elif query_type == "count":
            stats = db.get_task_stats()
            data  = str(stats)
            label = "task statistics"
        else:
            # General — send all tasks as context
            tasks = db.get_all_tasks()
            data  = _format_task_list(tasks)
            label = "all tasks"

        answer = ai.answer_query(message, data, employees)
        return {"type": "text", "content": answer}

    # ── ERROR ────────────────────────────────────────────────────────────────
    if intent == "ERROR":
        return {"type": "text", "content": f"⚠️ {intent_data.get('response', 'An error occurred.')}"}

    # ── GENERAL_QUERY ────────────────────────────────────────────────────────
    general_response = intent_data.get("response", "")
    if not general_response:
        # Fallback: forward to Gemini with full context
        tasks = db.get_all_tasks()
        data  = _format_task_list(tasks)
        general_response = ai.answer_query(message, data, employees)

    return {"type": "text", "content": general_response}


def insert_tasks_from_preview(tasks: list[dict]) -> list[int]:
    """Bulk-insert confirmed tasks into the database."""
    inserted_ids = []
    for t in tasks:
        task_id = db.create_task(
            title=t.get("title", "Untitled Task"),
            description=t.get("description", ""),
            assignee=t.get("assignee", ""),
            priority=t.get("priority", "MEDIUM"),
            deadline=t.get("deadline", ""),
            status=t.get("status", "TODO"),
        )
        inserted_ids.append(task_id)
    return inserted_ids
