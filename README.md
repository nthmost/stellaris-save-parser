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
- **NEW:** Parse bypass network (wormholes, gateways, hyper relays, L-Gates)
- **NEW:** Track wormhole pairs and gateway networks
- **NEW:** Identify FTL shortcuts and strategic bypass locations
- **NEW:** Track resource production and consumption (economics)
- **NEW:** Calculate system-level resource balances
- **NEW:** Identify resource deficits and surpluses
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

## Bypass Network (Wormholes, Gateways, Hyper Relays)

The library parses all FTL bypasses in the galaxy:

### Bypass Types

- **Wormholes** - Natural permanent connections between two systems
- **Gateways** - Ancient or constructed gates connecting to all other gateways
- **L-Gates** - Special gateway network to Terminal Egress
- **Hyper Relays** - Constructed relays for faster empire-internal travel
- **Shroud Tunnels** - Psionic bypasses through the Shroud

### Basic Usage

```python
# Load bypass network
bypass_network = save.get_bypass_network()

# Count bypasses by type
counts = bypass_network.count_by_type()
print(f"Wormholes: {counts.get('wormhole', 0)}")
print(f"Gateways: {counts.get('gateway', 0)}")

# Get all wormholes
wormholes = bypass_network.wormholes
for wh in wormholes:
    print(f"Wormhole {wh.id} in system {wh.system_id}")
    print(f"  Active: {wh.is_active}")
    print(f"  Links to: {wh.linked_to_id}")

# Get wormhole pairs (each pair returned once)
for wh1, wh2 in bypass_network.get_wormhole_pairs():
    print(f"{wh1.system_id} ↔ {wh2.system_id}")

# Get gateway networks
for network in bypass_network.get_gateway_networks():
    print(f"Gateway network with {len(network)} gates")
    for gateway in network:
        print(f"  Gateway {gateway.id} in system {gateway.system_id}")

# Filter by status
active_bypasses = bypass_network.get_active_bypasses()
inactive_bypasses = bypass_network.get_inactive_bypasses()
```

### Ownership Filtering

Filter bypasses by empire/territory:

```python
# Load both networks
galactic_map = save.get_galactic_map()
bypass_network = save.get_bypass_network()

# Method 1: Use system owner map
system_owner_map = galactic_map.get_system_owner_map()

# Get player's bypasses
player_bypasses = bypass_network.get_bypasses_by_owner('0', system_owner_map)
print(f"You control {len(player_bypasses)} bypasses")

# Count bypasses by empire
owner_counts = bypass_network.count_by_owner(system_owner_map)
for owner_id, count in owner_counts.items():
    print(f"Country {owner_id}: {count} bypasses")

# Method 2: Create filtered network
player_network = bypass_network.filter_by_galactic_map(galactic_map, owner_id='0')
print(f"Your wormholes: {len(player_network.wormholes)}")
print(f"Your gateways: {len(player_network.gateways)}")

# Get bypasses in specific systems
my_system_ids = ['123', '456', '789']
local_bypasses = bypass_network.get_bypasses_in_systems(my_system_ids)
```

### Bypass Properties

- `bypass.id` - Unique bypass ID
- `bypass.bypass_type` - BypassType enum (WORMHOLE, GATEWAY, etc.)
- `bypass.is_active` - Whether bypass is operational
- `bypass.system_id` - System containing this bypass
- `bypass.planet_id` - Planet/object reference (if applicable)

### Wormhole-Specific

- `wormhole.linked_to_id` - ID of the connected wormhole

### Gateway-Specific

- `gateway.connected_gateway_ids` - List of all connected gateway IDs
- `gateway.network_size` - Total gateways in network (including self)

### Hyper Relay-Specific

- `relay.connected_relay_ids` - List of connected relay IDs

## Economics and Resource Tracking

The library parses planet-level resource production and consumption, and can aggregate to system or empire level:

### Resource Types

All per-month values as stored in save files:

- **Basic**: `energy`, `minerals`, `food`
- **Advanced**: `consumer_goods`, `alloys`
- **Research**: `physics_research`, `society_research`, `engineering_research`
- **Special**: `unity`, `trade`, `influence`
- **Strategic**: `volatile_motes`, `exotic_gases`, `rare_crystals`, `living_metal`, `zro`, `dark_matter`, `nanites`

### Planet Resources

```python
# Get empire with resource data
player = save.get_player_empire()

# Check planet resources
for planet in player.planets:
    if planet.resources:
        # Production
        print(f"Produces energy: {planet.resources.produces.energy}")
        
        # Consumption
        print(f"Consumes energy: {planet.resources.upkeep.energy}")
        
        # Net (production - consumption)
        net = planet.resources.net
        print(f"Net energy: {net.energy:+.1f}")
        
        # Total research across all fields
        print(f"Research: {net.total_research:.1f}")
        
        # Identify deficits
        deficits = planet.resources.get_deficit_resources()
        if deficits:
            print(f"Resource deficits: {deficits}")
```

### System-Level Economics

Aggregate resources for an entire star system:

```python
# Query by system name
econ = save.get_system_economy_by_name("Sol")

if econ:
    print(f"System: {econ.system_name}")
    print(f"Planets: {econ.planet_count}")
    print(f"Total pops: {econ.total_pops}")
    
    # Net resources for the entire system
    net = econ.resources.net
    print(f"Energy: {net.energy:+.1f}")
    print(f"Minerals: {net.minerals:+.1f}")
    print(f"Food: {net.food:+.1f}")
    
    # Check for deficits
    deficits = econ.resources.get_deficit_resources()
    surpluses = econ.resources.get_surplus_resources()
    
# Get all systems with your planets
all_systems = save.get_all_system_economies()

# Sort by population
all_systems.sort(key=lambda e: e.total_pops, reverse=True)

# Calculate empire totals
total_energy = sum(e.resources.net.energy for e in all_systems)
total_research = sum(e.resources.net.total_research for e in all_systems)
```

### Resource Balance Properties

- `resources.produces` - ResourceAmount for production
- `resources.upkeep` - ResourceAmount for consumption
- `resources.net` - Calculated net (produces - upkeep)
- `resources.get_deficit_resources()` - Dict of negative net resources
- `resources.get_surplus_resources()` - Dict of positive net resources
- `resources.is_energy_positive` - True if net energy > 0
- `resources.is_mineral_positive` - True if net minerals > 0
- `resources.is_food_positive` - True if net food > 0

### ⚠️ Important Limitations

**The economic data parsed from planets represents BASE production/consumption only.**

What's **included**:
- Planet-level job production and upkeep
- District resource generation
- Building effects on production
- Pop resource consumption

What's **NOT included** (and can cause significant discrepancies with in-game totals):
- **Empire-wide multipliers** from technology, traditions, and edicts
- **Starbase production** from modules and buildings
- **Megastructure output** (Matter Decompressor, Dyson Sphere, etc.)
- **Trade policy conversions** (trade value converted to other resources)
- **Special resource sources** (events, relics, etc.)
- **Market auto-trades** and manual transactions

**Example**: A save file showing -280 minerals/month from planets might display +200 minerals/month in-game due to empire bonuses and other sources.

**Recommendation**: Use the library's economic data for:
- ✅ Comparative analysis between your planets/systems
- ✅ Identifying which planets are net producers vs consumers
- ✅ Finding resource specialization opportunities
- ✅ Detecting relative deficits and surpluses

Do NOT use for:
- ❌ Calculating exact empire-wide income (will be inaccurate)
- ❌ Matching in-game economy screen totals (missing too many sources)

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
