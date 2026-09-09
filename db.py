import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('actual', 'planned', 'rejected')
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path):
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with connect(database_path) as connection:
        connection.executescript(SCHEMA)


def query_all(database_path, sql, params=()):
    with connect(database_path) as connection:
        return connection.execute(sql, params).fetchall()


def query_one(database_path, sql, params=()):
    with connect(database_path) as connection:
        return connection.execute(sql, params).fetchone()


def execute(database_path, sql, params=()):
    with connect(database_path) as connection:
        cursor = connection.execute(sql, params)
        connection.commit()

        return cursor.lastrowid