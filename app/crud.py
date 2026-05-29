# app/crud.py

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Currency, ExchangeRate
from app.schemas import CurrencyCreate, ExchangeRateCreate

# ========= CURRENCIES =========


def get_all_currencies(
    db: Session,
    include_inactive: bool = False,
) -> List[Currency]:
    """
    �������� ������ ���� �����.

    Args:
        db: ������ ��
        include_inactive:
            ���� True � ���������� ��� ������.
            ���� False � ������ ��������.
    """

    query = db.query(Currency)

    if not include_inactive:
        query = query.filter(Currency.is_active == 1)

    return query.order_by(Currency.code).all()


def get_currency_by_code(
    db: Session,
    code: str,
    include_inactive: bool = False,
) -> Optional[Currency]:
    """
    ����� ������ �� ����.

    Args:
        db: ������ ��
        code: ��� ������
        include_inactive:
            ���� True � ���� ���� ���������� ������.
    """

    query = db.query(Currency).filter(Currency.code == code.upper())

    if not include_inactive:
        query = query.filter(Currency.is_active == 1)

    return query.first()


def deactivate_currency(
    db: Session,
    code: str,
) -> bool:
    """
    �������������� ������.
    """

    currency = get_currency_by_code(
        db,
        code,
        include_inactive=True,
    )

    if not currency:
        return False

    currency.is_active = 0

    db.commit()

    return True


def activate_currency(
    db: Session,
    code: str,
) -> bool:
    """
    ������������ ������.
    """

    currency = get_currency_by_code(
        db,
        code,
        include_inactive=True,
    )

    if not currency:
        return False

    currency.is_active = 1

    db.commit()

    return True


def create_currency(db: Session, currency_data: CurrencyCreate) -> Currency:
    db_currency = Currency(
        code=currency_data.code.upper(),
        full_name=currency_data.full_name,
        sign=currency_data.sign,
    )

    db.add(db_currency)

    try:
        db.commit()

        db.refresh(db_currency)

    except IntegrityError:
        db.rollback()
        raise

    return db_currency


# ========= EXCHANGE RATES =========


def get_all_exchange_rates(db: Session) -> List[ExchangeRate]:
    return (
        db.query(ExchangeRate)
        .options(
            joinedload(ExchangeRate.base_currency),
            joinedload(ExchangeRate.target_currency),
        )
        .all()
    )


def get_exchange_rate_by_pair(
    db: Session, base_code: str, target_code: str
) -> Optional[ExchangeRate]:
    base_currency = get_currency_by_code(db, base_code)

    target_currency = get_currency_by_code(db, target_code)

    if not base_currency or not target_currency:
        return None

    return (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency_id == base_currency.id,
            ExchangeRate.target_currency_id == target_currency.id,
        )
        .first()
    )


def create_exchange_rate(db: Session, rate_data: ExchangeRateCreate) -> ExchangeRate:
    base_currency = get_currency_by_code(db, rate_data.base_currency_code)

    target_currency = get_currency_by_code(db, rate_data.target_currency_code)

    if not base_currency:
        raise ValueError(f"Currency " f"{rate_data.base_currency_code} " f"not found")

    if not target_currency:
        raise ValueError(f"Currency " f"{rate_data.target_currency_code} " f"not found")

    db_rate = ExchangeRate(
        base_currency_id=base_currency.id,
        target_currency_id=target_currency.id,
        rate=rate_data.rate,
    )

    db.add(db_rate)

    try:
        db.commit()

        db.refresh(db_rate)

        db.refresh(db_rate, attribute_names=["base_currency", "target_currency"])

    except IntegrityError:
        db.rollback()
        raise

    return db_rate


def update_exchange_rate(
    db: Session, pair: str, new_rate: Decimal
) -> Optional[ExchangeRate]:
    if len(pair) != 6:
        raise ValueError("Pair must contain 6 chars")

    base_code = pair[:3]

    target_code = pair[3:]

    rate = get_exchange_rate_by_pair(db, base_code, target_code)

    if not rate:
        return None

    rate.rate = new_rate

    db.commit()

    db.refresh(rate)

    return rate
