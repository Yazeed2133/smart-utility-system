from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Utility System"
    app_version: str = "1.0.0"
    app_description: str = "Backend API for managing users, accounts, meters, readings, bills, and payments."
    contact_name: str = "Smart Utility System Team"
    contact_email: EmailStr = "support@example.com"

    database_url: str = "sqlite:///./smart_utility.db"

    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()