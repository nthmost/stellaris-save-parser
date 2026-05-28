#!/usr/bin/env python3
"""
Check why you can't terraform and what you need to unlock it.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave
from stellaris_save_parser.parser import load_gamestate
import re

def check_terraforming(save_path):
    save = StellarisSave(save_path)
    player = save.get_player_empire()
    budget = save.get_player_budget()
    gamestate = load_gamestate(save_path)
    
    print("="*80)
    print("TERRAFORMING READINESS CHECK")
    print("="*80)
    
    # Check 1: Technology
    print("\n🔬 TECHNOLOGY CHECK")
    print("─"*80)
    
    has_climate_restoration = 'climate_restoration' in gamestate.lower()
    has_terrestrial_sculpting = 'terrestrial_sculpting' in gamestate.lower()
    
    if has_climate_restoration:
        print("  ✅ Climate Restoration - RESEARCHED")
        can_terraform_basic = True
    else:
        print("  ❌ Climate Restoration - NOT RESEARCHED")
        print("     This is the BASIC terraforming technology")
        print("     You CANNOT terraform without this!")
        can_terraform_basic = False
    
    if has_terrestrial_sculpting:
        print("  ✅ Terrestrial Sculpting - RESEARCHED")
        print("     (Advanced terraforming options available)")
    else:
        print("  ⚠️  Terrestrial Sculpting - NOT RESEARCHED")
        print("     (Only basic terraforming available)")
    
    # Check 2: Resources
    print("\n💰 RESOURCE CHECK")
    print("─"*80)
    
    # Try to find energy stockpile
    energy_stockpile = None
    if gamestate:
        country_section_start = gamestate.find('country=')
        if country_section_start > 0:
            country_chunk = gamestate[country_section_start:country_section_start + 1000000]
            player_start = country_chunk.find('\n\t0=\t{')
            if player_start > 0:
                player_chunk = country_chunk[player_start:player_start + 100000]
                
                # Look for energy stockpile
                energy_match = re.search(r'modules=\s*\{.*?energy=\s*([\d.]+)', player_chunk, re.DOTALL)
                if energy_match:
                    energy_stockpile = float(energy_match.group(1))
    
    terraform_cost = 5000  # Base cost
    
    if energy_stockpile is not None:
        print(f"  Energy Stockpile: {energy_stockpile:.0f}")
        
        if energy_stockpile >= terraform_cost:
            print(f"  ✅ Enough energy to terraform (need ~{terraform_cost})")
            has_resources = True
        else:
            print(f"  ❌ Not enough energy to terraform")
            print(f"     Need: ~{terraform_cost}, Have: {energy_stockpile:.0f}")
            print(f"     Deficit: {terraform_cost - energy_stockpile:.0f}")
            has_resources = False
    else:
        print(f"  ⚠️  Could not determine energy stockpile")
        has_resources = False
    
    if budget:
        print(f"\n  Monthly Energy Income: {budget.net_energy:+.1f}")
        if energy_stockpile is not None and budget.net_energy > 0:
            months_to_save = (terraform_cost - energy_stockpile) / budget.net_energy
            if months_to_save > 0:
                years = months_to_save / 12
                print(f"  Time to save {terraform_cost}: ~{months_to_save:.0f} months ({years:.1f} years)")
    
    # Check 3: Ascension Perks
    print("\n🌟 ASCENSION PERKS")
    print("─"*80)
    
    has_world_shaper = 'ap_world_shaper' in gamestate
    
    if has_world_shaper:
        print("  ✅ World Shaper - UNLOCKED")
        print("     -25% terraform cost and time")
        print("     +2 max terraforming candidates")
        terraform_cost = int(terraform_cost * 0.75)
    else:
        print("  ⚠️  World Shaper - NOT UNLOCKED")
        print("     (Not required, but very helpful)")
    
    # Check 4: Candidate Planets
    print("\n🌍 CANDIDATE PLANETS")
    print("─"*80)
    
    terraformable_types = {
        'pc_desert', 'pc_arid', 'pc_savannah',
        'pc_tundra', 'pc_arctic', 'pc_alpine',
        'pc_tropical', 'pc_continental', 'pc_ocean',
    }
    
    candidates = []
    for planet in player.planets:
        if planet.planet_class in terraformable_types:
            candidates.append(planet)
    
    print(f"  You have {len(candidates)} planets that CAN be terraformed:")
    
    for planet in candidates[:5]:
        print(f"    • {planet.name:30} ({planet.planet_class})")
    
    if len(candidates) > 5:
        print(f"    ... and {len(candidates) - 5} more")
    
    # Final verdict
    print("\n" + "="*80)
    print("📋 VERDICT")
    print("="*80)
    
    if can_terraform_basic and has_resources:
        print("\n✅ YOU CAN TERRAFORM!")
        print("\nSteps:")
        print("  1. Select a planet you want to terraform")
        print("  2. Click 'Decisions' button")
        print("  3. Find 'Terraform to...' options")
        print("  4. Choose target planet type (Continental recommended)")
        print("  5. Click to start terraforming")
        print("  6. Assign construction ship if needed")
        print(f"\nCost: ~{terraform_cost} energy, ~10-20 years")
    
    elif can_terraform_basic and not has_resources:
        print("\n⚠️  YOU HAVE THE TECH BUT NOT ENOUGH ENERGY")
        print("\nYou need to save up more energy credits.")
        print(f"  Need: {terraform_cost}")
        print(f"  Have: {energy_stockpile:.0f}" if energy_stockpile else "  Have: Unknown")
        
        if budget and budget.net_energy > 0:
            print(f"\nWith your current income (+{budget.net_energy:.1f}/month):")
            months = (terraform_cost - (energy_stockpile or 0)) / budget.net_energy
            print(f"  You can terraform in ~{months:.0f} months ({months/12:.1f} years)")
        
        print("\nWays to get energy faster:")
        print("  • Build Generator Districts on planets")
        print("  • Add Solar Panel Networks to starbases")
        print("  • Sell excess resources on Galactic Market")
        print("  • Reduce energy expenses (disable buildings if needed)")
    
    elif not can_terraform_basic:
        print("\n❌ YOU CANNOT TERRAFORM YET")
        print("\nYou need to research 'Climate Restoration' technology first.")
        print("\n📚 How to get it:")
        print("  1. Open Research screen (F6)")
        print("  2. Go to SOCIETY research (green tab)")
        print("  3. Look for 'Climate Restoration' card")
        print("  4. Research it (~24-48 months)")
        
        print("\nRequirements:")
        print("  • Tier 2 technology")
        print("  • Prerequisites: New Worlds or Galactic Administration")
        print("  • Must have researched ~6 Tier 1 society techs")
        
        print("\nIf you don't see it:")
        print("  • Research other Society techs to unlock it")
        print("  • Tech draw is semi-random, might take a few draws")
        print("  • Keep researching society techs until it appears")
        
        if energy_stockpile and energy_stockpile < terraform_cost:
            print(f"\n💡 Also save up energy! You'll need {terraform_cost} (you have {energy_stockpile:.0f})")
    
    # Reality check
    if not can_terraform_basic:
        print("\n" + "="*80)
        print("💭 REALITY CHECK")
        print("="*80)
        print("\nTerraforming is a mid-late game feature.")
        print("It's expensive, slow, and usually not essential.")
        
        print(f"\nYour empire status:")
        print(f"  • {len(player.planets)} colonized planets (good!)")
        print(f"  • {sum(p.pops for p in player.planets)} total pops")
        
        if budget:
            print(f"  • Consumer goods: {budget.net_consumer_goods:+.1f}/month")
            print(f"  • Food: {budget.net_food:+.1f}/month")
            
            if budget.net_consumer_goods < 0 or budget.net_food < 0:
                print("\n⚠️  You have active resource crises!")
                print("    Focus on fixing your economy BEFORE terraforming.")
        
        print("\nTerraforming priorities come AFTER:")
        print("  1. Stable economy (no deficits)")
        print("  2. Good military (can defend borders)")
        print("  3. Tech advantage (competitive research)")
        print("  4. Strategic expansion (colonizing good planets)")
        print("\nDon't rush it! Terraform when you're rich and stable. 😊")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        save_path = sys.argv[1]
    else:
        save_path = os.path.expanduser(
            "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
            "blorgcommonality_-193568729/consumer goods crisis.sav"
        )
    
    check_terraforming(save_path)
