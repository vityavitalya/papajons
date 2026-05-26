# app/schemas.py

from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class CurrencyBase(BaseModel):

    code: str = Field(
        ...,
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$"
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    sign: str = Field(
        ...,
        min_length=1,
        max_length=10
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str):

        value = value.upper().strip()

        if not value.isalpha():
            raise ValueError(
                "Code must contain only letters"
            )

        if len(value) != 3:
            raise ValueError(
                "Code must be 3 letters"
            )

        return value


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):

    id: int

    class Config:
        from_attributes = True


class ExchangeRateBase(BaseModel):

    rate: Decimal = Field(
        ...,
        gt=0,
        decimal_places=6
    )


class ExchangeRateCreate(ExchangeRateBase):

    base_currency_code: str = Field(
        ...,
        min_length=3,
        max_length=3
    )

    target_currency_code: str = Field(
        ...,
        min_length=3,
        max_length=3
    )

    @field_validator(
        "base_currency_code",
        "target_currency_code"
    )
    @classmethod
    def validate_currency_code(
        cls,
        value: str
    ):

        value = value.upper().strip()

        if (
            not value.isalpha()
            or len(value) != 3
        ):
            raise ValueError(
                "Currency code must be 3 letters"
            )

        return value


class ExchangeRateResponse(
    ExchangeRateBase
):

    id: int

    base_currency: CurrencyResponse

    target_currency: CurrencyResponse

    class Config:
        from_attributes = True


class ExchangeRateUpdate(BaseModel):

    rate: Decimal = Field(
        ...,
        gt=0,
        decimal_places=6
    )


class ExchangeRequest(BaseModel):

    from_code: str = Field(
        ...,
        alias="from",
        min_length=3,
        max_length=3
    )

    to_code: str = Field(
        ...,
        min_length=3,
        max_length=3
    )

    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2
    )

    @field_validator(
        "from_code",
        "to_code"
    )
    @classmethod
    def validate_code(
        cls,
        value: str
    ):

        value = value.upper().strip()

        if (
            not value.isalpha()
            or len(value) != 3
        ):
            raise ValueError(
                "Currency code must be 3 letters"
            )

        return value


class ExchangeResponse(BaseModel):

    base_currency: CurrencyResponse

    target_currency: CurrencyResponse

    rate: Decimal

    amount: Decimal

    converted_amount: Decimal