# Stellaris Save Parser

A Python library for parsing and analyzing Stellaris save files.

## Features

- Parse Stellaris `.sav` files (Clausewitz engine format)
- Extract empire, planet, and leader data
- Analyze governor assignments and traits
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

- `basic_analysis.py` - Basic save file analysis
- `governor_optimization.py` - Governor assignment optimization
- `trait_analysis.py` - Leader trait analysis

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
Represents a colonized planet.

```python
planet = empire.planets[0]
print(f"{planet.name}: {planet.designation}, {planet.pops} pops")
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
