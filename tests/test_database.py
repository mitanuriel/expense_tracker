import sqlite3

from expense_tracker.database import connect, init_db


LEGACY_SCHEMA = """
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def test_init_db_migrates_real_amounts_to_integer_ore(tmp_path):
    database = tmp_path / "legacy.sqlite3"

    with sqlite3.connect(database) as connection:
        connection.executescript(LEGACY_SCHEMA)
        connection.execute(
            """
            INSERT INTO expenses (
                id, description, amount, expense_date, category, status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (42, "Netto", 99.95, "2026-09-08", "Mad", "actual"),
        )

    init_db(database)

    with connect(database) as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(expenses)")
        }
        expense = connection.execute(
            "SELECT * FROM expenses WHERE id = 42"
        ).fetchone()

    assert "amount" not in columns
    assert "amount_ore" in columns
    assert expense["amount_ore"] == 9_995
    assert expense["description"] == "Netto"
    assert expense["status"] == "actual"


def test_init_db_is_idempotent_for_the_current_schema(tmp_path):
    database = tmp_path / "current.sqlite3"

    init_db(database)
    init_db(database)

    with connect(database) as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(expenses)")
        }

    assert "amount_ore" in columns
