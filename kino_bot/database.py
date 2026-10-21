from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiosqlite

from .models import Movie, MovieAccess, UserProfile


class Database:
    def __init__(self, db_path: str = "./kino.sqlite3") -> None:
        # Normalize sqlite:/// path if passed
        self.db_path = db_path.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")

    @asynccontextmanager
    async def get_connection(self):
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn

    async def init_db(self, seed_path: Path | None = None) -> None:
        async with self.get_connection() as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_vip BOOLEAN DEFAULT 0,
                    vip_expires_at TEXT,
                    created_at TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS movies (
                    code TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    year INTEGER,
                    genre TEXT,
                    country TEXT,
                    imdb REAL,
                    description TEXT,
                    access TEXT DEFAULT 'free',
                    file_id TEXT,
                    view_count INTEGER DEFAULT 0
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    telegram_id INTEGER,
                    movie_code TEXT,
                    added_at TEXT,
                    PRIMARY KEY (telegram_id, movie_code)
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    query TEXT,
                    created_at TEXT
                )
                """
            )
            await db.commit()

            # Optional seeding from JSON if table empty
            cursor = await db.execute("SELECT COUNT(*) AS cnt FROM movies")
            row = await cursor.fetchone()
            if row and row["cnt"] == 0 and seed_path and seed_path.exists():
                data = json.loads(seed_path.read_text(encoding="utf-8"))
                for item in data:
                    await db.execute(
                        """
                        INSERT OR IGNORE INTO movies
                        (code, title, year, genre, country, imdb, description, access, file_id, view_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(item["code"]).upper(),
                            str(item["title"]),
                            int(item["year"]),
                            str(item["genre"]),
                            str(item["country"]),
                            float(item["imdb"]),
                            str(item["description"]),
                            str(item.get("access", "free")),
                            str(item.get("file_id", "")),
                            0,
                        ),
                    )
                await db.commit()

    async def get_or_create_user(
        self, telegram_id: int, username: str = "", first_name: str = ""
    ) -> UserProfile:
        now_iso = datetime.now(UTC).isoformat()
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT telegram_id, is_vip, vip_expires_at FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = await cursor.fetchone()
            if row:
                is_vip = bool(row["is_vip"])
                if row["vip_expires_at"]:
                    try:
                        exp = datetime.fromisoformat(row["vip_expires_at"])
                        if exp < datetime.now(UTC):
                            is_vip = False
                    except (ValueError, TypeError):
                        pass
                return UserProfile(telegram_id=telegram_id, is_vip=is_vip)

            await db.execute(
                """
                INSERT INTO users (telegram_id, username, first_name, is_vip, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (telegram_id, username, first_name, now_iso),
            )
            await db.commit()
            return UserProfile(telegram_id=telegram_id, is_vip=False)

    async def set_vip(
        self, telegram_id: int, is_vip: bool = True, expires_at: str | None = None
    ) -> None:
        async with self.get_connection() as db:
            await db.execute(
                """
                UPDATE users SET is_vip = ?, vip_expires_at = ? WHERE telegram_id = ?
                """,
                (1 if is_vip else 0, expires_at, telegram_id),
            )
            await db.commit()

    async def add_movie(self, movie: Movie) -> None:
        async with self.get_connection() as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO movies
                (code, title, year, genre, country, imdb, description, access, file_id, view_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', 0)
                """,
                (
                    movie.code.upper(),
                    movie.title,
                    movie.year,
                    movie.genre,
                    movie.country,
                    movie.imdb,
                    movie.description,
                    movie.access.value if hasattr(movie.access, "value") else str(movie.access),
                ),
            )
            await db.commit()

    async def get_movie(self, code: str) -> Movie | None:
        normalized = code.strip().upper()
        async with self.get_connection() as db:
            cursor = await db.execute("SELECT * FROM movies WHERE code = ?", (normalized,))
            row = await cursor.fetchone()
            if not row:
                return None
            return self._row_to_movie(row)

    async def search_movies(
        self, query: str, limit: int = 10, telegram_id: int | None = None
    ) -> list[Movie]:
        norm = query.strip().lower()
        async with self.get_connection() as db:
            if telegram_id:
                await db.execute(
                    "INSERT INTO searches (telegram_id, query, created_at) VALUES (?, ?, ?)",
                    (telegram_id, query, datetime.now(UTC).isoformat()),
                )
                await db.commit()

            if not norm:
                cursor = await db.execute(
                    "SELECT * FROM movies ORDER BY imdb DESC, title ASC LIMIT ?", (limit,)
                )
            else:
                like_pattern = f"%{norm}%"
                cursor = await db.execute(
                    """
                    SELECT * FROM movies
                    WHERE lower(title) LIKE ?
                       OR lower(genre) LIKE ?
                       OR lower(country) LIKE ?
                       OR lower(code) = ?
                       OR cast(year as text) = ?
                    ORDER BY imdb DESC, title ASC
                    LIMIT ?
                    """,
                    (like_pattern, like_pattern, like_pattern, norm, norm, limit),
                )
            rows = await cursor.fetchall()
            return [self._row_to_movie(r) for r in rows]

    async def get_top_movies(self, limit: int = 5) -> list[Movie]:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM movies ORDER BY imdb DESC, title ASC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [self._row_to_movie(r) for r in rows]

    async def get_random_movie(self) -> Movie | None:
        async with self.get_connection() as db:
            cursor = await db.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1")
            row = await cursor.fetchone()
            if not row:
                return None
            return self._row_to_movie(row)

    async def add_favorite(self, telegram_id: int, movie_code: str) -> bool:
        code = movie_code.strip().upper()
        async with self.get_connection() as db:
            cursor = await db.execute("SELECT 1 FROM movies WHERE code = ?", (code,))
            if not await cursor.fetchone():
                return False
            await db.execute(
                "INSERT OR IGNORE INTO favorites (telegram_id, movie_code, added_at) VALUES (?, ?, ?)",
                (telegram_id, code, datetime.now(UTC).isoformat()),
            )
            await db.commit()
            return True

    async def remove_favorite(self, telegram_id: int, movie_code: str) -> bool:
        code = movie_code.strip().upper()
        async with self.get_connection() as db:
            cursor = await db.execute(
                "DELETE FROM favorites WHERE telegram_id = ? AND movie_code = ?",
                (telegram_id, code),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_favorites(self, telegram_id: int) -> list[Movie]:
        async with self.get_connection() as db:
            cursor = await db.execute(
                """
                SELECT m.* FROM movies m
                JOIN favorites f ON m.code = f.movie_code
                WHERE f.telegram_id = ?
                ORDER BY f.added_at DESC
                """,
                (telegram_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_movie(r) for r in rows]

    async def is_favorite(self, telegram_id: int, movie_code: str) -> bool:
        code = movie_code.strip().upper()
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT 1 FROM favorites WHERE telegram_id = ? AND movie_code = ?",
                (telegram_id, code),
            )
            return (await cursor.fetchone()) is not None

    async def get_stats(self) -> dict[str, Any]:
        async with self.get_connection() as db:
            c1 = await db.execute("SELECT COUNT(*) AS total FROM users")
            r1 = await c1.fetchone()

            c2 = await db.execute("SELECT COUNT(*) AS total FROM users WHERE is_vip = 1")
            r2 = await c2.fetchone()

            c3 = await db.execute("SELECT COUNT(*) AS total FROM movies")
            r3 = await c3.fetchone()

            c4 = await db.execute("SELECT COUNT(*) AS total FROM searches")
            r4 = await c4.fetchone()

            return {
                "total_users": r1["total"] if r1 else 0,
                "vip_users": r2["total"] if r2 else 0,
                "total_movies": r3["total"] if r3 else 0,
                "total_searches": r4["total"] if r4 else 0,
            }

    def _row_to_movie(self, row: aiosqlite.Row) -> Movie:
        return Movie(
            code=str(row["code"]).upper(),
            title=str(row["title"]),
            year=int(row["year"]),
            genre=str(row["genre"]),
            country=str(row["country"]),
            imdb=float(row["imdb"]),
            description=str(row["description"]),
            access=MovieAccess(str(row["access"])),
        )
