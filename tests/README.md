# Acceptance tests

The files in `tests/features/` express the product specification as Gherkin acceptance tests. They are intentionally independent of Flask, FastAPI, a database, and a browser automation tool because those choices have not been made and the repository does not yet contain an application.

## Coverage

| Specification feature | Test file |
| --- | --- |
| Add an expense | `features/create_expense.feature` |
| Suggest and override a category | `features/create_expense.feature` |
| Monthly visualization and percentages | `features/monthly_overview.feature` |
| Delete or cancel deletion | `features/delete_expense.feature` |
| Create and resolve future expenses | `features/future_expense.feature` |

The scenarios use a fixed clock so tests remain deterministic. Monetary values are represented with two decimal places, and the overview example follows the specification by rounding percentages to the nearest whole percent.

## Making the scenarios executable

After the backend and UI technologies are selected, connect each step to the application using a Gherkin-compatible runner such as `pytest-bdd` or Behave. Keep domain setup steps (clock and stored expenses) below the UI layer, and drive user actions through the chosen HTTP client or browser driver.

The following product decisions remain intentionally unspecified and should be settled before adding narrower validation tests:

- whether zero or negative amounts are rejected;
- accepted date and decimal input formats;
- what happens to a rejected planned expense (retained with a rejected status or deleted);
- percentage precision and how rounding remainders are displayed;
- behavior when the selected month has no actual expenses;
- behavior when the categorization assistant is unavailable or uncertain.
