from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_FILES = ('.env', './.envs/api/.env')

dotenv_settings_config = SettingsConfigDict(
    extra='ignore',
    env_file=DOTENV_FILES,
    env_file_encoding='utf-8',
)


class AppMeta(BaseSettings):
    title: str = Field('InnoScream API')
    description: str = Field('Anonymous stress relief platform for students')
    version: str = Field('0.1.0')

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'app_'


class Database(BaseSettings):
    url: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'database_'


class Memes(BaseSettings):
    captions_font: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'meme_'


class Settings(BaseSettings):
    host: str = Field('127.0.0.1')
    port: int = Field(8000)
    app_meta: AppMeta = AppMeta()
    database: Database = Database()
    memes: Memes = Memes()

    model_config = dotenv_settings_config


settings = Settings()
