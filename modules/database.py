"""SQLite storage for users and quiz results (passwords are salted + hashed)."""
import hashlib
import hmac
import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "quiz_app.db"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                salt TEXT NOT NULL,
                pw_hash TEXT NOT NULL,
                created_at TEXT NOT NULL)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                total INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                percentage REAL NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id))"""
        )


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def create_user(name: str, email: str, password: str):
    """Returns (user_dict | None, error_message | None)."""
    name, email = name.strip(), email.strip().lower()
    if len(name) < 2:
        return None, "Enter your full name."
    if not EMAIL_RE.match(email):
        return None, "Enter a valid email address."
    if len(password) < 6:
        return None, "Password needs at least 6 characters."
    salt = os.urandom(16).hex()
    try:
        with _conn() as c:
            cur = c.execute(
                "INSERT INTO users(name,email,salt,pw_hash,created_at) VALUES(?,?,?,?,?)",
                (name, email, salt, _hash(password, salt), datetime.now().isoformat(timespec="seconds")),
            )
            return {"id": cur.lastrowid, "name": name, "email": email}, None
    except sqlite3.IntegrityError:
        return None, "An account with this email already exists. Sign in instead."


def verify_user(email: str, password: str):
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if row and hmac.compare_digest(row["pw_hash"], _hash(password, row["salt"])):
        return {"id": row["id"], "name": row["name"], "email": row["email"]}
    return None


def save_result(user_id: int, topic: str, difficulty: str, result: dict):
    with _conn() as c:
        c.execute(
            "INSERT INTO results(user_id,topic,difficulty,total,correct,percentage,details,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, topic[:120], difficulty, result["total"], result["correct"], result["percentage"],
             json.dumps(result["details"]), datetime.now().isoformat(timespec="seconds")),
        )


def get_results(user_id: int):
    with _conn() as c:
        rows = c.execute(
            "SELECT topic,difficulty,total,correct,percentage,created_at FROM results WHERE user_id=? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats(user_id: int):
    rows = get_results(user_id)
    if not rows:
        return {"quizzes": 0, "average": 0.0, "best": 0.0, "questions": 0}
    return {
        "quizzes": len(rows),
        "average": round(sum(r["percentage"] for r in rows) / len(rows), 1),
        "best": max(r["percentage"] for r in rows),
        "questions": sum(r["total"] for r in rows),
    }
