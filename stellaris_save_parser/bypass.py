"""
Data models for bypasses (wormholes, gateways, hyper relays, etc.).
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class BypassType(Enum):
    """Types of FTL bypasses in Stellaris."""
    WORMHOLE = "wormhole"
    GATEWAY = "gateway"
    LGATE = "lgate"  # L-Gates
    SHROUD_TUNNEL = "shroud_tunnel"
    RELAY = "relay_bypass"  # Hyper relays
    QUANTUM_CATAPULT = "quantum_catapult"
    UNKNOWN = "unknown"


@dataclass
class Bypass:
    """Base class for all FTL bypass types."""
    
    id: str
    bypass_type: BypassType
    is_active: bool
    system_id: Optional[str] = None
    planet_id: Optional[str] = None  # Physical location (planet/megastructure)
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"Bypass(id='{self.id}', type={self.bypass_type.value}, {status})"


@dataclass
class Wormhole(Bypass):
    """
    Natural wormhole - connects two specific points in space.
    
    Wormholes are permanent, bidirectional connections between two systems.
    Each wormhole has exactly one linked partner.
    """
    
    linked_to_id: Optional[str] = None  # ID of the linked wormhole
    
    def __post_init__(self):
        self.bypass_type = BypassType.WORMHOLE
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        link = f", links to {self.linked_to_id}" if self.linked_to_id else ""
        return f"Wormhole(id='{self.id}', {status}{link})"


@dataclass
class Gateway(Bypass):
    """
    Gateway - connects to all other gateways in a network.
    
    Gateways allow travel to any other active gateway in the galaxy.
    Ancient gateways must be reactivated; empires can also build new ones.
    """
    
    connected_gateway_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.bypass_type = BypassType.GATEWAY
    
    @property
    def network_size(self) -> int:
        """Number of gateways in this network (including self)."""
        return len(self.connected_gateway_ids) + 1
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"Gateway(id='{self.id}', {status}, network_size={self.network_size})"


@dataclass
class LGate(Bypass):
    """
    L-Gate - mysterious ancient gateways that connect to the Terminal Egress.
    
    L-Gates form a special network separate from regular gateways.
    All L-Gates connect to the Terminal Egress system.
    """
    
    connected_lgate_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.bypass_type = BypassType.LGATE
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"LGate(id='{self.id}', {status})"


@dataclass
class HyperRelay(Bypass):
    """
    Hyper Relay - constructed FTL relay for faster travel within empires.
    
    Hyper relays create faster travel routes between systems within
    the same empire's borders.
    """
    
    connected_relay_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.bypass_type = BypassType.RELAY
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"HyperRelay(id='{self.id}', {status}, connections={len(self.connected_relay_ids)})"


@dataclass
class ShroudTunnel(Bypass):
    """
    Shroud Tunnel - psionic bypass through the Shroud dimension.
    
    Only accessible to psionic empires with certain technologies/ascension perks.
    """
    
    def __post_init__(self):
        self.bypass_type = BypassType.SHROUD_TUNNEL
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"ShroudTunnel(id='{self.id}', {status})"


@dataclass
class BypassNetwork:
    """
    Container for all bypasses in the galaxy.
    
    Provides lookup and analysis methods for bypass infrastructure.
    """
    
    bypasses: List[Bypass] = field(default_factory=list)
    _bypass_map: dict = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        """Build bypass lookup map."""
        self._bypass_map = {b.id: b for b in self.bypasses}
    
    def get_bypass(self, bypass_id: str) -> Optional[Bypass]:
        """Get a bypass by ID."""
        return self._bypass_map.get(bypass_id)
    
    def get_bypasses_by_type(self, bypass_type: BypassType) -> List[Bypass]:
        """Get all bypasses of a specific type."""
        return [b for b in self.bypasses if b.bypass_type == bypass_type]
    
    def get_bypasses_in_system(self, system_id: str) -> List[Bypass]:
        """Get all bypasses in a specific system."""
        return [b for b in self.bypasses if b.system_id == system_id]
    
    @property
    def wormholes(self) -> List[Wormhole]:
        """Get all wormholes."""
        return [b for b in self.bypasses if isinstance(b, Wormhole)]
    
    @property
    def gateways(self) -> List[Gateway]:
        """Get all gateways."""
        return [b for b in self.bypasses if isinstance(b, Gateway)]
    
    @property
    def hyper_relays(self) -> List[HyperRelay]:
        """Get all hyper relays."""
        return [b for b in self.bypasses if isinstance(b, HyperRelay)]
    
    @property
    def lgates(self) -> List[LGate]:
        """Get all L-Gates."""
        return [b for b in self.bypasses if isinstance(b, LGate)]
    
    def get_wormhole_pairs(self) -> List[tuple[Wormhole, Wormhole]]:
        """
        Get all wormhole pairs (each pair returned once).
        
        Returns:
            List of (wormhole1, wormhole2) tuples
        """
        pairs = []
        processed = set()
        
        for wh in self.wormholes:
            if wh.id in processed:
                continue
            
            if wh.linked_to_id:
                partner = self.get_bypass(wh.linked_to_id)
                if partner and isinstance(partner, Wormhole):
                    pairs.append((wh, partner))
                    processed.add(wh.id)
                    processed.add(partner.id)
        
        return pairs
    
    def get_gateway_networks(self) -> List[List[Gateway]]:
        """
        Get all gateway networks (groups of connected gateways).
        
        Returns:
            List of gateway networks, where each network is a list of connected gateways
        """
        networks = []
        processed = set()
        
        for gw in self.gateways:
            if gw.id in processed:
                continue
            
            # Build network from this gateway
            network = [gw]
            processed.add(gw.id)
            
            # Add all connected gateways
            for conn_id in gw.connected_gateway_ids:
                conn_gw = self.get_bypass(conn_id)
                if conn_gw and isinstance(conn_gw, Gateway) and conn_id not in processed:
                    network.append(conn_gw)
                    processed.add(conn_id)
            
            if network:
                networks.append(network)
        
        return networks
    
    def count_by_type(self) -> dict:
        """
        Count bypasses by type.
        
        Returns:
            Dict mapping bypass type name to count
        """
        counts = {}
        for bypass in self.bypasses:
            type_name = bypass.bypass_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def get_active_bypasses(self) -> List[Bypass]:
        """Get all active bypasses."""
        return [b for b in self.bypasses if b.is_active]
    
    def get_inactive_bypasses(self) -> List[Bypass]:
        """Get all inactive bypasses."""
        return [b for b in self.bypasses if not b.is_active]
    
    def get_bypasses_in_systems(self, system_ids: List[str]) -> List[Bypass]:
        """
        Get all bypasses in a list of systems.
        
        Useful for filtering to a specific territory.
        
        Args:
            system_ids: List of system IDs to filter by
            
        Returns:
            List of bypasses in those systems
        """
        system_id_set = set(system_ids)
        return [b for b in self.bypasses if b.system_id in system_id_set]
    
    def get_bypasses_by_owner(self, owner_id: str, system_owner_map: dict) -> List[Bypass]:
        """
        Get all bypasses in systems owned by a specific country.
        
        Args:
            owner_id: Country ID to filter by
            system_owner_map: Dict mapping system_id -> owner_id
            
        Returns:
            List of bypasses in systems owned by this country
            
        Example:
            # Build system ownership map from GalacticMap
            system_owner_map = {s.id: s.owner_id for s in galactic_map.systems if s.owner_id}
            
            # Get player's bypasses
            player_bypasses = bypass_network.get_bypasses_by_owner('0', system_owner_map)
        """
        owned_systems = [sys_id for sys_id, owner in system_owner_map.items() if owner == owner_id]
        return self.get_bypasses_in_systems(owned_systems)
    
    def filter_by_galactic_map(self, galactic_map, owner_id: Optional[str] = None) -> 'BypassNetwork':
        """
        Create a new BypassNetwork filtered by galactic map criteria.
        
        Args:
            galactic_map: GalacticMap instance to cross-reference
            owner_id: If provided, only include bypasses in systems owned by this country
            
        Returns:
            New BypassNetwork with filtered bypasses
            
        Example:
            # Get only player's bypasses
            player_bypasses = bypass_network.filter_by_galactic_map(galactic_map, owner_id='0')
            
            # Get all bypasses in mapped systems (no owner filter)
            mapped_bypasses = bypass_network.filter_by_galactic_map(galactic_map)
        """
        if owner_id is not None:
            # Filter to specific owner
            owned_systems = galactic_map.get_systems_by_owner(owner_id)
            system_ids = [s.id for s in owned_systems]
        else:
            # Include all systems in galactic map
            system_ids = [s.id for s in galactic_map.systems]
        
        filtered_bypasses = self.get_bypasses_in_systems(system_ids)
        return BypassNetwork(bypasses=filtered_bypasses)
    
    def count_by_owner(self, system_owner_map: dict) -> dict:
        """
        Count bypasses by system owner.
        
        Args:
            system_owner_map: Dict mapping system_id -> owner_id
            
        Returns:
            Dict mapping owner_id -> count of bypasses in their systems
            
        Example:
            system_owner_map = {s.id: s.owner_id for s in galactic_map.systems if s.owner_id}
            owner_counts = bypass_network.count_by_owner(system_owner_map)
            print(f"Your bypasses: {owner_counts.get('0', 0)}")
        """
        counts = {}
        
        for bypass in self.bypasses:
            if bypass.system_id and bypass.system_id in system_owner_map:
                owner = system_owner_map[bypass.system_id]
                counts[owner] = counts.get(owner, 0) + 1
        
        return counts
