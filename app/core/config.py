from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/analytics_db"
    APP_NAME: str = "Analytics Backend Service"

    class Config:
        env_file = ".env"


settings = Settings()