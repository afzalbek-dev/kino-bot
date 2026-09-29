# Kino Bot — Telegram Kino Qidiruv Boti / Telegram Movie Discovery Bot

**Kino Bot** — bu **Python** va **Aiogram 3** freymvorkida yozilgan, kinolarni qidirish, VIP kirish huquqlarini tekshirish va qulay katalog tizimiga ega Telegram boti loyihasi.

---

## 🇺🇿 O'zbekcha Ma'lumot

### 📋 Loyiha Haqida

Kino Bot foydalanuvchilarga kinolarni nomi, kodi, janri, mamlakati yoki chiqarilgan yili bo'yicha tez va qulay qidirish imkonini beradi. Loyiha arxitekturasi toza (clean architecture) tamoyillariga asoslangan bo'lib, biznes mantiq Telegram API'dan ajratilgan. Bu testlarni osongina o'tkazish va kelajakda bazani PostgreSQL/SQLite yoki boshqa ma'lumotlar bazalariga ulashni yengillashtiradi.

---

### ✨ Asosiy Imkoniyatlar (Features)

- **Aiogram 3 Polling Mode:** Telegram Bot API bilan zamonaviy asinxron ishlash.
- **Kino Katalogi:** JSON formatidagi namunaviy kinolar bazasi (`sample_data/movies.json`).
- **Ko'p qirrali Qidiruv (Search):**
  - Kino kodi bo'yicha (masalan: `K001`, `K002`)
  - Nomi bo'yicha (masalan: `Night Runner`, `Inception`)
  - Janr bo'yicha (masalan: `Action`, `Comedy`)
  - Mamlakat bo'yicha (masalan: `USA`, `Uzbekistan`)
  - Chiqqan yili bo'yicha (masalan: `2025`, `2023`)
- **VIP & Bepul (Free) Kirish Tizimi:** Kinolarga kirish darajasini (bepul yoki VIP) tekshirish va tegishli xabarlarni ko'rsatish.
- **Konfiguratsiya va Xavfsizlik:** Pydantic va environment variables (`.env`) orqali sozlamalarni xavfsiz boshqarish.
- **Testlar va Kod Sifati:** Pytest va Ruff orqali avtomatik testlash va linter tekshiruvi.

---

### 🏗 Arxitektura va Tuzilish (Architecture)

```text
kino_bot/
├── __init__.py
├── access.py      # VIP va bepul kinolarga kirish qoidalari hamda xabarlar
├── bot.py         # Telegram handlerlar, handlerlarni ulash va start_polling
├── catalog.py     # Kinolarni qidirish, kod bo'yicha topish va saralash mantig'i
├── config.py      # Pydantic orqali .env sozlamalarini yuklash
├── demo.py        # Demo katalog yuklagich (JSON fayldan)
└── models.py      # Pydantic va Enum domen modellari (Movie, UserProfile va h.k.)

sample_data/
└── movies.json    # Namunaviy kinolar ma'lumotlar bazasi

tests/
└── test_catalog.py # Qidiruv, kod va VIP kirish huquqlarini tekshiruvchi testlar
```

---

### ⚙️ Texnologiyalar Staki (Tech Stack)

- **Python 3.11+**
- **Aiogram 3.x** — Telegram Bot API freymvorki
- **Pydantic v2 & Pydantic-Settings** — Ma'lumotlar validatsiyasi va sozlamalar
- **SQLAlchemy & Aiosqlite** — Asinxron ORM va ma'lumotlar bazasi tayyorgarligi
- **Pytest & Pytest-Asyncio** — Asinxron unit testlar
- **Ruff** — Tezkor Python linter va kod formatteri

---

### 🚀 O'rnatish va Ishga Tushirish (Installation & Run)

#### 1. Repozitoriyani klonlash va virtual muhitni yaratish:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Bog'liqliklarni (dependencies) o'rnatish:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

#### 3. `.env` faylini sozlash:

`.env.example` faylidan nusxa olib `.env` yaratasiz:

```bash
cp .env.example .env
```

`.env` fayliga BotFather'dan olingan tokeningizni kiriting:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
DATABASE_URL=sqlite+aiosqlite:///./kino.sqlite3
ADMIN_IDS=12345678,87654321
DEMO_MODE=True
LOG_LEVEL=INFO
```

#### 4. Botni ishga tushirish:

```bash
python3 -m kino_bot.bot
```

---

### 💡 Ishlatish (Usage Guide)

1. Botga `/start` buyrug'ini yuboring.
2. Qidirish uchun kino nomi (masalan: `Inception`), kodi (`K001`), janri (`Drama`), mamlakati (`Uzbekistan`) yoki yilini (`2025`) yuboring.
3. Agar kino VIP bo'lsa va foydalanuvchida VIP obuna bo'lmasa, bot obuna bo me'zonlarini eslatuvchi xabar beradi.

---

### 🧪 Testlash va Kod Sifatini Tekshirish (Testing)

Testlarni va linter tekshiruvini ishga tushirish uchun:

```bash
# Linter tekshiruvi
ruff check .

# Unit testlarni ishga tushirish
pytest
```

---

### 🔒 Xavfsizlik Eslatmalari (Security)

- `BOT_TOKEN` va maxfiy kalitlarni hech qachon GitHub repozitoriyasiga yuklamang (`.gitignore` sozlang).
- Admin panel va maxfiy buyruqlarni ishlatishdan oldin Telegram ID orqali xavfsiz tekshiruvdan o'tkazing.

---

## 🇬🇧 English Documentation

### 📋 About the Project

**Kino Bot** is a production-ready Telegram movie discovery bot built with **Python** and **Aiogram 3**. It offers search capabilities by movie code, title, genre, country, and release year, alongside VIP/free access control and clean domain logic separating Telegram handlers from core business rules.

### ✨ Key Features

- **Aiogram 3 Async Polling:** High-performance Telegram Bot API integration.
- **Movie Search:** Flexible searching by code, title, genre, country, or year.
- **VIP Access Control:** Differentiates free and VIP content.
- **Environment Configuration:** Pydantic settings with `.env` support.
- **Comprehensive Testing:** Unit tests with Pytest and linting with Ruff.

### 🚀 Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Set BOT_TOKEN in .env
python3 -m kino_bot.bot
```

---

© 2026 Kino Bot — Python & Telegram Bot Development
