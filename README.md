# AlexBot

A Discord bot for managing character-based raids and stats tracking.

## Features

- Character rolling system
- PvE raid battles with boss encounters
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

3. Run the bot:
```bash
python main.py
```

## Commands

### General
- `/roll` - Roll a random character
- `/show [name]` - Show a specific character
- `/stats [name]` - Show stats for a character or user
- `/deck [name]` - Show EX cards owned by a user

### Raid
- `/raid [mode]` - Start a raid (Campaign/Classic mode)
- `/server` - Show server stats

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