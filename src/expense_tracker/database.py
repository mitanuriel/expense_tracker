import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount_ore INTEGER NOT NULL CHECK (amount_ore > 0),
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


def _column_names(connection):
    return {
        row["name"]
        for row in connection.execute("PRAGMA table_info(expenses)")
    }


def _migrate_real_amounts_to_ore(connection):
    connection.execute("ALTER TABLE expenses RENAME TO expenses_legacy")
    connection.executescript(SCHEMA)
    connection.execute(
        """
        INSERT INTO expenses (
            id,
            description,
            amount_ore,
            expense_date,
            category,
            status,
            created_at
        )
        SELECT
            id,
            description,
            CAST(ROUND(amount * 100) AS INTEGER),
            expense_date,
            category,
            status,
            created_at
        FROM expenses_legacy
        """
    )
    connection.execute("DROP TABLE expenses_legacy")


def init_db(database_path):
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with connect(database_path) as connection:
        columns = _column_names(connection)

        if not columns:
            connection.executescript(SCHEMA)
        elif "amount_ore" in columns:
            return
        elif "amount" in columns:
            _migrate_real_amounts_to_ore(connection)
        else:
            raise RuntimeError("Unsupported expenses database schema")


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
