import os
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from .categorizer import CATEGORIES, suggest_category
from .clock import SystemClock
from .database import execute, init_db, query_all, query_one
from .money import ore_to_dkk, parse_dkk_to_ore


EXPENSE_COLUMNS = """
    id,
    description,
    amount_ore / 100.0 AS amount,
    expense_date,
    category,
    status,
    created_at
"""


def build_chart_data(category_rows):
    """Build whole percentages that add up to exactly 100."""
    monthly_total_ore = sum(row["total_ore"] for row in category_rows)

    if monthly_total_ore <= 0:
        return [], 0.0

    quotients_and_remainders = [
        divmod(row["total_ore"] * 100, monthly_total_ore)
        for row in category_rows
    ]
    percentages = [quotient for quotient, _ in quotients_and_remainders]
    remaining = 100 - sum(percentages)

    ranked_indexes = sorted(
        range(len(category_rows)),
        key=lambda index: quotients_and_remainders[index][1],
        reverse=True,
    )

    for index in ranked_indexes[:remaining]:
        percentages[index] += 1

    chart_data = [
        {
            "category": row["category"],
            "amount": ore_to_dkk(row["total_ore"]),
            "percentage": percentages[index],
        }
        for index, row in enumerate(category_rows)
    ]

    return chart_data, ore_to_dkk(monthly_total_ore)


def create_app(test_config=None):
    instance_path = os.environ.get(
        "EXPENSE_TRACKER_INSTANCE_PATH",
        str(Path.cwd() / "instance"),
    )
    app = Flask(
        __name__,
        instance_path=instance_path,
        instance_relative_config=True,
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("EXPENSE_TRACKER_SECRET_KEY"),
        DATABASE=os.environ.get(
            "EXPENSE_TRACKER_DATABASE",
            os.path.join(app.instance_path, "expenses.sqlite3"),
        ),
        CLOCK=SystemClock(),
    )

    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "EXPENSE_TRACKER_SECRET_KEY must be set before starting the application"
        )

    init_db(app.config["DATABASE"])

    @app.get("/")
    def index():
        today = app.config["CLOCK"].today()
        selected_month = request.args.get("month", today.strftime("%Y-%m"))
        database = app.config["DATABASE"]

        actual_expenses = query_all(
            database,
            f"""
            SELECT {EXPENSE_COLUMNS}
            FROM expenses
            WHERE status = 'actual'
              AND substr(expense_date, 1, 7) = ?
            ORDER BY expense_date DESC
            """,
            (selected_month,),
        )

        category_rows = query_all(
            database,
            """
            SELECT category, SUM(amount_ore) AS total_ore
            FROM expenses
            WHERE status = 'actual'
              AND substr(expense_date, 1, 7) = ?
            GROUP BY category
            """,
            (selected_month,),
        )

        chart_data, monthly_total = build_chart_data(category_rows)
        today_iso = today.isoformat()

        due_planned = query_all(
            database,
            f"""
            SELECT {EXPENSE_COLUMNS}
            FROM expenses
            WHERE status = 'planned' AND expense_date <= ?
            """,
            (today_iso,),
        )
        future_planned = query_all(
            database,
            f"""
            SELECT {EXPENSE_COLUMNS}
            FROM expenses
            WHERE status = 'planned' AND expense_date > ?
            """,
            (today_iso,),
        )

        return render_template(
            "index.html",
            categories=CATEGORIES,
            expenses=actual_expenses,
            chart_data=chart_data,
            monthly_total=monthly_total,
            due_planned=due_planned,
            future_planned=future_planned,
            selected_month=selected_month,
        )

    @app.post("/expenses")
    def add_expense():
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "")
        expense_date_raw = request.form.get("expense_date", "")
        category = request.form.get("category", "")

        if not description:
            flash("Description is required.", "error")
            return redirect(url_for("index"))

        try:
            amount_ore = parse_dkk_to_ore(amount_raw)
        except ValueError:
            flash("Amount must be greater than 0.", "error")
            return redirect(url_for("index"))

        try:
            expense_date = datetime.strptime(expense_date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("A valid date is required.", "error")
            return redirect(url_for("index"))

        if category not in CATEGORIES:
            category = suggest_category(description)

        status = (
            "planned"
            if expense_date > app.config["CLOCK"].today()
            else "actual"
        )

        execute(
            app.config["DATABASE"],
            """
            INSERT INTO expenses (
                description, amount_ore, expense_date, category, status
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                description,
                amount_ore,
                expense_date.isoformat(),
                category,
                status,
            ),
        )
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/delete")
    def delete_expense(expense_id):
        expense = query_one(
            app.config["DATABASE"],
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,),
        )

        if expense is None:
            flash("Expense not found.", "error")
            return redirect(url_for("index"))

        execute(
            app.config["DATABASE"],
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,),
        )
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/confirm")
    def confirm_expense(expense_id):
        expense = query_one(
            app.config["DATABASE"],
            """
            SELECT id, expense_date
            FROM expenses
            WHERE id = ? AND status = 'planned'
            """,
            (expense_id,),
        )

        if expense is None:
            flash("Planned expense not found.", "error")
            return redirect(url_for("index"))

        if expense["expense_date"] > app.config["CLOCK"].today().isoformat():
            flash("Expense is not due yet.", "error")
            return redirect(url_for("index"))

        execute(
            app.config["DATABASE"],
            "UPDATE expenses SET status = 'actual' WHERE id = ?",
            (expense_id,),
        )
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/reject")
    def reject_expense(expense_id):
        expense = query_one(
            app.config["DATABASE"],
            """
            SELECT id
            FROM expenses
            WHERE id = ? AND status = 'planned'
            """,
            (expense_id,),
        )

        if expense is None:
            flash("Planned expense not found.", "error")
            return redirect(url_for("index"))

        execute(
            app.config["DATABASE"],
            "UPDATE expenses SET status = 'rejected' WHERE id = ?",
            (expense_id,),
        )
        return redirect(url_for("index"))

    @app.get("/api/suggest-category")
    def category_suggestion():
        description = request.args.get("description", "")
        return jsonify({"category": suggest_category(description)})

    return app
