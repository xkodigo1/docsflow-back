from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Docsflow"
    app_env: str = "development"
    app_port: int = 8000

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expirations_minutes: int = 30

    # DB
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    # Uploads
    upload_directory: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
