from typing import Optional, Tuple, List
from pathlib import Path
import random
import asyncio

from config.config import IMAGES_DIR
from data.storage import storage
from game.stats import StatsManager
from utils.embeds import create_pvp_join_embed, create_pvp_battle_embed
from utils.helpers import get_image_extension
import discord

class PVPView(discord.ui.View):
    def __init__(self, pvp_manager, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.pvp_manager = pvp_manager
        
    @discord.ui.button(label="Accept Challenge", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Don't allow host to join their own PVP
        if interaction.user.name == self.pvp_manager.host_name:
            await interaction.response.send_message(
                "You cannot accept your own challenge!",
                ephemeral=True
            )
            return
            
        # Set challenger and disable button
        self.pvp_manager.challenger_name = interaction.user.name
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Start the battle
        await self.pvp_manager._conduct_pvp_battle()
        
    async def on_timeout(self):
        # Disable the button when the view times out
        for child in self.children:
            child.disabled = True
        # Message will be handled by the PVPManager

class PVPManager:
    def __init__(self, host_name: str, channel):
        self.host_name = host_name
        self.challenger_name: Optional[str] = None
        self.channel = channel
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
        print("Starting PVP battle")
        await self.channel.send(f"🏁 {self.challenger_name} has accepted the challenge! Battle starting...")
        
        while self.host_wins < 2 and self.challenger_wins < 2:
            self.current_round += 1
            
            # Roll characters for both players
            host_char = random.choice(list(storage.character_stats.keys()))
            challenger_char = random.choice(list(storage.character_stats.keys()))
            
            # Roll a tool for the round
            tool = random.choice(list(storage.tool_stats.keys()))
            tool_stats = storage.get_tool_stats(tool)
            
            # Calculate damage
            host_char_stats = storage.get_character_stats(host_char)
            challenger_char_stats = storage.get_character_stats(challenger_char)
            
            host_damage = host_char_stats.count * tool_stats.damage_multiplier
            challenger_damage = challenger_char_stats.count * tool_stats.damage_multiplier
            
            # Determine round winner
            round_winner = self.host_name if host_damage > challenger_damage else self.challenger_name
            if host_damage > challenger_damage:
                self.host_wins += 1
            else:
                self.challenger_wins += 1
                
            # Create and send battle embed
            embed = create_pvp_battle_embed(
                self.host_name,
                self.challenger_name,
                host_char,
                challenger_char,
                tool,
                host_damage,
                challenger_damage,
                round_winner,
                self.host_wins,
                self.challenger_wins,
                self.current_round
            )
            
            await self.channel.send(embed=embed)
            await asyncio.sleep(2)  # Brief pause between rounds
            
        # Update stats for winner
        winner = self.host_name if self.host_wins > self.challenger_wins else self.challenger_name
        StatsManager.increment_pvp_wins(winner)
        
        await self.channel.send(f"🏆 {winner} wins the PVP battle!")
        self.is_active = False 