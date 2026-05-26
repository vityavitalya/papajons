import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/currencies.db"
    )

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    API_PREFIX = "/api/v1"


config = Config()