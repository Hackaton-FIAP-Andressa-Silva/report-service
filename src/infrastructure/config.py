from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "report-service"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "report_db"

    # Internal auth
    INTERNAL_SERVICE_TOKEN: str = "internal-changeme"

    class Config:
        env_file = ".env"


settings = Settings()
