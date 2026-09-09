from decimal import Decimal, InvalidOperation


ORE_PER_DKK = 100
TWO_DECIMAL_PLACES = Decimal("0.01")


def parse_dkk_to_ore(value):
    """Parse a positive DKK value with at most two decimal places."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid monetary amount") from None

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be positive")

    normalized = amount.quantize(TWO_DECIMAL_PLACES)
    if normalized != amount:
        raise ValueError("Amount cannot contain fractions of an øre")

    return int(normalized * ORE_PER_DKK)


def ore_to_dkk(amount_ore):
    """Convert an integer number of øre to a presentation-layer float."""
    return float(Decimal(int(amount_ore)) / ORE_PER_DKK)
