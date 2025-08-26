import os
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from config.config import (
    APPLICATION_ID,
    OWNER_ID,
    IMAGES_DIR,
    ALLOWED_IMAGE_EXTENSIONS
)
from data.storage import storage
from game.stats import StatsManager

# Load environment variables
load_dotenv()

# Set up intents
intents = discord.Intents.all()
intents.message_content = True

DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN')

# Create bot instance
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    owner_id=OWNER_ID,
    activity=discord.CustomActivity("!roll is BACK! | Sword of Malcom coming soon!"),
    application_id=APPLICATION_ID
)

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print("Bot ready")
    await bot.tree.sync()

@bot.command(name='roll', help='Send random image to chat')
async def roll(ctx: commands.Context):
    """Roll a random character."""
    try:
        # Get all valid image files
        all_files = os.listdir(IMAGES_DIR)
        valid_files = [
            file for file in all_files
            if file.endswith(ALLOWED_IMAGE_EXTENSIONS)
        ]
        
        if not valid_files:
            await ctx.send("No valid images found!")
            return
            
        # Roll for EX card (1/777 chance)
        if random.randint(1, 777) == 777:
            ex_files = [
                file for file in os.listdir(f"{IMAGES_DIR}/EX")
                if file.endswith('.gif')
            ]
            if ex_files:
                ex_card = random.choice(ex_files)
                name = ex_card.split('.')[0].casefold()
                
                # Update stats
                storage.update_user_stats(
                    ctx.author.name,
                    deck=[name]
                )
                storage.update_server_stats(
                    ctx.guild.name,
                    ex_cards=+1
                )
                
                await ctx.reply(
                    "An EX card has been unleashed!",
                    file=discord.File(f"{IMAGES_DIR}/EX/{ex_card}")
                )
                print(f"\n{ctx.author.name} has rolled an EX\n")
                return
                
        # Normal roll
        random_image = random.choice(valid_files)
        name = random_image.split('.')[0].casefold()
        
        # Check for special characters
        if name == 'the unholy trinity':
            user_stats = storage.get_user_stats(ctx.author.name)
            if not user_stats.cursed:
                await ctx.send(
                    f"<@{ctx.author.id}> has been cursed!",
                    file=discord.File(f"{IMAGES_DIR}/assets/curse.gif")
                )
                storage.update_user_stats(ctx.author.name, cursed=True)
                
        elif name == 'the holy trinity':
            user_stats = storage.get_user_stats(ctx.author.name)
            if user_stats.cursed:
                await ctx.send(
                    f"<@{ctx.author.id}>'s curse has been lifted!",
                    file=discord.File(f"{IMAGES_DIR}/assets/curse lifted.gif")
                )
                storage.update_user_stats(ctx.author.name, cursed=False)
                
        # Send image and update stats
        await ctx.reply(file=discord.File(f"{IMAGES_DIR}/{random_image}"))
        status = StatsManager.increment_character_count(name)
        
        storage.update_user_stats(ctx.author.name, total_rolls=+1)
        storage.update_server_stats(ctx.guild.name, total_rolls=+1)
        
        # Handle status messages
        if status == 1:
            await ctx.send(f"{name} has taken the lead!")
        elif status == 2:
            await ctx.send(f"{name} has tied for the lead!")
        elif status == 100:
            await ctx.send(f"{name} IS THE FIRST TO THE 100TH ROLL!!!")
            
        await asyncio.sleep(.5)
        
    except Exception as e:
        print("\nRoll command failed\n", e)
        await ctx.send("Something went wrong. Discord servers might be causing issues.")

async def load_extensions():
    """Load all cog extensions."""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    """Main entry point."""
    # Load data
    storage.load_all()
    
    # Load extensions
    await load_extensions()
    
    # Start bot
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 