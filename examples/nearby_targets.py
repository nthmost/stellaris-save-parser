#!/usr/bin/env python3
"""
Find conquest targets NEAR your actual territory.

This script:
1. Finds YOUR systems
2. Looks at ADJACENT systems only
3. Identifies valuable targets within 1-2 jumps
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave

SAVE_PATH = os.path.expanduser(
    "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
    "blorgcommonality_-193568729/war is over for now.sav"
)

def main():
    print("="*80)
    print("NEARBY CONQUEST TARGETS")
    print("="*80)
    
    save = StellarisSave(SAVE_PATH)
    player = save.get_player_empire()
    galactic_map = save.get_galactic_map()
    
    print(f"\nYour empire: {len(player.planets)} planets")
    
    # Get YOUR systems
    your_systems = galactic_map.get_systems_by_owner('0')
    
    print(f"✓ You control {len(your_systems)} systems")
    
    if not your_systems:
        print("\n❌ Could not find your systems! Check save file.")
        return
    
    print(f"\nYour systems:")
    for sys in sorted(your_systems, key=lambda s: len(s.planet_ids), reverse=True):
        choke = " [CHOKEPOINT]" if sys.is_chokepoint else ""
        hub = " [HUB]" if sys.is_hub else ""
        print(f"  {sys.name:30} - {len(sys.planet_ids):2} planets, {sys.connection_count} connections{choke}{hub}")
    
    # Find ADJACENT systems (1 jump away)
    print("\n" + "="*80)
    print("ADJACENT SYSTEMS (1 jump from your territory)")
    print("="*80)
    
    your_system_ids = {sys.id for sys in your_systems}
    adjacent_system_ids = set()
    adjacent_to_your_system = {}  # maps adjacent system -> your border system names
    
    for your_sys in your_systems:
        for conn in your_sys.hyperlanes:
            neighbor_id = conn.to_system_id
            if neighbor_id not in your_system_ids:
                adjacent_system_ids.add(neighbor_id)
                if neighbor_id not in adjacent_to_your_system:
                    adjacent_to_your_system[neighbor_id] = []
                adjacent_to_your_system[neighbor_id].append(your_sys.name)
    
    print(f"\n{len(adjacent_system_ids)} systems adjacent to your borders")
    
    # Categorize adjacent systems
    adjacent_unclaimed = []
    adjacent_enemy = []
    adjacent_chokepoints = []
    adjacent_with_bypasses = []
    
    bypass_network = save.get_bypass_network()
    
    for adj_id in adjacent_system_ids:
        adj_sys = galactic_map.get_system(adj_id)
        if not adj_sys:
            continue
        
        # Check if it's a chokepoint
        is_chokepoint = adj_sys.is_chokepoint
        
        # Check for bypasses
        has_bypass = False
        bypass_types = []
        for gateway in bypass_network.gateways:
            if gateway.system_id == adj_id:
                has_bypass = True
                bypass_types.append("Gateway")
        for wormhole in bypass_network.wormholes:
            if wormhole.system_id == adj_id:
                has_bypass = True
                bypass_types.append(f"Wormhole (→{wormhole.linked_to})")
        for relay in bypass_network.hyper_relays:
            if relay.system_id == adj_id:
                has_bypass = True
                bypass_types.append("Hyper Relay")
        
        if adj_sys.owner_id:
            adjacent_enemy.append((adj_sys, is_chokepoint, bypass_types))
        else:
            adjacent_unclaimed.append((adj_sys, is_chokepoint, bypass_types))
        
        if is_chokepoint:
            adjacent_chokepoints.append((adj_sys, adjacent_to_your_system[adj_id]))
        
        if has_bypass:
            adjacent_with_bypasses.append((adj_sys, bypass_types, adjacent_to_your_system[adj_id]))
    
    # Display results
    print(f"  Unclaimed: {len(adjacent_unclaimed)}")
    print(f"  Enemy-controlled: {len(adjacent_enemy)}")
    print(f"  Chokepoints: {len(adjacent_chokepoints)}")
    print(f"  With bypasses: {len(adjacent_with_bypasses)}")
    
    # High-value targets
    if adjacent_with_bypasses:
        print("\n🎯 HIGHEST PRIORITY: Systems with Bypasses (adjacent)")
        print("-" * 80)
        for sys, bypass_types, borders in sorted(adjacent_with_bypasses, key=lambda x: len(x[0].planet_ids), reverse=True):
            owner_str = f"Enemy (Country {sys.owner_id})" if sys.owner_id else "UNCLAIMED"
            print(f"\n• {sys.name}")
            print(f"  Status: {owner_str}")
            print(f"  Bypasses: {', '.join(bypass_types)}")
            print(f"  Planets: {len(sys.planet_ids)}")
            print(f"  Connections: {sys.connection_count}")
            print(f"  Adjacent to your: {', '.join(borders[:3])}")
            if not sys.owner_id:
                print(f"  ⭐⭐⭐⭐ NO WAR NEEDED - Just claim and colonize!")
            else:
                print(f"  ⚔️  Conquest required")
    
    if adjacent_chokepoints:
        print("\n🎯 HIGH PRIORITY: Chokepoint Systems (adjacent)")
        print("-" * 80)
        enemy_chokepoints = [(s, b) for s, b in adjacent_chokepoints if s.owner_id]
        unclaimed_chokepoints = [(s, b) for s, b in adjacent_chokepoints if not s.owner_id]
        
        if unclaimed_chokepoints:
            print("\nUNCLAIMED Chokepoints:")
            for (sys, borders) in sorted(unclaimed_chokepoints, key=lambda x: len(x[0].planet_ids), reverse=True)[:10]:
                print(f"\n• {sys.name}")
                print(f"  Planets: {len(sys.planet_ids)}")
                print(f"  Connections: {sys.connection_count}")
                print(f"  Adjacent to: {', '.join(borders[:2])}")
                print(f"  ⭐⭐⭐ NO WAR NEEDED - Easy expansion!")
        
        if enemy_chokepoints:
            print("\nENEMY Chokepoints:")
            for (sys, borders) in sorted(enemy_chokepoints, key=lambda x: len(x[0].planet_ids), reverse=True)[:10]:
                print(f"\n• {sys.name}")
                print(f"  Owner: Country {sys.owner_id}")
                print(f"  Planets: {len(sys.planet_ids)}")
                print(f"  Connections: {sys.connection_count}")
                print(f"  Adjacent to: {', '.join(borders[:2])}")
                print(f"  ⚔️  Conquest required")
    
    # Show unclaimed adjacent systems with planets
    systems_with_planets = [(s, is_choke, bypasses) for s, is_choke, bypasses in adjacent_unclaimed if len(s.planet_ids) > 0]
    if systems_with_planets:
        print("\n📋 Other Unclaimed Adjacent Systems (with planets)")
        print("-" * 80)
        for sys, is_choke, bypasses in sorted(systems_with_planets, key=lambda x: len(x[0].planet_ids), reverse=True)[:15]:
            borders = adjacent_to_your_system[sys.id]
            choke_str = " [CHOKEPOINT]" if is_choke else ""
            bypass_str = f" [{', '.join(bypasses)}]" if bypasses else ""
            print(f"  {sys.name:30} - {len(sys.planet_ids):2} planets, {sys.connection_count} connections{choke_str}{bypass_str}")
            print(f"    Adjacent to: {', '.join(borders[:2])}")
    
    # Resource priority
    budget = save.get_player_budget()
    if budget:
        print("\n" + "="*80)
        print("RESOURCE PRIORITY GUIDANCE")
        print("="*80)
        print(f"\nYour current economy:")
        print(f"  Food:     {budget.net_food:+8.1f}")
        print(f"  Minerals: {budget.net_minerals:+8.1f}")
        print(f"  Energy:   {budget.net_energy:+8.1f}")
        print(f"  Research: {budget.total_research:8.1f}")
        
        print("\n💡 What to prioritize:")
        if budget.net_food < 50:
            print("  ⚠️  LOW FOOD - Look for agricultural systems")
            print("     • Check adjacent systems for Gaia worlds or farming planets")
            print("     • Build hydroponics bays on starbases")
        if budget.net_minerals < 200:
            print("  ⚠️  LOW MINERALS - Look for mineral-rich deposits")
            print("     • Prioritize systems with asteroid belts")
            print("     • Build mining stations on rich deposits")
        if budget.net_energy < 100:
            print("  ⚠️  LOW ENERGY - Build energy production")
            print("     • Solar panel networks on starbases")
            print("     • Dyson spheres if available")
    
    # Summary
    print("\n" + "="*80)
    print("QUICK SUMMARY")
    print("="*80)
    
    print(f"\n✓ You control {len(your_systems)} systems")
    print(f"✓ {len(adjacent_system_ids)} systems are 1 jump away")
    print(f"  - {len(adjacent_unclaimed)} unclaimed")
    print(f"  - {len(adjacent_enemy)} enemy-controlled")
    
    if adjacent_with_bypasses:
        unclaimed_bypasses = sum(1 for s, _, _ in adjacent_with_bypasses if not s.owner_id)
        print(f"\n🥇 {len(adjacent_with_bypasses)} systems with bypasses adjacent")
        if unclaimed_bypasses > 0:
            print(f"   ({unclaimed_bypasses} UNCLAIMED - grab these NOW!)")
    
    if unclaimed_chokepoints:
        print(f"🥈 {len(unclaimed_chokepoints)} unclaimed chokepoints adjacent - Easy expansion!")
    
    if enemy_chokepoints:
        print(f"🥉 {len(enemy_chokepoints)} enemy chokepoints adjacent - Strategic conquest targets")
    
    if systems_with_planets:
        print(f"📋 {len(systems_with_planets)} other unclaimed systems with colonizable planets nearby")
    
    print(f"\n💡 Expand into unclaimed adjacent systems before enemies claim them!")


if __name__ == '__main__':
    main()
