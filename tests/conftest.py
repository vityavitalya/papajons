import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app import crud
from app.schemas import CurrencyCreate, ExchangeRateCreate


@pytest.fixture(scope="function")
def db_session():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_currencies(db_session):

    currencies_data = [
        CurrencyCreate(
            code="USD",
            full_name="US Dollar",
            sign="$"
        ),
        CurrencyCreate(
            code="EUR",
            full_name="Euro",
            sign="€"
        ),
        CurrencyCreate(
            code="RUB",
            full_name="Russian Ruble",
            sign="₽"
        ),
    ]

    currencies = {}

    for currency_data in currencies_data:
        currency = crud.create_currency(db_session, currency_data)
        currencies[currency.code] = currency

    return currencies


@pytest.fixture
def sample_exchange_rates(db_session, sample_currencies):

    rates_data = [
        ExchangeRateCreate(
            base_currency_code="USD",
            target_currency_code="EUR",
            rate=0.92
        ),
        ExchangeRateCreate(
            base_currency_code="USD",
            target_currency_code="RUB",
            rate=92.50
        ),
    ]

    rates = []

    for rate_data in rates_data:
        rate = crud.create_exchange_rate(db_session, rate_data)
        rates.append(rate)

    return rates