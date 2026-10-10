from kino_bot.access import access_message, can_watch
from kino_bot.models import Movie, MovieAccess, UserProfile


def test_free_movie_accessible_to_all():
    free_movie = Movie(
        code="FREE1",
        title="Open Movie",
        year=2024,
        genre="Drama",
        country="Uzbekistan",
        imdb=7.5,
        description="Free for all",
        access=MovieAccess.FREE,
    )
    regular_user = UserProfile(telegram_id=1, is_vip=False)
    vip_user = UserProfile(telegram_id=2, is_vip=True)

    assert can_watch(free_movie, regular_user) is True
    assert can_watch(free_movie, vip_user) is True
    assert "is available" in access_message(free_movie, regular_user)


def test_vip_movie_gating():
    vip_movie = Movie(
        code="VIP1",
        title="Exclusive Premiere",
        year=2025,
        genre="Action",
        country="USA",
        imdb=9.1,
        description="Exclusive for VIP subscribers",
        access=MovieAccess.VIP,
    )
    regular_user = UserProfile(telegram_id=1, is_vip=False)
    vip_user = UserProfile(telegram_id=2, is_vip=True)

    assert can_watch(vip_movie, regular_user) is False
    assert can_watch(vip_movie, vip_user) is True

    assert "requires an active VIP subscription" in access_message(vip_movie, regular_user)
    assert "is available" in access_message(vip_movie, vip_user)
