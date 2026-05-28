#!/usr/bin/env python3
"""
Analyze and diagnose resource crises in your empire.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave
from collections import defaultdict

def analyze_crisis(save_path):
    save = StellarisSave(save_path)
    player = save.get_player_empire()
    budget = save.get_player_budget()
    
    print("="*80)
    print("STELLARIS RESOURCE CRISIS ANALYZER")
    print("="*80)
    
    # Identify crises
    crises = []
    if budget.net_consumer_goods < -20:
        crises.append(('consumer_goods', budget.net_consumer_goods, 'CRITICAL'))
    elif budget.net_consumer_goods < 0:
        crises.append(('consumer_goods', budget.net_consumer_goods, 'WARNING'))
    
    if budget.net_food < -20:
        crises.append(('food', budget.net_food, 'CRITICAL'))
    elif budget.net_food < 0:
        crises.append(('food', budget.net_food, 'WARNING'))
    
    if budget.net_energy < -50:
        crises.append(('energy', budget.net_energy, 'CRITICAL'))
    elif budget.net_energy < 0:
        crises.append(('energy', budget.net_energy, 'WARNING'))
    
    if budget.net_minerals < -50:
        crises.append(('minerals', budget.net_minerals, 'CRITICAL'))
    elif budget.net_minerals < 0:
        crises.append(('minerals', budget.net_minerals, 'WARNING'))
    
    if not crises:
        print("\n✅ NO CRISES DETECTED - Your economy is stable!")
        print("\n📊 Current Balance:")
        print(f"  Energy:         {budget.net_energy:+8.1f}")
        print(f"  Minerals:       {budget.net_minerals:+8.1f}")
        print(f"  Food:           {budget.net_food:+8.1f}")
        print(f"  Consumer Goods: {budget.net_consumer_goods:+8.1f}")
        print(f"  Alloys:         {budget.net_alloys:+8.1f}")
        return
    
    # Show all crises
    print(f"\n🚨 {len(crises)} RESOURCE CRISIS DETECTED!")
    for resource, deficit, severity in crises:
        icon = "🔴" if severity == "CRITICAL" else "⚠️"
        print(f"  {icon} {resource.upper()}: {deficit:+.1f}/month ({severity})")
    
    print("\n📊 Full Economy Status:")
    print(f"  Energy:         {budget.net_energy:+8.1f}")
    print(f"  Minerals:       {budget.net_minerals:+8.1f}")
    print(f"  Food:           {budget.net_food:+8.1f}")
    print(f"  Consumer Goods: {budget.net_consumer_goods:+8.1f}")
    print(f"  Alloys:         {budget.net_alloys:+8.1f}")
    
    # Analyze each crisis
    for resource, deficit, severity in sorted(crises, key=lambda x: x[1]):
        print("\n" + "="*80)
        analyze_resource_crisis(resource, deficit, budget, player, save)
    
    # Final recommendations
    print("\n" + "="*80)
    print("⚡ PRIORITY ORDER")
    print("="*80)
    
    # Sort by severity
    critical = [c for c in crises if c[2] == 'CRITICAL']
    warnings = [c for c in crises if c[2] == 'WARNING']
    
    priority = 1
    if critical:
        print(f"\n🔴 CRITICAL (Fix Immediately):")
        for resource, deficit, _ in sorted(critical, key=lambda x: x[1]):
            print(f"  {priority}. Fix {resource.replace('_', ' ').title()} ({deficit:+.0f}/month)")
            priority += 1
    
    if warnings:
        print(f"\n⚠️  WARNINGS (Fix Soon):")
        for resource, deficit, _ in sorted(warnings, key=lambda x: x[1]):
            print(f"  {priority}. Fix {resource.replace('_', ' ').title()} ({deficit:+.0f}/month)")
            priority += 1


def analyze_resource_crisis(resource, deficit, budget, player, save):
    deficit_amount = abs(deficit)
    
    print(f"🔴 {resource.replace('_', ' ').upper()} CRISIS: {deficit:+.1f}/month")
    print("─" * 80)
    
    if resource == 'consumer_goods':
        analyze_consumer_goods_crisis(deficit_amount, budget, player)
    elif resource == 'food':
        analyze_food_crisis(deficit_amount, budget, player)
    elif resource == 'energy':
        analyze_energy_crisis(deficit_amount, budget, player)
    elif resource == 'minerals':
        analyze_minerals_crisis(deficit_amount, budget, player)


def analyze_consumer_goods_crisis(deficit, budget, player):
    """Analyze consumer goods shortage and provide solutions."""
    
    cg_income = budget.income.get('consumer_goods', 0)
    cg_expenses = budget.expenses.get('consumer_goods', 0)
    
    print(f"\n💰 Current Situation:")
    print(f"  Production:  +{cg_income:.1f}")
    print(f"  Consumption: -{cg_expenses:.1f}")
    print(f"  Deficit:     -{deficit:.1f}")
    
    # Find planets producing consumer goods
    producing_planets = []
    for planet in player.planets:
        if planet.resources and planet.resources.produces.consumer_goods > 0:
            producing_planets.append((planet, planet.resources.produces.consumer_goods))
    
    if producing_planets:
        print(f"\n✓ {len(producing_planets)} planets currently producing:")
        for planet, prod in sorted(producing_planets, key=lambda x: -x[1])[:3]:
            print(f"    {planet.name[:30]:30} +{prod:6.1f}")
    else:
        print(f"\n❌ NO planets producing consumer goods!")
    
    # Calculate buildings needed
    buildings_needed = int(deficit / 10) + 1
    
    print(f"\n✅ SOLUTION:")
    print(f"  • Build {buildings_needed} Civilian Fabricators")
    print(f"  • Each produces ~12 consumer goods (2 Artisan jobs)")
    print(f"  • Costs: ~300 minerals each, ~180 days construction")
    
    # Find best planets
    best_planets = find_best_industrial_planets(player)
    
    print(f"\n🏭 BUILD ON THESE PLANETS:")
    for i, planet in enumerate(best_planets[:buildings_needed], 1):
        designation = planet.designation.replace('col_', '').title() if planet.designation else 'Unspecified'
        print(f"  {i}. {planet.name[:35]:35} ({planet.pops:4} pops, {designation})")
    
    print(f"\n💡 QUICK FIX (Temporary):")
    print(f"  • Galactic Market → Monthly Trade")
    print(f"  • BUY {int(deficit) + 10} consumer goods/month")
    print(f"  • Costs ~{int((deficit + 10) * 1.5)} energy/month")
    print(f"  • Buys time while fabricators are built")


def analyze_food_crisis(deficit, budget, player):
    """Analyze food shortage and provide solutions."""
    
    food_income = budget.income.get('food', 0)
    food_expenses = budget.expenses.get('food', 0)
    
    print(f"\n💰 Current Situation:")
    print(f"  Production:  +{food_income:.1f}")
    print(f"  Consumption: -{food_expenses:.1f}")
    print(f"  Deficit:     -{deficit:.1f}")
    
    # Find food-producing planets
    producing_planets = []
    for planet in player.planets:
        if planet.resources and planet.resources.produces.food > 0:
            producing_planets.append((planet, planet.resources.produces.food))
    
    if producing_planets:
        print(f"\n✓ {len(producing_planets)} planets producing food:")
        for planet, prod in sorted(producing_planets, key=lambda x: -x[1])[:5]:
            print(f"    {planet.name[:30]:30} +{prod:6.1f}")
    
    # Solutions
    buildings_needed = int(deficit / 20) + 1
    
    print(f"\n✅ SOLUTIONS:")
    print(f"  Option 1: Build {buildings_needed} Hydroponics Bays on starbases")
    print(f"    • Each starbase can have multiple")
    print(f"    • Produces ~5-8 food each")
    print(f"    • Quick and doesn't use planet slots")
    
    print(f"\n  Option 2: Build Agricultural Districts")
    print(f"    • On planets with farming designation")
    print(f"    • Each district = 2-3 Farmer jobs = ~6 food")
    print(f"    • Need {int(deficit / 6) + 1} districts")
    
    print(f"\n  Option 3: Build Agri-Processing Complexes")
    print(f"    • On farming worlds")
    print(f"    • Enhances existing food production")
    
    # Find best farming planets
    farming_planets = [p for p in player.planets if p.is_farming_world]
    if farming_planets:
        print(f"\n🌾 YOUR FARMING WORLDS:")
        for planet in farming_planets[:3]:
            food_prod = planet.resources.produces.food if planet.resources else 0
            print(f"    {planet.name[:30]:30} +{food_prod:6.1f} food")
    
    print(f"\n💡 QUICK FIX:")
    print(f"  • Build Hydroponics Bays on your starbases")
    print(f"  • They're cheap and fast to build")
    print(f"  • Need {buildings_needed} bays minimum")


def analyze_energy_crisis(deficit, budget, player):
    """Analyze energy shortage."""
    
    print(f"\n✅ SOLUTIONS:")
    print(f"  1. Build Solar Panel Networks on starbases")
    print(f"  2. Build Generator Districts on planets")
    print(f"  3. Assign more pops to Technician jobs")
    print(f"  4. Build Dyson Sphere (late game)")


def analyze_minerals_crisis(deficit, budget, player):
    """Analyze mineral shortage."""
    
    print(f"\n✅ SOLUTIONS:")
    print(f"  1. Build Mining Districts on planets")
    print(f"  2. Build Mining Stations on deposits in space")
    print(f"  3. Assign more pops to Miner jobs")


def find_best_industrial_planets(player):
    """Find best planets for building industrial buildings."""
    
    scored_planets = []
    for planet in player.planets:
        score = 0
        
        # High pop is good
        score += planet.pops / 100
        
        # Industrial designation is best
        if planet.is_industrial_world:
            score += 100
        
        # Capital is good (lots of building slots)
        if planet.is_capital:
            score += 50
        
        # Big planets have more slots
        score += planet.size
        
        scored_planets.append((score, planet))
    
    scored_planets.sort(reverse=True)
    return [p for _, p in scored_planets]


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        save_path = sys.argv[1]
    else:
        # Default to latest save
        save_path = os.path.expanduser(
            "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
            "blorgcommonality_-193568729/consumer goods crisis.sav"
        )
    
    analyze_crisis(save_path)
