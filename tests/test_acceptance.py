from dataclasses import dataclass, field
from datetime import date as real_date

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import expense_tracker.app as app_module
from expense_tracker.database import execute, query_all, query_one
from expense_tracker.money import parse_dkk_to_ore


scenarios(
    "features/create_expense.feature",
    "features/monthly_overview.feature",
    "features/delete_expense.feature",
    "features/future_expense.feature",
)


class FrozenClock:
    current = real_date(2026, 9, 9)

    def today(self):
        return self.current


@dataclass
class World:
    client: object
    database: str
    rendered: dict
    form: dict = field(default_factory=dict)
    response: object = None
    suggested_category: str | None = None
    selected_category: str | None = None
    selected_month: str | None = None
    pending_delete_id: int | None = None


def table_rows(datatable):
    headers, *rows = datatable
    return [dict(zip(headers, row)) for row in rows]


def insert_expense(world, row, default_status="actual"):
    return execute(
        world.database,
        """
        INSERT INTO expenses (
            id, description, amount_ore, expense_date, category, status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            int(row["id"]) if row.get("id") else None,
            row["description"],
            parse_dkk_to_ore(row["amount"]),
            row["date"],
            row["category"],
            row.get("status", default_status),
        ),
    )


def open_overview(world):
    query = {}
    if world.selected_month:
        query["month"] = world.selected_month
    world.rendered.clear()
    world.response = world.client.get("/", query_string=query)
    assert world.response.status_code == 200


@pytest.fixture
def world(tmp_path, monkeypatch):
    FrozenClock.current = real_date(2026, 9, 9)

    rendered = {}

    def capture_template(template_name, **context):
        rendered.update(template=template_name, context=context)
        return f"rendered:{template_name}"

    monkeypatch.setattr(app_module, "render_template", capture_template)

    database = str(tmp_path / "acceptance.sqlite3")
    flask_app = app_module.create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "acceptance-test",
            "DATABASE": database,
            "CLOCK": FrozenClock(),
        }
    )

    return World(flask_app.test_client(), database, rendered)


@given(parsers.parse('today is "{value}"'))
def today_is(value):
    FrozenClock.current = real_date.fromisoformat(value)


@given("the expense store is empty")
def empty_expense_store(world):
    execute(world.database, "DELETE FROM expenses")


@given("the user is on the new expense page")
def user_is_on_new_expense_page(world):
    world.form = {}


@when("the user enters the following expense:")
def enter_expense_table(world, datatable):
    row = table_rows(datatable)[0]
    world.form = {
        "description": row["description"],
        "amount": row["amount"],
        "expense_date": row["date"],
    }
    response = world.client.get(
        "/api/suggest-category",
        query_string={"description": row["description"]},
    )
    assert response.status_code == 200
    world.suggested_category = response.get_json()["category"]


@when(
    parsers.re(
        r'^the user enters description "(?P<description>.*)", amount '
        r'"(?P<amount>.*)" and date "(?P<expense_date>.*)"$'
    )
)
def enter_expense_fields(world, description, amount, expense_date):
    world.form = {
        "description": description,
        "amount": amount,
        "expense_date": expense_date,
    }


@when(parsers.re(r'^the user enters description "(?P<description>.*)"$'))
def enter_description(world, description):
    world.form["description"] = description
    response = world.client.get(
        "/api/suggest-category",
        query_string={"description": description},
    )
    assert response.status_code == 200
    world.suggested_category = response.get_json()["category"]


@then(parsers.parse('the suggested category is "{category}"'))
def suggested_category_is(world, category):
    assert world.suggested_category == category


@when(parsers.parse('the user selects category "{category}"'))
def select_category(world, category):
    world.selected_category = category


@when("the user saves the expense")
def save_expense(world):
    form = dict(world.form)
    if world.selected_category is not None:
        form["category"] = world.selected_category
    world.response = world.client.post("/expenses", data=form)
    assert world.response.status_code == 302


@then(parsers.parse("exactly {count:d} expense is stored"))
def exact_expense_count(world, count):
    rows = query_all(world.database, "SELECT * FROM expenses")
    assert len(rows) == count


@then("the expense list contains:")
def expense_list_contains(world, datatable):
    expected_rows = table_rows(datatable)
    open_overview(world)
    actual_rows = [dict(row) for row in world.rendered["context"]["expenses"]]

    for expected in expected_rows:
        assert any(
            row["description"] == expected["description"]
            and row["amount"] == float(expected["amount"])
            and row["expense_date"] == expected["date"]
            and row["category"] == expected["category"]
            and row["status"] == expected["status"]
            for row in actual_rows
        )


@then(parsers.parse('a validation message is shown for "{field_name}"'))
def validation_message_is_shown(world, field_name):
    expected_fragments = {
        "description": "Description is required",
        "amount": "Amount must be greater than 0",
        "date": "A valid date is required",
    }
    with world.client.session_transaction() as session:
        messages = [message for _, message in session.get("_flashes", [])]
    assert any(expected_fragments[field_name] in message for message in messages)


@then("no expense is stored")
def no_expense_is_stored(world):
    assert query_one(world.database, "SELECT * FROM expenses") is None


@then(parsers.parse('the stored expense has category "{category}"'))
def stored_expense_category(world, category):
    expense = query_one(world.database, "SELECT * FROM expenses")
    assert expense is not None
    assert expense["category"] == category


@when("the user opens the category selector")
def open_category_selector(world):
    world.response = world.client.get("/api/suggest-category?description=")
    assert world.response.status_code == 200


@then("the available categories are exactly:")
def available_categories_are(world, datatable):
    expected = [row["category"] for row in table_rows(datatable)]
    assert app_module.CATEGORIES == expected


@given("the following actual expenses exist:")
def actual_expenses_exist(world, datatable):
    for row in table_rows(datatable):
        insert_expense(world, row)


@given("the following actual expense exists:")
def actual_expense_exists(world, datatable):
    insert_expense(world, table_rows(datatable)[0])


@given(parsers.parse('the selected month is "{month}"'))
def selected_month_is(world, month):
    world.selected_month = month


@when("the user opens the monthly overview")
def user_opens_monthly_overview(world):
    open_overview(world)


@given("the monthly overview is open")
def monthly_overview_is_open(world):
    open_overview(world)


@then("a chart is displayed")
def chart_is_displayed(world):
    assert world.rendered["template"] == "index.html"
    assert "chart_data" in world.rendered["context"]


@then("the chart contains these category totals:")
def chart_has_category_totals(world, datatable):
    actual = {
        row["category"]: float(row["amount"])
        for row in world.rendered["context"]["chart_data"]
    }
    expected = {
        row["category"]: float(row["amount"])
        for row in table_rows(datatable)
    }
    assert actual == expected


@then(parsers.parse("the monthly total is {amount:f} DKK"))
def monthly_total_is(world, amount):
    assert world.rendered["context"]["monthly_total"] == pytest.approx(amount)


@then("the chart shows these percentages rounded to the nearest whole percent:")
def chart_has_percentages(world, datatable):
    actual = {
        row["category"]: row["percentage"]
        for row in world.rendered["context"]["chart_data"]
    }
    expected = {
        row["category"]: int(row["percentage"])
        for row in table_rows(datatable)
    }
    assert actual == expected


@when(parsers.parse('the user selects month "{month}"'))
def user_selects_month(world, month):
    world.selected_month = month
    open_overview(world)


@then(parsers.parse('the chart does not contain expenses dated in "{month}"'))
def chart_excludes_month(world, month):
    expenses = world.rendered["context"]["expenses"]
    assert all(not row["expense_date"].startswith(month) for row in expenses)


@when(parsers.parse('the user chooses to delete expense "{expense_id:d}"'))
def choose_delete(world, expense_id):
    world.pending_delete_id = expense_id


@then("a deletion confirmation is shown")
def deletion_confirmation_is_shown(world):
    assert world.pending_delete_id is not None


@when("the user confirms the deletion")
def confirm_deletion(world):
    world.response = world.client.post(
        f"/expenses/{world.pending_delete_id}/delete"
    )
    assert world.response.status_code == 302


@when("the user cancels the deletion")
def cancel_deletion(world):
    world.pending_delete_id = None


@then(parsers.parse('expense "{expense_id:d}" no longer exists'))
def expense_no_longer_exists(world, expense_id):
    assert query_one(
        world.database, "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ) is None


@then(parsers.parse('expense "{expense_id:d}" is not shown in the expense list'))
def expense_not_in_list(world, expense_id):
    open_overview(world)
    ids = [row["id"] for row in world.rendered["context"]["expenses"]]
    assert expense_id not in ids


@then(parsers.parse('expense "{expense_id:d}" still exists unchanged'))
def expense_still_exists_unchanged(world, expense_id):
    expense = query_one(
        world.database, "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    )
    assert expense["id"] == expense_id
    assert expense["description"] == "Netto"
    assert expense["amount_ore"] == 9_995
    assert expense["expense_date"] == "2026-09-08"
    assert expense["category"] == "Mad"
    assert expense["status"] == "actual"


@then(parsers.parse('expense "{expense_id:d}" is shown in the expense list'))
def expense_is_in_list(world, expense_id):
    open_overview(world)
    ids = [row["id"] for row in world.rendered["context"]["expenses"]]
    assert expense_id in ids


@then(parsers.parse('the expense is stored with status "{status}"'))
def expense_has_status(world, status):
    expense = query_one(world.database, "SELECT * FROM expenses")
    assert expense is not None
    assert expense["status"] == status


@then("it is not included in actual expense totals")
def expense_not_in_actual_totals(world):
    total = query_one(
        world.database,
        "SELECT COALESCE(SUM(amount_ore), 0) AS total FROM expenses WHERE status = 'actual'",
    )["total"]
    assert total == 0


@given("this planned expense exists:")
def planned_expense_exists(world, datatable):
    insert_expense(world, table_rows(datatable)[0], "planned")


@given("this due planned expense exists:")
def due_planned_expense_exists(world, datatable):
    insert_expense(world, table_rows(datatable)[0], "planned")


@when("the user opens the application")
def user_opens_application(world):
    open_overview(world)


@then(parsers.parse('no confirmation is requested for expense "{expense_id:d}"'))
def confirmation_not_requested(world, expense_id):
    due_ids = [row["id"] for row in world.rendered["context"]["due_planned"]]
    assert expense_id not in due_ids


@when(parsers.parse("the user opens the {location}"))
def user_opens_location(world, location):
    if location == "relevant monthly overview":
        world.selected_month = "2026-09"
    open_overview(world)


@then(parsers.parse('the user is asked whether expense "{expense_id:d}" took place'))
def confirmation_requested(world, expense_id):
    due_ids = [row["id"] for row in world.rendered["context"]["due_planned"]]
    assert expense_id in due_ids


@when(parsers.parse('the user confirms that expense "{expense_id:d}" took place'))
def confirm_planned_expense(world, expense_id):
    world.response = world.client.post(f"/expenses/{expense_id}/confirm")
    assert world.response.status_code == 302


@when(parsers.parse('the user states that expense "{expense_id:d}" did not take place'))
def reject_planned_expense(world, expense_id):
    world.response = world.client.post(f"/expenses/{expense_id}/reject")
    assert world.response.status_code == 302


@then(parsers.parse('expense "{expense_id:d}" has status "{status}"'))
def expense_id_has_status(world, expense_id, status):
    expense = query_one(
        world.database, "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    )
    assert expense is not None
    assert expense["status"] == status


@then(parsers.parse("{amount:f} DKK is included in the actual total for \"{month}\""))
def amount_in_actual_total(world, amount, month):
    total = query_one(
        world.database,
        """
        SELECT COALESCE(SUM(amount_ore), 0) AS total
        FROM expenses
        WHERE status = 'actual' AND substr(expense_date, 1, 7) = ?
        """,
        (month,),
    )["total"]
    assert total == parse_dkk_to_ore(amount)


@then(parsers.parse('expense "{expense_id:d}" is not an actual expense'))
def expense_is_not_actual(world, expense_id):
    expense = query_one(
        world.database, "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    )
    assert expense is not None
    assert expense["status"] != "actual"


@then(parsers.parse("{amount:f} DKK is not included in the actual total for \"{month}\""))
def amount_not_in_actual_total(world, amount, month):
    total = query_one(
        world.database,
        """
        SELECT COALESCE(SUM(amount_ore), 0) AS total
        FROM expenses
        WHERE status = 'actual' AND substr(expense_date, 1, 7) = ?
        """,
        (month,),
    )["total"]
    assert total == 0
