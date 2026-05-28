#!/usr/bin/env python3
"""
Analyze governor assignments and suggest optimizations.
Helps you assign the right governors to the right planets for maximum production.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave

# Trait categories and their bonuses
TRAIT_BONUSES = {
    # Industrial/Production traits
    'industrialist': ('Industrial', '+15% industrial output', ['consumer_goods', 'alloys']),
    'industrial_economist': ('Industrial', '+15% industrial output', ['consumer_goods', 'alloys']),
    'artisan': ('Artisan', '+10% consumer goods', ['consumer_goods']),
    'industrial': ('Industrial', '+10% industrial output', ['consumer_goods', 'alloys']),
    
    # Resource production traits
    'expertise_materials': ('Materials Expert', '+15% mining output', ['minerals']),
    'iron_fist': ('Iron Fist', '+10% mineral output', ['minerals']),
    'miner': ('Miner', '+10% mineral output', ['minerals']),
    
    'engineer': ('Engineer', '+10% energy output', ['energy']),
    'spark_of_genius': ('Genius', '+15% energy output', ['energy']),
    
    'rural': ('Rural', '+15% food output', ['food']),
    'agrarian': ('Agrarian', '+10% food output', ['food']),
    
    # Research traits
    'expertise_biology': ('Biology', '+15% society research', ['research']),
    'expertise_physics': ('Physics', '+15% physics research', ['research']),
    'expertise_materials': ('Materials', '+15% engineering research', ['research']),
    'maniacal': ('Maniacal', '+5% research speed', ['research']),
    
    # Economic/trade traits (NOT production)
    'entrepreneur': ('Entrepreneur', '+10% trade value', ['trade']),
    'thrifty': ('Thrifty', '+5% trade value', ['trade']),
}

PLANET_TYPES = {
    'col_factory': 'Factory (Consumer Goods)',
    'col_foundry': 'Foundry (Alloys)',
    'col_industrial': 'Industrial',
    'col_mining': 'Mining (Minerals)',
    'col_generator': 'Generator (Energy)',
    'col_farming': 'Farming (Food)',
    'col_research': 'Research',
    'col_capital': 'Capital',
}


def categorize_trait(trait_name):
    """Determine what a trait is good for."""
    trait_lower = trait_name.lower()
    
    for key, (category, bonus, resources) in TRAIT_BONUSES.items():
        if key in trait_lower:
            return (category, bonus, resources)
    
    # Generic detection
    if 'industrial' in trait_lower or 'artisan' in trait_lower:
        return ('Industrial', 'Production bonus', ['consumer_goods', 'alloys'])
    elif 'miner' in trait_lower or 'materials' in trait_lower:
        return ('Mining', 'Mineral bonus', ['minerals'])
    elif 'engineer' in trait_lower or 'energy' in trait_lower:
        return ('Energy', 'Energy bonus', ['energy'])
    elif 'rural' in trait_lower or 'agrar' in trait_lower or 'farm' in trait_lower:
        return ('Farming', 'Food bonus', ['food'])
    elif 'research' in trait_lower or 'scientist' in trait_lower:
        return ('Research', 'Research bonus', ['research'])
    elif 'entrepreneur' in trait_lower or 'trade' in trait_lower:
        return ('Trade', 'Trade value bonus', ['trade'])
    
    return (None, None, [])


def analyze_governors(save_path):
    save = StellarisSave(save_path)
    player = save.get_player_empire()
    budget = save.get_player_budget()
    
    print("="*80)
    print("GOVERNOR OPTIMIZATION ANALYZER")
    print("="*80)
    
    # Get all governors
    governors = [l for l in player.leaders if l.leader_class == 'official']
    
    print(f"\nYour empire has {len(governors)} governors (officials)")
    
    # Categorize governors by specialty
    industrial_govs = []
    mining_govs = []
    energy_govs = []
    farming_govs = []
    research_govs = []
    trade_govs = []
    generic_govs = []
    
    for gov in governors:
        specialties = set()
        for trait in gov.traits:
            category, bonus, resources = categorize_trait(trait)
            if category:
                specialties.add(category)
        
        if 'Industrial' in specialties:
            industrial_govs.append(gov)
        if 'Mining' in specialties:
            mining_govs.append(gov)
        if 'Energy' in specialties:
            energy_govs.append(gov)
        if 'Farming' in specialties:
            farming_govs.append(gov)
        if 'Research' in specialties:
            research_govs.append(gov)
        if 'Trade' in specialties:
            trade_govs.append(gov)
        if not specialties:
            generic_govs.append(gov)
    
    print("\n📋 GOVERNOR SPECIALIZATIONS:")
    print(f"  Industrial/Production:  {len(industrial_govs)}")
    print(f"  Mining:                 {len(mining_govs)}")
    print(f"  Energy:                 {len(energy_govs)}")
    print(f"  Farming:                {len(farming_govs)}")
    print(f"  Research:               {len(research_govs)}")
    print(f"  Trade/Economic:         {len(trade_govs)}")
    print(f"  Generic (no specialty): {len(generic_govs)}")
    
    # Analyze planet assignments
    print("\n" + "="*80)
    print("CURRENT PLANET ASSIGNMENTS")
    print("="*80)
    
    # Group by planet type
    planets_by_type = {}
    for planet in player.planets:
        ptype = planet.designation or 'unknown'
        if ptype not in planets_by_type:
            planets_by_type[ptype] = []
        planets_by_type[ptype].append(planet)
    
    mismatches = []
    
    for ptype in sorted(planets_by_type.keys()):
        planets = planets_by_type[ptype]
        ptype_name = PLANET_TYPES.get(ptype, ptype)
        
        print(f"\n{ptype_name} worlds ({len(planets)}):")
        
        for planet in planets:
            if planet.governor:
                gov = planet.governor
                
                # Check if governor is good for this planet
                specialties = []
                for trait in gov.traits:
                    category, bonus, resources = categorize_trait(trait)
                    if category:
                        specialties.append(f"{category}: {bonus}")
                
                if specialties:
                    spec_str = "; ".join(specialties)
                    print(f"  {planet.name[:30]:30} ← {gov.name[:25]:25} [{spec_str}]")
                else:
                    print(f"  {planet.name[:30]:30} ← {gov.name[:25]:25} [NO PRODUCTION TRAITS]")
                
                # Detect mismatches
                is_mismatch = False
                if 'factory' in ptype and not any('Industrial' in s for s in specialties):
                    is_mismatch = True
                    mismatches.append((planet, gov, 'Industrial', ptype_name))
                elif 'foundry' in ptype and not any('Industrial' in s for s in specialties):
                    is_mismatch = True
                    mismatches.append((planet, gov, 'Industrial', ptype_name))
                elif 'mining' in ptype and not any('Mining' in s for s in specialties):
                    is_mismatch = True
                    mismatches.append((planet, gov, 'Mining', ptype_name))
                elif 'generator' in ptype and not any('Energy' in s for s in specialties):
                    is_mismatch = True
                    mismatches.append((planet, gov, 'Energy', ptype_name))
                elif 'farming' in ptype and not any('Farming' in s for s in specialties):
                    is_mismatch = True
                    mismatches.append((planet, gov, 'Farming', ptype_name))
                
                if is_mismatch:
                    print(f"    ⚠️  MISMATCH: This planet needs a different governor!")
            else:
                print(f"  {planet.name[:30]:30} ← NO GOVERNOR")
    
    # Show optimization recommendations
    if mismatches:
        print("\n" + "="*80)
        print("⚠️  GOVERNOR-PLANET MISMATCHES DETECTED")
        print("="*80)
        
        print(f"\n{len(mismatches)} planets have suboptimal governor assignments:")
        
        for planet, gov, needed, ptype in mismatches:
            print(f"\n• {planet.name} ({ptype})")
            print(f"  Current: {gov.name} (wrong specialty)")
            print(f"  Needs:   Governor with {needed} traits")
            
            # Production impact
            if planet.resources:
                if needed == 'Industrial':
                    prod = planet.resources.produces.consumer_goods + planet.resources.produces.alloys
                    potential_gain = prod * 0.15  # 15% bonus
                    print(f"  Impact:  Losing ~{potential_gain:.1f}/month production bonus")
    
    # Show recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    if budget and budget.net_consumer_goods < 0:
        deficit = abs(budget.net_consumer_goods)
        print(f"\n🔴 You have a consumer goods deficit: {budget.net_consumer_goods:+.1f}/month")
        
        if len(industrial_govs) == 0:
            print(f"\n⚠️  CRITICAL: You have NO governors with industrial traits!")
            print(f"   Action: Check leader recruitment pool for:")
            print(f"     • Industrialist (+15% industrial output)")
            print(f"     • Industrial Economist (+15% industrial output)")
            print(f"     • Artisan (+10% consumer goods)")
            print(f"\n   If you hire ONE with +15% industrial trait:")
            print(f"     • Assign to biggest factory world")
            print(f"     • Gain ~+30-35 consumer goods/month")
            print(f"     • Reduces deficit to {budget.net_consumer_goods + 30:+.1f}/month")
        else:
            print(f"\n✓ You have {len(industrial_govs)} industrial governors:")
            for gov in industrial_govs:
                print(f"    • {gov.name}")
            print(f"  Make sure they're on your factory/foundry worlds!")
    
    if budget and budget.net_food < 0:
        print(f"\n🔴 You have a food deficit: {budget.net_food:+.1f}/month")
        if len(farming_govs) > 0:
            print(f"  ✓ You have {len(farming_govs)} farming governors - assign to farming worlds")
        else:
            print(f"  ⚠️  No farming governors - look for Rural/Agrarian traits")
    
    # Show available unassigned governors
    assigned_ids = {p.governor_id for p in player.planets if p.governor_id}
    unassigned = [g for g in governors if g.id not in assigned_ids]
    
    if unassigned:
        print(f"\n📋 UNASSIGNED GOVERNORS ({len(unassigned)}):")
        for gov in unassigned:
            specialties = []
            for trait in gov.traits:
                category, bonus, resources = categorize_trait(trait)
                if category:
                    specialties.append(category)
            
            if specialties:
                spec_str = ", ".join(set(specialties))
                print(f"  • {gov.name} (Level {gov.level}) - {spec_str}")
            else:
                print(f"  • {gov.name} (Level {gov.level}) - Generic")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        save_path = sys.argv[1]
    else:
        save_path = os.path.expanduser(
            "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
            "blorgcommonality_-193568729/consumer goods crisis.sav"
        )
    
    analyze_governors(save_path)
