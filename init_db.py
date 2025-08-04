import sqlite3
from flask import g
import os

DATABASE = os.environ.get("DATABASE_PATH", "users.db")


def ensure_folder_for_db(path):
    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_db():
    if "db" not in g:
        ensure_folder_for_db(DATABASE)
        conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row 
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    cursor = db.execute("SELECT COUNT(1) as cnt FROM users")
    if cursor.fetchone()["cnt"] == 0:
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("John Doe", "john@example.com", "password123"),
        )
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Jane Smith", "jane@example.com", "secret456"),
        )
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Bob Johnson", "bob@example.com", "qwerty789"),
        )
    db.commit()
