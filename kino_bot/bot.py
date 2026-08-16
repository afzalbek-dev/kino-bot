from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from .access import access_message
from .config import get_settings
from .demo import load_demo_catalog
from .models import UserProfile

catalog = load_demo_catalog()


async def start(message: Message) -> None:
    await message.answer(
        "Welcome to Kino Bot. Send a movie name, code, genre, country, or year to search."
    )


async def search_movies(message: Message) -> None:
    query = message.text or ""
    user = UserProfile(telegram_id=message.from_user.id if message.from_user else 0)
    results = catalog.search(query, limit=5)
    if not results:
        await message.answer("No movies found. Try another title or code.")
        return
    lines = [
        f"{movie.code} - {movie.title} ({movie.year}) | IMDb {movie.imdb} | "
        f"{access_message(movie, user)}"
        for movie in results
    ]
    await message.answer("\n".join(lines))


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.message.register(search_movies, F.text)
    return dp


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required unless you only run tests or demo code.")
    await build_dispatcher().start_polling(Bot(settings.bot_token))


if __name__ == "__main__":
    asyncio.run(main())
