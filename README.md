# Stellaris Save Parser

A Python library for parsing and analyzing Stellaris save files.

## Features

- Parse Stellaris `.sav` files (Clausewitz engine format)
- Extract empire, planet, and leader data
- Analyze governor assignments and traits
- **NEW:** Track planet districts and resource deposits
- **NEW:** Analyze district capacity and expansion opportunities
- **NEW:** Identify special planet features (Gaia worlds, strategic resources)
- **NEW:** Parse hyperlane network and system connections
- **NEW:** Analyze territory layout, chokepoints, and border systems
- **NEW:** Calculate distances between systems
- Identify optimization opportunities for resource production
- Support for both regular and gestalt consciousness empires

## Installation

```bash
pip install stellaris-save-parser
```

Or install from source:

```bash
git clone https://github.com/yourusername/stellaris-save-parser.git
cd stellaris-save-parser
pip install -e .
```

## Quick Start

```python
from stellaris_save_parser import StellarisSave

# Load a save file
save = StellarisSave("path/to/your/save.sav")

# Get your empire
empire = save.get_player_empire()

print(f"Empire: {empire.name}")
print(f"Planets: {len(empire.planets)}")
print(f"Leaders: {len(empire.leaders)}")

# Analyze governor assignments
for planet in empire.planets:
    if planet.governor:
        print(f"{planet.name}: {planet.governor.name} (Level {planet.governor.level})")
    else:
        print(f"{planet.name}: NO GOVERNOR")

# Find optimization opportunities
analysis = empire.analyze_governor_assignments()
print(f"\nMismatched governors: {len(analysis['mismatches'])}")
for mismatch in analysis['mismatches']:
    print(f"  - {mismatch['leader'].name} on {mismatch['planet'].name}")
```

## Examples

See the `examples/` directory for more detailed usage:

- `basic_analysis.py` - Basic save file analysis and governor assignments
- **`planet_resources.py`** - Analyze districts, deposits, and expansion opportunities
- **`hyperlane_network.py`** - Analyze hyperlane connections, chokepoints, and strategic systems

## Documentation

### Main Classes

#### `StellarisSave`
Main entry point for parsing save files.

```python
save = StellarisSave("path/to/save.sav")
```

#### `Empire`
Represents a playable empire with its planets, leaders, and resources.

```python
empire = save.get_player_empire()
print(empire.name)
print(empire.planets)
print(empire.leaders)
```

#### `Planet`
Represents a colonized planet with districts and resources.

```python
planet = empire.planets[0]
print(f"{planet.name}: {planet.designation}, {planet.pops} pops")
print(f"Districts: {planet.total_districts}/{planet.size} ({planet.available_district_slots} available)")
print(f"Built: {planet.districts}")  # e.g., {'district_city': 1, 'district_mining': 2}
print(f"Deposits: {len(planet.deposits)}")
print(f"Deposit summary: {planet.get_deposit_summary()}")

# Check district types
print(f"Mining districts: {planet.mining_districts}")
print(f"Generator districts: {planet.generator_districts}")
print(f"Farming districts: {planet.farming_districts}")

if planet.governor:
    print(f"Governor: {planet.governor.name}")
```

#### `Leader`
Represents a leader (official, scientist, commander).

```python
leader = empire.leaders[0]
print(f"{leader.name} (Level {leader.level})")
print(f"Class: {leader.leader_class}")
print(f"Traits: {leader.traits}")
```

## Planet Districts and Resources

The library now tracks detailed planet infrastructure:

### District Properties

- `planet.size` - Total district slots available
- `planet.total_districts` - Number of districts built
- `planet.available_district_slots` - Empty slots for expansion
- `planet.district_slots_used_percent` - Percentage capacity used
- `planet.districts` - Dict of built districts by type (e.g., `{'district_city': 1, 'district_mining': 2}`)

### District Type Properties

- `planet.city_districts` - Number of city districts
- `planet.mining_districts` - Number of mining districts
- `planet.generator_districts` - Number of generator districts
- `planet.farming_districts` - Number of farming districts
- `planet.industrial_districts` - Number of industrial districts

### Deposit Analysis

- `planet.deposits` - List of deposit types (e.g., `['d_minerals_6', 'd_hot_springs']`)
- `planet.get_deposit_summary()` - Returns dict with counts by category:
  - `minerals` - Mining deposits
  - `energy` - Generator deposits
  - `food` - Agriculture deposits
  - `research` - Research deposits
  - `strategic` - Strategic resources (motes, gases, crystals)
  - `other` - Other deposits

### Special Planet Features

- `planet.has_special_deposits` - True if planet has unique/strategic resources
- `planet.planet_class` - Planet type (e.g., `pc_tropical`, `pc_gaia`, `pc_desert`)

## Hyperlane Network and Territory Analysis

The library can parse the complete galactic map and analyze your empire's territory:

### Star System Properties

- `system.name` - System name
- `system.coordinates` - (x, y) galactic coordinates
- `system.star_class` - Star type (e.g., "sc_k", "sc_m", "sc_g")
- `system.planet_ids` - List of planet IDs in the system
- `system.hyperlanes` - List of HyperlaneConnection objects
- `system.owner_id` - Controlling country ID (if any)
- `system.connection_count` - Number of hyperlane connections
- `system.is_chokepoint` - True if only 1-2 connections (strategic bottleneck)
- `system.is_hub` - True if 5+ connections (major junction)

### Hyperlane Connections

- `hyperlane.to_system_id` - Connected system ID
- `hyperlane.length` - Travel distance along hyperlane

### Galactic Map Analysis

```python
# Load galactic map (optionally filtered to player territory)
galactic_map = save.get_galactic_map(filter_country_id='0')

# Get territory statistics
stats = galactic_map.calculate_territory_stats('0')
print(f"Systems: {stats['total_systems']}")
print(f"Border systems: {stats['border_systems']}")
print(f"Chokepoints: {stats['chokepoints']}")
print(f"Hubs: {stats['hubs']}")

# Find strategic systems
chokepoints = galactic_map.find_chokepoints('0')
borders = galactic_map.find_border_systems('0')

# Analyze connections
for system in galactic_map.systems:
    connected = galactic_map.get_connected_systems(system)
    print(f"{system.name} connects to {len(connected)} systems")
    
# Calculate distances
distance = system1.distance_to(system2)
```

## Supported Trait Analysis

The library includes trait categorization for:

- **Governor traits** - Traits that affect planetary production
  - Food production: `agrarian_upbringing`, `homesteader`
  - Energy production: `capitalist`, `energy_mogul`
  - Mineral production: `private_mines`
  - Alloy production: `scrapper`
  - Administrative: `bureaucrat`, `architectural_interest`

- **Councilor/Ruler traits** - Traits that only work on the council
  - Prefix: `trait_ruler_*`

- **Scientist traits** - Research and anomaly bonuses
  - Prefix: `leader_trait_expertise_*`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

## Known Limitations

- Currently supports Stellaris version 4.3+ (Cetus)
- Does not parse fleet or military data (yet)
- Does not parse diplomacy data (yet)

## License

MIT License - see LICENSE file for details

## Credits

Developed by the Stellaris modding community. Special thanks to:
- Paradox Interactive for Stellaris
- The Stellaris Wiki contributors for trait documentation
- Everyone who contributed save files for testing

## Changelog

### 0.1.0 (Initial Release)
- Basic save file parsing
- Empire, planet, and leader extraction
- Governor assignment analysis
- Trait categorization
