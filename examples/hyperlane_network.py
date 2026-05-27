#!/usr/bin/env python3
"""
Example: Analyze hyperlane network and territory.

Demonstrates:
- Loading the galactic map
- Finding player-controlled systems
- Analyzing hyperlane connections
- Identifying strategic chokepoints
- Finding border systems
- Mapping territory layout
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from stellaris_save_parser.save import StellarisSave


def analyze_hyperlane_network(save_path: str):
    """Analyze the hyperlane network and strategic positions."""
    
    # Load the save
    save = StellarisSave(save_path)
    player = save.get_player_empire()
    
    print(f"=== HYPERLANE NETWORK ANALYSIS ===")
    print(f"Empire: {player.name}")
    print(f"Game Date: {player.game_date}")
    print()
    
    # Load galactic map (filter to player's territory)
    player_country_id = save.get_player_country_id()
    print("Loading galactic map...")
    galactic_map = save.get_galactic_map(filter_country_id=player_country_id)
    
    print(f"Found {len(galactic_map.systems)} systems in player territory")
    print()
    
    # Calculate territory stats
    stats = galactic_map.calculate_territory_stats(player_country_id)
    
    print(f"=== TERRITORY STATISTICS ===")
    print(f"Total systems: {stats['total_systems']}")
    print(f"Total planets: {stats['total_planets']}")
    print(f"Border systems: {stats['border_systems']}")
    print(f"Chokepoints: {stats['chokepoints']}")
    print(f"Hub systems (5+ connections): {stats['hubs']}")
    print(f"Average connections per system: {stats['avg_connections']:.1f}")
    print()
    
    # Find and display chokepoints
    chokepoints = galactic_map.find_chokepoints(player_country_id)
    if chokepoints:
        print(f"=== STRATEGIC CHOKEPOINTS ===")
        print(f"Systems with 1-2 hyperlane connections (strategic bottlenecks):\n")
        
        for system in sorted(chokepoints, key=lambda s: s.connection_count)[:10]:
            print(f"{system.name} ({system.connection_count} connection{'s' if system.connection_count > 1 else ''})")
            
            # Show connected systems
            connected = galactic_map.get_connected_systems(system)
            for neighbor in connected:
                marker = ""
                if neighbor.id in [s.id for s in chokepoints]:
                    marker = " [ALSO CHOKEPOINT]"
                print(f"  → {neighbor.name}{marker}")
        
        print()
    
    # Find and display border systems
    border = galactic_map.find_border_systems(player_country_id)
    if border:
        print(f"=== BORDER SYSTEMS ===")
        print(f"Systems connecting to foreign territory:\n")
        
        for system in sorted(border, key=lambda s: s.name)[:15]:
            print(f"{system.name} ({system.connection_count} connections)")
            
            # Show which neighbors are foreign
            player_system_ids = {s.id for s in galactic_map.systems}
            connected = galactic_map.get_connected_systems(system)
            
            foreign_count = 0
            for neighbor in connected:
                if neighbor.id not in player_system_ids:
                    foreign_count += 1
                    print(f"  ⚠️  → {neighbor.name} [FOREIGN]")
            
            if foreign_count > 1:
                print(f"  💡 Multiple foreign connections - high priority defense")
        
        print()
    
    # Find hub systems
    hubs = [s for s in galactic_map.systems if s.is_hub]
    if hubs:
        print(f"=== HUB SYSTEMS ===")
        print(f"Major junction systems (5+ connections):\n")
        
        for system in sorted(hubs, key=lambda s: s.connection_count, reverse=True)[:10]:
            print(f"{system.name} ({system.connection_count} connections)")
            print(f"  Coordinates: ({system.x:.1f}, {system.y:.1f})")
            
            connected = galactic_map.get_connected_systems(system)
            conn_names = [n.name for n in connected[:5]]
            if len(connected) > 5:
                conn_names.append(f"... +{len(connected)-5} more")
            print(f"  Connects to: {', '.join(conn_names)}")
            print()
    
    # Show some detailed system info
    print(f"=== SAMPLE SYSTEM DETAILS ===")
    
    # Find home system
    home_planets = [p for p in player.planets if p.is_capital]
    if home_planets:
        home_planet_id = home_planets[0].id
        home_systems = galactic_map.find_systems_with_planets([home_planet_id])
        
        if home_systems:
            home = home_systems[0]
            print(f"\nHome System: {home.name}")
            print(f"  ID: {home.id}")
            print(f"  Coordinates: ({home.x:.1f}, {home.y:.1f})")
            print(f"  Star class: {home.star_class}")
            print(f"  Planets: {len(home.planet_ids)}")
            print(f"  Hyperlane connections: {home.connection_count}")
            
            # Show all connections with distances
            if home.hyperlanes:
                print(f"\n  Connected systems:")
                for hyperlane in home.hyperlanes:
                    neighbor = galactic_map.get_system(hyperlane.to_system_id)
                    if neighbor:
                        is_player = neighbor.id in [s.id for s in galactic_map.systems]
                        marker = "★" if is_player else "⚠️"
                        print(f"    {marker} {neighbor.name} (distance: {hyperlane.length:.1f})")
    
    # Distance calculations
    if len(galactic_map.systems) >= 2:
        print(f"\n=== SAMPLE DISTANCE CALCULATIONS ===")
        system1 = galactic_map.systems[0]
        system2 = galactic_map.systems[-1]
        distance = system1.distance_to(system2)
        print(f"Distance from {system1.name} to {system2.name}: {distance:.1f} units")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python hyperlane_network.py <path_to_save_file>")
        sys.exit(1)
    
    save_path = sys.argv[1]
    analyze_hyperlane_network(save_path)
