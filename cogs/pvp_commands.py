import discord
from discord import app_commands
from discord.ext import commands

from game.pvp import PVPManager

class PVPCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_pvp_sessions = {}

    @commands.hybrid_command(
        name='pvp',
        with_app_command=True,
        help='Start a PVP battle'
    )
    async def pvp(self, ctx: commands.Context) -> None:
        """Start a PVP battle session."""
        try:
            print(f"\nPVP command called by {ctx.author.name}")
            
            # Defer response if this is a slash command
            if isinstance(ctx, discord.Interaction) or ctx.interaction:
                await ctx.defer()
                print("Interaction deferred")
            
            # Check if user already has an active PVP session
            if ctx.author.name in self.active_pvp_sessions:
                await ctx.send("You already have an active PVP session!", ephemeral=True)
                return
                
            # Check if user is in an active raid
            # if ctx.channel.id in self.bot.get_cog('RaidCommands').active_raids:
            #     raid = self.bot.get_cog('RaidCommands').active_raids[ctx.channel.id]
            #     if raid.is_active and ctx.author.name in raid.participants:
            #         await ctx.send("You cannot start a PVP while in an active raid!", ephemeral=True)
            #         return
            
            # Create new PVP session
            pvp = PVPManager(ctx.author.name, ctx.channel, self.bot)
            self.active_pvp_sessions[ctx.author.name] = pvp
            
            # Start the PVP session
            success = await pvp.start_pvp()
            
            if not success:
                del self.active_pvp_sessions[ctx.author.name]
            
        except Exception as e:
            print(f"Error in pvp command: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)
            if ctx.author.name in self.active_pvp_sessions:
                del self.active_pvp_sessions[ctx.author.name]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PVPCommands(bot)) 