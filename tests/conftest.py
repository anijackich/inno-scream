import os
import pytest
import asyncio
from unittest.mock import patch


def pytest_configure(config):
    os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
    os.environ["ADMINS"] = "[1, 2, 3]"
    os.environ["REACTIONS"] = "[\"👍\", \"👎\", \"❤️\"]"
    os.environ["INNOSCREAM_BASE_URL"] = "http://test-api.com"


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env():
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "ADMINS": "[1, 2, 3]",
        "REACTIONS": "[\"👍\", \"👎\", \"❤️\"]",
        "INNOSCREAM_BASE_URL": "http://test-api.com"
    }
    with patch.dict(os.environ, env_vars):
        yield