import sqlite3
import json
from datetime import datetime
from pathlib import Path


# Database will be created inside the backend folder
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
