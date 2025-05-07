from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_FILES = ('.env', './.envs/bot/.env')

dotenv_settings_config = SettingsConfigDict(
    extra='ignore',
    env_file=DOTENV_FILES,
    env_file_encoding='utf-8',
)


class TelegramBot(BaseSettings):
    token: str = Field(..., validation_alias='telegram_bot_token')
    admins: list[int] = Field(...)
    reactions: list[str] = Field(...)

    model_config = dotenv_settings_config


class InnoScream(BaseSettings):
    base_url: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'innoscream_'


class Settings(BaseSettings):
    bot: TelegramBot = TelegramBot()
    innoscream: InnoScream = InnoScream()


settings = Settings()
