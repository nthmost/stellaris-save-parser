#!/usr/bin/env python3
"""
Example: Analyze planet resources and district capacity.

Demonstrates:
- District slot usage and capacity
- Deposit resource analysis
- Special planet features
- Identifying expansion opportunities
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from stellaris_save_parser.save import StellarisSave


def analyze_planet_resources(save_path: str):
    """Analyze planet resources and districts."""
    
    # Load the save
    save = StellarisSave(save_path)
    player = save.get_player_empire()
    
    print(f"=== PLANET RESOURCE ANALYSIS ===")
    print(f"Empire: {player.name}")
    print(f"Game Date: {player.game_date}")
    print(f"Total Planets: {len(player.planets)}")
    print()
    
    # Summary statistics
    total_slots = sum(p.size for p in player.planets)
    used_slots = sum(p.total_districts for p in player.planets)
    
    print(f"=== DISTRICT CAPACITY SUMMARY ===")
    print(f"Total district slots: {total_slots}")
    print(f"Used slots: {used_slots} ({used_slots/total_slots*100:.1f}%)")
    print(f"Available slots: {total_slots - used_slots}")
    print()
    
    # District type totals
    from collections import Counter
    all_districts = Counter()
    for planet in player.planets:
        for dtype, count in planet.districts.items():
            all_districts[dtype] += count
    
    print(f"=== EMPIRE-WIDE DISTRICT BREAKDOWN ===")
    for dtype, count in sorted(all_districts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dtype}: {count}")
    print()
    
    # Detailed planet analysis
    print(f"=== DETAILED PLANET ANALYSIS ===")
    for planet in sorted(player.planets, key=lambda p: p.name):
        print(f"\n{planet.name}")
        print(f"  Location: {planet.planet_class} (size {planet.size})")
        print(f"  Designation: {planet.designation}")
        print(f"  Population: {planet.pops:,}")
        print(f"  Governor: {planet.governor.name if planet.governor else 'None'}")
        
        # District usage
        print(f"\n  District Capacity: {planet.total_districts}/{planet.size} slots used " +
              f"({planet.district_slots_used_percent:.1f}%)")
        if planet.available_district_slots > 0:
            print(f"    → {planet.available_district_slots} slots available for expansion")
        
        if planet.districts:
            print(f"\n  Built Districts:")
            for dtype, count in sorted(planet.districts.items()):
                clean_name = dtype.replace('district_', '').title()
                print(f"    {clean_name}: {count}")
        
        # Deposit analysis
        if planet.deposits:
            deposit_summary = planet.get_deposit_summary()
            print(f"\n  Resource Deposits ({len(planet.deposits)} total):")
            
            resource_labels = {
                'minerals': 'Minerals',
                'energy': 'Energy',
                'food': 'Food/Agriculture',
                'research': 'Research',
                'strategic': 'Strategic Resources',
                'other': 'Other'
            }
            
            for category, label in resource_labels.items():
                count = deposit_summary[category]
                if count > 0:
                    print(f"    {label}: {count}")
            
            # Show some sample deposits
            if len(planet.deposits) <= 5:
                print(f"    Deposits: {', '.join(planet.deposits)}")
        
        # Special features
        if planet.has_special_deposits:
            print(f"\n  ⭐ SPECIAL: This planet has unique/strategic deposits!")
        
        if planet.planet_class == 'pc_gaia':
            print(f"\n  ⭐ SPECIAL: Gaia world - ideal for all species!")
        
        # Suggestions
        suggestions = []
        
        if planet.available_district_slots >= 10:
            suggestions.append(f"Large expansion capacity ({planet.available_district_slots} slots)")
        
        if planet.designation == 'col_generator' and deposit_summary.get('energy', 0) == 0:
            suggestions.append("Generator world but no energy deposits detected")
        
        if planet.designation == 'col_farming' and deposit_summary.get('food', 0) == 0:
            suggestions.append("Farming world but limited agriculture deposits")
        
        if planet.designation == 'col_mining' and deposit_summary.get('minerals', 0) == 0:
            suggestions.append("Mining world but no mineral deposits detected")
        
        if not planet.governor:
            suggestions.append("No governor assigned - production efficiency reduced")
        
        if suggestions:
            print(f"\n  💡 Suggestions:")
            for suggestion in suggestions:
                print(f"    • {suggestion}")
    
    # Find best expansion opportunities
    print(f"\n\n=== EXPANSION OPPORTUNITIES ===")
    expansion_candidates = sorted(
        player.planets,
        key=lambda p: p.available_district_slots,
        reverse=True
    )[:5]
    
    for planet in expansion_candidates:
        if planet.available_district_slots > 0:
            print(f"\n{planet.name}:")
            print(f"  {planet.available_district_slots} available slots (size {planet.size})")
            print(f"  Designation: {planet.designation}")
            
            deposit_summary = planet.get_deposit_summary()
            resources = []
            if deposit_summary['minerals'] > 0:
                resources.append(f"{deposit_summary['minerals']} mineral")
            if deposit_summary['energy'] > 0:
                resources.append(f"{deposit_summary['energy']} energy")
            if deposit_summary['food'] > 0:
                resources.append(f"{deposit_summary['food']} food")
            
            if resources:
                print(f"  Available resources: {', '.join(resources)}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python planet_resources.py <path_to_save_file>")
        sys.exit(1)
    
    save_path = sys.argv[1]
    analyze_planet_resources(save_path)
