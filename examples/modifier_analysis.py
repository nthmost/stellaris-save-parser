#!/usr/bin/env python3
"""
Example: Analyze active empire modifiers.

Shows how to:
- Get all active modifiers
- Categorize by effect type
- See which bonuses are temporary vs permanent
- Calculate total research bonuses
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
    
    # Get all modifiers
    modifiers = save.get_player_modifiers()
    
    print(f"\n{'='*80}")
    print(f"FOUND {len(modifiers)} ACTIVE MODIFIERS")
    print(f"{'='*80}\n")
    
    # Separate permanent and temporary
    permanent = [m for m in modifiers if m.is_permanent]
    temporary = [m for m in modifiers if m.is_temporary]
    
    print(f"Permanent: {len(permanent)}")
    print(f"Temporary: {len(temporary)}\n")
    
    # Categorize
    categorized = get_modifiers_by_category(modifiers)
    
    # Show each category
    for category, mods in categorized.items():
        if not mods:
            continue
            
        print(f"\n{'='*80}")
        print(f"{category.upper().replace('_', ' ')} ({len(mods)})")
        print(f"{'='*80}")
        
        for mod in sorted(mods, key=lambda m: m.name):
            print(f"\n• {mod.name}")
            
            if mod.description:
                print(f"  {mod.description}")
            
            # Show effects
            if mod.effects:
                for effect, value in sorted(mod.effects.items()):
                    if '_mult' in effect or '_speed' in effect:
                        print(f"    {effect}: {value:+.0%}")
                    elif '_add' in effect:
                        print(f"    {effect}: {value:+.2f}")
                    else:
                        print(f"    {effect}: {value}")
            
            # Show duration for temporary modifiers
            if mod.is_temporary:
                years = mod.days_remaining / 360
                print(f"    ⏱️  Expires in {mod.days_remaining} days ({years:.1f} years)")
    
    # Calculate total research bonus
    print(f"\n{'='*80}")
    print("CALCULATED RESEARCH BONUS")
    print(f"{'='*80}\n")
    
    total_research_bonus = 0.0
    research_sources = []
    
    for mod in modifiers:
        for effect, value in mod.effects.items():
            if 'research_speed' in effect or 'tech' in effect:
                total_research_bonus += value
                research_sources.append((mod.name, value))
    
    if research_sources:
        print("Contributing modifiers:")
        for name, bonus in research_sources:
            print(f"  {name}: {bonus:+.0%}")
        
        print(f"\nTotal research speed bonus: {total_research_bonus:+.0%}")
        print(f"Research multiplier: {1 + total_research_bonus:.2f}x")
    else:
        print("No research speed modifiers found.")
    
    # Show all modifiers without known effects
    unknown = [m for m in modifiers if not m.effects]
    if unknown:
        print(f"\n{'='*80}")
        print(f"MODIFIERS WITH UNKNOWN EFFECTS ({len(unknown)})")
        print(f"{'='*80}\n")
        
        for mod in sorted(unknown, key=lambda m: m.name):
            duration = f" ({mod.days_remaining} days)" if mod.is_temporary else " (permanent)"
            print(f"  • {mod.name}{duration}")
        
        print("\nNote: Effects for these modifiers are defined in game files.")
        print("The library includes a database of common modifiers.")


if __name__ == '__main__':
    main()
