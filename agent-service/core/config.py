from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    hf_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
