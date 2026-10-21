from pathlib import Path

import pytest

from kino_bot.database import Database
from kino_bot.models import Movie, MovieAccess


async def create_test_db(tmp_path: Path) -> Database:
    db_file = tmp_path / "test_kino.sqlite3"
    db = Database(str(db_file))
    seed_file = Path(__file__).resolve().parent.parent / "sample_data" / "movies.json"
    await db.init_db(seed_path=seed_file)
    return db


@pytest.mark.asyncio
async def test_init_db_and_seeding(tmp_path: Path):
    db = await create_test_db(tmp_path)
    stats = await db.get_stats()
    assert stats["total_movies"] >= 5
    assert stats["total_users"] == 0


@pytest.mark.asyncio
async def test_user_creation_and_vip_status(tmp_path: Path):
    db = await create_test_db(tmp_path)
    user = await db.get_or_create_user(telegram_id=12345, username="john_doe", first_name="John")
    assert user.telegram_id == 12345
    assert user.is_vip is False

    await db.set_vip(telegram_id=12345, is_vip=True)
    updated_user = await db.get_or_create_user(telegram_id=12345)
    assert updated_user.is_vip is True

    stats = await db.get_stats()
    assert stats["total_users"] == 1
    assert stats["vip_users"] == 1


@pytest.mark.asyncio
async def test_movie_crud_and_search(tmp_path: Path):
    db = await create_test_db(tmp_path)
    new_movie = Movie(
        code="TEST01",
        title="Automated Test Movie",
        year=2026,
        genre="Action, Sci-Fi",
        country="Uzbekistan",
        imdb=8.9,
        description="A great test movie.",
        access=MovieAccess.FREE,
    )
    await db.add_movie(new_movie)

    fetched = await db.get_movie("TEST01")
    assert fetched is not None
    assert fetched.title == "Automated Test Movie"
    assert fetched.imdb == 8.9

    # Case-insensitive code
    fetched_lower = await db.get_movie("test01")
    assert fetched_lower is not None

    # Search by title
    results = await db.search_movies("Automated", limit=5)
    assert len(results) >= 1
    assert any(m.code == "TEST01" for m in results)

    # Search by genre
    sci_fi = await db.search_movies("Sci-Fi", limit=5)
    assert len(sci_fi) >= 1


@pytest.mark.asyncio
async def test_favorites_lifecycle(tmp_path: Path):
    db = await create_test_db(tmp_path)
    user_id = 9999
    await db.get_or_create_user(user_id)

    # Add favorite
    success = await db.add_favorite(user_id, "K001")
    assert success is True
    assert await db.is_favorite(user_id, "K001") is True

    # Check favorites list
    favs = await db.get_favorites(user_id)
    assert len(favs) == 1
    assert favs[0].code == "K001"

    # Remove favorite
    removed = await db.remove_favorite(user_id, "K001")
    assert removed is True
    assert await db.is_favorite(user_id, "K001") is False


@pytest.mark.asyncio
async def test_random_and_top_movies(tmp_path: Path):
    db = await create_test_db(tmp_path)
    top_movies = await db.get_top_movies(limit=3)
    assert len(top_movies) == 3
    # Check descending IMDb order
    assert top_movies[0].imdb >= top_movies[1].imdb >= top_movies[2].imdb

    rnd = await db.get_random_movie()
    assert rnd is not None
    assert rnd.code != ""
