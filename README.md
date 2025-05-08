# InnoScream

[![https://t.me/inno-cream-bot](https://img.shields.io/badge/Open-Telegram_Bot-blue?logo=telegram)](https://t.me/KinescopeDL)
[![Python Version](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/anijackich/inno-scream/main/pyproject.toml)](https://github.com/anijackich/inno-scream/.python-version)
[![License: MIT](https://img.shields.io/github/license/anijackich/inno-scream)](https://github.com/anijackich/inno-scream/blob/master/LICENSE)

InnoScream is a Telegram-based platform where students can anonymously share their
frustrations and receive community support via reactions, memes, and analytics.

## ✨ Features

- [x] Anonymous posts (screams)
- [x] Reactions on posts
- [x] Showing most-voted posts
- [x] Automatically generated memes
- [x] Personal statistics
- [x] Weekly stress graphs
- [x] Admin moderation via deleting posts

## ⬇️ Download & Setup

Clone this repository:

```shell
git clone https://github.com/anijackich/inno-cream-bot
cd inno-cream-bot
```

### API

#### Set environment variables

```shell
mv .envs/api/.env.example .envs/api/.env
```

| Variable             | Description                | Example                         |
|----------------------|----------------------------|---------------------------------|
| `HOST`               | Host serving the API       | `127.0.0.1`                     |
| `PORT`               | Port serving the API       | `8080`                          |
| `DATABASE_URL`       | Database URL               | `sqlite+aiosqlite:///./test.db` |
| `MEME_CAPTIONS_FONT` | Path to meme captions font | `fonts/impact.ttf`              |

### Bot

#### Set environment variables

```shell
mv .envs/bot/.env.example .envs/bot/.env
```

| Variable              | Description             | Example                 |
|-----------------------|-------------------------|-------------------------|
| `TELEGRAM_BOT_TOKEN`  | Telegram bot token      | `12345678:ABCDefghijk`  |
| `ADMINS`              | Bot admins' ids list    | `[12345678, 87654321]`  |
| `REACTIONS`           | Allowed reactions       | `["💀", "🔥", "🤡"]`    |
| `INNOSCREAM_BASE_URL` | InnoScream API base URL | `http://127.0.0.1:8080` |

## 🐋 Docker

### Run

```shell
docker compose up -d
```

## 🚀 Run from sources

### API

#### Install dependencies

```shell
poetry install --with api
```

#### Run

```shell
poetry run python -m src.api
```

### Bot

#### Install dependencies

```shell
poetry install --with bot
```

#### Run

```shell
poetry run python -m src.bot
```