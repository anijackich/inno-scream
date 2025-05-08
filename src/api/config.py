"""API config."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_FILES = ('.env', './.envs/api/.env')
"""Environment files."""

dotenv_settings_config = SettingsConfigDict(
    extra='ignore',
    env_file=DOTENV_FILES,
    env_file_encoding='utf-8',
)
"""Config for .env."""


class AppMeta(BaseSettings):
    """Application metadata."""

    title: str = Field('InnoScream API')
    description: str = Field('Anonymous stress relief platform for students')
    version: str = Field('0.1.0')

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'app_'


class Database(BaseSettings):
    """Database config object."""

    url: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'database_'


class Memes(BaseSettings):
    """Memes config object."""

    captions_font: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'meme_'


class Settings(BaseSettings):
    """Application settings."""

    host: str = Field('127.0.0.1')
    port: int = Field(8000)
    app_meta: AppMeta = AppMeta()
    database: Database = Database()
    memes: Memes = Memes()

    model_config = dotenv_settings_config


settings = Settings()
"""Application settings."""
