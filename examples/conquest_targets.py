#!/usr/bin/env python3
"""
Conquest Target Analysis

Identifies the most valuable systems to conquer based on:
- Strategic chokepoints
- Resource-rich deposits (mining/research stations)
- Bypass access (gateways, wormholes)
- Proximity to your borders
- High-quality planets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave
from stellaris_save_parser.parser import load_gamestate, find_section
import re

# Path to your save file
SAVE_PATH = os.path.expanduser(
    "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
    "blorgcommonality_-193568729/war is over for now.sav"
)

def main():
    print("="*80)
    print("CONQUEST TARGET ANALYSIS")
    print("="*80)
    
    save = StellarisSave(SAVE_PATH)
    player = save.get_player_empire()
    
    print(f"\nYour empire: {len(player.planets)} planets")
    
    # Current economy
    budget = save.get_player_budget()
    if budget:
        print("\nCurrent economy:")
        print(f"  Energy:   {budget.net_energy:+.1f}")
        print(f"  Minerals: {budget.net_minerals:+.1f}")
        print(f"  Food:     {budget.net_food:+.1f}")
        print(f"  Research: {budget.total_research:.1f}")
        
        # Identify weaknesses
        print("\nResource priorities for conquest:")
        if budget.net_minerals < 100:
            print("  ⚠️  LOW MINERALS - Prioritize mineral-rich systems")
        if budget.net_food < 50:
            print("  ⚠️  LOW FOOD - Prioritize agricultural worlds")
        if budget.total_research < 500:
            print("  ⚠️  LOW RESEARCH - Prioritize systems with research deposits")
    
    # Get galactic map
    print("\n" + "="*80)
    print("GALACTIC OVERVIEW")
    print("="*80)
    
    galactic_map = save.get_galactic_map()
    
    # Count systems by owner
    owner_counts = {}
    for system in galactic_map.systems:
        owner = system.owner_id if system.owner_id else 'unclaimed'
        owner_counts[owner] = owner_counts.get(owner, 0) + 1
    
    player_systems = owner_counts.get('0', 0)
    unclaimed_systems = owner_counts.get('unclaimed', 0)
    enemy_systems = sum(v for k, v in owner_counts.items() if k not in ['0', 'unclaimed'])
    
    print(f"\nSystems in galaxy: {len(galactic_map.systems)}")
    print(f"  Your control: {player_systems}")
    print(f"  Unclaimed: {unclaimed_systems}")
    print(f"  Enemy control: {enemy_systems}")
    
    # STRATEGIC TARGETS: Chokepoints
    print("\n" + "="*80)
    print("STRATEGIC CHOKEPOINTS")
    print("="*80)
    
    # Find all chokepoints in the galaxy
    all_chokepoints = []
    owners_found = set()
    
    for system in galactic_map.systems:
        if system.owner_id:
            owners_found.add(system.owner_id)
    
    # Get chokepoints for each owner
    chokepoint_systems = []
    for owner in owners_found:
        owner_choke = galactic_map.find_chokepoints(owner)
        chokepoint_systems.extend(owner_choke)
    
    # Also find unclaimed chokepoints (systems with 1-2 connections and no owner)
    for system in galactic_map.systems:
        if not system.owner_id and system.is_chokepoint:
            chokepoint_systems.append(system)
    
    player_chokepoints = [s for s in chokepoint_systems if s.owner_id == '0']
    enemy_chokepoints = [s for s in chokepoint_systems if s.owner_id and s.owner_id != '0']
    unclaimed_chokepoints = [s for s in chokepoint_systems if not s.owner_id]
    
    print(f"\nTotal chokepoints: {len(chokepoint_systems)}")
    print(f"  You control: {len(player_chokepoints)}")
    print(f"  Enemies control: {len(enemy_chokepoints)}")
    print(f"  Unclaimed: {len(unclaimed_chokepoints)}")
    
    # Find enemy chokepoints adjacent to your territory
    print("\n🎯 HIGH-VALUE TARGETS: Enemy chokepoints near your borders")
    print("-" * 80)
    
    border_enemy_chokepoints = []
    for system in enemy_chokepoints:
        # Check if any neighbor is yours
        for conn in system.hyperlanes:
            neighbor = galactic_map.get_system(conn.to_system_id)
            if neighbor and neighbor.owner_id == '0':
                border_enemy_chokepoints.append(system)
                break
    
    if border_enemy_chokepoints:
        border_enemy_chokepoints.sort(key=lambda s: s.connection_count, reverse=True)
        
        for i, system in enumerate(border_enemy_chokepoints[:10], 1):
            print(f"\n{i}. {system.name}")
            print(f"   Owner: Country {system.owner_id}")
            print(f"   Connections: {system.connection_count} hyperlanes")
            print(f"   Strategic value: ⭐⭐⭐ Controls enemy access")
            
            # Check if it has bypasses
            bypass_network = save.get_bypass_network()
            bypasses_in_sys = [b for b in bypass_network.gateways if b.system_id == system.id]
            if bypasses_in_sys:
                print(f"   BONUS: Has gateway!")
    else:
        print("None found - no enemy chokepoints adjacent to your territory")
    
    # Unclaimed chokepoints
    if unclaimed_chokepoints:
        print("\n🎯 MEDIUM-VALUE TARGETS: Unclaimed chokepoints")
        print("-" * 80)
        
        # Find ones near your borders
        border_unclaimed = []
        for system in unclaimed_chokepoints:
            for conn in system.hyperlanes:
                neighbor = galactic_map.get_system(conn.to_system_id)
                if neighbor and neighbor.owner_id == '0':
                    border_unclaimed.append(system)
                    break
        
        if border_unclaimed:
            border_unclaimed.sort(key=lambda s: s.connection_count, reverse=True)
            
            for i, system in enumerate(border_unclaimed[:5], 1):
                print(f"\n{i}. {system.name}")
                print(f"   Connections: {system.connection_count} hyperlanes")
                print(f"   Strategic value: ⭐⭐ No war needed!")
    
    # BYPASS TARGETS
    print("\n" + "="*80)
    print("BYPASS NETWORK CONTROL")
    print("="*80)
    
    bypass_network = save.get_bypass_network()
    
    print(f"\nTotal bypasses:")
    print(f"  Wormholes: {len(bypass_network.wormholes)} pairs")
    print(f"  Gateways: {len(bypass_network.gateways)}")
    print(f"  Hyper Relays: {len(bypass_network.hyper_relays)}")
    
    # Count player-owned bypasses using system ownership
    player_bypass_network = bypass_network.filter_by_galactic_map(galactic_map, owner_id='0')
    
    print(f"\nYou control:")
    print(f"  {len(player_bypass_network.gateways)} gateways")
    print(f"  {len(player_bypass_network.hyper_relays)} hyper relays")
    
    # Find enemy gateways (in systems owned by others)
    enemy_gateways = []
    for gateway in bypass_network.gateways:
        system = galactic_map.get_system(gateway.system_id)
        if system and system.owner_id and system.owner_id != '0':
            enemy_gateways.append((gateway, system))
    
    if enemy_gateways:
        print(f"\n🎯 HIGH-VALUE TARGETS: Enemy gateways ({len(enemy_gateways)} total)")
        print("-" * 80)
        
        # Find ones near your borders
        border_gateways = []
        for gateway, system in enemy_gateways:
            # Check if adjacent to your territory
            for conn in system.hyperlanes:
                neighbor = galactic_map.get_system(conn.to_system_id)
                if neighbor and neighbor.owner_id == '0':
                    border_gateways.append((gateway, system))
                    break
        
        if border_gateways:
            for i, (gateway, system) in enumerate(border_gateways[:5], 1):
                print(f"\n{i}. {system.name}")
                print(f"   Owner: Country {system.owner_id}")
                print(f"   Strategic value: ⭐⭐⭐⭐ Gateway access!")
                print(f"   Network size: {len(gateway.connected_gateway_ids)} connected gateways")
        else:
            print("No enemy gateways adjacent to your territory")
    
    # Count wormholes by ownership (simplified - just count in player vs enemy systems)
    player_wormhole_systems = 0
    enemy_wormhole_systems = 0
    
    for wormhole in bypass_network.wormholes:
        system = galactic_map.get_system(wormhole.system_id)
        if system:
            if system.owner_id == '0':
                player_wormhole_systems += 1
            elif system.owner_id:
                enemy_wormhole_systems += 1
    
    print(f"\nWormhole systems:")
    print(f"  Your territory: {player_wormhole_systems}")
    print(f"  Enemy territory: {enemy_wormhole_systems}")
    
    if enemy_wormhole_systems > 0:
        print(f"\n💡 Note: Conquering systems with wormholes provides instant long-distance travel")
    
    # YOUR BORDERS
    print("\n" + "="*80)
    print("YOUR EXPANSION FRONTS")
    print("="*80)
    
    border_systems = galactic_map.find_border_systems('0')
    
    print(f"\nYou have {len(border_systems)} border systems (expansion/defense points)")
    
    if border_systems:
        # Find the most connected border systems
        border_systems.sort(key=lambda s: s.connection_count, reverse=True)
        
        print("\nYour most important border systems:")
        for i, system in enumerate(border_systems[:10], 1):
            print(f"  {i}. {system.name} - {system.connection_count} connections")
    
    # SUMMARY
    print("\n" + "="*80)
    print("CONQUEST PRIORITY SUMMARY")
    print("="*80)
    
    print("\n🥇 HIGHEST PRIORITY:")
    if border_enemy_chokepoints:
        print(f"   ✓ Enemy chokepoints on your border: {len(border_enemy_chokepoints)} found")
    if border_gateways:
        print(f"   ✓ Enemy gateways on your border: {len(border_gateways)} found")
    
    print("\n🥈 MEDIUM PRIORITY:")
    if enemy_wormhole_systems > 0:
        print(f"   ✓ Enemy wormhole systems: {enemy_wormhole_systems} found")
    if unclaimed_chokepoints:
        print(f"   ✓ Unclaimed chokepoints: {len(unclaimed_chokepoints)} available (no war needed!)")
    
    print("\n💡 RECOMMENDATION:")
    if budget:
        if budget.net_minerals < 100:
            print("   • Focus on systems with mineral deposits")
        if budget.total_research < 500:
            print("   • Prioritize systems with research deposits")
    
    print("   • Secure chokepoints first to control enemy access")
    print("   • Gateways provide strategic mobility")
    print("   • Claim unclaimed chokepoints before enemies do")


if __name__ == '__main__':
    main()
