from kino_bot.access import access_message, can_watch
from kino_bot.demo import load_demo_catalog
from kino_bot.models import UserProfile


def test_search_by_country_and_sorting() -> None:
    catalog = load_demo_catalog()
    results = catalog.search("Uzbekistan")
    assert [movie.code for movie in results] == ["K001", "K003"]


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
