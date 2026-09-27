"""
FlowMind AI — Database Layer
SQLite CRUD operations, schema setup, demo data seeding.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from config import DB_PATH, DEMO_EMPLOYEES


# ─── Connection ───────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# ─── Schema ───────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist and seed demo data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL UNIQUE,
            role      TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            assignee    TEXT    DEFAULT '',
            priority    TEXT    NOT NULL DEFAULT 'MEDIUM',
            deadline    TEXT    DEFAULT '',
            status      TEXT    NOT NULL DEFAULT 'TODO',
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        );
    """)
    conn.commit()

    # Seed employees only once
    existing = cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if existing == 0:
        for emp in DEMO_EMPLOYEES:
            cur.execute(
                "INSERT OR IGNORE INTO employees (name, role) VALUES (?, ?)",
                (emp["name"], emp["role"])
            )
        conn.commit()
        _seed_demo_tasks(conn)

    conn.close()


def _seed_demo_tasks(conn: sqlite3.Connection):
    """Insert a realistic mix of demo tasks."""
    now = datetime.now()
    fmt = "%Y-%m-%d %H:%M:%S"

    def dt(days: int, hour: int = 17) -> str:
        """Return a formatted datetime string offset by `days` from today."""
        d = now + timedelta(days=days)
        return d.replace(hour=hour, minute=0, second=0, microsecond=0).strftime(fmt)

    tasks = [
        # Completed tasks
        ("Q3 Sales Report", "Compile quarterly sales figures", "Rahul", "HIGH", dt(-5), "COMPLETED"),
        ("Vendor Payment - TechCorp", "Transfer pending payment to TechCorp", "Amit", "URGENT", dt(-3), "COMPLETED"),
        ("Office Supply Order", "Reorder stationery and printer ink", "Priya", "LOW", dt(-2), "COMPLETED"),
        ("HR Policy Update", "Update leave policy document", "Priya", "MEDIUM", dt(-7), "COMPLETED"),

        # Overdue tasks (deadline in the past, not completed)
        ("Client Proposal - Sharma Group", "Send revised proposal to Sharma Group", "Rahul", "URGENT", dt(-2), "TODO"),
        ("GST Filing", "File monthly GST returns", "Amit", "URGENT", dt(-1), "TODO"),
        ("Inventory Audit - Warehouse B", "Complete audit and send report", "Neha", "HIGH", dt(-3), "IN_PROGRESS"),

        # Due today
        ("ABC Invoice", "Finalize and send ABC Corp invoice", "Rahul", "HIGH", dt(0), "TODO"),
        ("Daily Stand-up Notes", "Record and share stand-up notes", "Priya", "LOW", dt(0), "TODO"),
        ("Bank Reconciliation", "Reconcile bank statements for September", "Amit", "HIGH", dt(0), "IN_PROGRESS"),

        # In progress
        ("Stock Check - Main Warehouse", "Verify current stock levels", "Neha", "MEDIUM", dt(1), "IN_PROGRESS"),
        ("Website Content Review", "Review and approve new website copy", "Priya", "MEDIUM", dt(2), "IN_PROGRESS"),

        # Upcoming
        ("Client Meeting - Verma Industries", "Quarterly review meeting", "Rahul", "HIGH", dt(2), "TODO"),
        ("Sharma Payment Follow-up", "Call Sharma regarding pending payment", "Amit", "HIGH", dt(1), "TODO"),
        ("New Employee Onboarding", "Prepare onboarding kit for new hire", "Priya", "MEDIUM", dt(3), "TODO"),
        ("Monthly Expense Report", "Submit October expense report", "Amit", "MEDIUM", dt(5), "TODO"),
        ("Social Media Campaign Plan", "Draft Q4 campaign strategy", "Rahul", "LOW", dt(7), "TODO"),
        ("Safety Inspection Prep", "Prepare documents for safety audit", "Neha", "HIGH", dt(4), "TODO"),
        ("Supplier Contract Renewal", "Renew contract with Raj Suppliers", "Priya", "HIGH", dt(6), "TODO"),
        ("Training Session Materials", "Prepare slides for team training", "Neha", "LOW", dt(10), "TODO"),
    ]

    ts = now.strftime(fmt)
    for (title, desc, assignee, priority, deadline, status) in tasks:
        conn.execute(
            """INSERT INTO tasks
               (title, description, assignee, priority, deadline, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, desc, assignee, priority, deadline, status, ts, ts)
        )
    conn.commit()


# ─── Employee CRUD ────────────────────────────────────────────────────────────

def get_all_employees() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_employee_names() -> list[str]:
    return [e["name"] for e in get_all_employees()]


# ─── Task CRUD ────────────────────────────────────────────────────────────────

def get_all_tasks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tasks_by_status(status: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status = ? ORDER BY priority DESC, deadline ASC",
        (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tasks_by_assignee(assignee: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE LOWER(assignee) = LOWER(?) ORDER BY status, priority DESC",
        (assignee,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_tasks() -> list[dict]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM tasks
           WHERE deadline != '' AND deadline < ? AND status != 'COMPLETED'
           ORDER BY deadline ASC""",
        (now,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tasks_due_today() -> list[dict]:
    today_start = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    today_end   = datetime.now().replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM tasks
           WHERE deadline >= ? AND deadline <= ? AND status != 'COMPLETED'
           ORDER BY priority DESC""",
        (today_start, today_end)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_high_priority_tasks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE priority IN ('HIGH','URGENT') AND status != 'COMPLETED' ORDER BY priority DESC, deadline ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_task(title: str, description: str = "", assignee: str = "",
                priority: str = "MEDIUM", deadline: str = "", status: str = "TODO") -> int:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO tasks (title, description, assignee, priority, deadline, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, description, assignee, priority.upper(), deadline, status.upper(), ts, ts)
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id


def update_task(task_id: int, **kwargs) -> bool:
    allowed = {"title", "description", "assignee", "priority", "deadline", "status"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return False
    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cols = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [task_id]
    conn = get_connection()
    conn.execute(f"UPDATE tasks SET {cols} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return True


def delete_task(task_id: int) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True


def find_task_by_title(partial_title: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE LOWER(title) LIKE LOWER(?) ORDER BY updated_at DESC",
        (f"%{partial_title}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task_by_id(task_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Analytics ────────────────────────────────────────────────────────────────

def get_task_stats() -> dict:
    all_tasks     = get_all_tasks()
    overdue       = get_overdue_tasks()
    due_today     = get_tasks_due_today()
    high_priority = get_high_priority_tasks()

    total      = len(all_tasks)
    pending    = sum(1 for t in all_tasks if t["status"] == "TODO")
    in_prog    = sum(1 for t in all_tasks if t["status"] == "IN_PROGRESS")
    completed  = sum(1 for t in all_tasks if t["status"] == "COMPLETED")
    unassigned = sum(1 for t in all_tasks if not t["assignee"].strip())

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_prog,
        "completed": completed,
        "overdue": len(overdue),
        "due_today": len(due_today),
        "high_priority": len(high_priority),
        "unassigned": unassigned,
    }


def get_employee_stats() -> list[dict]:
    employees = get_all_employees()
    all_tasks = get_all_tasks()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = []
    for emp in employees:
        name = emp["name"]
        emp_tasks = [t for t in all_tasks if t["assignee"].lower() == name.lower()]
        overdue_count = sum(
            1 for t in emp_tasks
            if t["deadline"] and t["deadline"] < now_str and t["status"] != "COMPLETED"
        )
        result.append({
            "name": name,
            "role": emp["role"],
            "total": len(emp_tasks),
            "pending": sum(1 for t in emp_tasks if t["status"] == "TODO"),
            "in_progress": sum(1 for t in emp_tasks if t["status"] == "IN_PROGRESS"),
            "completed": sum(1 for t in emp_tasks if t["status"] == "COMPLETED"),
            "overdue": overdue_count,
        })
    return result
