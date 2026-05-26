# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables ready")

    yield

    print("Stopping application...")


app = FastAPI(
    title="Currency Exchange API",

    description=(
        "Currency exchange service"
    ),

    version="1.0.0",

    lifespan=lifespan,
)


@app.get("/")
def root():

    return {
        "message": "Currency Exchange API",

        "docs": "/docs",

        "endpoints": [
            "GET /currencies",
            "GET /exchangeRates",
            "GET /exchange"
        ]
    }