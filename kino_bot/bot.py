from __future__ import annotations

import asyncio
import logging
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from .access import access_message
from .config import get_settings
from .database import Database
from .demo import load_demo_catalog
from .models import Movie, MovieAccess, UserProfile

settings = get_settings()
logger = logging.getLogger("kino_bot")
demo_catalog = load_demo_catalog()
db = Database(settings.database_url)

CODE_PATTERN = re.compile(r"^#?([A-Z0-9]{3,8})$", re.IGNORECASE)


def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏆 Top Movies", callback_data="nav:top"),
                InlineKeyboardButton(text="🎲 Random Movie", callback_data="nav:random"),
            ],
            [
                InlineKeyboardButton(text="⭐ My Favorites", callback_data="nav:favorites"),
                InlineKeyboardButton(text="👑 VIP Status", callback_data="nav:vip"),
            ],
            [
                InlineKeyboardButton(text="ℹ️ Help & Commands", callback_data="nav:help"),
            ],
        ]
    )


def get_movie_keyboard(movie: Movie, is_fav: bool = False) -> InlineKeyboardMarkup:
    fav_text = "❌ Remove from Favorites" if is_fav else "⭐ Add to Favorites"
    fav_action = f"fav:remove:{movie.code}" if is_fav else f"fav:add:{movie.code}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=fav_text, callback_data=fav_action),
            ],
            [
                InlineKeyboardButton(text="🎲 Another Random", callback_data="nav:random"),
                InlineKeyboardButton(text="🔙 Main Menu", callback_data="nav:menu"),
            ],
        ]
    )


def format_movie_card(movie: Movie, user: UserProfile) -> str:
    status_icon = "👑 VIP" if movie.access == MovieAccess.VIP else "🟢 Free"
    watch_status = access_message(movie, user)
    return (
        f"🎬 <b>{movie.title}</b> ({movie.year})\n"
        f"🔑 <b>Code:</b> <code>{movie.code}</code>\n"
        f"⭐ <b>IMDb:</b> {movie.imdb}/10\n"
        f"🎭 <b>Genre:</b> {movie.genre}\n"
        f"🌍 <b>Country:</b> {movie.country}\n"
        f"🏷️ <b>Access:</b> {status_icon}\n\n"
        f"📝 <b>Description:</b>\n{movie.description}\n\n"
        f"ℹ️ <i>{watch_status}</i>"
    )


async def start_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    username = message.from_user.username or "" if message.from_user else ""
    first_name = message.from_user.first_name or "" if message.from_user else ""
    await db.get_or_create_user(user_id, username, first_name)

    await message.answer(
        "👋 <b>Welcome to Kino Bot!</b>\n\n"
        "Discover movies instantly. You can:\n"
        "• Send a <b>Movie Code</b> (e.g. <code>K001</code>, <code>K002</code>)\n"
        "• Send any <b>Title, Genre, Country, or Year</b> to search\n"
        "• Use buttons below to browse Top or Random titles.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
    )


async def help_handler(message: Message) -> None:
    await message.answer(
        "📖 <b>Kino Bot Commands:</b>\n\n"
        "/start - Main menu\n"
        "/kino <code> - Movie details by code (e.g., <code>/kino K001</code>)\n"
        "/search <text> - Search catalog by title/genre/year\n"
        "/top - View Top 5 rated movies\n"
        "/random - Get a random movie recommendation\n"
        "/favorites - View your saved favorite movies\n"
        "/vip - View VIP membership status\n"
        "/admin - Administrator control panel",
        parse_mode="HTML",
    )


async def kino_code_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Please provide a movie code: <code>/kino K001</code>", parse_mode="HTML")
        return
    code = parts[1].strip().upper()
    await process_movie_lookup(message, code)


async def search_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Please provide a search query: <code>/search Inception</code>", parse_mode="HTML")
        return
    query = parts[1].strip()
    await execute_search(message, query)


