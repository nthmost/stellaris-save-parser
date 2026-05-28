#!/usr/bin/env python3
"""
Example: Complete empire analysis including modifiers and budget.

This example shows how to:
- Get active empire modifiers
- Analyze the complete budget (income, expenses, trade)
- See where resources come from
- Compare planet production vs total empire income
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stellaris_save_parser import StellarisSave
from stellaris_save_parser.modifiers import get_modifiers_by_category

# Path to your save file
SAVE_PATH = os.path.expanduser(
    "~/Library/Application Support/Steam/userdata/98808057/281990/remote/save games/"
    "blorgcommonality_-193568729/snowballing.sav"
)

def main():
    print("Loading save file...")
    save = StellarisSave(SAVE_PATH)
    
    print("\n" + "="*80)
    print("ACTIVE EMPIRE MODIFIERS")
    print("="*80)
    
    # Get all active modifiers
    modifiers = save.get_player_modifiers()
    
    # Categorize them
    categorized = get_modifiers_by_category(modifiers)
    
    # Show research modifiers
    if categorized['research']:
        print(f"\nRESEARCH MODIFIERS ({len(categorized['research'])}):")
        for mod in categorized['research']:
            print(f"  • {mod.name}")
            if mod.description:
                print(f"    {mod.description}")
            if mod.effects:
                for effect, value in mod.effects.items():
                    if '_mult' in effect or '_speed' in effect:
                        print(f"    {effect}: {value:+.0%}")
                    else:
                        print(f"    {effect}: {value:+.3f}")
            if mod.is_temporary:
                print(f"    Expires in {mod.days_remaining} days")
    
    # Show resource production modifiers
    if categorized['resource_production']:
        print(f"\nRESOURCE PRODUCTION MODIFIERS ({len(categorized['resource_production'])}):")
        for mod in categorized['resource_production']:
            print(f"  • {mod.name}")
            if mod.description:
                print(f"    {mod.description}")
            if mod.effects:
                for effect, value in mod.effects.items():
                    if '_mult' in effect:
                        print(f"    {effect}: {value:+.0%}")
    
    # Show military modifiers
    if categorized['military']:
        print(f"\nMILITARY MODIFIERS ({len(categorized['military'])}):")
        for mod in categorized['military']:
            print(f"  • {mod.name}")
            if mod.description:
                print(f"    {mod.description}")
    
    print("\n" + "="*80)
    print("COMPLETE EMPIRE BUDGET")
    print("="*80)
    
    # Get budget
    budget = save.get_player_budget()
    
    if budget:
        print("\nMONTHLY NET INCOME:")
        print(f"  Energy:      {budget.net_energy:+8.1f}")
        print(f"  Minerals:    {budget.net_minerals:+8.1f}")
        print(f"  Food:        {budget.net_food:+8.1f}")
        print(f"  Alloys:      {budget.net_alloys:+8.1f}")
        print(f"  Consumer Goods: {budget.net_consumer_goods:+8.1f}")
        print(f"  Unity:       {budget.net_unity:+8.1f}")
        print(f"  Influence:   {budget.net_influence:+8.1f}")
        print()
        print(f"  Physics Research:     {budget.net_physics_research:+8.1f}")
        print(f"  Society Research:     {budget.net_society_research:+8.1f}")
        print(f"  Engineering Research: {budget.net_engineering_research:+8.1f}")
        print(f"  Total Research:       {budget.total_research:+8.1f}")
    
    print("\n" + "="*80)
    print("RESOURCE INCOME BREAKDOWN")
    print("="*80)
    
    # Get detailed breakdown
    breakdown = save.get_player_budget_breakdown()
    
    if breakdown:
        # Show mineral sources
        print("\nMINERAL INCOME SOURCES:")
        mineral_sources = breakdown.get_income_for_resource('minerals')
        for source, amount in sorted(mineral_sources.items(), key=lambda x: x[1], reverse=True):
            if amount > 0:
                print(f"  {source.replace('_', ' ').title():40} {amount:+8.1f}")
        
        print(f"\n  {'TOTAL MINERAL INCOME':40} {sum(mineral_sources.values()):+8.1f}")
        
        # Show mineral expenses
        print("\nMINERAL EXPENSES:")
        mineral_expenses = breakdown.get_expenses_for_resource('minerals')
        for source, amount in sorted(mineral_expenses.items(), key=lambda x: x[1], reverse=True):
            if amount > 0:
                print(f"  {source.replace('_', ' ').title():40} {amount:+8.1f}")
        
        if mineral_expenses:
            print(f"\n  {'TOTAL MINERAL EXPENSES':40} {sum(mineral_expenses.values()):+8.1f}")
        
        # Show research sources
        print("\n" + "="*80)
        print("RESEARCH SOURCES:")
        print("="*80)
        
        for research_type in ['physics_research', 'society_research', 'engineering_research']:
            sources = breakdown.get_income_for_resource(research_type)
            if sources:
                print(f"\n{research_type.replace('_', ' ').title()}:")
                for source, amount in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                    if amount > 0:
                        print(f"  {source.replace('_', ' ').title():40} {amount:+8.1f}")
    
    print("\n" + "="*80)
    print("PLANET VS EMPIRE COMPARISON")
    print("="*80)
    
    # Get planet-only production
    player = save.get_player_empire()
    
    planet_resources = {
        'energy': 0,
        'minerals': 0,
        'food': 0,
        'physics_research': 0,
        'society_research': 0,
        'engineering_research': 0,
    }
    
    for planet in player.planets:
        if planet.resources:
            planet_resources['energy'] += planet.resources.net.energy
            planet_resources['minerals'] += planet.resources.net.minerals
            planet_resources['food'] += planet.resources.net.food
            planet_resources['physics_research'] += planet.resources.net.physics_research
            planet_resources['society_research'] += planet.resources.net.society_research
            planet_resources['engineering_research'] += planet.resources.net.engineering_research
    
    if budget:
        print("\nResource           | Planets  | Empire   | Non-Planet | % from Planets")
        print("-" * 85)
        
        for resource in ['energy', 'minerals', 'food', 'physics_research', 'society_research', 'engineering_research']:
            planet_val = planet_resources[resource]
            empire_val = budget.get_net(resource)
            non_planet = empire_val - planet_val
            
            if empire_val != 0:
                pct = (planet_val / empire_val * 100)
            else:
                pct = 0
            
            print(f"{resource:18} | {planet_val:+8.1f} | {empire_val:+8.1f} | {non_planet:+10.1f} | {pct:6.1f}%")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    
    if budget and breakdown:
        # Find biggest income source for each resource
        print("\nLargest income sources:")
        
        for resource in ['energy', 'minerals', 'physics_research']:
            sources = breakdown.get_income_for_resource(resource)
            if sources:
                largest = max(sources.items(), key=lambda x: x[1])
                print(f"  {resource.capitalize():20} → {largest[0].replace('_', ' ').title()} ({largest[1]:+.1f})")


if __name__ == '__main__':
    main()
