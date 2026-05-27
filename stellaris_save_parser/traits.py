"""
Trait categorization and analysis.

This module categorizes leader traits based on their effects and applicability.
"""

from enum import Enum
from typing import Optional


class TraitCategory(Enum):
    """Categories of leader traits."""
    
    # Governor traits (apply to planetary production)
    FOOD_PRODUCTION = "food_production"
    ENERGY_PRODUCTION = "energy_production"
    MINERAL_PRODUCTION = "mineral_production"
    ALLOY_PRODUCTION = "alloy_production"
    RESEARCH_PRODUCTION = "research_production"
    UNITY_PRODUCTION = "unity_production"
    AMENITIES = "amenities"
    CRIME_REDUCTION = "crime_reduction"
    BUILD_SPEED = "build_speed"
    PLANET_MANAGEMENT = "planet_management"
    
    # Councilor/Ruler only traits
    RULER_ONLY = "ruler_only"
    
    # Scientist traits
    SCIENTIST_EXPERTISE = "scientist_expertise"
    SCIENTIST_ANOMALY = "scientist_anomaly"
    
    # Commander traits
    COMMANDER_COMBAT = "commander_combat"
    
    # Generic traits
    EXPERIENCE_GAIN = "experience_gain"
    LIFESPAN = "lifespan"
    UPKEEP = "upkeep"
    GENERIC = "generic"
    
    # Negative traits
    NEGATIVE = "negative"


# Trait keyword mappings
TRAIT_KEYWORDS = {
    TraitCategory.FOOD_PRODUCTION: [
        'agrarian_upbringing',
        'homesteader',
        'fertility',
    ],
    TraitCategory.ENERGY_PRODUCTION: [
        'capitalist',
        'energy_mogul',
    ],
    TraitCategory.MINERAL_PRODUCTION: [
        'private_mines',
    ],
    TraitCategory.ALLOY_PRODUCTION: [
        'scrapper',
        'industrialist',
    ],
    TraitCategory.RESEARCH_PRODUCTION: [
        'expertise_',  # Partial match for expertise_materials, expertise_physics, etc.
    ],
    TraitCategory.UNITY_PRODUCTION: [
        'bureaucrat',
        'unifier',
    ],
    TraitCategory.AMENITIES: [
        'celebrity',
        'venerated',
    ],
    TraitCategory.CRIME_REDUCTION: [
        'righteous',
    ],
    TraitCategory.BUILD_SPEED: [
        'architectural_interest',
        'environmental_engineer',
    ],
    TraitCategory.PLANET_MANAGEMENT: [
        'meticulous',
        'principled',
    ],
    TraitCategory.EXPERIENCE_GAIN: [
        'adaptable',
        'eager',
        'gifted',
    ],
    TraitCategory.LIFESPAN: [
        'resilient',
        'substance_abuser',
    ],
    TraitCategory.UPKEEP: [
        'eager',
    ],
}


def categorize_trait(trait: str) -> TraitCategory:
    """
    Categorize a leader trait.
    
    Args:
        trait: The trait identifier (e.g., 'leader_trait_agrarian_upbringing')
        
    Returns:
        The trait category
    """
    trait_lower = trait.lower()
    
    # Check for ruler-only traits
    if trait.startswith('trait_ruler_'):
        return TraitCategory.RULER_ONLY
    
    # Check for scientist expertise traits
    if 'expertise_' in trait_lower:
        return TraitCategory.SCIENTIST_EXPERTISE
    
    # Check for negative traits
    if any(kw in trait_lower for kw in ['corrupt', 'stubborn', 'arrested_development', 
                                         'substance_abuser', 'lawless', 'carefree',
                                         'procrastinator', 'cruel', 'sadistic']):
        return TraitCategory.NEGATIVE
    
    # Check against keyword mappings
    for category, keywords in TRAIT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in trait_lower:
                return category
    
    return TraitCategory.GENERIC


def is_governor_production_trait(trait: str) -> bool:
    """
    Check if a trait affects planetary production when governing.
    
    Args:
        trait: The trait identifier
        
    Returns:
        True if this trait boosts planetary production
    """
    category = categorize_trait(trait)
    
    return category in [
        TraitCategory.FOOD_PRODUCTION,
        TraitCategory.ENERGY_PRODUCTION,
        TraitCategory.MINERAL_PRODUCTION,
        TraitCategory.ALLOY_PRODUCTION,
        TraitCategory.RESEARCH_PRODUCTION,
        TraitCategory.UNITY_PRODUCTION,
    ]


def get_trait_description(trait: str) -> str:
    """
    Get a human-readable description of what a trait does.
    
    Args:
        trait: The trait identifier
        
    Returns:
        Description string
    """
    category = categorize_trait(trait)
    
    descriptions = {
        TraitCategory.FOOD_PRODUCTION: "Boosts food production on governed planet",
        TraitCategory.ENERGY_PRODUCTION: "Boosts energy production on governed planet",
        TraitCategory.MINERAL_PRODUCTION: "Boosts mineral production on governed planet",
        TraitCategory.ALLOY_PRODUCTION: "Boosts alloy production on governed planet",
        TraitCategory.RESEARCH_PRODUCTION: "Boosts research output",
        TraitCategory.UNITY_PRODUCTION: "Boosts unity production on governed planet",
        TraitCategory.AMENITIES: "Provides amenities bonus",
        TraitCategory.CRIME_REDUCTION: "Reduces crime on governed planet",
        TraitCategory.BUILD_SPEED: "Improves construction speed/cost",
        TraitCategory.PLANET_MANAGEMENT: "General planetary management bonus",
        TraitCategory.RULER_ONLY: "Only applies when serving as ruler or councilor",
        TraitCategory.SCIENTIST_EXPERTISE: "Research specialization bonus",
        TraitCategory.EXPERIENCE_GAIN: "Increases experience gain",
        TraitCategory.LIFESPAN: "Affects leader lifespan",
        TraitCategory.UPKEEP: "Reduces leader upkeep cost",
        TraitCategory.NEGATIVE: "Negative trait with penalties",
        TraitCategory.GENERIC: "Generic trait",
    }
    
    return descriptions.get(category, "Unknown trait effect")


def get_optimal_planet_type(trait: str) -> Optional[str]:
    """
    Get the optimal planet designation for a trait.
    
    Args:
        trait: The trait identifier
        
    Returns:
        Recommended planet designation type, or None if not applicable
    """
    category = categorize_trait(trait)
    
    optimal_types = {
        TraitCategory.FOOD_PRODUCTION: "Farming/Agricultural World",
        TraitCategory.ENERGY_PRODUCTION: "Generator/Energy World",
        TraitCategory.MINERAL_PRODUCTION: "Mining World",
        TraitCategory.ALLOY_PRODUCTION: "Forge/Foundry World",
        TraitCategory.RESEARCH_PRODUCTION: "Research World",
    }
    
    return optimal_types.get(category)