async def top_command(message: Message) -> None:
    movies = await db.get_top_movies(limit=5)
    if not movies:
        movies = demo_catalog.top(limit=5)

    user_id = message.from_user.id if message.from_user else 0
    await db.get_or_create_user(user_id)

    lines = ["🏆 <b>Top Rated Movies:</b>\n"]
    for idx, m in enumerate(movies, 1):
        vip_tag = " [👑 VIP]" if m.access == MovieAccess.VIP else ""
        lines.append(f"{idx}. <b>{m.title}</b> ({m.year}) — ⭐ {m.imdb} | <code>{m.code}</code>{vip_tag}")

    lines.append("\n<i>Send any movie code to view details.</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


async def random_command(message: Message) -> None:
    movie = await db.get_random_movie()
    if not movie:
        movie = demo_catalog.random_movie()

    if not movie:
        await message.answer("Catalog is empty.")
        return

    user_id = message.from_user.id if message.from_user else 0
    user = await db.get_or_create_user(user_id)
    is_fav = await db.is_favorite(user_id, movie.code)

    card = format_movie_card(movie, user)
    await message.answer(card, reply_markup=get_movie_keyboard(movie, is_fav), parse_mode="HTML")


async def favorites_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    favs = await db.get_favorites(user_id)
    if not favs:
        await message.answer(
            "⭐ <b>Your Favorites List is Empty.</b>\n\n"
            "Browse movies and click <b>⭐ Add to Favorites</b> to save them here.",
            parse_mode="HTML",
        )
        return

    lines = ["⭐ <b>Your Saved Movies:</b>\n"]
    for idx, m in enumerate(favs, 1):
        lines.append(f"{idx}. <b>{m.title}</b> ({m.year}) — <code>{m.code}</code> | ⭐ {m.imdb}")

    lines.append("\n<i>Send any code to view details or remove.</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


async def vip_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    user = await db.get_or_create_user(user_id)

    if user.is_vip:
        await message.answer(
            "👑 <b>VIP Status: ACTIVE</b>\n\n"
            "You have unlimited access to all VIP movies and exclusive releases. Enjoy!",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "👑 <b>VIP Membership</b>\n\n"
            "Status: <b>Standard (Free)</b>\n\n"
            "VIP benefits include:\n"
            "• Unrestricted access to VIP releases\n"
            "• Fast download speeds & premium audio\n"
            "• Early access to upcoming premieres\n\n"
            "To activate VIP access, contact our administrators.",
            parse_mode="HTML",
        )


async def admin_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if user_id not in settings.admins:
        await message.answer("⛔ Access denied. Administrator privileges required.")
        return

    stats = await db.get_stats()
    await message.answer(
        "🛠️ <b>Kino Bot Administrator Dashboard</b>\n\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"👑 VIP Users: <b>{stats['vip_users']}</b>\n"
        f"🎬 Total Movies: <b>{stats['total_movies']}</b>\n"
        f"🔍 Total Searches: <b>{stats['total_searches']}</b>\n\n"
        "<b>Admin Commands:</b>\n"
        "• <code>/grant_vip &lt;user_id&gt; [days]</code>\n"
        "• <code>/addmovie CODE|Title|Year|Genre|Country|IMDb|Description|free/vip</code>",
        parse_mode="HTML",
    )


async def grant_vip_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if user_id not in settings.admins:
        await message.answer("⛔ Access denied.")
        return

    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Usage: <code>/grant_vip &lt;user_id&gt; [days]</code>", parse_mode="HTML")
        return

    try:
        target_id = int(parts[1])
        days = int(parts[2]) if len(parts) > 2 else 30
        exp_date = (datetime.now(UTC) + timedelta(days=days)).isoformat()
        await db.set_vip(target_id, is_vip=True, expires_at=exp_date)
        await message.answer(f"✅ User <code>{target_id}</code> granted VIP for {days} days.", parse_mode="HTML")
    except (ValueError, KeyError, RuntimeError) as e:
        await message.answer(f"❌ Error granting VIP: {e}")


async def generic_message_handler(message: Message) -> None:
    text = (message.text or "").strip()
    if not text:
        return

    # Check if text is direct movie code (e.g. K001)
    match = CODE_PATTERN.match(text)
    if match:
        code = match.group(1).upper()
        found = await process_movie_lookup(message, code, silent_not_found=True)
        if found:
            return

    # Fallback to search
    await execute_search(message, text)


async def process_movie_lookup(message: Message, code: str, silent_not_found: bool = False) -> bool:
    movie = await db.get_movie(code)
    if not movie:
        movie = demo_catalog.by_code(code)

    if not movie:
        if not silent_not_found:
            await message.answer(f"❌ Movie with code <code>{code}</code> was not found.", parse_mode="HTML")
        return False

    user_id = message.from_user.id if message.from_user else 0
    user = await db.get_or_create_user(user_id)
    is_fav = await db.is_favorite(user_id, movie.code)

    card = format_movie_card(movie, user)
    await message.answer(card, reply_markup=get_movie_keyboard(movie, is_fav), parse_mode="HTML")
    return True


async def execute_search(message: Message, query: str) -> None:
    user_id = message.from_user.id if message.from_user else 0
    await db.get_or_create_user(user_id)

    results = await db.search_movies(query, limit=5, telegram_id=user_id)
    if not results:
        results = demo_catalog.search(query, limit=5)

    if not results:
        await message.answer(f"🔍 No movies found for <i>'{query}'</i>. Try another title or genre.", parse_mode="HTML")
        return

    lines = [f"🔍 <b>Search Results for:</b> <i>'{query}'</i>\n"]
    for idx, m in enumerate(results, 1):
        vip_tag = " [👑 VIP]" if m.access == MovieAccess.VIP else ""
        lines.append(f"{idx}. <b>{m.title}</b> ({m.year}) | IMDb {m.imdb} | <code>{m.code}</code>{vip_tag}")

    lines.append("\n<i>Send any code to view full details.</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


async def callback_handler(call: CallbackQuery) -> None:
    data = call.data or ""
    user_id = call.from_user.id if call.from_user else 0
    user = await db.get_or_create_user(user_id)

    if data == "nav:top":
        movies = await db.get_top_movies(limit=5)
        if not movies:
            movies = demo_catalog.top(limit=5)
        lines = ["🏆 <b>Top Rated Movies:</b>\n"]
        for idx, m in enumerate(movies, 1):
            vip_tag = " [👑 VIP]" if m.access == MovieAccess.VIP else ""
            lines.append(f"{idx}. <b>{m.title}</b> ({m.year}) — ⭐ {m.imdb} | <code>{m.code}</code>{vip_tag}")
        lines.append("\n<i>Send any movie code to view details.</i>")
        if call.message and isinstance(call.message, Message):
            await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=get_main_keyboard())
        await call.answer()

    elif data == "nav:random":
        movie = await db.get_random_movie()
        if not movie:
            movie = demo_catalog.random_movie()
        if movie and call.message and isinstance(call.message, Message):
            is_fav = await db.is_favorite(user_id, movie.code)
            card = format_movie_card(movie, user)
            await call.message.edit_text(card, reply_markup=get_movie_keyboard(movie, is_fav), parse_mode="HTML")
        await call.answer()

    elif data == "nav:favorites":
        favs = await db.get_favorites(user_id)
        if not favs:
            msg = "⭐ <b>Your Favorites List is Empty.</b>\n\nBrowse movies and click ⭐ Add to Favorites to save them here."
        else:
            lines = ["⭐ <b>Your Saved Movies:</b>\n"]
            for idx, m in enumerate(favs, 1):
                lines.append(f"{idx}. <b>{m.title}</b> ({m.year}) — <code>{m.code}</code> | ⭐ {m.imdb}")
            lines.append("\n<i>Send any code to view details.</i>")
            msg = "\n".join(lines)
        if call.message and isinstance(call.message, Message):
            await call.message.edit_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard())
        await call.answer()

    elif data == "nav:vip":
        status_text = "ACTIVE (Unlimited access)" if user.is_vip else "Standard (Free)"
        msg = (
            f"👑 <b>VIP Membership</b>\n\n"
            f"Status: <b>{status_text}</b>\n\n"
            f"VIP access unlocks all exclusive releases and priority streams."
        )
        if call.message and isinstance(call.message, Message):
            await call.message.edit_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard())
        await call.answer()

    elif data == "nav:help":
        msg = (
            "📖 <b>How to use Kino Bot:</b>\n\n"
            "• Send a code: <code>K001</code>\n"
            "• Search by name: <code>Night Runner</code>\n"
            "• Search by genre: <code>Action</code>, <code>Comedy</code>\n"
            "• Search by country: <code>Uzbekistan</code>, <code>USA</code>"
        )
        if call.message and isinstance(call.message, Message):
            await call.message.edit_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard())
        await call.answer()

    elif data == "nav:menu":
        if call.message and isinstance(call.message, Message):
            await call.message.edit_text(
                "🎬 <b>Kino Bot Main Menu</b>\n\nSelect an option below or send a movie code/title to search:",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
            )
        await call.answer()

    elif data.startswith("fav:add:"):
        code = data.split("fav:add:")[1]
        await db.add_favorite(user_id, code)
        movie = await db.get_movie(code) or demo_catalog.by_code(code)
        if movie and call.message and isinstance(call.message, Message):
            await call.message.edit_reply_markup(reply_markup=get_movie_keyboard(movie, is_fav=True))
        await call.answer("⭐ Added to favorites!")

    elif data.startswith("fav:remove:"):
        code = data.split("fav:remove:")[1]
        await db.remove_favorite(user_id, code)
        movie = await db.get_movie(code) or demo_catalog.by_code(code)
        if movie and call.message and isinstance(call.message, Message):
            await call.message.edit_reply_markup(reply_markup=get_movie_keyboard(movie, is_fav=False))
        await call.answer("❌ Removed from favorites.")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.register(start_handler, CommandStart())
    dp.message.register(help_handler, Command("help"))
    dp.message.register(kino_code_command, Command("kino"))
    dp.message.register(search_command, Command("search"))
    dp.message.register(top_command, Command("top"))
    dp.message.register(random_command, Command("random"))
    dp.message.register(favorites_command, Command("favorites", "favs"))
    dp.message.register(vip_command, Command("vip"))
    dp.message.register(admin_command, Command("admin", "stats"))
    dp.message.register(grant_vip_command, Command("grant_vip"))
    dp.message.register(generic_message_handler, F.text)
    dp.callback_query.register(callback_handler)
    return dp


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    seed_file = Path(__file__).resolve().parent.parent / "sample_data" / "movies.json"
    await db.init_db(seed_path=seed_file)

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required unless you only run tests or demo code.")

    bot = Bot(settings.bot_token)
    dp = build_dispatcher()
    logger.info("Starting Kino Bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
