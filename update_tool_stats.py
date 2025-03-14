import json

# Load original tool stats
with open('original_tool_stats.json', 'r') as f:
    original_stats = json.load(f)

# Load current tool stats
with open('data/tool_stats.json', 'r') as f:
    new_stats = json.load(f)

# Process each tool
for tool_name, tool_data in original_stats.items():
    # Get or set default multiplier
    default_multiplier = tool_data.get('Default', 1.0)
    
    # Calculate threshold range (±25% of default)
    lower_threshold = default_multiplier * 0.75
    upper_threshold = default_multiplier * 1.25
    
    # Create or update tool entry
    if tool_name not in new_stats:
        new_stats[tool_name] = {
            "default_multiplier": default_multiplier,
            "group": tool_data.get('group', 'None'),
            "character_multipliers": {}
        }
    else:
        new_stats[tool_name]["default_multiplier"] = default_multiplier
        
    # Add character multipliers outside threshold range
    for char_name, multiplier in tool_data.items():
        if char_name not in ['Default', 'group']:
            if multiplier < lower_threshold or multiplier > upper_threshold:
                new_stats[tool_name]["character_multipliers"][char_name.casefold()] = multiplier

# Save updated tool stats
with open('data/tool_stats.json', 'w') as f:
    json.dump(new_stats, f, indent=2) 