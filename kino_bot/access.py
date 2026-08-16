from .models import Movie, MovieAccess, UserProfile


def can_watch(movie: Movie, user: UserProfile) -> bool:
    return movie.access == MovieAccess.FREE or user.is_vip


def access_message(movie: Movie, user: UserProfile) -> str:
    if can_watch(movie, user):
        return f"{movie.title} is available."
    return f"{movie.title} requires an active VIP subscription."
