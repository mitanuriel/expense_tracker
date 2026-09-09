# Expense Tracker

Expense Tracker is a Flask application for recording, categorizing, reviewing, and planning personal expenses. The product requirements are documented in `SPECIFICATION.md`.

## Development setup

Create the project environment and install the application with its development dependencies:

```sh
uv sync --locked --extra dev --no-editable
```

VS Code is configured to use `.venv/bin/python` automatically.

## Run the application

Set a private Flask session key and start the development server:

```sh
export EXPENSE_TRACKER_SECRET_KEY="replace-with-a-long-random-value"
.venv/bin/expense-tracker
```

The SQLite database defaults to `instance/expenses.sqlite3` below the directory where the command is started. Set `EXPENSE_TRACKER_INSTANCE_PATH` to move the complete instance directory, or `EXPENSE_TRACKER_DATABASE` to select a database file directly. Databases created by the earlier schema are migrated from floating-point DKK amounts to integer øre when the application starts.

## Run the tests

```sh
.venv/bin/python -m pytest
```

See `tests/README.md` for coverage and test boundaries.
