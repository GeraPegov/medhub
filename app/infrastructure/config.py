from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
print(BASE_DIR)


class Setting(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_DB_URL: str
    TEST_DB_URL: str
    PROD_DB_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    HOST_REDIS: str
    PORT_REDIS: int

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


settings = Setting()
