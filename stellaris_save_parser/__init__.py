"""
Stellaris Save Parser

A Python library for parsing and analyzing Stellaris save files.
"""

from .save import StellarisSave
from .models import Empire, Planet, Leader
from .traits import TraitCategory, categorize_trait, get_trait_description, is_governor_production_trait, get_optimal_planet_type

__version__ = "0.1.0"
__all__ = [
    "StellarisSave",
    "Empire",
    "Planet",
    "Leader",
    "TraitCategory",
    "categorize_trait",
    "get_trait_description",
    "is_governor_production_trait",
    "get_optimal_planet_type"
]
