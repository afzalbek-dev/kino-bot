from kino_bot.bot import (
    CODE_PATTERN,
    build_dispatcher,
    format_movie_card,
    get_main_keyboard,
    get_movie_keyboard,
)
from kino_bot.models import Movie, MovieAccess, UserProfile


def test_code_regex_matching():
    # Valid codes
    assert CODE_PATTERN.match("K001") is not None
    assert CODE_PATTERN.match("#K002") is not None
    assert CODE_PATTERN.match("k12345") is not None
    assert CODE_PATTERN.match("MOVIE99") is not None

    # Invalid codes
    assert CODE_PATTERN.match("K") is None  # Too short
    assert CODE_PATTERN.match("This is a search query") is None
    assert CODE_PATTERN.match("") is None


def test_keyboards_structure():
    main_kb = get_main_keyboard()
    assert len(main_kb.inline_keyboard) == 3
    # Check top row
    top_row = main_kb.inline_keyboard[0]
    assert len(top_row) == 2
    assert top_row[0].callback_data == "nav:top"
    assert top_row[1].callback_data == "nav:random"

    movie = Movie(
        code="K001",
        title="Test Movie",
        year=2024,
        genre="Drama",
        country="USA",
        imdb=8.0,
        description="Desc",
        access=MovieAccess.FREE,
    )
    fav_kb = get_movie_keyboard(movie, is_fav=False)
    assert fav_kb.inline_keyboard[0][0].callback_data == "fav:add:K001"

    unfav_kb = get_movie_keyboard(movie, is_fav=True)
    assert unfav_kb.inline_keyboard[0][0].callback_data == "fav:remove:K001"


def test_format_movie_card():
    movie = Movie(
        code="K100",
        title="Epic Adventure",
        year=2025,
        genre="Adventure",
        country="Uzbekistan",
        imdb=8.5,
        description="A great journey across ancient lands.",
        access=MovieAccess.VIP,
    )
    regular_user = UserProfile(telegram_id=1, is_vip=False)
    card_regular = format_movie_card(movie, regular_user)
    assert "Epic Adventure" in card_regular
    assert "K100" in card_regular
    assert "8.5/10" in card_regular
    assert "requires an active VIP subscription" in card_regular

    vip_user = UserProfile(telegram_id=2, is_vip=True)
    card_vip = format_movie_card(movie, vip_user)
    assert "is available" in card_vip


def test_dispatcher_builder():
    dp = build_dispatcher()
    assert dp is not None
    assert dp.message is not None
    assert dp.callback_query is not None
