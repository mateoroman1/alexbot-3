from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from config.config import MAIN_GUILD_ID, ALEXBOT_GUILD_ID
from config.messages import *
from data.models import RaidMode
from game.raid import RaidManager

class RaidCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(
        name='raid',
        description='Start a PvE raid!'
    )
    @app_commands.guilds(discord.Object(id=MAIN_GUILD_ID), discord.Object(id=ALEXBOT_GUILD_ID))
    @app_commands.choices(mode=[
        app_commands.Choice(name="Campaign", value="campaign"),
        app_commands.Choice(name="Classic", value="classic")
    ])
    async def raid(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str]
    ) -> None:
        """Start a raid battle."""
        try:
            print(f"\nRaid initiated by {interaction.user.name}")
            print(f"Mode selected: {mode.value}")
            
            # Create raid manager
            raid_manager = RaidManager(
                RaidMode(mode.value),
                interaction.guild.name
            )
            
            # Initial response and context setup
            await interaction.response.defer(ephemeral=False)
            print("Interaction deferred")
            
            # Create custom context
            ctx = await commands.Context.from_interaction(interaction)
            ctx.send = lambda *args, **kwargs: interaction.followup.send(*args, **kwargs)
            ctx.channel = interaction.channel
            print("Context created with channel:", ctx.channel)
            
            # Start raid
            print("Starting raid...")
            await interaction.followup.send("Starting raid...")
            
            if await raid_manager.start_raid(ctx):
                print("Raid started successfully, processing results...")
                await raid_manager.process_raid_results(ctx)
                print("Raid completed")
            else:
                print("Raid failed to start")
                await interaction.followup.send(
                    "Failed to start raid. There may already be one in progress.",
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"\nError in raid command: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            error_msg = f"An error occurred during the raid instance: {str(e)}"
            if not interaction.response.is_done():
                await interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await interaction.followup.send(error_msg, ephemeral=True)

    @commands.command(name='raidResults')
    async def raid_results(
        self,
        ctx: commands.Context,
        raid_state: RaidManager,
        mode: str
    ) -> None:
        """Process raid results (internal command)."""
        await raid_state.process_raid_results(ctx)

    @commands.command(name='deathVotes')
    async def death_votes(self, ctx: commands.Context) -> None:
        """Process death vote sequence (internal command)."""
        raid_manager = RaidManager(RaidMode.CAMPAIGN, ctx.guild.name)
        await raid_manager.process_death_vote(ctx)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RaidCommands(bot)) 