import sqlite3
import json
from datetime import datetime
from pathlib import Path


# ============================================================
# DATABASE PATH
# ============================================================

DB_PATH = Path(__file__).resolve().parent.parent / "financial_users.db"


# ============================================================
# DAY 8 - CALLS TABLE
# ============================================================

def create_calls_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            call_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            channel TEXT,
            language TEXT,
            duration INTEGER DEFAULT 0,
            outcome TEXT NOT NULL,
            failure_reason TEXT,
            outcome_result TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)

    # --------------------------------------------------------
    # ESCALATIONS TABLE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DAY 8 CALLS TABLE
    # --------------------------------------------------------

    create_calls_table()


# ============================================================
# USER FUNCTIONS
# ============================================================

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


# ============================================================
# ESCALATION FUNCTIONS
# ============================================================

def create_escalation(
    who_needs_help: str,
    what_happened: str,
    what_was_checked: str,
    urgency: str,
    language: str,
    preferred_followup: str
):

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

    return updated


def get_escalation(reference_id: str):

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


# ============================================================
# DAY 8 - SAVE CALL
# ============================================================

def save_call(
    user_id: str,
    channel: str,
    language: str,
    duration: int,
    outcome: str,
    failure_reason: str = None,
    outcome_result: str = None
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO calls (
            user_id,
            channel,
            language,
            duration,
            outcome,
            failure_reason,
            outcome_result,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        channel,
        language,
        duration,
        outcome,
        failure_reason,
        outcome_result,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# ============================================================
# DAY 8 - CALL STATISTICS
# ============================================================

def get_call_stats():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total calls
    cursor.execute("""
        SELECT COUNT(*)
        FROM calls
    """)

    total_calls = cursor.fetchone()[0]

    # Successful calls
    cursor.execute("""
        SELECT COUNT(*)
        FROM calls
        WHERE outcome = 'Success'
    """)

    successful_calls = cursor.fetchone()[0]

    # Failed calls
    cursor.execute("""
        SELECT COUNT(*)
        FROM calls
        WHERE outcome = 'Failed'
    """)

    failed_calls = cursor.fetchone()[0]

    # Average duration
    cursor.execute("""
        SELECT AVG(duration)
        FROM calls
    """)

    avg_duration = cursor.fetchone()[0] or 0

    conn.close()

    # Success percentage
    success_rate = 0

    if total_calls > 0:

        success_rate = round(
            (successful_calls / total_calls) * 100
        )

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "success_rate": success_rate,
        "avg_duration": round(avg_duration, 2)
    }


# ============================================================
# DAY 8 - RECENT CALL HISTORY
# ============================================================

def get_call_history(limit=10):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            created_at,
            user_id,
            channel,
            language,
            duration,
            outcome,
            failure_reason,
            outcome_result
        FROM calls
        ORDER BY call_id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append({
            "date_time": row[0],
            "user_id": row[1],
            "channel": row[2],
            "language": row[3],
            "duration": row[4],
            "outcome": row[5],
            "failure_reason": row[6],
            "outcome_result": row[7]
        })

    return history


# ============================================================
# DAY 8 - FAILURE CATEGORIES
# ============================================================

def get_failure_categories():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            failure_reason,
            COUNT(*)
        FROM calls
        WHERE outcome = 'Failed'
        GROUP BY failure_reason
    """)

    rows = cursor.fetchall()

    conn.close()

    categories = {}

    for reason, count in rows:

        reason = reason or "Unknown"

        categories[reason] = count

    return categories


# ============================================================
# DATABASE TEST
# ============================================================

if __name__ == "__main__":

    init_db()

    print("Database initialized successfully.")
    print(f"Database location: {DB_PATH}")
