import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Smart Utility System API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION = os.getenv(
        "APP_DESCRIPTION",
        "Backend API for managing users, accounts, meters, readings, bills, and payments."
    )
    CONTACT_NAME = os.getenv("CONTACT_NAME", "Smart Utility System Team")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "support@example.com")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_utility.db")


settings = Settings()