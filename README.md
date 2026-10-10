[English](README.md) | [Русский](README.ru.md)

# 🎬 Kino Bot

> **Enterprise-grade Telegram movie discovery bot built with Python and Aiogram 3, featuring async SQLite persistence, VIP access gating, favorite collections, and admin analytics.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-lightgrey.svg)](https://aiosqlite.omnilib.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Target Audience & Purpose

- **Target Audience**: Telegram communities, movie channels, media curators, cinema enthusiasts, and bot operators.
- **Core Purpose**: Deliver an instant, interactive cinema discovery experience within Telegram where users can look up movies by code, search by title/genre/country/year, manage personal favorites, and access exclusive VIP releases.

---

## Main Features

1. **Movie Lookup & Search Engine**:
   - Instant code lookup (e.g., `K001`, `#K001`, `/kino K001`).
   - Multi-field search across title, genre, country, and release year with IMDb rating sorting.
   - Curated Top 5 movies and random movie discovery button.
2. **Access Control & VIP Subscriptions**:
   - Two-tier catalog: Free and VIP.
   - Strict gating for VIP releases with subscription prompts for regular users.
   - Admin command to grant timed VIP memberships.
3. **Favorites & User Collections**:
   - Save favorite movies with one-click inline buttons (`⭐ Add to Favorites`).
   - Dedicated `/favorites` menu to browse saved titles.
4. **Interactive Telegram UX**:
   - Clean HTML-formatted movie cards with title, year, IMDb score, genre, country, and synopsis.
   - Inline keyboards with instant callback handlers.
5. **Database Persistence**:
   - Async SQLite engine (`aiosqlite`) with automatic database initialization and schema migration.
   - Automatic seeding from curated sample dataset (`sample_data/movies.json`).
6. **Administrator Dashboard**:
   - `/admin` and `/stats` commands for real-time user metrics, VIP counts, movie catalog size, and search queries.

---

## Architecture & Tech Stack

- **Framework**: Aiogram 3.10+ (Router and Dispatcher architecture)
- **Database**: SQLite via `aiosqlite` with asynchronous connection pooling
- **Validation**: Pydantic v2 & Pydantic-Settings
- **Testing**: Pytest & pytest-asyncio (18 unit & integration tests)
- **Packaging**: Standard `pyproject.toml` with setuptools

```
kino-bot/
├── kino_bot/
│   ├── __init__.py
│   ├── access.py        # Free & VIP permission verification
│   ├── bot.py           # Telegram handlers, commands, keyboards, and polling
│   ├── catalog.py       # Domain catalog search and lookup logic
│   ├── config.py        # Resilient environment settings loader
│   ├── database.py      # Async SQLite persistence, users, favorites, and stats
│   ├── demo.py          # Fallback JSON catalog loader
│   └── models.py        # Domain models (Movie, MovieAccess, UserProfile)
├── sample_data/
│   └── movies.json      # Curated starter movie catalog
├── tests/
│   ├── test_access.py        # VIP access gating tests
│   ├── test_bot_handlers.py  # Keyboards, formatting, and regex tests
│   ├── test_catalog.py       # Catalog search and sorting tests
│   └── test_database.py      # Async SQLite CRUD, favorites, and stats tests
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Requirements & Configuration

### Prerequisites
- Python 3.11+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `BOT_TOKEN` | Yes | `""` | Telegram Bot API token from BotFather |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./kino.sqlite3` | SQLite database connection string |
| `ADMIN_IDS` | No | `""` | Comma-separated Telegram user IDs of bot admins |
| `DEMO_MODE` | No | `true` | Fallback to bundled sample data if database empty |
| `LOG_LEVEL` | No | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`) |

---

## Installation & Running

### Local Environment

```bash
# 1. Clone repository
git clone https://github.com/afzalbek-dev/kino-bot.git
cd kino-bot

# 2. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Configure environment
cp .env.example .env
# Edit .env and insert your BOT_TOKEN

# 5. Run bot
python -m kino_bot.bot
```

### Running with Docker

```bash
docker compose up -d --build
```

---

## Testing Guide

Run all unit and integration tests:

```bash
pytest -v
```

All 18 tests execute in isolation using temporary test SQLite databases.

---

## Telegram Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Open main menu with interactive inline buttons |
| `/help` | Display command guide and search tips |
| `/kino <code>` | View movie card by code (e.g. `/kino K001`) |
| `/search <text>` | Search movies by title, genre, country, or year |
| `/top` | Display Top 5 rated movies by IMDb score |
| `/random` | Get a random movie recommendation |
| `/favorites` | View personal list of saved favorite movies |
| `/vip` | Check current VIP membership status |
| `/admin` | Administrator statistics and control panel |
| `/grant_vip <id> [days]` | (Admin only) Grant VIP access to specified Telegram user |

---

## Security Notes

- **Pre-Push Hook**: Local pre-push hook installed to enforce manual authorization.
- **Zero Secrets**: Bot tokens and private credentials are excluded via `.gitignore`.
- **Database Safety**: Parameterized SQL queries prevent SQL injection vulnerabilities.

---

## Implementation & Test Status

- **Status**: Production-Ready
- **Unit & Integration Tests**: 18 / 18 Passed (100%)
- **License**: MIT
- **Author**: Afzalbek
