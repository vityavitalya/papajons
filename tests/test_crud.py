from decimal import Decimal

import pytest

from sqlalchemy.exc import IntegrityError

from app import crud
from app.schemas import CurrencyCreate
from app.schemas import ExchangeRateCreate


class TestCurrencyCRUD:

    def test_create_currency_success(
        self,
        db_session
    ):

        currency_data = CurrencyCreate(
            code="GBP",
            full_name="British Pound",
            sign="£"
        )

        result = crud.create_currency(
            db_session,
            currency_data
        )

        assert result.id is not None
        assert result.code == "GBP"
        assert result.full_name == "British Pound"
        assert result.sign == "£"

    def test_create_currency_duplicate_code(
        self,
        db_session
    ):

        currency_data = CurrencyCreate(
            code="USD",
            full_name="US Dollar",
            sign="$"
        )

        crud.create_currency(
            db_session,
            currency_data
        )

        duplicate = CurrencyCreate(
            code="USD",
            full_name="US Dollar 2",
            sign="$"
        )

        with pytest.raises(IntegrityError):

            crud.create_currency(
                db_session,
                duplicate
            )

    def test_get_currency_by_code(
        self,
        db_session
    ):

        crud.create_currency(
            db_session,
            CurrencyCreate(
                code="JPY",
                full_name="Yen",
                sign="¥"
            )
        )

        found = crud.get_currency_by_code(
            db_session,
            "JPY"
        )

        assert found is not None
        assert found.code == "JPY"

        not_found = crud.get_currency_by_code(
            db_session,
            "XXX"
        )

        assert not_found is None

    def test_get_all_currencies(
        self,
        db_session
    ):

        crud.create_currency(
            db_session,
            CurrencyCreate(
                code="USD",
                full_name="US Dollar",
                sign="$"
            )
        )

        crud.create_currency(
            db_session,
            CurrencyCreate(
                code="EUR",
                full_name="Euro",
                sign="€"
            )
        )

        all_currencies = crud.get_all_currencies(
            db_session
        )

        assert len(all_currencies) == 2

        codes = [
            c.code
            for c in all_currencies
        ]

        assert "USD" in codes
        assert "EUR" in codes


class TestExchangeRateCRUD:

    def test_create_exchange_rate_success(
        self,
        db_session,
        sample_currencies
    ):

        rate_data = ExchangeRateCreate(
            base_currency_code="USD",
            target_currency_code="EUR",
            rate=Decimal("0.92")
        )

        result = crud.create_exchange_rate(
            db_session,
            rate_data
        )

        assert result.id is not None
        assert result.rate == Decimal("0.92")

    def test_create_exchange_rate_duplicate_pair(
        self,
        db_session,
        sample_currencies
    ):

        rate_data = ExchangeRateCreate(
            base_currency_code="USD",
            target_currency_code="EUR",
            rate=Decimal("0.92")
        )

        crud.create_exchange_rate(
            db_session,
            rate_data
        )

        duplicate = ExchangeRateCreate(
            base_currency_code="USD",
            target_currency_code="EUR",
            rate=Decimal("0.95")
        )

        with pytest.raises(IntegrityError):

            crud.create_exchange_rate(
                db_session,
                duplicate
            )

    def test_create_exchange_rate_currency_not_found(
        self,
        db_session
    ):

        rate_data = ExchangeRateCreate(
            base_currency_code="XXX",
            target_currency_code="EUR",
            rate=Decimal("0.92")
        )

        with pytest.raises(ValueError) as exc_info:

            crud.create_exchange_rate(
                db_session,
                rate_data
            )

        assert "not found" in str(exc_info.value)

    def test_get_exchange_rate_by_pair(
        self,
        db_session,
        sample_currencies
    ):

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92")
            )
        )

        found = crud.get_exchange_rate_by_pair(
            db_session,
            "USD",
            "EUR"
        )

        assert found is not None
        assert found.rate == Decimal("0.92")

        not_found = crud.get_exchange_rate_by_pair(
            db_session,
            "USD",
            "RUB"
        )

        assert not_found is None

    def test_update_exchange_rate(
        self,
        db_session,
        sample_currencies
    ):

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92")
            )
        )

        updated = crud.update_exchange_rate(
            db_session,
            "USDEUR",
            Decimal("0.95")
        )

        assert updated is not None
        assert updated.rate == Decimal("0.95")

        found = crud.get_exchange_rate_by_pair(
            db_session,
            "USD",
            "EUR"
        )

        assert found.rate == Decimal("0.95")

    def test_update_exchange_rate_not_found(
        self,
        db_session
    ):

        updated = crud.update_exchange_rate(
            db_session,
            "USDEUR",
            Decimal("0.95")
        )

        assert updated is None