from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_uri: str = "mysql+aiomysql://user:pass@127.0.0.1:5432/db"


settings = Settings()