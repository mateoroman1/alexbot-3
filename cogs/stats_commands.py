from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

from config.config import MAIN_GUILD_ID, IMAGES_DIR, EX_DIR, ASSETS_DIR
from config.messages import *
from data.storage import storage
from game.stats import StatsManager
from utils.helpers import find_closest_match, get_image_extension
from utils.embeds import (
    create_character_stats_embed,
    create_user_stats_embed,
    create_server_stats_embed,
    create_highest_rolls_embed,
    create_raid_master_embed,
    create_library_embed
)

class StatsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='stats',
        with_app_command=True,
        help='Display stats for a character, user, or overall rankings'
    )
    async def stats(
        self,
        ctx: commands.Context,
        *,
        arg: str = 'All'
    ) -> None:
        """Display various statistics."""
        try:
            print(f"\nStats command called by {ctx.author.name}")
            print(f"Argument: {arg}")
            
            # Defer response if this is a slash command
            if isinstance(ctx, discord.Interaction) or ctx.interaction:
                await ctx.defer()
                print("Interaction deferred")
            
            if arg != 'All':
                # Try to find user first
                print("Looking for user...")
                user = discord.utils.get(ctx.guild.members, name=arg)
                if not user:
                    user = discord.utils.get(ctx.guild.members, nick=arg)
                    
                if user:
                    print(f"User found: {user.name}")
                    # Display user stats
                    stats = storage.get_user_stats(arg)
                    if not stats:
                        embed = discord.Embed(title=f'{arg}\'s Stats:')
                        embed.add_field(name=ERR_NO_STATS, value=None)
                    else:
                        embed = create_user_stats_embed(
                            arg,
                            stats,
                            str(user.display_avatar)
                        )
                    await ctx.send(embed=embed)
                    
                else:
                    print(f"Looking for character: {arg}")
                    # Try to find character
                    closest_match = find_closest_match(
                        arg.casefold(),
                        storage.character_stats.keys()
                    )
                    
                    if closest_match:
                        print(f"Character found: {closest_match}")
                        stats = storage.get_character_stats(closest_match)
                        
                        # Try to find the image with any valid extension
                        image = None
                        if stats.count == 0:
                            image = Path(IMAGES_DIR) / "q.png"
                        else:
                            for ext in [".png", ".jpg", ".jpeg", ".gif"]:
                                test_path = Path(IMAGES_DIR) / f"{closest_match}{ext}"
                                if test_path.exists():
                                    image = test_path
                                    break
                            
                            if not image:
                                print(f"Warning: No image found for {closest_match}")
                                image = Path(IMAGES_DIR) / "q.png"
                            
                        print(f"Using image path: {image}")
                        embed = create_character_stats_embed(arg, stats, image)
                        await ctx.send(embed=embed, file=discord.File(image, filename="image.png"))
                    else:
                        print(f"No character found matching: {arg}")
                        await ctx.send(
                            ERR_CHARACTER_NOT_FOUND.format(name=arg),
                            ephemeral=True
                        )
            else:
                print("Displaying overall rankings")
                # Display overall rankings
                character, count = StatsManager.get_most_common_character()
                raid_char, raid_wins = StatsManager.get_winningest_raider()
                
                # Most common character(s)
                if isinstance(character, list):
                    embed = create_highest_rolls_embed(character, count, is_tie=True)
                    embed.set_image(url="attachment://image.png")
                    file = discord.File(Path(ASSETS_DIR) / "dice.png", filename="image.png")
                    await ctx.send(embed=embed, file=file)
                else:
                    # Find character image
                    image = None
                    for ext in [".png", ".jpg", ".jpeg", ".gif"]:
                        test_path = Path(IMAGES_DIR) / f"{character}{ext}"
                        if test_path.exists():
                            image = test_path
                            break
                    
                    if not image:
                        print(f"Warning: No image found for {character}")
                        image = Path(ASSETS_DIR) / "q.png"
                    
                    print(f"Using image path for most common: {image}")
                    embed = create_highest_rolls_embed(character, count)
                    embed.set_image(url="attachment://image.png")
                    await ctx.send(embed=embed, file=discord.File(image, filename="image.png"))
                
                # Most successful raider(s)
                if isinstance(raid_char, list):
                    embed = create_raid_master_embed(", ".join(raid_char), raid_wins)
                    embed.set_image(url="attachment://image.png")
                    file = discord.File(Path(ASSETS_DIR) / "raid.png", filename="image.png")
                    await ctx.send(embed=embed, file=file)
                else:
                    # Find raider image
                    image = None
                    for ext in [".png", ".jpg", ".jpeg", ".gif"]:
                        test_path = Path(IMAGES_DIR) / f"{raid_char}{ext}"
                        if test_path.exists():
                            image = test_path
                            break
                    
                    if not image:
                        print(f"Warning: No image found for {raid_char}")
                        image = Path(ASSETS_DIR) / "q.png"
                    
                    print(f"Using image path for raid master: {image}")
                    embed = create_raid_master_embed(raid_char, raid_wins)
                    embed.set_image(url="attachment://image.png")
                    await ctx.send(embed=embed, file=discord.File(image, filename="image.png"))
                    
        except Exception as e:
            print(f"Error in stats command: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(
        name='server',
        with_app_command=True,
        help='Display server stats'
    )
    async def server(self, ctx: commands.Context) -> None:
        """Display server statistics."""
        try:
            print(f"\nServer stats requested by {ctx.author.name}")
            
            # Defer response if this is a slash command
            if isinstance(ctx, discord.Interaction) or ctx.interaction:
                await ctx.defer()
                print("Interaction deferred")
            
            server = ctx.guild.name
            stats = storage.get_server_stats(server)
            
            if not stats:
                embed = discord.Embed(title=f'{server}\'s Stats:')
                embed.add_field(name="No stats were found.", value=None)
            else:
                embed = create_server_stats_embed(
                    server,
                    stats,
                    str(ctx.guild.icon.url) if ctx.guild.icon else None
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Error in server command: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(
        name='deck',
        with_app_command=True,
        help='Show EX cards a user owns'
    )
    async def deck(
        self,
        ctx: commands.Context,
        *,
        arg: str = 'All'
    ) -> None:
        """Display a user's EX card collection."""
        try:
            print(f"\nDeck command called by {ctx.author.name}")
            print(f"Argument: {arg}")
            
            # Defer response if this is a slash command
            if isinstance(ctx, discord.Interaction) or ctx.interaction:
                await ctx.defer()
                print("Interaction deferred")
            
            if arg != 'All':
                user = discord.utils.get(ctx.guild.members, name=arg)
                if not user:
                    user = discord.utils.get(ctx.guild.members, nick=arg)
                    
                if user:
                    stats = storage.get_user_stats(arg)
                    if not stats or not stats.deck:
                        embed = create_library_embed(arg)
                        await ctx.send(embed=embed)
                        return
                        
                    # Create deck view
                    current_card = 0
                    file = discord.File(
                        Path(EX_DIR) / f"{stats.deck[0]}.gif",
                        filename="image.gif"
                    )
                    
                    embed = discord.Embed(title=EMBED_LIBRARY.format(name=arg))
                    embed.set_image(url="attachment://image.gif")
                    embed.add_field(name='EX cards owned', value=len(stats.deck))
                    
                    view = discord.ui.View()
                    
                    # Add navigation buttons
                    async def next_callback(interaction: discord.Interaction):
                        nonlocal current_card
                        current_card = (current_card + 1) % len(stats.deck)
                        new_file = discord.File(
                            Path(IMAGES_DIR) / "EX" / f"{stats.deck[current_card]}.gif",
                            filename="nextcard.gif"
                        )
                        new_embed = discord.Embed(title=EMBED_LIBRARY.format(name=arg))
                        new_embed.set_image(url="attachment://nextcard.gif")
                        await interaction.response.edit_message(
                            embed=new_embed,
                            attachments=[new_file]
                        )
                        
                    async def prev_callback(interaction: discord.Interaction):
                        nonlocal current_card
                        if current_card > 0:
                            current_card -= 1
                            new_file = discord.File(
                                Path(IMAGES_DIR) / "EX" / f"{stats.deck[current_card]}.gif",
                                filename="nextcard.gif"
                            )
                            new_embed = discord.Embed(title=EMBED_LIBRARY.format(name=arg))
                            new_embed.set_image(url="attachment://nextcard.gif")
                            await interaction.response.edit_message(
                                embed=new_embed,
                                attachments=[new_file]
                            )
                    
                    next_button = discord.ui.Button(label="View Next")
                    prev_button = discord.ui.Button(label="View Previous")
                    
                    next_button.callback = next_callback
                    prev_button.callback = prev_callback
                    
                    view.add_item(prev_button)
                    view.add_item(next_button)
                    
                    await ctx.send(embed=embed, file=file, view=view)
                    
        except Exception as e:
            print(f"Error in deck command: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCommands(bot)) 