"""Decimal money and unit conversion helpers."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Quantize a monetary amount without binary floating point."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def length_rate_to_meter(rate: Decimal, unit: str) -> Decimal:
    """Convert a length-based rate to CNY/meter for supported exact units."""
    factors = {
        "meter": Decimal("1"),
        "kilometer": Decimal("0.001"),
        "yard": Decimal("1.0936132983"),
    }
    if unit not in factors:
        raise ValueError(f"不支持的长度单位：{unit}")
    return rate * factors[unit]
