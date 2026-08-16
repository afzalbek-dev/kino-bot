from pathlib import Path

from .catalog import MovieCatalog


def load_demo_catalog() -> MovieCatalog:
    return MovieCatalog.from_json(Path(__file__).resolve().parent.parent / "sample_data" / "movies.json")
