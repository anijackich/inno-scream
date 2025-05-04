from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMeta(BaseSettings):
    title: str = Field('InnoScream API')
    description: str = Field('Anonymous stress relief platform for students')
    version: str = Field('0.1.0')

    model_config = SettingsConfigDict(env_prefix='app_')


class Database(BaseSettings):
    url: str = Field(...)

    model_config = SettingsConfigDict(env_prefix='database_')


class Settings(BaseSettings):
    host: str = Field('127.0.0.1')
    port: int = Field(8000)
    app_meta: AppMeta = AppMeta()
    database: Database = Database()


settings = Settings()
