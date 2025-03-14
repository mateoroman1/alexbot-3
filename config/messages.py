from typing import Final

# Error messages
ERR_OWNER_ONLY: Final[str] = "This command is owner-only!"
ERR_RAID_IN_PROGRESS: Final[str] = "Cannot start a raid while one is in progress!"
ERR_CHARACTER_EXISTS: Final[str] = "This character may already exist"
ERR_INVALID_GROUP: Final[str] = "Group {group} not found. Check your spelling or use !groups to see the full list"
ERR_ALREADY_IN_GROUP: Final[str] = "{name} is already in the {group} group."
ERR_TOOL_EXISTS: Final[str] = "This tool already exists. Stat updates are not implemented just yet."
ERR_MISSING_IMAGE: Final[str] = "You need to attach an image to create a new tool"
ERR_INVALID_PATH: Final[str] = "Invalid file path detected"
ERR_CHARACTER_NOT_FOUND: Final[str] = "Unable to find character {name}. Check your spelling and try again."
ERR_CHARACTER_NOT_REVEALED: Final[str] = "This character has not been revealed! Try using !roll to unlock the ability to view them here."
ERR_NO_STATS: Final[str] = "No stats were found. Try !roll or /raid to start."

# Success messages
SUCCESS_SYNC: Final[str] = "Command tree synced."
SUCCESS_CHARACTER_ADDED: Final[str] = "Character {name} has been added!"
SUCCESS_GROUP_UPDATED: Final[str] = "{name} has been assigned to the {group} group."
SUCCESS_TOOL_ADDED: Final[str] = "Tool {name} has been added!"
SUCCESS_TOOL_DEFAULT: Final[str] = "Tool {name} has been added as a default tool!"

# Raid messages
RAID_WEAKNESS: Final[str] = "{weakness} is my weakness!"
RAID_GROUP_COMBO: Final[str] = "{groups} HAVE COMBINED FOR A {combo}x GROUP COMBO(s)! BONUS DAMAGE UNLOCKED!"
RAID_VICTORY: Final[str] = "Your party declares victory over {boss}, dealing {damage} total damage!"
RAID_DEFEAT: Final[str] = "Your party attacks and leaves {boss} at {health} HP\n{boss} slays your party, leaving no one alive...."
RAID_DEATH_DEFEAT: Final[str] = "It wasn't enough..."

# Death vote messages
DEATH_PROMPT: Final[str] = "Turn back now, or face the forces of death again if you dare..."
DEATH_RETRY: Final[str] = "Death awaits you yet again..."
DEATH_RETREAT: Final[str] = " "  # Empty title for retreat

# Evolution messages
EVOLUTION_UNLOCK: Final[str] = "{tool1} and {tool2} have evolved!"
EX_CARD_UNLOCK: Final[str] = "An EX card has been unleashed!"

# Curse messages
CURSE_APPLIED: Final[str] = "{user} has been cursed!"
CURSE_LIFTED: Final[str] = "{user}'s curse has been lifted!"

# Stats messages
STATS_LEAD: Final[str] = "{name} has taken the lead!"
STATS_TIE: Final[str] = "{name} has tied for the lead!"
STATS_MILESTONE: Final[str] = "{name} IS THE FIRST TO THE 100TH ROLL!!!"

# Button labels
BTN_JOIN_RAID: Final[str] = "Join Raid"
BTN_START_RAID: Final[str] = "Start Raid"
BTN_STARTING: Final[str] = "Starting...."
BTN_TRY_AGAIN: Final[str] = "It's not over!"
BTN_RETREAT: Final[str] = "I'm not ready..."
BTN_PLAYERS: Final[str] = "{count} player(s)"

# Embed titles
EMBED_LIBRARY: Final[str] = "{name}'s Library:"
EMBED_SERVER_STATS: Final[str] = "{server}'s Stats:"
EMBED_CHARACTER_STATS: Final[str] = "{name} Stats:"
EMBED_HIGHEST_ROLL: Final[str] = "Highest Roll:"
EMBED_HIGHEST_ROLL_TIE: Final[str] = "Highest Roll - Tie:"
EMBED_RAID_MASTER: Final[str] = "The Raid Master:" 