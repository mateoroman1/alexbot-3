import asyncio
from typing import List, Optional, Dict, Union, Tuple
import discord
from pathlib import Path

from config.config import (
    RAID_TIMEOUT,
    RAID_HARDMODE_THRESHOLD,
    RAID_NIGHTMARE_THRESHOLD,
    HARDMODE_HEALTH_MULTIPLIER,
    NIGHTMARE_HEALTH_MULTIPLIER,
    CAMPAIGN_HEALTH_SCALING,
    ASSETS_DIR,
    EVOLUTIONS_DIR,
    IMAGES_DIR,
    TOOLS_DIR,
    BOSSES_DIR
)
from config.messages import *
from data.models import RaidState, RaidHand, RaidMode, EVOLUTION_RECIPES
from data.storage import storage
from utils.helpers import roll_character, roll_tool, roll_boss, calculate_damage_multiplier
from utils.embeds import create_raid_join_embed, create_death_vote_embed

class JoinRaidButton(discord.ui.View):
    def __init__(self, host: str, *, timeout: int = RAID_TIMEOUT):
        super().__init__(timeout=timeout)
        self.players = [host]
        self.count = 1
        self.embed = discord.Embed()

    @discord.ui.button(label=BTN_JOIN_RAID, style=discord.ButtonStyle.primary)
    async def raid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.players:
            button.style = discord.ButtonStyle.success
            self.count += 1
            button.label = BTN_PLAYERS.format(count=self.count)
            self.players.append(interaction.user.name)
            storage.update_user_stats(interaction.user.name, total_raids=+1)
            
            if len(self.players) > 1:
                self.embed.add_field(name="Raid Member:", value=self.players[self.count-1])
                
            try:
                await interaction.response.edit_message(view=self, embed=self.embed)
            except Exception as e:
                print(f"Error in raid button: {e}")

    @discord.ui.button(label=BTN_START_RAID, style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.players) > 0 and interaction.user.name == self.players[0]:
            button.label = BTN_STARTING
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

