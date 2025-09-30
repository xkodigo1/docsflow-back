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

    # SMTP/Email
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool = False
    sender_email: str
    email_debug: bool = True

    # Frontend
    frontend_base_url: str | None = None

    # CORS
    cors_allowed_origins: list[str] = ["http://localhost:5174"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
