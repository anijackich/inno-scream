"""Configuration settings for the Anonymous Scream Bot.

This module defines settings classes for loading and validating
environment-based configuration using `pydantic` and `pydantic-settings`.

It includes settings for:
- Telegram bot authentication and behavior
- InnoScream backend service endpoint
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_FILES = ('.env', './.envs/bot/.env')

dotenv_settings_config = SettingsConfigDict(
    extra='ignore',
    env_file=DOTENV_FILES,
    env_file_encoding='utf-8',
)


class TelegramBot(BaseSettings):
    """Configuration for the Telegram bot.

    Attributes:
        token (str): The bot token used to authenticate with Telegram.
        admins (list[int]): A list of Telegram user IDs with admin privileges.
        reactions (list[str]): A list of available reaction emojis.
    """

    token: str = Field(..., validation_alias='telegram_bot_token')
    admins: list[int] = Field(...)
    reactions: list[str] = Field(...)

    model_config = dotenv_settings_config


class InnoScream(BaseSettings):
    """Configuration for the InnoScream service.

    Attributes:
        base_url (str): Base URL of the InnoScream API service.
    """

    base_url: str = Field(...)

    model_config = dotenv_settings_config
    model_config['env_prefix'] = 'innoscream_'


class Settings(BaseSettings):
    """Aggregated settings for the application.

    Attributes:
        bot (TelegramBot): Settings related to the Telegram bot.
        innoscream (InnoScream): Settings related to the InnoScream service.
    """

    bot: TelegramBot = TelegramBot()
    innoscream: InnoScream = InnoScream()


settings = Settings()
