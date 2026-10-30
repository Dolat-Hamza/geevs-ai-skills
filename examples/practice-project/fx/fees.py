"""Tiered FX transfer fees."""
from decimal import ROUND_HALF_UP, Decimal

MINIMUM_FEE = Decimal("2.00")
TIERS = (
    (Decimal("10000"), Decimal("0.0025")),
    (Decimal("1000"), Decimal("0.005")),
    (Decimal("0"), Decimal("0.01")),
)


def tier_rate(amount: Decimal) -> Decimal:
    for threshold, rate in TIERS:
        if amount > threshold:
            return rate
    return TIERS[-1][1]


def transfer_fee(amount: Decimal) -> Decimal:
    if amount <= 0:
        raise ValueError("amount must be positive")
    fee = (amount * tier_rate(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return max(fee, MINIMUM_FEE)
