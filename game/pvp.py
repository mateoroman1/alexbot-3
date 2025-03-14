from typing import Optional, Tuple, List
from pathlib import Path
import random
import asyncio
import discord

from config.config import IMAGES_DIR, TOOLS_DIR
from data.storage import storage
from game.stats import StatsManager
from utils.embeds import create_pvp_join_embed, create_pvp_battle_embed
from utils.helpers import roll_character, roll_tool, calculate_damage_multiplier

class PVPView(discord.ui.View):
    def __init__(self, pvp_manager, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.pvp_manager = pvp_manager
        self.has_challenger = False  # Add flag to track if we have a challenger
        
    @discord.ui.button(label="Accept Challenge", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Don't allow host to join their own PVP
            if interaction.user.name == self.pvp_manager.host_name:
                await interaction.response.send_message(
                    "You cannot accept your own challenge!",
                    ephemeral=True
                )
                return
                
            # Don't allow joining if we already have a challenger
            if self.has_challenger:
                await interaction.response.send_message(
                    "This PVP match already has two players!",
                    ephemeral=True
                )
                return
                
            print(f"User {interaction.user.name} clicked join button")
            
            # Set challenger and disable button
            self.pvp_manager.challenger_name = interaction.user.name
            self.has_challenger = True
            button.disabled = True
            
            # Acknowledge the interaction first
            await interaction.response.defer()
            
            # Update the message with disabled button
            await interaction.message.edit(view=self)
            
            # Start the battle in a new task to avoid blocking
            self.pvp_manager.bot.loop.create_task(self.pvp_manager._conduct_pvp_battle())
            
        except Exception as e:
            print(f"Error in join button: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await interaction.followup.send("An error occurred while joining the PVP.", ephemeral=True)
        
    async def on_timeout(self):
        # Disable the button when the view times out
        for child in self.children:
            child.disabled = True
        # Message will be handled by the PVPManager

class PVPManager:
    def __init__(self, host_name: str, channel, bot: discord.Client):
        self.host_name = host_name
        self.challenger_name: Optional[str] = None
        self.channel = channel
        self.bot = bot  # Store bot reference for creating tasks
        self.is_active = False
        self.host_wins = 0
        self.challenger_wins = 0
        self.current_round = 0
        self.timeout = 60  # 60 seconds timeout for joining

    async def start_pvp(self) -> bool:
        """Start a PVP session and wait for a challenger to join."""
        try:
            print(f"Starting PVP session hosted by {self.host_name}")
            self.is_active = True
            
            # Create and send join embed with button
            embed = create_pvp_join_embed(self.host_name)
            view = PVPView(self)
            message = await self.channel.send(embed=embed, view=view)
            
            # Wait for the view to timeout or for battle to complete
            await view.wait()
            
            # If no one joined, send timeout message
            if not self.challenger_name:
                print("PVP session timed out - no challenger joined")
                await self.channel.send(f"PVP session expired - no one accepted {self.host_name}'s challenge!")
                self.is_active = False
                return False
                
            return True
            
        except Exception as e:
            print(f"Error in start_pvp: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            self.is_active = False
            return False

    async def _conduct_pvp_battle(self) -> None:
        """Conduct the best-of-3 PVP battle."""
        try:
            print("Starting PVP battle")
            await self.channel.send(f"🏁 {self.challenger_name} has accepted the challenge! Battle starting...")
            await asyncio.sleep(2)  # Longer initial delay
            
            # Roll characters for both players and announce them
            host_char = roll_character()
            challenger_char = roll_character()
            
            # Announce host's character with image
            await self.channel.send(
                f"{self.host_name} enters the arena with {host_char.split('.')[0]}!",
                file=discord.File(f"{IMAGES_DIR}/{host_char}")
            )
            await asyncio.sleep(3)  # Longer delay between character announcements
            
            # Announce challenger's character with image
            await self.channel.send(
                f"{self.challenger_name} enters the arena with {challenger_char.split('.')[0]}!",
                file=discord.File(f"{IMAGES_DIR}/{challenger_char}")
            )
            await asyncio.sleep(3)  # Longer delay before battle starts
        
            
            while self.host_wins < 2 and self.challenger_wins < 2:
                self.current_round += 1
                print(f"Starting round {self.current_round}")
                
                # Roll tools for the round
                host_tool = roll_tool()
                challenger_tool = roll_tool()
                
                # Announce tools with images
                await self.channel.send(
                    f"{host_char.split('.')[0]} uses {host_tool.split('.')[0]}!",
                    file=discord.File(f"{TOOLS_DIR}/{host_tool}")
                )
                await asyncio.sleep(3)  # Delay between tool announcements
                
                await self.channel.send(
                    f"{challenger_char.split('.')[0]} uses {challenger_tool.split('.')[0]}!",
                    file=discord.File(f"{TOOLS_DIR}/{challenger_tool}")
                )
                await asyncio.sleep(2)  # Delay before damage calculation
                
                # Calculate damage using helper function
                host_damage = calculate_damage_multiplier(
                    host_char.split('.')[0].casefold(),
                    host_tool.split('.')[0]
                )
                challenger_damage = calculate_damage_multiplier(
                    challenger_char.split('.')[0].casefold(),
                    challenger_tool.split('.')[0]
                )
                
                # Update character stats
                storage.update_character_stats(host_char.split('.')[0].casefold(), total_pvp=+1)
                storage.update_character_stats(challenger_char.split('.')[0].casefold(), total_pvp=+1)
                
                # Determine round winner
                round_winner = self.host_name if host_damage > challenger_damage else self.challenger_name
                winner_char = host_char if host_damage > challenger_damage else challenger_char
                winner_damage = host_damage if host_damage > challenger_damage else challenger_damage
                
                if host_damage > challenger_damage:
                    self.host_wins += 1
                    storage.update_character_stats(host_char.split('.')[0].casefold(), pvp_wins=+1)
                else:
                    self.challenger_wins += 1
                    storage.update_character_stats(challenger_char.split('.')[0].casefold(), pvp_wins=+1)
                    
                print(f"Round {self.current_round} winner: {round_winner}")
                
                # Create and send battle results embed
                embed = discord.Embed(
                    title=f"Round {self.current_round} Winner: {round_winner}",
                    description=f"{winner_char.split('.')[0]} deals {winner_damage:.2f} damage!",
                    color=discord.Color.gold()
                )
                
                # Add battle stats
                embed.add_field(
                    name=f"{self.host_name}'s Damage",
                    value=f"{host_damage:.2f}",
                    inline=True
                )
                embed.add_field(
                    name=f"{self.challenger_name}'s Damage",
                    value=f"{challenger_damage:.2f}",
                    inline=True
                )
                embed.add_field(
                    name="Match Score",
                    value=f"{self.host_name}: {self.host_wins} | {self.challenger_name}: {self.challenger_wins}",
                    inline=False
                )
                
                # Set the winner's character as the embed image
                embed.set_thumbnail(url="attachment://winner.png")
                await self.channel.send(
                    embed=embed,
                    file=discord.File(f"{IMAGES_DIR}/{winner_char}", filename="winner.png")
                )
                await asyncio.sleep(4)  # Longer delay between rounds
                
            # Update stats for winner
            winner = self.host_name if self.host_wins > self.challenger_wins else self.challenger_name
            winner_char = host_char if self.host_wins > self.challenger_wins else challenger_char
            StatsManager.increment_pvp_wins(winner)
            
            # Update user stats
            storage.update_user_stats(self.host_name, total_pvp=+1)
            storage.update_user_stats(self.challenger_name, total_pvp=+1)
            storage.update_user_stats(winner, pvp_wins=+1)
            
            # Send final victory message with winner's character
            await self.channel.send(
                f"🏆 {winner} wins the PVP battle with {winner_char.split('.')[0]}!",
                file=discord.File(f"{IMAGES_DIR}/{winner_char}")
            )
            storage.save_all()
            
        except Exception as e:
            print(f"Error in conduct_pvp_battle: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await self.channel.send("An error occurred during the PVP battle.")
        finally:
            self.is_active = False 