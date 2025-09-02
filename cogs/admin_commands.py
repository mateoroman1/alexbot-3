import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path
from typing import Optional

from config.config import (
    MAIN_GUILD_ID,
    ALEXBOT_GUILD_ID,
    OWNER_ID,
    IMAGES_DIR,
    TOOLS_DIR,
    CHARACTER_GROUPS
)
from config.messages import *
from data.storage import storage
from utils.helpers import is_valid_image_path

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='sync')
    async def sync(self, ctx: commands.Context) -> None:
        """Sync application commands (owner only)."""
        if ctx.author.id == OWNER_ID:
            await self.bot.tree.sync(guild=discord.Object(id=MAIN_GUILD_ID))
            await self.bot.tree.sync(guild=discord.Object(id=ALEXBOT_GUILD_ID))
            await ctx.send(SUCCESS_SYNC)
        else:
            await ctx.send(ERR_OWNER_ONLY)

    @commands.command(name='updateStats')
    async def update_stats(self, ctx: commands.Context) -> None:
        """Update tool and boss stats (owner only)."""
        if ctx.author.id == OWNER_ID:
            storage.load_all()
            await ctx.send("Stats updated successfully!")
        else:
            await ctx.send(ERR_OWNER_ONLY, ephemeral=True)

    @app_commands.command(
        name='submit',
        description='Submit a character'
    )
    @app_commands.guilds(discord.Object(id=MAIN_GUILD_ID))
    @app_commands.describe(
        attachment='The file to upload',
        name='The character\'s name'
    )
    async def submit(
        self,
        interaction: discord.Interaction,
        attachment: discord.Attachment,
        name: str
    ) -> None:
        """Submit a new character."""
        print(f'\n{interaction.user.nick} is adding a character: {name}')
        
        if not is_valid_image_path(attachment.filename):
            await interaction.response.send_message(ERR_INVALID_PATH, ephemeral=True)
            return
            
        if storage.get_character_stats(name.casefold()):
            await interaction.response.send_message(ERR_CHARACTER_EXISTS, ephemeral=True)
            return
            
        # Save image and create stats
        ext = attachment.filename[attachment.filename.rfind('.'):]
        await attachment.save(Path(IMAGES_DIR) / f"{name.casefold()}{ext}")
        storage.update_character_stats(name.casefold())
        
        await interaction.response.send_message(
            SUCCESS_CHARACTER_ADDED.format(name=name),
            ephemeral=False
        )

    @app_commands.command(
        name='updategroup',
        description='Update an unsorted character\'s group'
    )
    @app_commands.guilds(discord.Object(id=MAIN_GUILD_ID))
    @app_commands.describe(
        name='The character\'s name',
        group='The desired group'
    )
    async def update_group(
        self,
        interaction: discord.Interaction,
        name: str,
        group: str
    ) -> None:
        """Update a character's group."""
        if not name or not group:
            await interaction.response.send_message(
                "You forgot something",
                ephemeral=True
            )
            return
            
        if group not in CHARACTER_GROUPS:
            await interaction.response.send_message(
                ERR_INVALID_GROUP.format(group=group),
                ephemeral=True
            )
            return
            
        try:
            print(f'\n{interaction.user.nick} is updating a group: {name} {group}')
            char_stats = storage.get_character_stats(name.casefold())
            
            if char_stats.group != "_unsorted":
                await interaction.response.send_message(
                    ERR_ALREADY_IN_GROUP.format(
                        name=name,
                        group=char_stats.group
                    ),
                    ephemeral=True
                )
            else:
                storage.update_character_stats(name.casefold(), group=group)
                await interaction.response.send_message(
                    SUCCESS_GROUP_UPDATED.format(name=name, group=group)
                )
        except Exception as e:
            print(f"Error updating group: {e}")
            await interaction.response.send_message(
                ERR_CHARACTER_NOT_FOUND.format(name=name),
                ephemeral=True
            )

    @app_commands.command(
        name='submittools',
        description='Submit or make changes to a tool'
    )
    @app_commands.guilds(discord.Object(id=MAIN_GUILD_ID))
    @app_commands.describe(
        name='The name of the tool',
        attachment='The tool\'s image',
        default='The default multiplier',
        characters='name,multiplier pairs (comma separated)'
    )
    async def submit_tool(
        self,
        interaction: discord.Interaction,
        name: str,
        default: float,
        attachment: discord.Attachment,
        characters: Optional[str] = None
    ) -> None:
        """Submit a new tool or update an existing one."""
        try:
            print(f'\n{interaction.user.nick} is adding a tool: {name}')
            
            if name in storage.tool_stats:
                await interaction.response.send_message(
                    ERR_TOOL_EXISTS,
                    ephemeral=True
                )
                return
                
            if not is_valid_image_path(attachment.filename):
                await interaction.response.send_message(
                    ERR_INVALID_PATH,
                    ephemeral=True
                )
                return
                
            # Save image
            ext = attachment.filename[attachment.filename.rfind('.'):]
            await attachment.save(Path(TOOLS_DIR) / f"{name}{ext}")
            
            # Create tool stats
            multipliers = {}
            if characters:
                stats = characters.split(', ')
                for i in range(0, len(stats), 2):
                    if i + 1 < len(stats):
                        char_name = stats[i]
                        multiplier = float(stats[i + 1])
                        multipliers[char_name] = multiplier
                        print(f'Character {char_name} added with {multiplier}')
                        
            storage.tool_stats[name] = {
                "default_multiplier": default,
                "group": "None",
                "character_multipliers": multipliers
            }
            storage.save_all()
            
            await interaction.response.send_message(
                SUCCESS_TOOL_ADDED.format(name=name),
                ephemeral=False
            )
            
        except Exception as e:
            print(f"Error submitting tool: {e}")
            await interaction.response.send_message(ERR_MISSING_IMAGE)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCommands(bot)) 