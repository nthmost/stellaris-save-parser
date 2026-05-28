"""
Main StellarisSave class for loading and parsing save files.
"""

import re
from typing import Optional
from .parser import (
    load_gamestate,
    find_section,
    find_subsection,
    extract_blocks,
    extract_value,
    extract_list,
    extract_leader_name
)
from .models import Empire, Planet, Leader
from .system import StarSystem, HyperlaneConnection, GalacticMap
from .bypass import (
    Bypass, BypassType, BypassNetwork,
    Wormhole, Gateway, LGate, HyperRelay, ShroudTunnel
)
from .economics import ResourceAmount, ResourceBalance, SystemEconomy


class StellarisSave:
    """Main class for loading and parsing Stellaris save files."""
    
    def __init__(self, save_path: str):
        """
        Load a Stellaris save file.
        
        Args:
            save_path: Path to the .sav file
            
        Raises:
            FileNotFoundError: If the save file doesn't exist
            ValueError: If the save file is invalid
        """
        self.save_path = save_path
        self.gamestate = load_gamestate(save_path)
        self._player_country_id: Optional[str] = None
        self._empires: dict[str, Empire] = {}
        
        # Extract basic metadata
        self.game_date = extract_value(self.gamestate, 'date', 'unknown')
        self.save_name = extract_value(self.gamestate, 'name', 'unknown')
    
    def get_player_country_id(self) -> str:
        """
        Find the player's country ID.
        
        Returns:
            The country ID as a string
        """
        if self._player_country_id:
            return self._player_country_id
        
        # Method 1: Check player= section
        player_match = re.search(r'player=\s*\{.*?country=(\d+)', self.gamestate, re.DOTALL)
        if player_match:
            self._player_country_id = player_match.group(1)
            return self._player_country_id
        
        # Method 2: Find empire with most colonies matching save name
        # This is more complex and would require parsing all empires
        # For now, default to country 0
        self._player_country_id = "0"
        return self._player_country_id
    
    def get_player_empire(self) -> Empire:
        """
        Get the player's empire with all data loaded.
        
        Returns:
            An Empire object representing the player
        """
        country_id = self.get_player_country_id()
        return self.get_empire(country_id)
    
    def get_empire(self, country_id: str) -> Empire:
        """
        Get an empire by country ID.
        
        Args:
            country_id: The country ID to load
            
        Returns:
            An Empire object
        """
        if country_id in self._empires:
            return self._empires[country_id]
        
        empire = Empire(
            country_id=country_id,
            name=self.save_name,
            game_date=self.game_date
        )
        
        # Load planets
        empire.planets = self._load_planets(country_id)
        
        # Load leaders
        empire.leaders = self._load_leaders(country_id)
        
        # Link governors to planets
        for planet in empire.planets:
            if planet.governor_id:
                planet.governor = empire.get_leader_by_id(planet.governor_id)
        
        self._empires[country_id] = empire
        return empire
    
    def _load_planets(self, country_id: str) -> list[Planet]:
        """Load all planets for a country."""
        planets = []
        
        # Find planets section
        planets_section = find_section(self.gamestate, 'planets')
        if not planets_section:
            return planets
        
        # Find planet= subsection
        planet_data = find_subsection(planets_section, 'planet')
        if not planet_data:
            return planets
        
        # Extract all planet blocks
        planet_blocks = extract_blocks(planet_data, indent_level=2)
        
        # Load district database for mapping IDs to types
        district_types = self._load_district_types()
        
        # Load deposit database for mapping IDs to types
        deposit_types = self._load_deposit_types()
        
        for planet_id, block in planet_blocks.items():
            # Check if owned by this country
            owner = extract_value(block, 'owner')
            if owner != int(country_id):
                continue
            
            # Check if colonized (has designation)
            designation = extract_value(block, 'final_designation')
            if not designation:
                continue
            
            # Extract planet data
            name_match = re.search(r'key="([^"]+)"', block)
            name = name_match.group(1) if name_match else f'Planet_{planet_id}'
            
            # Parse districts
            districts = self._parse_planet_districts(block, district_types)
            
            # Parse deposits
            deposits = self._parse_planet_deposits(block, deposit_types)
            
            # Parse resources (production and consumption)
            resources = self._parse_planet_resources(block)
            
            planet = Planet(
                id=planet_id,
                name=name,
                designation=designation,
                planet_class=extract_value(block, 'planet_class', 'unknown'),
                size=extract_value(block, 'planet_size', 0),
                pops=extract_value(block, 'num_sapient_pops', 0),
                owner_id=country_id,
                governor_id=str(extract_value(block, 'governor')) if extract_value(block, 'governor') else None,
                sector_id=str(extract_value(block, 'sector')) if extract_value(block, 'sector') else None,
                stability=extract_value(block, 'stability', 0.0),
                colonize_date=extract_value(block, 'colonize_date'),
                districts=districts,
                deposits=deposits,
                resources=resources
            )
            
            planets.append(planet)
        
        return planets
    
    def _load_leaders(self, country_id: str) -> list[Leader]:
        """Load all leaders for a country."""
        leaders = []
        
        # Find leaders section
        leaders_section = find_section(self.gamestate, 'leaders')
        if not leaders_section:
            return leaders
        
        # Extract all leader blocks
        leader_blocks = extract_blocks(leaders_section, indent_level=1)
        
        for leader_id, block in leader_blocks.items():
            # Check if this leader belongs to this country
            country = extract_value(block, 'country')
            if country != int(country_id):
                continue
            
            # Check if this is an official (governor)
            leader_class = extract_value(block, 'class')
            if not leader_class:
                continue
            
            # Extract leader data
            name = extract_leader_name(block) or f'Leader_{leader_id}'
            
            leader = Leader(
                id=leader_id,
                name=name,
                leader_class=leader_class,
                level=extract_value(block, 'level', 0),
                traits=extract_list(block, 'traits'),
                country_id=country_id,
                previous_job=extract_value(block, 'job')
            )
            
            leaders.append(leader)
        
        return leaders
    
    def _load_district_types(self) -> dict[str, str]:
        """Load district ID to type mapping."""
        districts_section = find_section(self.gamestate, 'districts')
        if not districts_section:
            return {}
        
        district_blocks = extract_blocks(districts_section, indent_level=1)
        district_map = {}
        
        for dist_id, block in district_blocks.items():
            dist_type = extract_value(block, 'type')
            if dist_type:
                district_map[dist_id] = dist_type
        
        return district_map
    
    def _load_deposit_types(self) -> dict[str, str]:
        """Load deposit ID to type mapping."""
        deposit_section = find_section(self.gamestate, 'deposit')
        if not deposit_section:
            return {}
        
        deposit_blocks = extract_blocks(deposit_section, indent_level=1)
        deposit_map = {}
        
        for dep_id, block in deposit_blocks.items():
            dep_type = extract_value(block, 'type')
            if dep_type:
                deposit_map[dep_id] = dep_type
        
        return deposit_map
    
    def _parse_planet_districts(self, planet_block: str, district_types: dict[str, str]) -> dict[str, int]:
        """Parse built districts from planet block."""
        from collections import Counter
        
        # Find districts= { ... }
        districts_match = re.search(r'districts=\s*\{\s*([0-9\s]+)\}', planet_block)
        if not districts_match:
            return {}
        
        district_ids = districts_match.group(1).split()
        
        # Map IDs to types
        types = []
        for dist_id in district_ids:
            if dist_id in district_types:
                types.append(district_types[dist_id])
        
        # Count by type
        return dict(Counter(types))
    
    def _parse_planet_deposits(self, planet_block: str, deposit_types: dict[str, str]) -> list[str]:
        """Parse deposits from planet block."""
        # Find deposits= { ... }
        deposits_match = re.search(r'deposits=\s*\{\s*([0-9\s]+)\}', planet_block)
        if not deposits_match:
            return []
        
        deposit_ids = deposits_match.group(1).split()
        
        # Map IDs to types
        types = []
        for dep_id in deposit_ids:
            if dep_id in deposit_types:
                types.append(deposit_types[dep_id])
        
        return types
    
    def _parse_planet_resources(self, planet_block: str) -> Optional[ResourceBalance]:
        """Parse resource production and consumption from planet block."""
        # Parse produces section
        produces_match = re.search(r'produces=\s*\{([^}]+)\}', planet_block)
        produces = ResourceAmount()
        if produces_match:
            resource_data = produces_match.group(1)
            resources = re.findall(r'([a-z_]+)=([-0-9.]+)', resource_data)
            for res_type, amount in resources:
                if hasattr(produces, res_type):
                    setattr(produces, res_type, float(amount))
        
        # Parse upkeep section
        upkeep_match = re.search(r'upkeep=\s*\{([^}]+)\}', planet_block)
        upkeep = ResourceAmount()
        if upkeep_match:
            resource_data = upkeep_match.group(1)
            resources = re.findall(r'([a-z_]+)=([-0-9.]+)', resource_data)
            for res_type, amount in resources:
                if hasattr(upkeep, res_type):
                    setattr(upkeep, res_type, float(amount))
        
        # Only return ResourceBalance if we found any data
        if produces_match or upkeep_match:
            return ResourceBalance(produces=produces, upkeep=upkeep)
        
        return None
    
    def get_galactic_map(self, filter_country_id: Optional[str] = None) -> GalacticMap:
        """
        Load the galactic map with all star systems and hyperlanes.
        
        Args:
            filter_country_id: If provided, only load systems controlled by this country.
                              Uses cached planet data for efficiency.
            
        Returns:
            GalacticMap object with all systems
        """
        systems = []
        
        # Find galactic_object section
        galactic_section = find_section(self.gamestate, 'galactic_object')
        if not galactic_section:
            return GalacticMap(systems=[])
        
        # If filtering, pre-load player planet IDs for efficiency
        player_planet_ids = set()
        if filter_country_id is not None:
            # Use already-loaded empire data if available
            country_id = filter_country_id
            if country_id in self._empires:
                player_planet_ids = {p.id for p in self._empires[country_id].planets}
            else:
                # Quick scan for player planets
                planets_section = find_section(self.gamestate, 'planets')
                if planets_section:
                    # Just do a quick regex scan instead of full extraction
                    owner_pattern = rf'\n\t\t\towner={filter_country_id}\s'
                    planet_matches = re.finditer(r'\n\t\t(\d+)=\s*\{[^}]*?' + owner_pattern, planets_section, re.DOTALL)
                    for match in planet_matches:
                        player_planet_ids.add(match.group(1))
        
        # Extract all galactic objects
        object_blocks = extract_blocks(galactic_section, indent_level=1)
        
        for obj_id, block in object_blocks.items():
            # Only process star systems (skip planets, asteroids, etc.)
            if 'type=star' not in block:
                continue
            
            # Get planet IDs early for filtering
            planet_ids = re.findall(r'planet=(\d+)', block)
            
            # Filter by country if requested
            if filter_country_id is not None:
                # Check if any planet in this system belongs to the player
                has_player_planet = any(pid in player_planet_ids for pid in planet_ids)
                if not has_player_planet:
                    continue
            
            # Get system name
            name_match = re.search(r'name=\s*\{\s*key="([^"]+)"', block)
            name = name_match.group(1) if name_match else f'System_{obj_id}'
            
            # Get coordinates
            coord_match = re.search(r'coordinate=\s*\{\s*x=([-\d.]+)\s*y=([-\d.]+)', block)
            if not coord_match:
                continue
            coordinates = (float(coord_match.group(1)), float(coord_match.group(2)))
            
            # Get star class
            star_class = extract_value(block, 'star_class', 'unknown')
            
            # Get owner (may not be set for unclaimed systems)
            owner_id = extract_value(block, 'owner')
            owner_str = str(owner_id) if owner_id is not None else None
            
            # If filtering and we found player planets, set owner to filter_country_id
            if filter_country_id is not None and any(pid in player_planet_ids for pid in planet_ids):
                owner_str = filter_country_id
            
            # Parse hyperlanes
            hyperlanes = []
            hyperlane_section = re.search(r'hyperlane=\s*\{(.*?)\n\t\t\}', block, re.DOTALL)
            if hyperlane_section:
                # Find all connection blocks
                to_values = re.findall(r'to=(\d+)', hyperlane_section.group(1))
                length_values = re.findall(r'length=([\d.]+)', hyperlane_section.group(1))
                
                for to_id, length in zip(to_values, length_values):
                    hyperlanes.append(HyperlaneConnection(
                        to_system_id=to_id,
                        length=float(length)
                    ))
            
            # Create system object
            system = StarSystem(
                id=obj_id,
                name=name,
                coordinates=coordinates,
                star_class=star_class,
                planet_ids=planet_ids,
                hyperlanes=hyperlanes,
                owner_id=owner_str
            )
            
            systems.append(system)
        
        return GalacticMap(systems=systems)
    
    def get_bypass_network(self) -> BypassNetwork:
        """
        Load all bypasses (wormholes, gateways, hyper relays, etc.).
        
        Returns:
            BypassNetwork object containing all bypasses
        """
        bypasses = []
        
        # Find bypasses section
        bypass_section = find_section(self.gamestate, 'bypasses')
        if not bypass_section:
            return BypassNetwork(bypasses=[])
        
        # Extract all bypass blocks
        bypass_blocks = extract_blocks(bypass_section, indent_level=1)
        
        # Build bypass-to-system map (more reliable than planet-to-system for bypasses)
        bypass_to_system = self._get_bypass_to_system_map()
        
        for bypass_id, block in bypass_blocks.items():
            # Get bypass type
            type_str = extract_value(block, 'type')
            if not type_str:
                continue
            
            # Get common attributes
            is_active = extract_value(block, 'active') == 'yes'
            
            # Get system location from bypass-to-system map
            # (More reliable than using bypass owner field)
            system_id = bypass_to_system.get(bypass_id)
            
            # Get planet ID from owner field (for reference, but not used for location)
            planet_id = None
            owner_match = re.search(r'owner=\s*\{[^}]*?id=(\d+)', block)
            if owner_match:
                planet_id = owner_match.group(1)
            
            # Create specific bypass type
            bypass = None
            
            if type_str == 'wormhole':
                linked_to = extract_value(block, 'linked_to')
                bypass = Wormhole(
                    id=bypass_id,
                    bypass_type=BypassType.WORMHOLE,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id,
                    linked_to_id=str(linked_to) if linked_to else None
                )
            
            elif type_str == 'gateway':
                connections = self._parse_connections(block)
                bypass = Gateway(
                    id=bypass_id,
                    bypass_type=BypassType.GATEWAY,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id,
                    connected_gateway_ids=connections
                )
            
            elif type_str == 'lgate':
                connections = self._parse_connections(block)
                bypass = LGate(
                    id=bypass_id,
                    bypass_type=BypassType.LGATE,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id,
                    connected_lgate_ids=connections
                )
            
            elif type_str == 'relay_bypass':
                connections = self._parse_connections(block)
                bypass = HyperRelay(
                    id=bypass_id,
                    bypass_type=BypassType.RELAY,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id,
                    connected_relay_ids=connections
                )
            
            elif type_str == 'shroud_tunnel':
                bypass = ShroudTunnel(
                    id=bypass_id,
                    bypass_type=BypassType.SHROUD_TUNNEL,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id
                )
            
            elif type_str == 'quantum_catapult':
                bypass = Bypass(
                    id=bypass_id,
                    bypass_type=BypassType.QUANTUM_CATAPULT,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id
                )
            
            else:
                # Unknown bypass type - store as generic
                try:
                    bypass_type_enum = BypassType(type_str)
                except ValueError:
                    bypass_type_enum = BypassType.UNKNOWN
                
                bypass = Bypass(
                    id=bypass_id,
                    bypass_type=bypass_type_enum,
                    is_active=is_active,
                    system_id=system_id,
                    planet_id=planet_id
                )
            
            if bypass:
                bypasses.append(bypass)
        
        return BypassNetwork(bypasses=bypasses)
    
    def _get_planet_to_system_map(self) -> dict:
        """Build a map of planet ID to system ID (cached)."""
        planet_to_system = {}
        
        galactic_section = find_section(self.gamestate, 'galactic_object')
        if not galactic_section:
            return planet_to_system
        
        object_blocks = extract_blocks(galactic_section, indent_level=1)
        
        for sys_id, sys_block in object_blocks.items():
            if 'type=star' not in sys_block:
                continue
            
            planet_ids = re.findall(r'\bplanet=(\d+)', sys_block)
            for pid in planet_ids:
                planet_to_system[pid] = sys_id
        
        return planet_to_system
    
    def _get_bypass_to_system_map(self) -> dict:
        """
        Build a map of bypass ID to system ID.
        
        Systems list their bypasses in the bypasses={...} field.
        This is the authoritative source for bypass locations.
        """
        bypass_to_system = {}
        
        galactic_section = find_section(self.gamestate, 'galactic_object')
        if not galactic_section:
            return bypass_to_system
        
        object_blocks = extract_blocks(galactic_section, indent_level=1)
        
        for sys_id, sys_block in object_blocks.items():
            if 'type=star' not in sys_block:
                continue
            
            # Parse bypasses field
            bypasses_match = re.search(r'bypasses=\s*\{([^}]+)\}', sys_block)
            if bypasses_match:
                bypass_ids = bypasses_match.group(1).strip().split()
                for bypass_id in bypass_ids:
                    bypass_to_system[bypass_id] = sys_id
        
        return bypass_to_system
    
    def _parse_connections(self, bypass_block: str) -> list[str]:
        """Parse connection IDs from a bypass block."""
        connections_match = re.search(r'connections=\s*\{([^}]+)\}', bypass_block)
        if connections_match:
            return connections_match.group(1).strip().split()
        return []
    
    def get_system_economy(self, system_id: str, empire: Optional[Empire] = None) -> Optional[SystemEconomy]:
        """
        Get aggregated economic data for a star system.
        
        Args:
            system_id: The system ID to analyze
            empire: Optional Empire object (will use player empire if not provided)
            
        Returns:
            SystemEconomy object with aggregated resource data, or None if system not found
        """
        # Load galactic map to get system info
        galactic_map = self.get_galactic_map()
        system = galactic_map.get_system(system_id)
        
        if not system:
            return None
        
        # Get empire if not provided
        if empire is None:
            empire = self.get_player_empire()
        
        # Find planets in this system owned by this empire
        system_planets = [p for p in empire.planets if p.id in system.planet_ids]
        
        if not system_planets:
            return None
        
        # Aggregate resources
        total_resources = ResourceBalance()
        total_pops = 0
        
        for planet in system_planets:
            if planet.resources:
                total_resources = total_resources + planet.resources
            total_pops += planet.pops
        
        return SystemEconomy(
            system_id=system_id,
            system_name=system.name,
            planet_count=len(system_planets),
            total_pops=total_pops,
            resources=total_resources
        )
    
    def get_system_economy_by_name(self, system_name: str, empire: Optional[Empire] = None) -> Optional[SystemEconomy]:
        """
        Get aggregated economic data for a star system by name.
        
        Args:
            system_name: The system name to search for (case-insensitive)
            empire: Optional Empire object (will use player empire if not provided)
            
        Returns:
            SystemEconomy object with aggregated resource data, or None if system not found
            
        Example:
            econ = save.get_system_economy_by_name("Sol")
            if econ:
                print(f"{econ.system_name}: {econ.total_pops} pops")
                print(f"Net energy: {econ.resources.net.energy:.1f}")
        """
        # Load galactic map to find system
        galactic_map = self.get_galactic_map()
        system = galactic_map.get_system_by_name(system_name)
        
        if not system:
            return None
        
        return self.get_system_economy(system.id, empire)
    
    def get_all_system_economies(self, empire: Optional[Empire] = None) -> List[SystemEconomy]:
        """
        Get economic data for all systems with empire planets.
        
        Args:
            empire: Optional Empire object (will use player empire if not provided)
            
        Returns:
            List of SystemEconomy objects for all systems with empire presence
        """
        if empire is None:
            empire = self.get_player_empire()
        
        # Build map of system ID to planets
        galactic_map = self.get_galactic_map()
        system_planets = {}
        
        for planet in empire.planets:
            # Find which system this planet is in
            for system in galactic_map.systems:
                if planet.id in system.planet_ids:
                    if system.id not in system_planets:
                        system_planets[system.id] = []
                    system_planets[system.id].append(planet)
                    break
        
        # Create SystemEconomy for each system
        economies = []
        for system_id, planets in system_planets.items():
            system = galactic_map.get_system(system_id)
            if not system:
                continue
            
            # Aggregate resources
            total_resources = ResourceBalance()
            total_pops = 0
            
            for planet in planets:
                if planet.resources:
                    total_resources = total_resources + planet.resources
                total_pops += planet.pops
            
            economies.append(SystemEconomy(
                system_id=system_id,
                system_name=system.name,
                planet_count=len(planets),
                total_pops=total_pops,
                resources=total_resources
            ))
        
        return economies
