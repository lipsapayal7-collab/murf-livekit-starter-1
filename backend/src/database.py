import sqlite3
import json
from datetime import datetime
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent.parent / "financial_users.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            who_needs_help TEXT NOT NULL,
            what_happened TEXT NOT NULL,
            what_was_checked TEXT NOT NULL,
            urgency TEXT NOT NULL,
            language TEXT NOT NULL,
            preferred_followup TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
def lookup_user(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            user_id,
            name,
            language_preference,
            facts,
            last_interaction
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "user_id": row[0],
        "name": row[1],
        "language_preference": row[2],
        "facts": json.loads(row[3]) if row[3] else {},
        "last_interaction": row[4],
    }
def save_user(
    user_id: str,
    name: str,
    language_preference: str,
    facts: dict
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO users (
            user_id,
            name,
            language_preference,
            facts,
            last_interaction
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            facts = excluded.facts,
            last_interaction = excluded.last_interaction
    """, (
        user_id,
        name,
        language_preference,
        json.dumps(facts),
        now
    ))
    conn.commit()
    conn.close()
def delete_user(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
def create_escalation(
    who_needs_help: str,
    what_happened: str,
    what_was_checked: str,
    urgency: str,
    language: str,
    preferred_followup: str
):
    """
    Create a human-support escalation request.
    Only useful, non-sensitive information should be stored.
    Do NOT store:
    - Passwords
    - OTPs
    - PINs
    - CVVs
    - Card numbers
    - Full bank account numbers
    - Aadhaar numbers
    - PAN numbers
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO escalations (
            who_needs_help,
            what_happened,
            what_was_checked,
            urgency,
            language,
            preferred_followup,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        who_needs_help,
        what_happened,
        what_was_checked,
        urgency,
        language,
        preferred_followup,
        "Open",
        created_at
    ))
    escalation_number = cursor.lastrowid
    conn.commit()
    conn.close()
    reference_id = f"ESC-{escalation_number:04d}"
    return reference_id
def get_open_escalations():
    """
    Return all currently open human-support requests.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            escalation_id,
            who_needs_help,
            what_happened,
            what_was_checked,
            urgency,
            language,
            preferred_followup,
            status,
            created_at
        FROM escalations
        WHERE status = 'Open'
        ORDER BY escalation_id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    escalations = []
    for row in rows:
        escalations.append({
            "reference_id": f"ESC-{row[0]:04d}",
            "who_needs_help": row[1],
            "what_happened": row[2],
            "what_was_checked": row[3],
            "urgency": row[4],
            "language": row[5],
            "preferred_followup": row[6],
            "status": row[7],
            "created_at": row[8],
        })
    return escalations
def update_escalation_status(
    reference_id: str,
    status: str
):
    """
    Update the status of a human-support request.
    Example statuses:
    Open
    In Progress
    Resolved
    """
    try:
        escalation_id = int(
            reference_id.replace("ESC-", "")
        )
    except ValueError:
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE escalations
        SET status = ?
        WHERE escalation_id = ?
    """, (
        status,
        escalation_id
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
def get_escalation(reference_id: str):
    """
    Retrieve one escalation using its reference ID.
    """
    try:
        escalation_id = int(
            reference_id.replace("ESC-", "")
        )
    except ValueError:
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            escalation_id,
            who_needs_help,
            what_happened,
            what_was_checked,
            urgency,
            language,
            preferred_followup,
            status,
            created_at
        FROM escalations
        WHERE escalation_id = ?
    """, (escalation_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "reference_id": f"ESC-{row[0]:04d}",
        "who_needs_help": row[1],
        "what_happened": row[2],
        "what_was_checked": row[3],
        "urgency": row[4],
        "language": row[5],
        "preferred_followup": row[6],
        "status": row[7],
        "created_at": row[8],
    }
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print(f"Database location: {DB_PATH}")
