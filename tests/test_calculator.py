from decimal import Decimal

import pytest

from app import calculator
from app.schemas import ExchangeRateCreate


class TestCalculatorDirectRate:
    def test_direct_rate_conversion(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )

        result, method = calculator.convert_currency(
            db_session, from_code="USD", to_code="EUR", amount=Decimal("100")
        )

        assert result == Decimal("92.00")
        assert method == "direct"

    def test_direct_rate_with_high_precision(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.921234"),
            ),
        )

        result, method = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )

        assert result == Decimal("92.12")
        assert method == "direct"


class TestCalculatorReverseRate:
    def test_reverse_rate_conversion(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )

        result, method = calculator.convert_currency(
            db_session, "EUR", "USD", Decimal("100")
        )

        assert result == Decimal("108.70")
        assert method == "reverse"


class TestCalculatorCrossRate:
    def test_cross_rate_via_usd(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="RUB",
                rate=Decimal("92.50"),
            ),
        )

        result, method = calculator.convert_currency(
            db_session, "EUR", "RUB", Decimal("100")
        )

        expected = Decimal("10054.35")

        assert result == expected
        assert method == "cross_usd"

    def test_cross_rate_missing_usd_link(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )

        with pytest.raises(ValueError):
            calculator.convert_currency(db_session, "EUR", "RUB", Decimal("100"))


class TestCalculatorEdgeCases:
    def test_negative_amount(self, db_session, sample_currencies):
        with pytest.raises(ValueError):
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("-100"))

    def test_zero_amount(self, db_session, sample_currencies):
        with pytest.raises(ValueError):
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("0"))

    def test_same_currency(self, db_session, sample_currencies):
        result, method = calculator.convert_currency(
            db_session, "USD", "USD", Decimal("100")
        )

        assert result == Decimal("100.00")
        assert method == "same_currency"

    def test_currency_not_found(self, db_session):
        with pytest.raises(ValueError):
            calculator.convert_currency(db_session, "XXX", "USD", Decimal("100"))

    def test_no_rate_available(self, db_session, sample_currencies):
        with pytest.raises(ValueError):
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("100"))

    def test_decimal_rounding(self, db_session, sample_currencies):
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.9255"),
            ),
        )

        result, _ = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )

        assert result == Decimal("92.55")

        db_session.query(crud.ExchangeRate).delete()

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92555"),
            ),
        )

        result, _ = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )

        assert result == Decimal("92.56")
