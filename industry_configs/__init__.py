"""
Multi-industry configuration registry.
"""

from .restaurants import CONFIG as _RESTAURANTS
from .paper_packaging import CONFIG as _PAPER
from .gaming import CONFIG as _GAMING
from .leisure import CONFIG as _LEISURE
from .movie_theaters import CONFIG as _MOVIES

INDUSTRIES = {
    "Restaurants":       _RESTAURANTS,
    "Paper & Packaging": _PAPER,
    "Gaming":            _GAMING,
    "Leisure":           _LEISURE,
    "Movie Theaters":    _MOVIES,
}

INDUSTRY_NAMES = list(INDUSTRIES.keys())


def get_industry_config(name: str) -> dict:
    """Return the full config dict for an industry."""
    return INDUSTRIES[name]
