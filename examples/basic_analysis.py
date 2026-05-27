#!/usr/bin/env python3
"""
Basic Stellaris save file analysis example.

This script shows how to load a save file and extract basic information.
"""

import sys
from stellaris_save_parser import StellarisSave

def main():
    if len(sys.argv) < 2:
        print("Usage: python basic_analysis.py <path_to_save_file.sav>")
        sys.exit(1)
    
    save_path = sys.argv[1]
    
    print("Loading save file...")
    save = StellarisSave(save_path)
    
    print(f"Save: {save.save_name}")
    print(f"Date: {save.game_date}")
    print()
    
    # Get player empire
    empire = save.get_player_empire()
    
    print("="*80)
    print(f"EMPIRE: {empire.name}")
    print("="*80)
    print()
    
    # Basic statistics
    print("STATISTICS")
    print("-"*80)
    print(f"Total Planets: {len(empire.planets)}")
    print(f"Total Leaders: {len(empire.leaders)}")
    print(f"  - Officials: {len(empire.officials)}")
    print(f"  - Scientists: {len(empire.scientists)}")
    print(f"  - Commanders: {len(empire.commanders)}")
    print()
    
    # Planet information
    print("PLANETS")
    print("-"*80)
    
    # Sort by population
    sorted_planets = sorted(empire.planets, key=lambda p: p.pops, reverse=True)
    
    for planet in sorted_planets[:10]:  # Show top 10
        gov_info = f"Gov: {planet.governor.name}" if planet.governor else "NO GOVERNOR"
        print(f"{planet.name:30} {planet.designation:20} {planet.pops:5} pops | {gov_info}")
    
    if len(empire.planets) > 10:
        print(f"... and {len(empire.planets) - 10} more planets")
    
    print()
    
    # Planet specialization
    print("PLANET SPECIALIZATION")
    print("-"*80)
    analysis = empire.analyze_governor_assignments()
    stats = analysis['statistics']
    
    print(f"Generator/Energy Worlds: {stats['generator_worlds']}")
    print(f"Farming/Food Worlds: {stats['farming_worlds']}")
    print(f"Industrial/Forge Worlds: {stats['industrial_worlds']}")
    print(f"Mining Worlds: {stats['mining_worlds']}")
    print(f"Research Worlds: {stats['research_worlds']}")
    print(f"⚠️  Unspecialized: {stats['unspecialized']}")
    print()
    
    # Governor assignments
    print("GOVERNOR STATUS")
    print("-"*80)
    print(f"Planets with governors: {stats['planets_with_governors']}/{stats['total_planets']}")
    print(f"Unassigned officials: {stats['unassigned_officials']}")
    
    if analysis['mismatches']:
        print(f"\n⚠️  Found {len(analysis['mismatches'])} trait mismatches:")
        for mismatch in analysis['mismatches'][:5]:
            leader = mismatch['leader']
            planet = mismatch['planet']
            print(f"  - {leader.name} on {planet.name} ({planet.designation})")
            print(f"    Suggestion: {mismatch['suggestion']}")
    
    print()
    
    # Show all officials
    print("ALL OFFICIALS")
    print("-"*80)
    
    # Sort by level
    sorted_officials = sorted(empire.officials, key=lambda l: l.level, reverse=True)
    
    for official in sorted_officials:
        # Find what planet they're governing
        governing = None
        for planet in empire.planets:
            if planet.governor_id == official.id:
                governing = planet
                break
        
        if governing:
            location = f"→ {governing.name} ({governing.designation})"
        else:
            location = "UNASSIGNED"
        
        print(f"\n{official.name} (Level {official.level}) {location}")
        
        if official.traits:
            from stellaris_save_parser import categorize_trait, get_trait_description
            
            print("  Traits:")
            for trait in official.traits:
                category_desc = get_trait_description(trait)
                print(f"    • {trait}: {category_desc}")
    
    print()

if __name__ == "__main__":
    main()
