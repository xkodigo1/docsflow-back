from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Backend MVC"
    db_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expirations_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

