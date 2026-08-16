# Kino Bot

Kino Bot is a production-oriented Telegram movie discovery bot written in **Python**
with **Aiogram 3**. It demonstrates a clean movie catalog, VIP access checks, search
by title, code, country, genre, and year, plus a documented path for connecting a real
database and Telegram deployment.

## Features

- Aiogram 3 polling bot entrypoint
- Demo movie catalog with structured JSON sample data
- Search by movie code, title, genre, country, or release year
- VIP/free access validation
- Clear error handling for missing bot configuration
- Unit-tested core domain logic
- GitHub Actions CI with Ruff and Pytest
- MIT licensed and portfolio-ready documentation

## Architecture

```text
kino_bot/
  bot.py       Telegram handlers and dispatcher wiring
  catalog.py   Movie search and lookup logic
  access.py    VIP access rules
  config.py    Environment-based settings
  demo.py      Demo catalog loader
  models.py    Domain models
```

The Telegram adapter is intentionally thin. Business rules live in small modules that
can be tested without a Telegram token or network access.

## Requirements

- Python 3.11+
- Telegram bot token from BotFather for real bot usage

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Set `BOT_TOKEN` in `.env` before running the Telegram bot.

## Configuration

| Variable | Required | Description |
|---|---:|---|
| `BOT_TOKEN` | Yes for bot runtime | Telegram Bot API token |
| `DATABASE_URL` | No | Future database connection string |
| `ADMIN_IDS` | No | Comma-separated Telegram admin IDs |
| `DEMO_MODE` | No | Keeps the app on bundled sample data |
| `LOG_LEVEL` | No | Python logging level |

Never commit `.env`, tokens, database dumps, or private Telegram data.

## Run

```bash
python -m kino_bot.bot
```

Demo data is loaded from `sample_data/movies.json`.

## Usage

1. Start the bot with `/start`.
2. Send a movie title such as `Night Runner`.
3. Send a code such as `K002`.
4. Search by `Uzbekistan`, `Comedy`, or `2025`.

VIP movies return a clear subscription message for regular users.

## Testing and Quality

```bash
ruff check .
pytest
```

The tests cover search, code lookup, and VIP access validation.

## Database Plan

The current repository ships a deterministic demo catalog so the project runs
immediately. For production, replace `MovieCatalog.from_json` with a SQLAlchemy
repository backed by PostgreSQL or SQLite. Keep the `MovieCatalog` interface stable
so Telegram handlers and tests remain simple.

## Security Notes

- Keep `BOT_TOKEN` and production database credentials in environment variables only.
- Validate admin IDs before enabling privileged commands.
- Avoid storing raw payment screenshots or private user messages unless a retention
  policy exists.
- Use Telegram file IDs instead of downloading private media when possible.

## Limitations

- The bundled implementation uses JSON demo data, not a production database.
- Admin CRUD, payments, and channel subscription checks are documented extension points.
- Webhook mode is not included; polling is used for a simple deploy story.

## Future Improvements

- SQLAlchemy movie, user, favorite, and subscription tables
- Admin movie CRUD conversation flow
- Mandatory channel subscription checks
- Payment approval workflow
- Favorites and watch history
- Docker deployment profile

## License

MIT
- Exportable summaries

PDF reporting can also be included when required.

---

## 🔐 Security & Access Control

The project is designed with controlled administrative access and protected configuration.

Security considerations include:

- Admin-only management commands
- Secure bot token storage
- Environment-based secrets
- Permission checks
- User access validation
- Payment verification controls
- Rate-limit / anti-spam options

Sensitive credentials are never intended to be exposed publicly.

---

## ⚙️ Technology Stack

The project is designed around a modern Python Telegram stack:

- **Python 3.11+**
- **Aiogram 3.x**
- **SQLite / PostgreSQL**
- **SQLAlchemy**
- **Telegram Bot API**
- **Async programming**
- **Linux hosting / VPS deployment**
- Optional Redis and background task processing for larger deployments

---

## 📈 Designed for Growth

The architecture can be extended with additional modules such as:

- Recommendation engine
- Multi-language interface
- Referral program
- Promo codes
- Premium packages
- Movie request system
- Comments and ratings
- Personalized recommendations
- Web admin dashboard
- Telegram Mini App
- External movie API integrations
- Automatic metadata collection

---

## 🎯 Use Cases

This solution is suitable for:

- Telegram movie channels
- Media communities
- Subscription-based entertainment projects
- Private premium movie communities
- Movie catalog services
- Telegram content businesses

---

## 👨‍💻 Developer

**Afzalbek — Python & Telegram Bot Developer**

Specialized in:

- Telegram Bots
- Aiogram 3.x
- FastAPI Backend Development
- Telegram Mini Apps
- Admin Panels
- API Integrations
- AI Automation
- Web Applications

### Contact

- **Telegram:** [@Obunachi786](https://t.me/Obunachi786)
- **WhatsApp:** [+62 838-6529-5905](https://wa.me/6283865295905)
- **Location:** Qashqadaryo, Uzbekistan

---

## 📌 Note

This repository contains **project information and portfolio documentation only**. The source code of the commercial bot is not publicly available.

---

© 2026 Afzalbek — Telegram Bot & Python Developer
