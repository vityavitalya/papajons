# app/main.py

from contextlib import asynccontextmanager
from decimal import Decimal
from typing import List

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import engine
from app.database import Base
from app.database import get_db

from app import crud
from app import calculator

from app.schemas import CurrencyCreate
from app.schemas import CurrencyResponse

from app.schemas import ExchangeRateCreate
from app.schemas import ExchangeRateResponse
from app.schemas import ExchangeRateUpdate

from app.schemas import ExchangeResponse


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    Base.metadata.create_all(bind=engine)

    print("Database tables ready")

    yield

    print("Stopping application...")


app = FastAPI(
    title="Currency Exchange API",

    description="""
Currency exchange API with conversion support.
""",

    version="1.0.0",

    lifespan=lifespan
)


# ========= ROOT =========

@app.get(
    "/",
    tags=["System"]
)
def root():

    return {
        "api": "Currency Exchange API",

        "version": "1.0.0",

        "endpoints": {
            "currencies": "/currencies",

            "exchange_rates": "/exchangeRates",

            "convert":
                "/exchange"
                "?from=USD"
                "&to=EUR"
                "&amount=100",

            "docs": "/docs"
        }
    }


# ========= CURRENCIES =========

@app.get(
    "/currencies",

    response_model=List[CurrencyResponse],

    tags=["Currencies"],

    summary="Get all currencies"
)
def get_currencies(
    db: Session = Depends(get_db)
):

    return crud.get_all_currencies(db)


@app.get(
    "/currency/{code}",

    response_model=CurrencyResponse,

    tags=["Currencies"],

    summary="Get currency by code"
)
def get_currency(
    code: str,

    db: Session = Depends(get_db)
):

    currency = crud.get_currency_by_code(
        db,
        code
    )

    if not currency:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,

            detail=(
                f"Currency "
                f"{code} "
                f"not found"
            )
        )

    return currency


@app.post(
    "/currencies",

    response_model=CurrencyResponse,

    status_code=status.HTTP_201_CREATED,

    tags=["Currencies"],

    summary="Create currency"
)
def create_currency(
    currency: CurrencyCreate,

    db: Session = Depends(get_db)
):

    try:

        return crud.create_currency(
            db,
            currency
        )

    except IntegrityError:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,

            detail=(
                f"Currency "
                f"{currency.code} "
                f"already exists"
            )
        )


# ========= EXCHANGE RATES =========

@app.get(
    "/exchangeRates",

    response_model=List[
        ExchangeRateResponse
    ],

    tags=["Exchange Rates"],

    summary="Get all exchange rates"
)
def get_exchange_rates(
    db: Session = Depends(get_db)
):

    return crud.get_all_exchange_rates(db)


@app.get(
    "/exchangeRate/{pair}",

    response_model=ExchangeRateResponse,

    tags=["Exchange Rates"],

    summary="Get exchange rate by pair"
)
def get_exchange_rate(
    pair: str,

    db: Session = Depends(get_db)
):

    if len(pair) != 6:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,

            detail=(
                "Pair must contain "
                "6 characters"
            )
        )

    base_code = pair[:3]

    target_code = pair[3:]

    rate = crud.get_exchange_rate_by_pair(
        db,
        base_code,
        target_code
    )

    if not rate:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,

            detail=(
                f"Rate "
                f"{base_code} -> "
                f"{target_code} "
                f"not found"
            )
        )

    return rate


@app.post(
    "/exchangeRates",

    response_model=ExchangeRateResponse,

    status_code=status.HTTP_201_CREATED,

    tags=["Exchange Rates"],

    summary="Create exchange rate"
)
def create_exchange_rate(
    rate_data: ExchangeRateCreate,

    db: Session = Depends(get_db)
):

    try:

        return crud.create_exchange_rate(
            db,
            rate_data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(e)
        )

    except IntegrityError:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,

            detail=(
                f"Rate "
                f"{rate_data.base_currency_code}"
                f" -> "
                f"{rate_data.target_currency_code} "
                f"already exists"
            )
        )


@app.patch(
    "/exchangeRate/{pair}",

    response_model=ExchangeRateResponse,

    tags=["Exchange Rates"],

    summary="Update exchange rate"
)
def update_exchange_rate(
    pair: str,

    update_data: ExchangeRateUpdate,

    db: Session = Depends(get_db)
):

    if len(pair) != 6:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,

            detail=(
                "Pair must contain "
                "6 characters"
            )
        )

    updated = crud.update_exchange_rate(
        db,
        pair,
        update_data.rate
    )

    if not updated:

        base_code = pair[:3]

        target_code = pair[3:]

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,

            detail=(
                f"Rate "
                f"{base_code} -> "
                f"{target_code} "
                f"not found"
            )
        )

    return updated


# ========= CONVERSION =========

@app.get(
    "/exchange",

    response_model=ExchangeResponse,

    tags=["Exchange"],

    summary="Convert currency"
)
def convert(
    from_code: str = Query(
        ...,

        alias="from",

        min_length=3,

        max_length=3
    ),

    to_code: str = Query(
        ...,

        min_length=3,

        max_length=3
    ),

    amount: Decimal = Query(
        ...,

        gt=0
    ),

    db: Session = Depends(get_db)
):

    from_code = from_code.upper()

    to_code = to_code.upper()

    try:

        converted_amount, method = (
            calculator.convert_currency(
                db,
                from_code,
                to_code,
                amount
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(e)
        )

    from_currency = crud.get_currency_by_code(
        db,
        from_code
    )

    to_currency = crud.get_currency_by_code(
        db,
        to_code
    )

    rate = (
        converted_amount / amount
    ).quantize(
        Decimal("0.000001")
    )

    response = ExchangeResponse(
        base_currency=from_currency,

        target_currency=to_currency,

        rate=rate,

        amount=amount,

        converted_amount=converted_amount
    )

    return response