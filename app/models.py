# app/models.py

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String(3), nullable=False, unique=True, index=True)

    full_name = Column(String(100), nullable=False)

    sign = Column(String(10), nullable=False)

    is_active = Column(Integer, default=1, nullable=False)

    base_rates = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.base_currency_id",
        back_populates="base_currency",
        cascade="all, delete-orphan",
    )

    target_rates = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.target_currency_id",
        back_populates="target_currency",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Currency {self.code}>"


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)

    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    target_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    rate = Column(Numeric(10, 6), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "base_currency_id", "target_currency_id", name="uq_currency_pair"
        ),
    )

    base_currency = relationship(
        "Currency", foreign_keys=[base_currency_id], back_populates="base_rates"
    )

    target_currency = relationship(
        "Currency", foreign_keys=[target_currency_id], back_populates="target_rates"
    )

    def __repr__(self):
        return (
            f"<ExchangeRate " f"{self.base_currency_id}->" f"{self.target_currency_id}>"
        )
