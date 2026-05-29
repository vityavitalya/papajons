# app/calculator.py

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.crud import get_currency_by_code, get_exchange_rate_by_pair


def _get_usd_rate(db: Session, currency_code: str) -> Optional[Decimal]:
    if currency_code == "USD":
        return Decimal("1")

    rate_direct = get_exchange_rate_by_pair(db, "USD", currency_code)

    if rate_direct:
        return rate_direct.rate

    rate_reverse = get_exchange_rate_by_pair(db, currency_code, "USD")

    if rate_reverse:
        return Decimal("1") / rate_reverse.rate

    return None


def convert_currency(
    db: Session, from_code: str, to_code: str, amount: Decimal
) -> Tuple[Optional[Decimal], str]:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    from_currency = get_currency_by_code(db, from_code)

    to_currency = get_currency_by_code(db, to_code)

    if not from_currency:
        raise ValueError(f"Currency {from_code} not found")

    if not to_currency:
        raise ValueError(f"Currency {to_code} not found")

    if from_code == to_code:
        return (
            amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "same_currency",
        )

    rate = None

    method = ""

    # DIRECT RATE

    direct_rate = get_exchange_rate_by_pair(db, from_code, to_code)

    if direct_rate:
        rate = direct_rate.rate

        method = "direct"

    # REVERSE RATE

    if rate is None:
        reverse_rate = get_exchange_rate_by_pair(db, to_code, from_code)

        if reverse_rate:
            rate = Decimal("1") / reverse_rate.rate

            method = "reverse"

    # CROSS RATE VIA USD

    # CROSS RATE VIA USD

    if rate is None:
        usd_to_from = get_exchange_rate_by_pair(db, "USD", from_code)

        from_to_usd = get_exchange_rate_by_pair(db, from_code, "USD")

        usd_to_to = get_exchange_rate_by_pair(db, "USD", to_code)

        to_to_usd = get_exchange_rate_by_pair(db, to_code, "USD")

        from_rate = None
        to_rate = None

        # FROM currency relative to USD
        if usd_to_from:
            from_rate = usd_to_from.rate

        elif from_to_usd:
            from_rate = Decimal("1") / from_to_usd.rate

        # TO currency relative to USD
        if usd_to_to:
            to_rate = usd_to_to.rate

        elif to_to_usd:
            to_rate = Decimal("1") / to_to_usd.rate

        if from_rate and to_rate:
            rate = to_rate / from_rate

            method = "cross_usd"

    if rate is None:
        raise ValueError(f"Rate " f"{from_code} -> {to_code} " f"not found")

    converted = amount * rate

    converted = converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return converted, method


def get_cross_rate_via_usd(
    db: Session, from_code: str, to_code: str
) -> Optional[Decimal]:
    try:
        converted, _ = convert_currency(db, from_code, to_code, Decimal("1"))

        return converted

    except ValueError:
        return None
