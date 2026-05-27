"""
Low-level Clausewitz engine format parser.

Stellaris save files use the Clausewitz engine format, which is a
structured text format with nested key-value pairs.
"""

import re
import zipfile
from typing import Optional


def load_gamestate(save_path: str) -> str:
    """
    Load and extract the gamestate from a Stellaris save file.
    
    Args:
        save_path: Path to the .sav file
        
    Returns:
        The gamestate content as a string
        
    Raises:
        FileNotFoundError: If the save file doesn't exist
        zipfile.BadZipFile: If the save file is corrupted
    """
    with zipfile.ZipFile(save_path, 'r') as zf:
        return zf.read('gamestate').decode('utf-8', errors='ignore')


def find_section(gamestate: str, section_name: str) -> Optional[str]:
    """
    Find and extract a top-level section from the gamestate.
    
    Args:
        gamestate: The full gamestate text
        section_name: Name of the section (e.g., 'leaders', 'planets')
        
    Returns:
        The section content, or None if not found
    """
    pattern = rf'\n{section_name}=\s*\{{'
    match = re.search(pattern, gamestate)
    if not match:
        return None
    
    start_pos = match.end()
    depth = 1
    end_pos = start_pos
    
    for i in range(start_pos, len(gamestate)):
        if gamestate[i] == '{':
            depth += 1
        elif gamestate[i] == '}':
            depth -= 1
            if depth == 0:
                end_pos = i
                break
    
    return gamestate[start_pos:end_pos]


def find_subsection(section: str, subsection_name: str) -> Optional[str]:
    """
    Find a subsection within a section.
    
    Args:
        section: The parent section text
        subsection_name: Name of the subsection
        
    Returns:
        The subsection content, or None if not found
    """
    pattern = rf'\n\t{subsection_name}=\s*\{{'
    match = re.search(pattern, section)
    if not match:
        return None
    
    start_pos = match.end()
    depth = 1
    end_pos = start_pos
    
    for i in range(start_pos, len(section)):
        if section[i] == '{':
            depth += 1
        elif section[i] == '}':
            depth -= 1
            if depth == 0:
                end_pos = i
                break
    
    return section[start_pos:end_pos]


def extract_blocks(text: str, indent_level: int = 1) -> dict[str, str]:
    """
    Extract all top-level blocks from a section.
    
    Args:
        text: The section text
        indent_level: Indentation level (number of tabs)
        
    Returns:
        Dict mapping block IDs to their content
    """
    blocks = {}
    indent = '\t' * indent_level
    pattern = re.compile(rf'\n{indent}(\d+)=\s*\{{', re.MULTILINE)
    
    for match in pattern.finditer(text):
        block_id = match.group(1)
        block_start = match.end()
        
        # Find end of this block
        depth = 1
        i = block_start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        
        blocks[block_id] = text[block_start:i-1]
    
    return blocks


def extract_value(text: str, key: str, default=None):
    """
    Extract a simple value from text.
    
    Args:
        text: The text to search
        key: The key name
        default: Default value if not found
        
    Returns:
        The extracted value, or default if not found
    """
    # Try quoted string
    pattern = rf'\n\t+{key}="([^"]+)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    # Try unquoted value
    pattern = rf'\n\t+{key}=(\S+)'
    match = re.search(pattern, text)
    if match:
        value = match.group(1)
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    
    return default


def extract_list(text: str, key: str) -> list:
    """
    Extract all values for a key that appears multiple times.
    
    Args:
        text: The text to search
        key: The key name
        
    Returns:
        List of all values found
    """
    pattern = rf'\n\t+{key}="([^"]+)"'
    return re.findall(pattern, text)


def extract_leader_name(block: str) -> Optional[str]:
    """
    Extract a leader's name from their data block.
    
    Leader names in Stellaris can be simple strings or complex
    variable-based formats.
    
    Args:
        block: The leader's data block
        
    Returns:
        The leader's name, or None if not found
    """
    # Check for simple name format
    simple_name = re.search(r'key="([^"]+)"\s*\}\s*use_full_regnal_name', block)
    if simple_name and not simple_name.group(1).startswith('%'):
        return simple_name.group(1)
    
    # Complex name with variables
    var_match = re.search(r'variables=\s*\{(.*?)\n\t\t\t\}', block, re.DOTALL)
    if var_match:
        vars_text = var_match.group(1)
        
        # Extract first name (key="1")
        first_name_match = re.search(
            r'key="1".*?value=\s*\{.*?key="([^"]+)"',
            vars_text,
            re.DOTALL
        )
        
        # Extract last name (key="2")
        last_name_match = re.search(
            r'key="2".*?value=\s*\{.*?key="([^"]+)"',
            vars_text,
            re.DOTALL
        )
        
        if first_name_match and last_name_match:
            first = first_name_match.group(1)
            last = last_name_match.group(1)
            return f"{first} {last}"
        elif first_name_match:
            return first_name_match.group(1)
    
    return None
