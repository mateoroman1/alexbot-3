from typing import List, Optional, Union
import discord
from pathlib import Path

from config.messages import *
from config.config import ASSETS_DIR
from data.models import CharacterStats, UserStats, ServerStats

def create_raid_join_embed(host: str, boss_message: str) -> discord.Embed:
    """Create the raid join embed."""
    embed = discord.Embed(title=boss_message, color=discord.Color.gold())
    embed.add_field(name="Host:", value=host)
    return embed

def create_character_stats_embed(
    name: str,
    stats: CharacterStats,
    image_path: Optional[Path] = None
) -> discord.Embed:
    """Create character stats embed."""
    embed = discord.Embed(
        title=EMBED_CHARACTER_STATS.format(name=name),
        color=discord.Color.dark_red()
    )
    embed.add_field(name="# Rolls: ", value=stats.count, inline=True)
    embed.add_field(name="Raids Won: ", value=stats.raids_won, inline=True)
    embed.add_field(name="Raids Completed: ", value=stats.raids_completed, inline=True)
    embed.add_field(name="Group: ", value=stats.group, inline=True)
    
    if image_path:
        embed.set_thumbnail(url="attachment://image.png")
        
    return embed

def create_user_stats_embed(
    name: str,
    stats: UserStats,
    avatar_url: Optional[str] = None
) -> discord.Embed:
    """Create user stats embed."""
    embed = discord.Embed(title=f'{name}\'s Stats:')
    
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)
        
    embed.add_field(name='Total Rolls:', value=stats.total_rolls)
    embed.add_field(name='Raid Wins:', value=stats.raid_wins)
    embed.add_field(name='Highest Damage:', value=stats.highest_damage)
    embed.add_field(name='Average Raid Damage:', value=round(stats.average_damage, 2))
    embed.add_field(name='Total Raids:', value=stats.total_raids)
    embed.add_field(name='EX Cards Owned:', value=len(stats.deck))
    
    return embed

def create_server_stats_embed(
    server: str,
    stats: ServerStats,
    icon_url: Optional[str] = None
) -> discord.Embed:
    """Create server stats embed."""
    embed = discord.Embed(title=EMBED_SERVER_STATS.format(server=server))
    
    if icon_url:
        embed.set_thumbnail(url=icon_url)
        
    embed.add_field(name='Total Rolls:', value=stats.total_rolls)
    embed.add_field(name='Raid Wins:', value=stats.raid_wins)
    embed.add_field(name='Users:', value=stats.users)
    embed.add_field(name='Campaign Tier:', value=stats.campaign_completed)
    embed.add_field(name='Total Raids:', value=stats.total_raids)
    embed.add_field(name='EX Cards Rolled:', value=stats.ex_cards)
    
    return embed

def create_highest_rolls_embed(
    names: Union[str, List[str]],
    count: int,
    is_tie: bool = False
) -> discord.Embed:
    """Create highest rolls embed."""
    embed = discord.Embed(
        title=EMBED_HIGHEST_ROLL_TIE if is_tie else EMBED_HIGHEST_ROLL,
        color=discord.Color.red()
    )
    
    if isinstance(names, list):
        embed.add_field(name=count, value=", ".join(names))
    else:
        embed.add_field(name=names, value=count, inline=True)
        
    return embed

def create_raid_master_embed(
    name: str,
    wins: int,
    image_path: Optional[Path] = None
) -> discord.Embed:
    """Create raid master embed."""
    embed = discord.Embed(title=EMBED_RAID_MASTER, color=discord.Color.red())
    embed.add_field(name=name, value=wins, inline=True)
    
    if image_path:
        embed.set_thumbnail(url="attachment://image.png")
        
    return embed

def create_death_vote_embed() -> discord.Embed:
    """Create death vote embed."""
    return discord.Embed(title=DEATH_PROMPT)

def create_library_embed(name: str) -> discord.Embed:
    """Create library embed."""
    embed = discord.Embed(title=EMBED_LIBRARY.format(name=name))
    embed.add_field(name="No EX cards were found. Try !roll to find one!", value=None)
    return embed

def create_pvp_join_embed(host_name: str) -> discord.Embed:
    """Create an embed for users to join a PVP battle."""
    embed = discord.Embed(
        title="Alexbot PvP",
        description=f"{host_name} challenges anyone to a PVP battle!",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Format",
        value="Best of 3\nOne character, random tools\nHighest damage wins."
    )
    embed.set_footer(text="This challenge will expire in 60 seconds")
    return embed

def create_pvp_battle_embed(
    host_name: str,
    challenger_name: str,
    host_char: str,
    challenger_char: str,
    tool: str,
    host_damage: float,
    challenger_damage: float,
    round_winner: str,
    host_wins: int,
    challenger_wins: int,
    current_round: int
) -> discord.Embed:
    """Create an embed for a PVP battle round."""
    embed = discord.Embed(
        title=f"⚔️ PVP Battle - Round {current_round}",
        color=discord.Color.gold()
    )
    
    # Add player fields
    embed.add_field(
        name=f"{host_name} ({host_wins} wins)",
        value=f"Character: {host_char}\nDamage: {host_damage:.2f}",
        inline=True
    )
    embed.add_field(
        name=f"{challenger_name} ({challenger_wins} wins)",
        value=f"Character: {challenger_char}\nDamage: {challenger_damage:.2f}",
        inline=True
    )
    
    # Add tool field
    embed.add_field(
        name="Tool Used",
        value=tool,
        inline=False
    )
    
    # Add round winner
    embed.add_field(
        name="Round Winner",
        value=f"🏆 {round_winner}",
        inline=False
    )
    
    return embed 