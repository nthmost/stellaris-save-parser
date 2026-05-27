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
                colonize_date=extract_value(block, 'colonize_date')
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
