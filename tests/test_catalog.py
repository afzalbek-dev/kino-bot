import pytest

from kino_bot.access import access_message, can_watch
from kino_bot.demo import load_demo_catalog
from kino_bot.models import UserProfile


def test_search_by_country_and_sorting() -> None:
    catalog = load_demo_catalog()
    results = catalog.search("Uzbekistan")
    codes = [movie.code for movie in results]
    assert "K001" in codes
    assert "K003" in codes
    assert results[0].imdb >= results[1].imdb


def test_code_lookup_is_case_insensitive() -> None:
    assert load_demo_catalog().by_code("k002").title == "Night Runner"


def test_vip_gate() -> None:
    movie = load_demo_catalog().by_code("K002")
    regular = UserProfile(telegram_id=1)
    vip = UserProfile(telegram_id=2, is_vip=True)
    assert movie is not None
    assert not can_watch(movie, regular)
    assert can_watch(movie, vip)
    assert "requires" in access_message(movie, regular)


def test_random_movie() -> None:
    catalog = load_demo_catalog()
    movie = catalog.random_movie()
    assert movie is not None
    assert movie.code in [m.code for m in catalog.all()]


def test_genres_aggregation() -> None:
    catalog = load_demo_catalog()
    genres = catalog.genres()
    assert len(genres) > 0
    assert any("Action" in g for g in genres)


def test_search_empty_and_limits() -> None:
    catalog = load_demo_catalog()
    all_top = catalog.search("", limit=3)
    assert len(all_top) == 3

    with pytest.raises(ValueError):
        catalog.search("test", limit=0)


def test_nonexistent_code_returns_none() -> None:
    catalog = load_demo_catalog()
    assert catalog.by_code("NONEXISTENT_999") is None
