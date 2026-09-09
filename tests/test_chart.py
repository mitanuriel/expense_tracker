from expense_tracker.app import build_chart_data


def test_chart_uses_largest_remainders_and_totals_one_hundred_percent():
    rows = [
        {"category": "Mad", "total_ore": 250_000},
        {"category": "Transport", "total_ore": 70_000},
        {"category": "Underholdning", "total_ore": 45_000},
        {"category": "Shopping", "total_ore": 100_000},
    ]

    chart_data, monthly_total = build_chart_data(rows)

    assert monthly_total == 4_650.00
    assert [row["percentage"] for row in chart_data] == [54, 15, 10, 21]
    assert sum(row["percentage"] for row in chart_data) == 100


def test_chart_handles_an_empty_month():
    assert build_chart_data([]) == ([], 0.0)