class RaidManager:
    def __init__(self, mode: RaidMode, server_name: str):
        self.mode = mode
        self.server_name = server_name
        self.raid_state: Optional[RaidState] = None

    async def start_raid(self, ctx: discord.ext.commands.Context) -> bool:
        """Start a new raid session."""
        try:
            print("Checking server raid status...")
            server_stats = storage.get_server_stats(self.server_name)
            if server_stats.active_raid:
                print("Raid already in progress")
                await ctx.send(ERR_RAID_IN_PROGRESS)
                return False

            print("Setting active raid status...")
            storage.update_server_stats(self.server_name, active_raid=True)
            view = JoinRaidButton(ctx.author.name)
            
            # Initialize raid state
            print("Rolling boss...")
            boss = roll_boss(self.mode.value, self.server_name)
            print(f"Boss rolled: {boss}")
            
            print("Getting boss stats...")
            boss_name = boss.split(".")[0]
            boss_stats = storage.get_boss_stats(boss_name)
            if not boss_stats:
                print(f"Error: No stats found for boss {boss_name}")
                await ctx.send(f"Error: Could not find stats for boss {boss_name}")
                storage.update_server_stats(self.server_name, active_raid=False)
                return False
            print(f"Boss stats retrieved: {boss_stats}")
            
            print("Creating raid state...")
            self.raid_state = RaidState(
                player_list=list(view.players),
                boss=boss,
                boss_health=boss_stats.health * (1 + CAMPAIGN_HEALTH_SCALING * server_stats.campaign_completed),
                boss_weakness=boss_stats.weakness
            )
            print("Raid state created")

            # Create and send join embed
            print("Creating raid embed...")
            embed = create_raid_join_embed(view.players[0], boss_stats.wake_message)
            print("Embed created")
            
            print("Setting up embed image...")
            image_path = ASSETS_DIR / ("classic.png" if self.mode == RaidMode.CLASSIC else "campaign.png")
            if not image_path.exists():
                print(f"Error: Image not found at {image_path}")
                await ctx.send("Error: Could not find raid mode image")
                storage.update_server_stats(self.server_name, active_raid=False)
                return False
            
            file = discord.File(image_path, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
            view.embed = embed
            print("Embed image setup complete")
            
            print("Sending raid join message...")
            await ctx.send(view=view, embed=embed, file=file)
            print("Join message sent")
            
            # Wait for raid to start
            print("Waiting for raid to start...")
            timeout = RAID_TIMEOUT
            while not view.children[1].disabled and timeout > 0:
                await asyncio.sleep(1)
                timeout -= 1
                if timeout % 5 == 0:
                    print(f"Waiting... {timeout} seconds remaining")
            
            
            print("Raid starting with players:", view.players)
            self.raid_state.player_list = list(view.players)
            
            # Apply difficulty modifiers
            if len(self.raid_state.player_list) >= RAID_NIGHTMARE_THRESHOLD:
                self.raid_state.boss_health *= NIGHTMARE_HEALTH_MULTIPLIER
                self.raid_state.nightmare = True
                print("Nightmare mode activated")
            elif len(self.raid_state.player_list) >= RAID_HARDMODE_THRESHOLD:
                self.raid_state.boss_health *= HARDMODE_HEALTH_MULTIPLIER
                self.raid_state.hard_mode = True
                print("Hard mode activated")
            
            return True
        except Exception as e:
            print(f"Error in start_raid: {e}")
            storage.update_server_stats(self.server_name, active_raid=False)
            return False

    async def draw_cards(self) -> None:
        """Draw cards for all players in the raid."""
        evolution_check = []
        
        for player in self.raid_state.player_list:
            # Draw character and tool
            character = roll_character()
            tool = roll_tool()
            evolution_check.append(tool.split('.')[0])
            
            # Calculate damage
            damage = calculate_damage_multiplier(
                character.split('.')[0].casefold(),
                tool.split('.')[0]
            )
            
            # Create hand
            self.raid_state.player_data[player] = RaidHand(
                character=character,
                tool=tool,
                damage_index=damage
            )
            
        # Check for evolutions
        for evolved, recipe in EVOLUTION_RECIPES.items():
            if recipe[0] in evolution_check and recipe[1] in evolution_check:
                self.raid_state.player_data["evolutions_FLAG"] = (evolved, recipe[0], recipe[1])

    async def process_special_tools(self, ctx: discord.ext.commands.Context, player: str, hand: RaidHand) -> List[discord.File]:
        """Process special tool effects."""
        files = []
        
        if hand.tool == 'backup.jpg':
            try:
                backup_character = roll_character()
                backup_tool = roll_tool()
                backup_hand = RaidHand(
                    character=backup_character,
                    tool=backup_tool,
                    damage_index=calculate_damage_multiplier(
                        backup_character.split('.')[0].casefold(),
                        backup_tool.split('.')[0]
                    )
                )
                files.extend([
                    discord.File(f"{IMAGES_DIR}/{backup_hand.character}"),
                    discord.File(f"{TOOLS_DIR}/{backup_hand.tool}")
                ])
                hand.damage_index += backup_hand.damage_index
            except Exception as e:
                print(f"Backup tool failed: {e}")
                
        elif hand.tool == 'convoy.jpg':
            try:
                for _ in range(5):
                    convoy_character = roll_character()
                    convoy_hand = RaidHand(
                        character = convoy_character,
                        tool=None,
                        damage_index=calculate_damage_multiplier(
                            convoy_character.split('.')[0].casefold(),
                            None
                        )
                    )
                    files.append(discord.File(f"{IMAGES_DIR}/{convoy_hand.character}"))
                    hand.damage_index += convoy_hand.damage_index
            except Exception as e:
                print(f"Convoy tool failed: {e}")
                
        elif hand.tool == 'Call of the wild.png':
            try:
                for _ in range(5):
                    character = roll_character(lambda c: storage.get_character_stats(c).group == "non human")
                    wild_hand = RaidHand(
                        character=character,
                        tool=None,
                        damage_index=calculate_damage_multiplier(
                            character.split('.')[0].casefold(),
                            None
                        )
                    )
                    files.append(discord.File(f"{IMAGES_DIR}/{wild_hand.character}"))
                    hand.damage_index += wild_hand.damage_index
            except Exception as e:
                print(f"Call of the Wild failed: {e}")
                
        return files

    async def process_raid_results(self, ctx: discord.ext.commands.Context) -> None:
        """Process and display raid results."""
        await self.draw_cards()
        total_damage = 0
        hand_files = []
        groups = []

        # Process each player's hand
        for player, data in self.raid_state.player_data.items():
            if player == "evolutions_FLAG":
                await ctx.send(
                    EVOLUTION_UNLOCK.format(tool1=data[1], tool2=data[2]),
                    file=discord.File(f"{EVOLUTIONS_DIR}/{data[0]}.gif")
                )
                total_damage *= storage.get_tool_stats(data[0]).default_multiplier
                break

            if isinstance(data, RaidHand):
                # Update character stats
                char_name = data.character.split(".")[0].casefold()
                storage.update_character_stats(
                    char_name,
                    raids_completed=+1
                )

                # Add base hand files
                hand_files = [
                    discord.File(f"{IMAGES_DIR}/{data.character}"),
                    discord.File(f"{TOOLS_DIR}/{data.tool}")
                ]

                # Track groups for combo
                char_stats = storage.get_character_stats(char_name)
                if char_stats.group != "_unsorted":
                    groups.append(char_stats.group)

                # Process special tools
                special_files = await self.process_special_tools(ctx, player, data)
                hand_files.extend(special_files)

                # Check weakness
                if (self.raid_state.boss_weakness == char_stats.group or
                    self.raid_state.boss_weakness == char_name or
                    self.raid_state.boss_weakness == data.tool.split('.')[0]):
                    await ctx.send(RAID_WEAKNESS.format(weakness=self.raid_state.boss_weakness))
                    data.damage_index *= 2

                # Display hand
                await ctx.send(
                    f"{player}'s hand, dealing {round(data.damage_index, 2)} damage:",
                    files=hand_files
                )
                
                # Update stats
                storage.update_user_stats(
                    player,
                    total_damage=round(data.damage_index, 2)
                )
                total_damage += round(data.damage_index, 0)
                hand_files.clear()
                await asyncio.sleep(5)

        # Process group combos
        if len(groups) != len(set(groups)):
            combo = len(groups) - len(set(groups))
            combo *= 2
            
            try:
                groups_check = set()
                combo_groups = [g for g in groups if g in groups_check or groups_check.add(g)]
                groups_string = ", ".join(combo_groups)
                await ctx.send(RAID_GROUP_COMBO.format(groups=groups_string, combo=combo))
            except:
                await ctx.send(RAID_GROUP_COMBO.format(groups=combo, combo=combo))
                
            total_damage *= combo

        # Display boss
        await ctx.send(file=discord.File(f"{BOSSES_DIR}/{self.raid_state.boss}"))
        storage.update_server_stats(self.server_name, total_raids=+1)

        # Process outcome
        if self.raid_state.boss_health > total_damage:
            if self.raid_state.boss.split(".")[0] == "death":
                await ctx.send(RAID_DEATH_DEFEAT)
                await self.process_death_vote(ctx)
            else:
                await ctx.send(
                    RAID_DEFEAT.format(
                        boss=self.raid_state.boss.split(".")[0],
                        health=self.raid_state.boss_health - total_damage,
                        boss_name=self.raid_state.boss.split(".")[0]
                    )
                )
                storage.update_boss_stats(
                    self.raid_state.boss.split(".")[0],
                    times_won=+1
                )
        else:
            await ctx.send(
                RAID_VICTORY.format(
                    boss=self.raid_state.boss.split(".")[0],
                    damage=total_damage
                )
            )
            
            boss_name = self.raid_state.boss.split(".")[0]
            storage.update_boss_stats(boss_name, times_defeated=+1)
            storage.update_server_stats(
                self.server_name,
                raid_wins=+1,
                total_damage=total_damage
            )

            if self.mode == RaidMode.CAMPAIGN:
                if boss_name == "KRYPTIS ZYPHER":
                    await ctx.send(file=discord.File(f"{ASSETS_DIR}/demise.gif"))
                    storage.update_server_stats(self.server_name, campaign="death")
                    
                boss_stats = storage.get_boss_stats(boss_name)
                if boss_stats.campaign_id == "COMPLETE":
                    storage.update_server_stats(
                        self.server_name,
                        campaign=boss_stats.campaign_id,
                        campaign_completed=+1
                    )
                    self.new_game()
                else:
                    storage.update_server_stats(
                        self.server_name,
                        campaign=boss_stats.campaign_id
                    )

            # Update player stats
            for player in self.raid_state.player_list:
                storage.update_user_stats(player, raid_wins=+1)
                
            # Update character stats
            for hand in self.raid_state.player_data.values():
                if isinstance(hand, RaidHand):
                    char_name = hand.character.split(".")[0].casefold()
                    storage.update_character_stats(char_name, raids_won=+1)
                    
                    if hand.tool:
                        tool_name = hand.tool.split(".")[0]
                        tool_stats = storage.get_tool_stats(tool_name)
                        multiplier_increase = (
                            0.20 if self.raid_state.nightmare else
                            0.10 if self.raid_state.hard_mode else
                            0.05
                        )
                        if tool_stats.character_multipliers.get(char_name):
                            tool_stats.character_multipliers[char_name] += multiplier_increase
                        else: 
                            tool_stats.character_multipliers[char_name] = (tool_stats.default_multiplier + multiplier_increase)

        # Cleanup
        storage.update_server_stats(self.server_name, active_raid=False)
        storage.save_all()

    def new_game(self) -> None:
        """Start a new game cycle."""
        for boss_name, stats in storage.boss_stats.items():
            if boss_name != "death":
                stats.health *= 1.25

    async def process_death_vote(self, ctx: discord.ext.commands.Context) -> None:
        """Process death vote sequence."""
        embed = create_death_vote_embed()
        brave = 0
        coward = 0
        
        view = discord.ui.View()
        
        async def try_again_callback(interaction: discord.Interaction):
            nonlocal brave, view
            brave += 1
            view.clear_items()
            embed.clear_fields()
            storage.update_server_stats(self.server_name, campaign="death")
            embed.color = discord.Colour.dark_blue()
            embed.title = DEATH_RETRY
            await interaction.response.edit_message(embed=embed, view=view)
            
        async def retreat_callback(interaction: discord.Interaction):
            nonlocal coward, view
            coward += 1
            view.clear_items()
            embed.clear_fields()
            storage.update_server_stats(self.server_name, campaign="COMPLETE")
            file = discord.File(ASSETS_DIR / "coward.gif", filename="coward.gif")
            embed.set_image(url="attachment://coward.gif")
            embed.color = discord.Colour.dark_red()
            embed.title = DEATH_RETREAT
            await interaction.response.edit_message(embed=embed, view=view, attachments=[file])
            
        try_again = discord.ui.Button(label=BTN_TRY_AGAIN, style=discord.ButtonStyle.success)
        retreat = discord.ui.Button(label=BTN_RETREAT, style=discord.ButtonStyle.danger)
        
        try_again.callback = try_again_callback
        retreat.callback = retreat_callback
        
        view.add_item(try_again)
        view.add_item(retreat)
        view.timeout = 7
        
        message = await ctx.send(embed=embed, view=view)
        
        if brave == 0 and coward == 0:
            try:
                await retreat_callback(message.interaction)
            except:
                storage.update_server_stats(self.server_name, campaign="COMPLETE") 