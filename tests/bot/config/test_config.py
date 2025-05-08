import os
import pytest
from unittest.mock import patch

from src.bot.config.config import TelegramBot, InnoScream, Settings


@pytest.fixture
def mock_env_vars():
    env_vars = {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'ADMINS': '[1, 2, 3]',
        'REACTIONS': '["👍", "👎", "❤️"]',
        'INNOSCREAM_BASE_URL': 'http://test-api.com',
    }
    with patch.dict(os.environ, env_vars):
        yield


def test_telegram_bot_config(mock_env_vars):
    bot_config = TelegramBot()

    assert bot_config.token == 'test_token'
    assert bot_config.admins == [1, 2, 3]
    assert bot_config.reactions == ['👍', '👎', '❤️']


def test_telegram_bot_config_empty_admins():
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'ADMINS': '[]',
        'REACTIONS': '["👍", "👎", "❤️"]',
    }):
        bot_config = TelegramBot()
        assert bot_config.admins == []


def test_telegram_bot_config_empty_reactions():
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'ADMINS': '[1, 2, 3]',
        'REACTIONS': '[]',
    }):
        bot_config = TelegramBot()
        assert bot_config.reactions == []


def test_innoscream_config(mock_env_vars):
    innoscream_config = InnoScream()

    assert innoscream_config.base_url == 'http://test-api.com'


def test_settings(mock_env_vars):
    settings = Settings()

    assert settings.bot.token == 'test_token'
    assert settings.bot.admins == [1, 2, 3]
    assert settings.bot.reactions == ['👍', '👎', '❤️']
    assert settings.innoscream.base_url == 'http://test-api.com'
