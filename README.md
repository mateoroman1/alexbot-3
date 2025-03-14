# AlexBot

A Discord bot-based game platform with character-based raids, pvp, and stats tracking. Can be set up with custom data to personalize for your friends and server.

NOTE: This is primarily developed for the Alexbot official Discord server. I am sharing it for use as a reference, rather than as an SDK, but you are welcome to take the code and do whatever you want with it. But if you extend it and make cool features you have to promise to show me it.

## Features

- Character rolling system
- PvE raid battles with boss encounters
- PvP mode
- Character evolution mechanics
- Stats tracking for users and servers
- Campaign progression system

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```
3. Add custom data to the assets directory - Starter Assets can be found at: https://github.com/mateoroman1/alexbot-starter-assets
- assets/utility - Game icons
- assets/characters - Images for characters rolled with the .roll command
- assets/bosses - Images for the raid mode bosses
- assets/EX - Images for special edition characters
- assets/items - Images for the items/weapons used in raid mode
- assets/evolutions - Optional folder for item evolutions if defined in models.py
- the data directory should automatically create .json files when the bot is ran
   
4. Run the bot:
```bash
python main.py
```

## Commands

### General
- `.roll` - Roll a random character
- `.show [name]` - Show a specific character
- `/stats [name]` - Show stats for a character or user
- `/deck [name]` - Show EX cards owned by a user

### Raid
- `/raid [mode]` - Start a raid (Campaign/Classic mode)
- `/server` - Show server stats

### PVP
- `.pvp` - Creates a 1v1 PvP instance

### Admin
- `/submit` - Submit a new character
- `/updategroup` - Update a character's group
- `/submittools` - Submit or update tools


## Project Structure

```
alexbot/
├── config/      # Configuration and constants
├── data/        # Data models and storage
├── game/        # Game mechanics
├── cogs/        # Discord command modules
└── utils/       # Utility functions
``` 
