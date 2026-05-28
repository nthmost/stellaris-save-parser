"""
Module for parsing empire modifiers and their effects.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class Modifier:
    """Represents an active empire modifier."""
    name: str
    days_remaining: int  # -1 = permanent
    description: Optional[str] = None
    effects: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_permanent(self) -> bool:
        """True if this modifier is permanent."""
        return self.days_remaining == -1
    
    @property
    def is_temporary(self) -> bool:
        """True if this modifier is temporary."""
        return self.days_remaining > 0


# Known modifier effects (from Stellaris game files)
# This is a partial list - the game has hundreds of modifiers
KNOWN_MODIFIER_EFFECTS = {
    'drone_mining_techniques': {
        'description': 'Drone Mining Techniques',
        'effects': {'country_minerals_produces_mult': 0.05}
    },
    'promoted_xenophile': {
        'description': 'Promoted Xenophile Faction',
        'effects': {'pop_happiness': 0.05}
    },
    'promoted_militarist': {
        'description': 'Promoted Militarist Faction',
        'effects': {'country_claim_influence_cost_mult': -0.10}
    },
    'black_hole_pantagruel_research': {
        'description': 'Black Hole Research',
        'effects': {'all_technology_research_speed': 0.05}
    },
    'curator_buff_stellarite': {
        'description': 'Curator Stellarite Insight',
        'effects': {'ship_shield_hp_mult': 0.10}
    },
    'curator_insight': {
        'description': 'Curator Insight',
        'effects': {'all_technology_research_speed': 0.10}
    },
    'enclave_trade_3_rig': {
        'description': 'Riggan Commercial Pact',
        'effects': {'country_energy_produces_mult': 0.05}
    },
    'harmonious_crew': {
        'description': 'Harmonious Crew',
        'effects': {'ship_fire_rate_mult': 0.10}
    },
    'pacified_amoebas': {
        'description': 'Pacified Space Amoebas',
        'effects': {'ship_hull_regen_add_perc': 0.01}
    },
    'streamlined_ship_design': {
        'description': 'Streamlined Ship Design',
        'effects': {'country_naval_cap_mult': 0.05}
    },
    'asteroid_hive_weak_points': {
        'description': 'Asteroid Hive Weak Points',
        'effects': {'ship_weapon_damage': 0.05}
    },
    'eldritch_horror_mod': {
        'description': 'Dimensional Horror Insights',
        'effects': {'ship_weapon_damage': 0.10}
    },
    'agenda_open_arms_finish': {
        'description': 'Open Arms Agenda Complete',
        'effects': {'pop_growth_speed': 0.10}
    },
    # Tech-based modifiers
    'tech_mining_1': {
        'description': 'Improved Mining Technology',
        'effects': {'country_minerals_produces_mult': 0.10}
    },
    'tech_mining_2': {
        'description': 'Advanced Mining Technology',
        'effects': {'country_minerals_produces_mult': 0.15}
    },
    # Add more as needed...
}


def parse_active_modifiers(country_data: str) -> List[Modifier]:
    """
    Parse active modifiers from country data.
    
    Args:
        country_data: The country block data from the save file
        
    Returns:
        List of Modifier objects
    """
    modifiers = []
    
    # Find modifier section
    modifier_match = re.search(
        r'modifier=\s*\{.*?items=\s*\{(.*?)\n\t\t\t\}',
        country_data,
        re.DOTALL
    )
    
    if not modifier_match:
        return modifiers
    
    modifiers_data = modifier_match.group(1)
    
    # Parse individual modifiers
    modifier_pattern = r'\{\s*modifier="([^"]+)"\s*days=([-0-9]+)'
    
    for match in re.finditer(modifier_pattern, modifiers_data):
        mod_name = match.group(1)
        days = int(match.group(2))
        
        # Look up known effects
        known_info = KNOWN_MODIFIER_EFFECTS.get(mod_name, {})
        
        modifier = Modifier(
            name=mod_name,
            days_remaining=days,
            description=known_info.get('description'),
            effects=known_info.get('effects', {})
        )
        
        modifiers.append(modifier)
    
    return modifiers


def get_modifiers_by_category(modifiers: List[Modifier]) -> Dict[str, List[Modifier]]:
    """
    Categorize modifiers by their effect type.
    
    Args:
        modifiers: List of Modifier objects
        
    Returns:
        Dictionary mapping category names to lists of modifiers
    """
    categories = {
        'research': [],
        'resource_production': [],
        'military': [],
        'diplomacy': [],
        'pop_growth': [],
        'happiness': [],
        'other': []
    }
    
    for modifier in modifiers:
        categorized = False
        
        # Categorize by effect types
        for effect_name in modifier.effects.keys():
            if 'research' in effect_name or 'tech' in effect_name:
                categories['research'].append(modifier)
                categorized = True
                break
            elif any(x in effect_name for x in ['mineral', 'energy', 'food', 'alloy', 'produces']):
                categories['resource_production'].append(modifier)
                categorized = True
                break
            elif any(x in effect_name for x in ['ship', 'weapon', 'damage', 'armor', 'shield', 'hull']):
                categories['military'].append(modifier)
                categorized = True
                break
            elif 'pop_growth' in effect_name:
                categories['pop_growth'].append(modifier)
                categorized = True
                break
            elif 'happiness' in effect_name:
                categories['happiness'].append(modifier)
                categorized = True
                break
        
        # Also categorize by name if no effects known
        if not categorized:
            if any(x in modifier.name.lower() for x in ['research', 'tech']):
                categories['research'].append(modifier)
            elif any(x in modifier.name.lower() for x in ['mining', 'mineral', 'energy', 'food', 'alloy']):
                categories['resource_production'].append(modifier)
            elif any(x in modifier.name.lower() for x in ['weapon', 'damage', 'ship', 'military']):
                categories['military'].append(modifier)
            elif 'growth' in modifier.name.lower():
                categories['pop_growth'].append(modifier)
            elif 'happiness' in modifier.name.lower() or 'faction' in modifier.name.lower():
                categories['happiness'].append(modifier)
            else:
                categories['other'].append(modifier)
    
    return categories


def format_modifier_effect(effect_name: str, value: float) -> str:
    """
    Format a modifier effect for display.
    
    Args:
        effect_name: The effect identifier
        value: The effect value
        
    Returns:
        Formatted string
    """
    if '_mult' in effect_name or '_speed' in effect_name:
        # Multiplier - show as percentage
        return f"{value:+.0%}"
    elif '_add' in effect_name:
        # Additive - show as number
        return f"{value:+.1f}"
    else:
        # Unknown - show as decimal
        return f"{value:+.3f}"
