from dataclasses import dataclass
from enum import Enum


class MovieAccess(str, Enum):
    FREE = "free"
    VIP = "vip"


@dataclass(frozen=True)
class Movie:
    code: str
    title: str
    year: int
    genre: str
    country: str
    imdb: float
    description: str
    access: MovieAccess = MovieAccess.FREE


@dataclass(frozen=True)
class UserProfile:
    telegram_id: int
    is_vip: bool = False
