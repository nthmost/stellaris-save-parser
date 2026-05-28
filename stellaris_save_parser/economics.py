"""
Data models for economic resources and production/consumption.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ResourceAmount:
    """
    Represents production, consumption, or net amount of a specific resource.
    
    All amounts are per-month values as stored in the save file.
    """
    
    # Basic resources
    energy: float = 0.0
    minerals: float = 0.0
    food: float = 0.0
    
    # Advanced resources
    consumer_goods: float = 0.0
    alloys: float = 0.0
    
    # Research
    physics_research: float = 0.0
    society_research: float = 0.0
    engineering_research: float = 0.0
    
    # Special
    unity: float = 0.0
    trade: float = 0.0
    influence: float = 0.0
    
    # Strategic resources (rare/volatile)
    volatile_motes: float = 0.0
    exotic_gases: float = 0.0
    rare_crystals: float = 0.0
    living_metal: float = 0.0
    zro: float = 0.0
    dark_matter: float = 0.0
    nanites: float = 0.0
    
    # Amenities and other
    amenities: float = 0.0
    
    @property
    def total_research(self) -> float:
        """Total research production across all three fields."""
        return self.physics_research + self.society_research + self.engineering_research
    
    @property
    def total_basic_resources(self) -> float:
        """Total basic resources (energy + minerals + food)."""
        return self.energy + self.minerals + self.food
    
    @property
    def total_advanced_resources(self) -> float:
        """Total advanced resources (consumer goods + alloys)."""
        return self.consumer_goods + self.alloys
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary, excluding zero values."""
        result = {}
        for field_name, value in self.__dict__.items():
            if value != 0.0:
                result[field_name] = value
        return result
    
    def __add__(self, other: 'ResourceAmount') -> 'ResourceAmount':
        """Add two ResourceAmount objects together."""
        result = ResourceAmount()
        for field_name in self.__dataclass_fields__:
            setattr(result, field_name, getattr(self, field_name) + getattr(other, field_name))
        return result
    
    def __sub__(self, other: 'ResourceAmount') -> 'ResourceAmount':
        """Subtract one ResourceAmount from another."""
        result = ResourceAmount()
        for field_name in self.__dataclass_fields__:
            setattr(result, field_name, getattr(self, field_name) - getattr(other, field_name))
        return result
    
    def __repr__(self) -> str:
        non_zero = self.to_dict()
        if not non_zero:
            return "ResourceAmount(empty)"
        items = [f"{k}={v:.2f}" for k, v in sorted(non_zero.items())[:5]]
        if len(non_zero) > 5:
            items.append(f"... +{len(non_zero)-5} more")
        return f"ResourceAmount({', '.join(items)})"


@dataclass
class ResourceBalance:
    """
    Represents the production/consumption balance for a planet or system.
    """
    
    produces: ResourceAmount = field(default_factory=ResourceAmount)
    upkeep: ResourceAmount = field(default_factory=ResourceAmount)
    
    @property
    def net(self) -> ResourceAmount:
        """Net resources (production - consumption)."""
        return self.produces - self.upkeep
    
    @property
    def is_energy_positive(self) -> bool:
        """True if net energy production is positive."""
        return self.net.energy > 0
    
    @property
    def is_mineral_positive(self) -> bool:
        """True if net mineral production is positive."""
        return self.net.minerals > 0
    
    @property
    def is_food_positive(self) -> bool:
        """True if net food production is positive."""
        return self.net.food > 0
    
    def get_deficit_resources(self) -> Dict[str, float]:
        """Get resources where consumption exceeds production."""
        deficits = {}
        net_dict = self.net.to_dict()
        for resource, amount in net_dict.items():
            if amount < 0:
                deficits[resource] = amount
        return deficits
    
    def get_surplus_resources(self) -> Dict[str, float]:
        """Get resources where production exceeds consumption."""
        surplus = {}
        net_dict = self.net.to_dict()
        for resource, amount in net_dict.items():
            if amount > 0:
                surplus[resource] = amount
        return surplus
    
    def __add__(self, other: 'ResourceBalance') -> 'ResourceBalance':
        """Combine two resource balances."""
        return ResourceBalance(
            produces=self.produces + other.produces,
            upkeep=self.upkeep + other.upkeep
        )
    
    def __repr__(self) -> str:
        net = self.net.to_dict()
        if not net:
            return "ResourceBalance(balanced)"
        
        items = []
        for k, v in sorted(net.items())[:3]:
            sign = "+" if v >= 0 else ""
            items.append(f"{k}={sign}{v:.1f}")
        
        if len(net) > 3:
            items.append(f"... +{len(net)-3} more")
        
        return f"ResourceBalance({', '.join(items)})"


@dataclass
class SystemEconomy:
    """
    Aggregated economic data for an entire star system.
    """
    
    system_id: str
    system_name: str
    planet_count: int
    total_pops: int
    resources: ResourceBalance = field(default_factory=ResourceBalance)
    
    def __repr__(self) -> str:
        return (f"SystemEconomy(system='{self.system_name}', "
                f"planets={self.planet_count}, pops={self.total_pops})")
