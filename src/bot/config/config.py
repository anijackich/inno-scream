from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBot(BaseSettings):
    token: str = Field(..., validation_alias='telegram_bot_token')
    admins: list[int] = Field(...)
    reactions: list[str] = Field(...)


class InnoScream(BaseSettings):
    base_url: str = Field(...)

    model_config = SettingsConfigDict(env_prefix='innoscream_')


class Settings(BaseSettings):
    bot: TelegramBot = TelegramBot()
    innoscream: InnoScream = InnoScream()


settings = Settings()
