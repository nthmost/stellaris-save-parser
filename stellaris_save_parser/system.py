"""
Data models for star systems and galactic geography.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class HyperlaneConnection:
    """Represents a hyperlane connection to another system."""
    
    to_system_id: str
    length: float  # Travel distance
    
    def __repr__(self) -> str:
        return f"Hyperlane(to={self.to_system_id}, length={self.length})"


@dataclass
class StarSystem:
    """Represents a star system with planets and hyperlanes."""
    
    id: str
    name: str
    coordinates: Tuple[float, float]  # (x, y)
    star_class: str  # e.g., "sc_k", "sc_m", "sc_g"
    planet_ids: List[str] = field(default_factory=list)
    hyperlanes: List[HyperlaneConnection] = field(default_factory=list)
    owner_id: Optional[str] = None
    has_starbase: bool = False
    starbase_level: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"StarSystem(name='{self.name}', planets={len(self.planet_ids)}, hyperlanes={len(self.hyperlanes)})"
    
    @property
    def x(self) -> float:
        """X coordinate of the system."""
        return self.coordinates[0]
    
    @property
    def y(self) -> float:
        """Y coordinate of the system."""
        return self.coordinates[1]
    
    @property
    def connection_count(self) -> int:
        """Number of hyperlane connections."""
        return len(self.hyperlanes)
    
    @property
    def is_chokepoint(self) -> bool:
        """True if system has only 1-2 hyperlane connections (strategic bottleneck)."""
        return 1 <= self.connection_count <= 2
    
    @property
    def is_hub(self) -> bool:
        """True if system has many connections (5+)."""
        return self.connection_count >= 5
    
    def get_connected_system_ids(self) -> List[str]:
        """Get list of system IDs this system connects to."""
        return [h.to_system_id for h in self.hyperlanes]
    
    def distance_to(self, other: 'StarSystem') -> float:
        """Calculate Euclidean distance to another system."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx**2 + dy**2) ** 0.5


@dataclass
class GalacticMap:
    """Represents the galactic map with all systems."""
    
    systems: List[StarSystem] = field(default_factory=list)
    _system_map: dict = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        """Build system ID lookup map."""
        self._system_map = {s.id: s for s in self.systems}
    
    def get_system(self, system_id: str) -> Optional[StarSystem]:
        """Get a system by ID."""
        return self._system_map.get(system_id)
    
    def get_system_by_name(self, name: str) -> Optional[StarSystem]:
        """Get a system by name."""
        for system in self.systems:
            if system.name.lower() == name.lower():
                return system
        return None
    
    def get_systems_by_owner(self, owner_id: str) -> List[StarSystem]:
        """Get all systems owned by a specific country."""
        return [s for s in self.systems if s.owner_id == owner_id]
    
    def find_systems_with_planets(self, planet_ids: List[str]) -> List[StarSystem]:
        """Find all systems containing any of the given planet IDs."""
        result = []
        planet_set = set(planet_ids)
        for system in self.systems:
            if any(pid in planet_set for pid in system.planet_ids):
                result.append(system)
        return result
    
    def get_connected_systems(self, system: StarSystem) -> List[StarSystem]:
        """Get all systems directly connected to this system via hyperlanes."""
        connected = []
        for hyperlane in system.hyperlanes:
            neighbor = self.get_system(hyperlane.to_system_id)
            if neighbor:
                connected.append(neighbor)
        return connected
    
    def find_border_systems(self, owner_id: str) -> List[StarSystem]:
        """
        Find border systems for a country (systems that connect to foreign systems).
        
        Args:
            owner_id: The country ID to analyze
            
        Returns:
            List of border systems
        """
        border = []
        owner_systems = self.get_systems_by_owner(owner_id)
        owner_ids = {s.id for s in owner_systems}
        
        for system in owner_systems:
            # Check if any connected system is not owned by this player
            for hyperlane in system.hyperlanes:
                if hyperlane.to_system_id not in owner_ids:
                    border.append(system)
                    break
        
        return border
    
    def find_chokepoints(self, owner_id: str) -> List[StarSystem]:
        """
        Find strategic chokepoints (1-2 connections) in a country's territory.
        
        Args:
            owner_id: The country ID to analyze
            
        Returns:
            List of chokepoint systems
        """
        owner_systems = self.get_systems_by_owner(owner_id)
        return [s for s in owner_systems if s.is_chokepoint]
    
    def calculate_territory_stats(self, owner_id: str) -> dict:
        """
        Calculate statistics about a country's territory.
        
        Returns dict with:
        - total_systems: Number of systems controlled
        - total_planets: Number of planets in those systems
        - border_systems: Systems on the border
        - chokepoints: Strategic bottleneck systems
        - hubs: Major junction systems
        - avg_connections: Average hyperlane connections per system
        """
        owner_systems = self.get_systems_by_owner(owner_id)
        
        if not owner_systems:
            return {
                'total_systems': 0,
                'total_planets': 0,
                'border_systems': 0,
                'chokepoints': 0,
                'hubs': 0,
                'avg_connections': 0.0
            }
        
        total_planets = sum(len(s.planet_ids) for s in owner_systems)
        border_systems = self.find_border_systems(owner_id)
        chokepoints = [s for s in owner_systems if s.is_chokepoint]
        hubs = [s for s in owner_systems if s.is_hub]
        avg_connections = sum(s.connection_count for s in owner_systems) / len(owner_systems)
        
        return {
            'total_systems': len(owner_systems),
            'total_planets': total_planets,
            'border_systems': len(border_systems),
            'chokepoints': len(chokepoints),
            'hubs': len(hubs),
            'avg_connections': avg_connections
        }
