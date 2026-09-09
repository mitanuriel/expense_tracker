# Acceptance tests

The files in `tests/features/` express the product specification as Gherkin scenarios. The executable step definitions and assertions in `test_acceptance.py` bind those scenarios to the Flask routes and SQLite database.

## Coverage

| Specification feature | Test file |
| --- | --- |
| Add an expense | `features/create_expense.feature` |
| Suggest and override a category | `features/create_expense.feature` |
| Monthly visualization and percentages | `features/monthly_overview.feature` |
| Delete or cancel deletion | `features/delete_expense.feature` |
| Create and resolve future expenses | `features/future_expense.feature` |

The suite currently contains 21 generated pytest scenarios. Each test uses a temporary database and a fixed clock, so runs are isolated and deterministic. Monetary values use two decimal places, and monthly percentages are allocated as whole numbers that add up to 100%.

## Set up the development environment

Create a persistent virtual environment and install the test dependencies:

```sh
uv venv .venv --python python3
uv pip install --python .venv/bin/python -r requirements-dev.txt
```

The repository's VS Code configuration points Python tooling at `.venv/bin/python` so imports from `pytest` and `pytest_bdd` resolve in the editor.

## Run the tests

From the project root:

```sh
.venv/bin/python -m pytest
```

The expected result for the current implementation is:

```text
21 passed
```

## Test boundaries

The tests exercise the Flask application through its test client and assert persisted data directly through the SQLite helpers. Template rendering is captured so monthly totals and chart data can be verified without coupling the backend suite to an HTML structure or chart library.

The following areas still require separate tests when the frontend and related behavior are implemented:

- behavior when the selected month has no actual expenses;
- behavior when the categorization assistant is unavailable or uncertain;
- browser rendering of the chart;
- browser confirmation and cancellation dialogs.
