"""
Data models for Stellaris game objects.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from collections import Counter


@dataclass
class Leader:
    """Represents a leader (official, scientist, commander, etc.)."""
    
    id: str
    name: str
    leader_class: str  # "official", "scientist", "commander", "envoy"
    level: int
    traits: List[str] = field(default_factory=list)
    country_id: str = ""
    previous_job: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Leader(name='{self.name}', class='{self.leader_class}', level={self.level})"
    
    def has_trait(self, trait: str) -> bool:
        """Check if leader has a specific trait."""
        return trait in self.traits
    
    def has_trait_type(self, trait_type: str) -> bool:
        """Check if leader has any trait containing a keyword."""
        return any(trait_type.lower() in trait.lower() for trait in self.traits)


@dataclass
class Planet:
    """Represents a colonized planet."""
    
    id: str
    name: str
    designation: str
    planet_class: str
    size: int
    pops: int
    owner_id: str
    governor_id: Optional[str] = None
    governor: Optional[Leader] = None
    sector_id: Optional[str] = None
    stability: float = 0.0
    colonize_date: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Planet(name='{self.name}', designation='{self.designation}', pops={self.pops})"
    
    @property
    def is_capital(self) -> bool:
        """Check if this is a capital planet."""
        return 'capital' in self.designation.lower()
    
    @property
    def is_generator_world(self) -> bool:
        """Check if this is a generator/energy world."""
        return any(kw in self.designation.lower() for kw in ['generator', 'energy'])
    
    @property
    def is_farming_world(self) -> bool:
        """Check if this is a farming/agricultural world."""
        return any(kw in self.designation.lower() for kw in ['farm', 'agri', 'rural'])
    
    @property
    def is_industrial_world(self) -> bool:
        """Check if this is an industrial/forge world."""
        return any(kw in self.designation.lower() 
                  for kw in ['forge', 'foundry', 'factory', 'industrial'])
    
    @property
    def is_mining_world(self) -> bool:
        """Check if this is a mining world."""
        return 'mining' in self.designation.lower()
    
    @property
    def is_research_world(self) -> bool:
        """Check if this is a research world."""
        return 'research' in self.designation.lower() or 'tech' in self.designation.lower()
    
    @property
    def is_unspecialized(self) -> bool:
        """Check if planet lacks specialization."""
        return 'default' in self.designation.lower() or self.designation == 'none'


@dataclass
class Empire:
    """Represents a playable empire."""
    
    country_id: str
    name: str
    planets: List[Planet] = field(default_factory=list)
    leaders: List[Leader] = field(default_factory=list)
    game_date: str = ""
    
    def __repr__(self) -> str:
        return f"Empire(name='{self.name}', planets={len(self.planets)}, leaders={len(self.leaders)})"
    
    def get_leader_by_id(self, leader_id: str) -> Optional[Leader]:
        """Get a leader by their ID."""
        for leader in self.leaders:
            if leader.id == leader_id:
                return leader
        return None
    
    def get_planet_by_name(self, name: str) -> Optional[Planet]:
        """Get a planet by name."""
        for planet in self.planets:
            if planet.name == name:
                return planet
        return None
    
    @property
    def officials(self) -> List[Leader]:
        """Get all officials/governors."""
        return [l for l in self.leaders if l.leader_class == 'official']
    
    @property
    def scientists(self) -> List[Leader]:
        """Get all scientists."""
        return [l for l in self.leaders if l.leader_class == 'scientist']
    
    @property
    def commanders(self) -> List[Leader]:
        """Get all commanders."""
        return [l for l in self.leaders if l.leader_class == 'commander']
    
    @property
    def planets_with_governors(self) -> List[Planet]:
        """Get all planets that have governors assigned."""
        return [p for p in self.planets if p.governor]
    
    @property
    def planets_without_governors(self) -> List[Planet]:
        """Get all planets without governors."""
        return [p for p in self.planets if not p.governor]
    
    @property
    def unassigned_officials(self) -> List[Leader]:
        """Get officials not assigned to any planet."""
        assigned_ids = {p.governor_id for p in self.planets if p.governor_id}
        return [o for o in self.officials if o.id not in assigned_ids]
    
    def get_planets_by_designation(self, designation_type: str) -> List[Planet]:
        """Get all planets of a specific type."""
        designation_type = designation_type.lower()
        return [p for p in self.planets if designation_type in p.designation.lower()]
    
    def analyze_governor_assignments(self) -> dict:
        """
        Analyze governor assignments and find optimization opportunities.
        
        Returns a dict with:
        - mismatches: List of governors on wrong planet types
        - unassigned_planets: Planets without governors
        - unassigned_officials: Officials not governing planets
        - statistics: Various statistics
        """
        from .traits import categorize_trait, TraitCategory
        
        mismatches = []
        
        for planet in self.planets_with_governors:
            if not planet.governor:
                continue
            
            gov = planet.governor
            
            # Check for production trait mismatches
            has_food_trait = any(
                categorize_trait(t) == TraitCategory.FOOD_PRODUCTION
                for t in gov.traits
            )
            has_energy_trait = any(
                categorize_trait(t) == TraitCategory.ENERGY_PRODUCTION
                for t in gov.traits
            )
            has_alloy_trait = any(
                categorize_trait(t) == TraitCategory.ALLOY_PRODUCTION
                for t in gov.traits
            )
            has_mineral_trait = any(
                categorize_trait(t) == TraitCategory.MINERAL_PRODUCTION
                for t in gov.traits
            )
            
            # Flag mismatches
            if has_food_trait and not planet.is_farming_world:
                mismatches.append({
                    'type': 'food_mismatch',
                    'leader': gov,
                    'planet': planet,
                    'suggestion': 'Move to farming world'
                })
            
            if has_energy_trait and not planet.is_generator_world:
                mismatches.append({
                    'type': 'energy_mismatch',
                    'leader': gov,
                    'planet': planet,
                    'suggestion': 'Move to generator world'
                })
            
            if has_alloy_trait and not planet.is_industrial_world:
                mismatches.append({
                    'type': 'alloy_mismatch',
                    'leader': gov,
                    'planet': planet,
                    'suggestion': 'Move to industrial/forge world'
                })
            
            if has_mineral_trait and not planet.is_mining_world:
                mismatches.append({
                    'type': 'mineral_mismatch',
                    'leader': gov,
                    'planet': planet,
                    'suggestion': 'Move to mining world'
                })
        
        # Get designation statistics
        designation_counts = Counter(p.designation for p in self.planets)
        
        return {
            'mismatches': mismatches,
            'unassigned_planets': self.planets_without_governors,
            'unassigned_officials': self.unassigned_officials,
            'statistics': {
                'total_planets': len(self.planets),
                'total_officials': len(self.officials),
                'planets_with_governors': len(self.planets_with_governors),
                'planets_without_governors': len(self.planets_without_governors),
                'unassigned_officials': len(self.unassigned_officials),
                'designation_counts': dict(designation_counts),
                'generator_worlds': len([p for p in self.planets if p.is_generator_world]),
                'farming_worlds': len([p for p in self.planets if p.is_farming_world]),
                'industrial_worlds': len([p for p in self.planets if p.is_industrial_world]),
                'mining_worlds': len([p for p in self.planets if p.is_mining_world]),
                'research_worlds': len([p for p in self.planets if p.is_research_world]),
                'unspecialized': len([p for p in self.planets if p.is_unspecialized]),
            }
        }
