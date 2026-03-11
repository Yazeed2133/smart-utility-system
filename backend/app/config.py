from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Utility System API"
    debug: bool = True
    database_url: str = "sqlite:///./smart_utility.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()