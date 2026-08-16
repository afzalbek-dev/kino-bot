from __future__ import annotations

import json
from pathlib import Path

from .models import Movie, MovieAccess


class MovieCatalog:
    def __init__(self, movies: list[Movie]) -> None:
        self._movies = movies

    @classmethod
    def from_json(cls, path: Path) -> MovieCatalog:
        rows = json.loads(path.read_text(encoding="utf-8"))
        movies = [
            Movie(
                code=str(row["code"]).upper(),
                title=str(row["title"]),
                year=int(row["year"]),
                genre=str(row["genre"]),
                country=str(row["country"]),
                imdb=float(row["imdb"]),
                description=str(row["description"]),
                access=MovieAccess(str(row.get("access", "free"))),
            )
            for row in rows
        ]
        return cls(movies)

    def all(self) -> list[Movie]:
        return list(self._movies)

    def by_code(self, code: str) -> Movie | None:
        normalized = code.strip().upper()
        return next((movie for movie in self._movies if movie.code == normalized), None)

    def search(self, query: str, *, limit: int = 10) -> list[Movie]:
        if limit < 1:
            raise ValueError("limit must be positive")
        normalized = query.strip().lower()
        if not normalized:
            return self._movies[:limit]
        results = [
            movie
            for movie in self._movies
            if normalized in movie.title.lower()
            or normalized in movie.genre.lower()
            or normalized in movie.country.lower()
            or normalized == movie.code.lower()
            or normalized == str(movie.year)
        ]
        return sorted(results, key=lambda movie: (-movie.imdb, movie.title))[:limit]

    def top(self, *, limit: int = 5) -> list[Movie]:
        return sorted(self._movies, key=lambda movie: (-movie.imdb, movie.title))[:limit]
