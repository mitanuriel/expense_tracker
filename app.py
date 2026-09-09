from datetime import date, datetime
from math import floor
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)

from categorizer import CATEGORIES, suggest_category
from db import (
    execute,
    init_db,
    query_all,
    query_one
)


def build_chart_data(category_rows):
    """Build whole percentages that add up to exactly 100."""
    monthly_total = sum(row["total"] for row in category_rows)

    if monthly_total <= 0:
        return [], monthly_total

    raw_percentages = [
        row["total"] / monthly_total * 100
        for row in category_rows
    ]
    percentages = [floor(value) for value in raw_percentages]

    # Allocate the remaining percentage points to the largest fractions.
    remaining = 100 - sum(percentages)
    ranked_indexes = sorted(
        range(len(category_rows)),
        key=lambda index: raw_percentages[index] - percentages[index],
        reverse=True,
    )

    for index in ranked_indexes[:remaining]:
        percentages[index] += 1

    chart_data = [
        {
            "category": row["category"],
            "amount": row["total"],
            "percentage": percentages[index],
        }
        for index, row in enumerate(category_rows)
    ]

    return chart_data, monthly_total


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev-secret",
        DATABASE=str(
            Path(app.instance_path) /
            "expenses.sqlite3"
        )
    )

    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    # ----------------------------------
    # HOME / MONTHLY OVERVIEW
    # ----------------------------------

    @app.get("/")
    def index():

        selected_month = request.args.get(
            "month",
            date.today().strftime("%Y-%m")
        )

        database = app.config["DATABASE"]

        actual_expenses = query_all(
            database,
            """
            SELECT *
            FROM expenses
            WHERE status = 'actual'
            AND substr(expense_date, 1, 7) = ?
            ORDER BY expense_date DESC
            """,
            (selected_month,)
        )

        category_rows = query_all(
            database,
            """
            SELECT
                category,
                SUM(amount) AS total
            FROM expenses
            WHERE status = 'actual'
            AND substr(expense_date, 1, 7) = ?
            GROUP BY category
            """,
            (selected_month,)
        )

        chart_data, monthly_total = build_chart_data(
            category_rows
        )

        today = date.today().isoformat()

        due_planned = query_all(
            database,
            """
            SELECT *
            FROM expenses
            WHERE status = 'planned'
            AND expense_date <= ?
            """,
            (today,)
        )

        future_planned = query_all(
            database,
            """
            SELECT *
            FROM expenses
            WHERE status = 'planned'
            AND expense_date > ?
            """,
            (today,)
        )

        return render_template(
            "index.html",
            categories=CATEGORIES,
            expenses=actual_expenses,
            chart_data=chart_data,
            monthly_total=monthly_total,
            due_planned=due_planned,
            future_planned=future_planned,
            selected_month=selected_month
        )

    # ----------------------------------
    # ADD EXPENSE
    # ----------------------------------

    @app.post("/expenses")
    def add_expense():

        description = request.form.get(
            "description",
            ""
        ).strip()

        amount_raw = request.form.get(
            "amount",
            ""
        )

        expense_date_raw = request.form.get(
            "expense_date",
            ""
        )

        category = request.form.get(
            "category",
            ""
        )

        # Validation

        if not description:
            flash(
                "Description is required.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        try:
            amount = float(amount_raw)

            if amount <= 0:
                raise ValueError

        except ValueError:

            flash(
                "Amount must be greater than 0.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        try:

            expense_date = datetime.strptime(
                expense_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "A valid date is required.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        # AI suggestion if user
        # hasn't selected a valid category

        if category not in CATEGORIES:

            category = suggest_category(
                description
            )

        # Future or actual expense?

        if expense_date > date.today():
            status = "planned"
        else:
            status = "actual"

        execute(
            app.config["DATABASE"],
            """
            INSERT INTO expenses (
                description,
                amount,
                expense_date,
                category,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                description,
                amount,
                expense_date.isoformat(),
                category,
                status
            )
        )

        return redirect(
            url_for("index")
        )

    # ----------------------------------
    # DELETE EXPENSE
    # ----------------------------------

    @app.post(
        "/expenses/<int:expense_id>/delete"
    )
    def delete_expense(expense_id):

        expense = query_one(
            app.config["DATABASE"],
            """
            SELECT *
            FROM expenses
            WHERE id = ?
            """,
            (expense_id,)
        )

        if expense is None:

            flash(
                "Expense not found.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        execute(
            app.config["DATABASE"],
            """
            DELETE FROM expenses
            WHERE id = ?
            """,
            (expense_id,)
        )

        return redirect(
            url_for("index")
        )

    # ----------------------------------
    # CONFIRM FUTURE EXPENSE
    # ----------------------------------

    @app.post(
        "/expenses/<int:expense_id>/confirm"
    )
    def confirm_expense(expense_id):

        expense = query_one(
            app.config["DATABASE"],
            """
            SELECT *
            FROM expenses
            WHERE id = ?
            AND status = 'planned'
            """,
            (expense_id,)
        )

        if expense is None:

            flash(
                "Planned expense not found.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        # Do not allow confirmation
        # before its planned date

        if (
            expense["expense_date"]
            > date.today().isoformat()
        ):

            flash(
                "Expense is not due yet.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        execute(
            app.config["DATABASE"],
            """
            UPDATE expenses
            SET status = 'actual'
            WHERE id = ?
            """,
            (expense_id,)
        )

        return redirect(
            url_for("index")
        )

    # ----------------------------------
    # REJECT FUTURE EXPENSE
    # ----------------------------------

    @app.post(
        "/expenses/<int:expense_id>/reject"
    )
    def reject_expense(expense_id):

        expense = query_one(
            app.config["DATABASE"],
            """
            SELECT *
            FROM expenses
            WHERE id = ?
            AND status = 'planned'
            """,
            (expense_id,)
        )

        if expense is None:

            flash(
                "Planned expense not found.",
                "error"
            )

            return redirect(
                url_for("index")
            )

        execute(
            app.config["DATABASE"],
            """
            UPDATE expenses
            SET status = 'rejected'
            WHERE id = ?
            """,
            (expense_id,)
        )

        return redirect(
            url_for("index")
        )

    # ----------------------------------
    # CATEGORY SUGGESTION API
    # ----------------------------------

    @app.get("/api/suggest-category")
    def category_suggestion():

        description = request.args.get(
            "description",
            ""
        )

        category = suggest_category(
            description
        )

        return jsonify({
            "category": category
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
