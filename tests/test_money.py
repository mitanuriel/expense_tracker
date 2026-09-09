import pytest

from expense_tracker.money import ore_to_dkk, parse_dkk_to_ore


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", 100),
        ("99.95", 9_995),
        ("125.50", 12_550),
        (125, 12_500),
    ],
)
def test_parse_dkk_to_ore_is_exact(value, expected):
    assert parse_dkk_to_ore(value) == expected


@pytest.mark.parametrize("value", ["", "invalid", "0", "-1", "1.001", "NaN"])
def test_parse_dkk_to_ore_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_dkk_to_ore(value)


def test_ore_to_dkk_converts_at_the_presentation_boundary():
    assert ore_to_dkk(9_995) == 99.95
