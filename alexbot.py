from typing import Any, Optional
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import json
import asyncio
from fuzzywuzzy import fuzz

load_dotenv()
newCounts = {}
bossCounts = {}
toolStats = {}
userStats = {}
serverStats = {}
activeRaid = False

script_directory = os.path.abspath(os.path.dirname(__file__))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=108378541988515840, tree = tree, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)

def load_stats():
    global newCounts
    global bossCounts
    global toolStats
    global userStats
    global serverStats
    try:
        with open('character_stats.json', 'r', encoding="utf8") as char_file:
            newCounts = json.load(char_file)
        with open('bossStats.json', 'r', encoding="utf8") as boss_file:
            bossCounts = json.load(boss_file)
        with open('toolStats.json', 'r', encoding="utf8") as tools_file:
            toolStats = json.load(tools_file)
        with open('user_stats.json', 'r', encoding="utf8") as user_file:
            userStats = json.load(user_file)
        with open('server_stats.json', 'r', encoding='utf8') as servers_file:
            serverStats = json.load(servers_file)
    except (FileNotFoundError, json.JSONDecodeError):
        bossCounts = {}
        toolStats = {}
        newCounts = {}
        userStats= {}
        serverStats = {}
        print("Statfile Loading Failed....")

def save_stats():
    with open('bossStats.json', 'w') as boss_file:
        json.dump(bossCounts, boss_file, indent=2)
    with open('toolStats.json', 'w', encoding="utf8") as tool_file:
        json.dump(toolStats, tool_file, indent=2)
    with open('character_stats.json', 'w', encoding="utf8") as char_file:
        json.dump(newCounts, char_file, indent=2)
    with open('user_stats.json', 'w', encoding="utf8") as user_file:
        json.dump(userStats, user_file, indent=2)
    with open('server_stats.json', 'w', encoding='utf8') as servers_file:
        json.dump(serverStats, servers_file, indent=2)

def addImageCount(filename):
     # Increment the count for the specified image
    x, num = newGetMostCommon()
    newCounts[filename]["count"] += 1 #newCounts.get(filename).get("count", 0) + 1
    if newCounts[filename]["count"] > num:
        save_stats()
        return 1
    elif newCounts[filename]["count"] == num:
        save_stats()
        return 2
    elif newCounts[filename]["count"] > num and newCounts[filename]["count"] == 100:
        save_stats()
        return 100
    save_stats()
    return 0

def addServerStats(server, statline, val=0, name="none", campaign="none"):
    if server not in serverStats:
        serverStats[server] = {
                "activeRaid": False,
                "totalRolls": 0, 
                "Campaign": "None",
                "cCompleted": 0, 
                "users": 0, 
                "Exs": 0, 
                "raidWins": 0, 
                "totalRaids": 0,
                "totalDamage": 0,
                "highestDamage": 0, 
                "successful user":{
                    "name": "None", 
                    "raidWins": 0
                }
            }
        
    #there is definitley a better way to do this but i just wanna get this uypdate done so working > proper, easily changed later cry about it idk
    if statline == "roll":
        serverStats[server]["totalRolls"] += 1
    elif statline == "Campaign":
        serverStats[server]["Campaign"] = campaign
    elif statline == "users":
        serverStats[server]["users"] += 1
    elif statline == "EX":
        serverStats[server]["Exs"] += 1
    elif statline == "Win":
        serverStats[server]["raidWins"] += 1
    elif statline == "Raid":
        serverStats[server]["totalRaids"] += 1
    elif statline == "Completed":
        serverStats[server]["cCompleted"] += 1
    elif statline == "Damage":
        if val > serverStats[server]["highestDamage"]:
            serverStats[server]["highestDamage"] = val
        serverStats[server]["totalDamage"] += val
def addUserStat(user, statline, val=0, excard = "None"):
    if user not in userStats:
        userStats.update({user:{'totalRolls':0,'highestDamage':0,'averageDamage':0,'totalDamage':0,'totalRaids':0,'raidWins':0, 'deck': [], 'tolls': 0, 'cursed': False}})
    if statline == 'roll':
        userStats[user]['totalRolls'] += 1
    elif statline == 'toll':
        userStats[user]['tolls'] += 1
    elif statline == 'raid':
        if val == 1:
            userStats[user]['raidWins'] += 1
        else:
            userStats[user]['totalRaids'] += 1
    elif statline == 'damage':
        userStats[user]['totalDamage'] += val
        userStats[user]['averageDamage'] = userStats[user]['totalDamage'] / userStats[user]['totalRaids']
        if val > userStats[user]['highestDamage']:
            userStats[user]['highestDamage'] = val
    elif statline == 'deck':
        userStats[user]['deck'].append(excard)
    elif statline == 'curse':
        if val == 1:
            userStats[user]['cursed'] = False
        else:
            userStats[user]['cursed'] = True
    save_stats()
    return

def newGetMostCommon():
    ties = 0
    tienames = []
    most_common_image = max(newCounts.items(), key=lambda x: x[1]["count"])
    most_common_count = newCounts[most_common_image[0]]["count"]
    for name,data in newCounts.items():
        if data["count"] == most_common_count:
            ties += 1
            tienames.append(name)
    if ties > 1:
        return tienames, most_common_count
    else:
        return most_common_image[0], most_common_count

def getWinningestRaider():
    ties = 0
    tienames = []
    most_wins_char = max(newCounts.items(), key=lambda x: x[1]["raidsWon"])
    most_wins_count = newCounts[most_wins_char[0]]["raidsWon"]
    for name,data in newCounts.items():
        if data["raidsWon"] == most_wins_count:
            ties += 1
            tienames.append(name)
    if ties > 1:
        return tienames, most_wins_count
    else:
        return most_wins_char[0], most_wins_count

def newLoadAllImages(): 
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    for i in all_images:
        if i.split('.')[0].casefold() not in newCounts.keys():
            newCounts.update({i.split('.')[0].casefold():{
                    "count": 0,
                    "group": '_unsorted',
                    "raidsWon": 0,
                    "raidsCompleted": 0,
                    "favoriteWeapon": 'None',
                    "is1.0": False}})
            print(i)


def getImageExtenstion(name):
    for filename in os.listdir(f"{script_directory}/images/"):
    # Check if the current file has the same name (excluding extension)
        if os.path.splitext(filename)[0].casefold() == name:
            return os.path.join(f"{script_directory}/images/", filename)
#        
#
#DISCORD FUNCTIONS ----------------------------------------------------------------------------------------------------------
#
#}+•¥
        
@bot.command(name='updateStats', help='Updates tool stats and boss stats')
async def update(ctx):
    global activeRaid
    if ctx.author.id == bot.owner_id:
        load_stats()
        newLoadAllImages()
        activeRaid = False
    else:
        await ctx.send("Erm... thats owner only!", ephemeral=True)

@bot.command(name='groups', help='View all groups')
async def update(ctx):
    await ctx.send("alex, alex call center, alex drag strip, alex garage, alex scholars, alex shamans, alexcon, ALEXFORCE, china expansion, classics, classics family, drip havers, duos, evil geniuses, experiment, geekers, hamburger, hooligans, intuitive eaters, magic cards, magic entities, majhong club, middle east, money getters, negative morale, non human, non living, oldheads, poopbutt industries, prisoners, quans, racing team, rec center, retirement home, shapeshifter, shawties, stoners, shop class, space war, squads, tater dynasty, the arcane, the cookout, truck month, warriors, yurt kitchen, yurt trucking, yurttears, _unsorted")

@bot.command(name='roll', help='Send random image to chat')
async def images(ctx):
    try:
        all_files = os.listdir(f"{script_directory}/images")
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
        all_images = [file for file in all_files if
                    file.endswith(allowed_extensions)]
    # Choose random image and add path to it
        random_image = random.choice(all_images)
        if random.randint(1, 777) == 777:
            all_files = os.listdir(f"{script_directory}/EX")
            allowed_extensions = ('.gif')
            all_images = [file for file in all_files if file.endswith(allowed_extensions)]
            random_image = random.choice(all_images)
            addUserStat(ctx.author.name, 'deck', excard=random_image.split('.')[0].casefold())
            addServerStats(ctx.author.guild.name, "EX")
            #april fools 24 - await ctx.reply("EX卡已解放！", file=discord.File(f"{script_directory}/EX/{random_image}"))
            await ctx.reply("An EX card has been unleashed!", file=discord.File(f"{script_directory}/EX/{random_image}"))
            print(f"\n{ctx.author.name} has rolled an EX\n")
        else:
            if random_image.split('.')[0].casefold() == 'the unholy trinity':
                if userStats[ctx.author.name]['cursed'] == False:
                    #await ctx.send(f"<@{ctx.author.id}> 已经被诅咒了！", file = discord.File(f"{script_directory}/assets/curse.gif"))
                    await ctx.send(f"<@{ctx.author.id}> has been cursed!", file = discord.File(f"{script_directory}/assets/curse.gif"))
                addUserStat(ctx.author.name, 'curse', 0)
            elif random_image.split('.')[0].casefold() == 'the holy trinity':
                if userStats[ctx.author.name]['cursed'] == True:
                    #await ctx.send(f"<@{ctx.author.id}> 诅咒已解除！", file = discord.File(f"{script_directory}/assets/curse lifted.gif"))
                    await ctx.send(f"<@{ctx.author.id}>'s curse has been lifted!", file = discord.File(f"{script_directory}/assets/curse lifted.gif"))
                addUserStat(ctx.author.name, 'curse', 1)
            await ctx.reply(file=discord.File(f"{script_directory}/images/{random_image}"))
        tiebreaker = addImageCount(random_image.split('.')[0].casefold())
        #await ctx.send(file=discord.File(f"{script_directory}/images/{random_image}"))
        addUserStat(ctx.author.name, 'roll')
        addServerStats(ctx.author.guild.name, "roll")
        if tiebreaker == 1:
            #await ctx.send(f"{random_image.split('.')[0]} 已经领先了！")
            await ctx.send(f"{random_image.split('.')[0]} has taken the lead!")
        elif tiebreaker == 2:
            #await ctx.send(f"{random_image.split('.')[0]} 已经并列领先！")
            await ctx.send(f"{random_image.split('.')[0]} has tied for the lead!")
        elif tiebreaker == 100:
            await ctx.send(f"{random_image.split('.')[0]} IS THE FIRST TO THE 100TH ROLL!!!")
        await asyncio.sleep(.5)
    except Exception as e:
        print("\nRoll command failed\n",e)
        #await ctx.send(" 出了些问题。 Discord 服务器可能会导致问题。")
        await ctx.send("Something went wrong. Discord servers might be causing issues.")

@bot.tree.command(name='show', description='Shows a specific character, excluding unrevelead characters', guild=discord.Object(id=240265833199173633)) #Uses OS Name - Stays the same
@app_commands.describe(name='The characters name')
async def submit(interaction: discord.Interaction, name: str):
    if len(name) == 0:
        await interaction.response.send_message(f'No character name was entered', ephemeral=True)
    else:
        closest_score = -1
        closest_match = None
        for k in newCounts.keys():
            simScore = fuzz.ratio(name.casefold(), k)
            if simScore > closest_score:
                closest_score = simScore
                closest_match = k
        if newCounts[closest_match]["count"] == 0:
            await interaction.response.send_message(content="This character has not been revealed! Try using !roll to unlock the ability to view them here.", ephemeral=True)
        elif closest_score >= 93:
            try:
                await interaction.response.send_message(file=discord.File(f"{script_directory}/images/{closest_match}.jpg"), ephemeral=True)
            except:
                try:
                    await interaction.response.send_message(file=discord.File(f"{script_directory}/images/{closest_match}.png"), ephemeral=True)
                except:
                    try:
                        await interaction.response.send_message(file=discord.File(f"{script_directory}/images/{closest_match}.gif"), ephemeral=True)
                    except:
                        try:
                            await interaction.response.send_message(file=discord.File(f"{script_directory}/images/{closest_match}.jpeg"), ephemeral=True)
                        except:
                            print("Shits fucked")
        else:
            await interaction.response.send_message(f'Unable to find character {name}. Check your spelling and try again.', ephemeral=True)

@bot.command(name='toll', help='Pay the trolls toll')
async def troll(ctx):
    #sends the troll
    random_image = f"{script_directory}/assets/{'troll.jpg'}"
    addUserStat(ctx.author.name, 'toll')
    #await ctx.reply(f"呃-哦！您不小心输入了收费站！现在你必须向巨魔支付通行费！", file=discord.File(random_image))
    await ctx.reply(f"Uh-oh! You accidentally typed toll! Now you must pay the trolls toll!", file=discord.File(random_image))
    #await ctx.send(file=discord.File(random_image))

@bot.hybrid_command(name='deck', with_app_command=True, help='Shows EX cards a user owns.') 
async def deck(ctx, *, arg = 'All'):
    if arg != 'All':
        user = discord.utils.get(ctx.guild.members, name=arg)
        if user == None:
            user = discord.utils.get(ctx.guild.members, nick=arg)
        if user != None:
            try:
                user = discord.utils.get(ctx.guild.members, name=arg)
                EXcard = f'{script_directory}/EX/{userStats[arg]["deck"][0]}.gif'
                deckindex = 0
                file = discord.File(EXcard, filename="image.gif")
                #embed = discord.Embed(title=f'{arg} 图书馆:')
                embed = discord.Embed(title=f'{arg}\'s Library:')
                embed.set_image(url=f"attachment://image.gif")
                embed.add_field(name = 'EX cards owned', value = len(userStats[arg]['deck']))
                simple_view = discord.ui.View()
                simple_button = discord.ui.Button(label="View Next")
                userDeck = userStats[arg]["deck"]
                async def simple_callback(button_inter: discord.Interaction):
                    nonlocal deckindex
                    deckindex += 1
                    next_card = userDeck[deckindex]
                    new_file = discord.File(f'{script_directory}/EX/{next_card}.gif', filename='nextcard.gif')
                    new_embed = discord.Embed(title=f'{arg}\'s Library:')

                    new_embed.set_image(url="attachment://nextcard.gif") # set the embed's image to `img2.png`

                    await button_inter.response.edit_message(embed=new_embed, attachments=[new_file]) # attach the new image file with the embed
                simple_button.callback = simple_callback

                prev_button = discord.ui.Button(label="View Previous")
                async def previous_callback(button_inter: discord.Interaction):
                    nonlocal deckindex
                    if deckindex != 0:
                        deckindex -= 1
                        prev_card = userStats[arg]["deck"][deckindex]
                        new_file = discord.File(f'{script_directory}/EX/{prev_card}.gif', filename='nextcard.gif')
                        new_embed = discord.Embed(title=f'{arg}\'s Library:')

                        new_embed.set_image(url="attachment://nextcard.gif") # set the embed's image to `img2.png`
                        await button_inter.response.edit_message(embed=new_embed, attachments=[new_file]) # attach the new image file with the embed

                simple_button.callback = simple_callback
                prev_button.callback = previous_callback
                simple_view.add_item(item=prev_button)
                simple_view.add_item(item=simple_button)
                await ctx.send(embed=embed, file=file, view=simple_view)

            except:
                embed = discord.Embed(title=f'{arg}\'s Library:')
                embed.add_field(name="No EX cards were found. Try !roll to find one!", value=None)
                await ctx.send(embed=embed)


@bot.hybrid_command(name='server', with_app_command=True, help='displays the current server stats') 
async def stats(ctx):
    server = ctx.author.guild.name
    embed = discord.Embed(title=f'{server}\'s Stats:')
    embed.set_thumbnail(url=str(ctx.author.guild.icon.url))
    try:
        embed.add_field(name = 'Total Rolls:', value = serverStats[server]['totalRolls'])
        embed.add_field(name = 'Raid Wins:', value = serverStats[server]['raidWins'])
        embed.add_field(name = 'Users:', value = serverStats[server]['users'])
        embed.add_field(name = 'Campaign Tier:', value = serverStats[server]["cCompleted"])
        embed.add_field(name = 'Total Raids:', value = serverStats[server]["totalRaids"])
        embed.add_field(name = 'EX Cards Rolled:', value = serverStats[server]["Exs"])
    except:
        embed.add_field(name="No stats were found.", value=None)
    await ctx.send(embed=embed)


@bot.hybrid_command(name='stats', with_app_command=True, help='displays the current most common characters') 
async def stats(ctx, *, arg = 'All'):
    if arg != 'All':
        user = discord.utils.get(ctx.guild.members, name=arg)
        if user != None:
            user = discord.utils.get(ctx.guild.members, name=arg)
            avatar_url = user.display_avatar
            embed = discord.Embed(title=f'{arg}\'s Stats:')
            embed.set_thumbnail(url=str(avatar_url))
            try:
                '''embed.add_field(name = '总卷：', value = userStats[arg]['totalRolls'])
                embed.add_field(name = '突袭胜利：', value = userStats[arg]['raidWins'])
                embed.add_field(name = '最高伤害：', value = userStats[arg]['highestDamage'])
                embed.add_field(name = '平均袭击伤害：', value = round(userStats[arg]['averageDamage'], 2))
                embed.add_field(name = '总袭击次数：', value = userStats[arg]['totalRaids'])
                embed.add_field(name = '拥有的 EX 卡：', value = len(userStats[arg]['deck']))'''
                embed.add_field(name = 'Total Rolls:', value = userStats[arg]['totalRolls'])
                embed.add_field(name = 'Raid Wins:', value = userStats[arg]['raidWins'])
                embed.add_field(name = 'Highest Damage:', value = userStats[arg]['highestDamage'])
                embed.add_field(name = 'Average Raid Damage:', value = round(userStats[arg]['averageDamage'], 2))
                embed.add_field(name = 'Total Raids:', value = userStats[arg]['totalRaids'])
                embed.add_field(name = 'EX Cards Owned:', value = len(userStats[arg]['deck']))
                
            except:
                embed.add_field(name="No stats were found. Try !roll or /raid to start.", value=None)
            await ctx.send(embed=embed)
        else:  
            closest_score = -1
            closest_match = None
            for k in newCounts.keys():
                simScore = fuzz.ratio(arg.casefold(), k)
                if simScore > closest_score:
                    closest_score = simScore
                    closest_match = k
            if closest_score >= 92:
                image = getImageExtenstion(closest_match)
                if newCounts[closest_match]["count"] == 0:
                    image = f"{script_directory}/assets/q.png"
                file = discord.File(image, filename="image.png")
                '''embed = discord.Embed(title=f'{arg} 统计数据：', color=discord.Color.dark_red())
                embed.add_field(name="＃ 劳斯莱斯： ", value = newCounts[closest_match]["count"], inline=True)
                embed.add_field(name="突袭获胜： ", value=newCounts[closest_match]["raidsWon"], inline=True)
                embed.add_field(name="突袭完成： ", value=newCounts[closest_match]["raidsCompleted"], inline=True)
                embed.add_field(name="团体： ", value=newCounts[closest_match]["group"], inline=True)
                embed.set_thumbnail(url="attachment://image.png")'''
                embed = discord.Embed(title=f'{arg} Stats:', color=discord.Color.dark_red())
                embed.add_field(name="# Rolls: ", value = newCounts[closest_match]["count"], inline=True)
                embed.add_field(name="Raids Won: ", value=newCounts[closest_match]["raidsWon"], inline=True)
                embed.add_field(name="Raids Completed: ", value=newCounts[closest_match]["raidsCompleted"], inline=True)
                embed.add_field(name="Group: ", value=newCounts[closest_match]["group"], inline=True)
                embed.set_thumbnail(url="attachment://image.png")
                await ctx.send(embed=embed, file=file)
                #await ctx.send(f'{closest_match} has been rolled {newCounts[closest_match]["count"]} time(s).\nGroup: {newCounts[closest_match]["group"]}\nRaids won: {newCounts[closest_match]["raidsWon"]}\nRaids Completed: {newCounts[closest_match]["raidsCompleted"]}')
            else:
                await ctx.send(f'Unable to find character {arg}. Check your spelling and try again.', ephemeral=True)
    else:
        character, count = newGetMostCommon()
        raidChar, raidWins = getWinningestRaider()
        if type(character) is list:
            names = ", ".join(character)
            image = f'{script_directory}/assets/dice.png'
            file = discord.File(image, filename="image.png")
            #embed = discord.Embed(title = "最高滚动 - 并列：", color=discord.Color.red())
            embed = discord.Embed(title = "Highest Roll - Tie:", color=discord.Color.red())
            embed.add_field(name = count, value = names)
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.send(embed=embed, file=file)
            #wait ctx.send(f'There is a tie between {names} with {count} rolls.')
        else:
            image = getImageExtenstion(character)
            file = discord.File(image, filename="image.png")
            #embed = discord.Embed(title='最高滚动：', color=discord.Color.red())
            embed = discord.Embed(title='Highest Roll:', color=discord.Color.red())
            embed.add_field(name=character, value = count, inline=True)
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.send(embed=embed, file=file)
            #await ctx.send(f'{character} is the most common roll with {count} rolls.')
        if type(raidChar) is list:
            rnames = ", ".join(raidChar)
            image = f'{script_directory}/assets/raid.png'
            file = discord.File(image, filename="image.png")
            #embedRaid = discord.Embed(title=f"最多突袭胜利：", color=discord.Color.red())
            embedRaid = discord.Embed(title=f"Most Raid Wins:", color=discord.Color.red())
            embedRaid.add_field(name = raidWins, value=rnames, inline=True)
            embedRaid.set_thumbnail(url="attachment://image.png")
            await ctx.send(embed=embedRaid, file=file)
            #await ctx.send(f'The raiders with the most wins are {rnames}, having won {raidWins} times.')
        else:
            image = getImageExtenstion(raidChar)
            file = discord.File(image, filename="image.png")
            #embedRaid = discord.Embed(title='突袭大师：', color=discord.Color.red())
            embedRaid = discord.Embed(title='The Raid Master:', color=discord.Color.red())
            embedRaid.add_field(name=raidChar, value = raidWins, inline=True)
            embedRaid.set_thumbnail(url="attachment://image.png")
            await ctx.send(embed=embedRaid, file=file)
            #await ctx.send(f'{raidChar} is the most successful raider, with {raidWins} wins.')

@bot.tree.command(name='submit', description='Submit a character', guild=discord.Object(id=240265833199173633)) 
@app_commands.describe(attachment='The file to upload', name='The characters name')
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, name: str):
    print(f'\n{interaction.user.nick} is adding a character: {name}')
    if "../" in name or "../" in attachment.filename:
        await interaction.response.send_message(f'Erm, no flipping messing around bro', ephemeral=True)
    elif newCounts.get(name.casefold()) != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif newCounts.get(name.casefold()) != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif attachment.filename[-4] == '.':
        await attachment.save(f"{script_directory}/images/{name.casefold()}{attachment.filename[-4:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)
        newLoadAllImages()
    else:
        await attachment.save(f"{script_directory}/images/{name.casefold()}{attachment.filename[-5:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)
        newLoadAllImages()


@bot.tree.command(name='updategroup', description='update an unsorted characters group', guild=discord.Object(id=240265833199173633)) 
@app_commands.describe(name='The characters name', group = "The desired group: do !groups to see a list of all groups")
async def updategroup(interaction: discord.Interaction, name: str, group: str):
    if name ==  None or group == None:
        await interaction.response.send_message(f'You forgot something', ephemeral=True)
    elif group not in ["alex", "mom", "geekers", "stoners", "alex call center", "alex drag strip", "alex garage", "alex scholars", "alex shamans", "alexcon", "ALEXFORCE", "china expansion", "classics", "classics family", "drip havers", "duos", "evil geniuses", "experiment", "hamburger", "hooligans", "intuitive eaters", "magic cards", "magic entities", "majhong club", "middle east", "money getters", "negative morale", "non human", "non living", "oldheads", "poopbutt industries", "prisoners", "quans", "racing team", "rec center", "retirement home", "shapeshifter", "shawties", "shop class", "space war", "squads", "tater dynasty", "the arcane", "the cookout", "truck month", "warriors", "yurt kitchen", "yurt trucking", "yurttears", "_unsorted"]:
        await interaction.response.send_message(f'group {group} not found. Check your spelling or use !groups to see the full list', ephemeral=True)
    else:
        try:
            print(f'\n{interaction.user.nick} is updating a group: {name} {group}')
            if newCounts[name.casefold()]["group"] != "_unsorted":
                await interaction.response.send_message(f'{name} is already in the {newCounts[name.casefold()]["group"]} group.', ephemeral=True)
            else:
                newCounts[name.casefold()]["group"] = group
                await interaction.response.send_message(f'{name} has been assigned to the {group} group.')
        except:
            await interaction.response.send_message(f'An error occured trying to set {name} as part of {group} group. Check your spelling and try again.', ephemeral=True)


@bot.tree.command(name='submittools', description='Submit or make changes to a tool', guild=discord.Object(id=240265833199173633))
@app_commands.describe(name='The name of the tool you are submitting', attachment='The corresponding image for that tool', default='The default multiplier for the tool', characters='The name, multiplier you want to specify. SEPERATE ALL BY COMMA')
async def submittool(interaction: discord.Interaction,name: str, default: float, attachment: discord.Attachment, characters: Optional[str]):
    try:
        print(f'\n{interaction.user.nick} is adding a tool: {name}')
        if name in toolStats.keys():
            await interaction.response.send_message("This tool already exists. Stat updates are not implemented just yet.", ephemeral=True)
        elif "../" in name or "../" in attachment.filename:
             await interaction.response.send_message("gualar bills", ephemeral=True)  
        elif characters == None and attachment != None:
            toolStats.update({name : {"Default" : default, "group": "None"}})
            await attachment.save(f"{script_directory}/tools/{name}{attachment.filename[-4:]}")
            await interaction.response.send_message(f'Tool {name} has been added as a default tool!', ephemeral=False)
            save_stats()           
        elif characters != None and attachment != None:
            toolStats.update({name : {"Default" : 1}})
            stats = characters.split(', ')
            for i, val in enumerate(stats):
                    if i == (len(stats) + 1):
                        break
                    if i % 2 == 0:
                        toolStats[name].update({val : float(stats[i+ 1])})
                        print(f'Character {val} added with {stats[i+ 1]}')
            toolStats[name]["Default"] = default
            toolStats[name]["group"] = "None"
            await attachment.save(f"{script_directory}/tools/{name}{attachment.filename[-4:]}")
            await interaction.response.send_message(f'Tool {name} has been added!', ephemeral=False)
            save_stats()  
        else:
            await interaction.response.send_message("You need to attach an image to create a new tool", ephemeral=True)
    except Exception as e:
        print("\nSomething went wrong:\n", e)
        await interaction.response.send_message("An error occured during submission.")
#        
#
#PVE MODE ----------------------------------------------------------------------------------------------------------
#
#
        
evolutions = {
    "full power gorb": 
        ("the gorb", "the necromancers skull"), 
    "psychosis":
        ("voice to skull", "alexs pure lsd"), 
    "indescribable wealth": 
        ("gerder gumpsneeds guaranteed jackpot method", "luck of the irish"), 
    "planetary annihilation":
        ("spindablocks storage", "liquid tiberium bomb"),
    "wok fortress":
        ("loan from chinese mike", "wok28"),
    "holy pact":
        ("tome of divine knowledge", "the gorb"),
    "dark pact":
        ("tome of irreverent knowledge", "the gorb"),
    "dads shotgun":
        ("dads gun", "moms purse"),
    "ultimate brain freeze":
        ("wok ki ki energy vortex", "coke flavored slurpee"),
    "avatar of the wok ki ki guardian":
        ("wok ki ki energy vortex", "ancient slapahoe peace pipe of good fortune and fruit"),
    "thugnars modified glock":
        ("thugnars glock", "the prollum solva"),
    "infinite omnipotent awareness":
        ("tome of divine knowledge","tome of irreverent knowledge"),
    "alexbot militia":
        ("convoy", "backup"),
    "20 ton discount":
        ("10 finger discount", "titanium pimp hand")
    }


class JoinRaidButton(discord.ui.View):
    def __init__(self, host: str, *, timeout=20):
        super().__init__(timeout=timeout)
        self.players = [host]
        self.count = 1
        self.embed = discord.Embed()
        #Add an embed here for raid members
    #@discord.ui.button(label="加入突袭",style=discord.ButtonStyle.primary)
    @discord.ui.button(label="Join Raid",style=discord.ButtonStyle.primary)
    async def raid_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name not in self.players:
            button.style=discord.ButtonStyle.success
            self.count += 1           
            #button.label=f"{self.count} 突袭成员："
            button.label=f"{self.count} player(s)"
            self.players.append(interaction.user.name)
            addUserStat(interaction.user.name, 'raid')
            if len(self.players) > 1:
                #self.embed.add_field(name="突袭成员：", value=self.players[self.count-1])
                self.embed.add_field(name="Raid Member:", value=self.players[self.count-1])
            try:         
                await interaction.response.edit_message(view=self, embed=self.embed)
            except:
                print("Something went wrong during raid\n")
    #@discord.ui.button(label="开始突袭", style=discord.ButtonStyle.danger)
    @discord.ui.button(label="Start Raid", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction:discord.Interaction, child: discord.ui.Button):
        if len(self.players) > 0 and interaction.user.name == self.players[0]:
            #child.label = "开始...."
            child.label = "Starting...."
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

def newGame():
    for boss in bossCounts.keys():
        if boss != "death":
            bossCounts[boss]["health"] *= 1.25
            pass

def rollRaid():
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = random.choice(all_images)
    return random_image

def rollTool(): 
    all_files = os.listdir(f"{script_directory}/tools")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = random.choice(all_images)
    return random_image

def rollBoss(mode: str, server: str):
    if mode == "campaign":
        boss = serverStats[server]["Campaign"]
        if boss == "None":
            boss = "david"
        elif serverStats[server]["Campaign"] == "COMPLETE":
            if serverStats[server]["cCompleted"] % 2 == 1:
                boss = "Tipp Tronix"
                serverStats[server]["Campaign"] = "Tipp Tronix"
            else:
                boss = "david"
                serverStats[server]["Campaign"] = "david"
        random_image = f"{boss}.jpg"
        return random_image
    else:
        all_files = os.listdir(f"{script_directory}/bosses")
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        # All available images with supported extensions
        all_images = [file for file in all_files if
                    file.endswith(allowed_extensions)]
        # Choose random image and add path to it
        random_image = random.choice(all_images)
        while bossCounts[random_image.split('.')[0]]["timesDefeated"] == 0:
            random_image = random.choice(all_images)
        return random_image

class RaidState:
    def __init__(self, playerList, mode: str, server: str):
        self.playerData = {}  # Dictionary to store player data (user ID as key)
        self.playerList = playerList
        self.boss = rollBoss(mode, server)
        #self.boss_health = (bossCounts.get(self.boss.split('.')[0], {}).get("health", 0))
        self.boss_health = (bossCounts.get(self.boss.split('.')[0], {}).get("health", 0) * (0.25 * serverStats[server]["cCompleted"] + 1))  # Initial boss health
        self.boss_weakness = bossCounts.get(self.boss.split('.')[0], {}).get("weakness", "None")
        self.hardmode = False
        self.nightmare = False

    async def draw_cards(self): #Uses OS Name
        #await asyncio.sleep(60)
        if len(self.playerList) > 0:
            evolutionCheck = []
            for player_id in self.playerList:
                character = rollRaid()
                while newCounts[character.split('.')[0].casefold()]["count"] == 0:
                    character = rollRaid()
                tool = rollTool()
                while tool.split('.')[0] not in toolStats.keys():
                    print(tool, "wasnt found\n")
                    tool = rollTool()
                evolutionCheck.append(tool.split('.')[0])
                pHand = {"character": character, "tool": tool, "damageIndex": newCounts[character.split('.')[0].casefold()]["count"] * 10}
                if tool.split('.')[0] not in toolStats.keys():
                    pHand["damageIndex"] = random.randint(0,1000)
                    print(tool, "Was not found in the tool file")
                elif character.split('.')[0] in toolStats[tool.split('.')[0]].keys():
                    pHand['damageIndex'] *= toolStats[tool.split('.')[0]][character.split('.')[0]]
                    toolStats[tool.split('.')[0]][character.split('.')[0]] += 0.05
                else:
                    pHand['damageIndex'] *= toolStats[tool.split('.')[0]]["Default"]
                    toolStats[tool.split('.')[0]].update({character.split('.')[0] : toolStats[tool.split('.')[0]]["Default"] + 0.05})
                if toolStats[tool.split('.')[0]]["group"] == newCounts[character.split('.')[0].casefold()]["group"]:
                    pHand["damageIndex"] *= 2   
                self.playerData[player_id] = pHand

            for evolved, recipe in evolutions.items():
                if recipe[0] in evolutionCheck and recipe[1] in evolutionCheck:
                    self.playerData["evolutions_FLAG"] = (evolved, recipe[0], recipe[1])
            
                
    async def backup_hand(self):
        character = rollRaid()
        while newCounts[character.split('.')[0].casefold()]["count"] == 0:
            character = rollRaid()
        tool = rollTool()
        while tool == 'backup.jpg':
            tool = rollTool()
        pHand = {"character": character, "tool": tool, "damageIndex": newCounts[character.split('.')[0].casefold()]["count"] * 10}
        if tool.split('.')[0] not in toolStats.keys():
            pHand["damageIndex"] = random.randint(0,1000)
            print(tool, "Was not found in the tool file")
        elif character.split('.')[0] in toolStats[tool.split('.')[0]].keys():
            pHand['damageIndex'] *= toolStats[tool.split('.')[0]][character.split('.')[0]]
            toolStats[tool.split('.')[0]][character.split('.')[0]] += 0.05
        else:
            pHand['damageIndex'] *= toolStats[tool.split('.')[0]]["Default"]
            toolStats[tool.split('.')[0]].update({character.split('.')[0] : toolStats[tool.split('.')[0]]["Default"] + 0.05})
        if toolStats[tool.split('.')[0]]["group"] == newCounts[character.split('.')[0].casefold()]["group"]:
            pHand["damageIndex"] *= 2
        return pHand
    
    async def convoy(self):
        character = rollRaid()
        while newCounts[character.split('.')[0].casefold()]["count"] == 0:
            character = rollRaid()
        pHand = {"character": character, "damageIndex": newCounts[character.split('.')[0].casefold()]["count"] * 10}
        return pHand
    
    async def callotw(self):
        character = rollRaid()
        while newCounts[character.split('.')[0].casefold()]["count"] == 0 or newCounts[character.split('.')[0].casefold()]["group"] != "non human":
            character = rollRaid()
        pHand = {"character": character, "damageIndex": newCounts[character.split('.')[0].casefold()]["count"] * 10}
        return pHand
    


@bot.tree.command(name='raid', description='Start a PvE raid!') 
#@app_commands.describe(mode="活动 - 继续你的公会的进步 |经典 - 返回与您之前击败过的任何 Boss 作战")
@app_commands.describe(mode="Campaign - continue your guild's progress | Classic - Return to fight any of the bosses you've defeated before")
@app_commands.choices(mode=[
    #app_commands.Choice(name="活动", value="campaign"), 
    #app_commands.Choice(name="经典的", value="classic")
    app_commands.Choice(name="Campaign", value="campaign"), 
    app_commands.Choice(name="Classic", value="classic")
    ])
async def raid(interaction: discord.Interaction, mode: app_commands.Choice[str]):
    try:
        ctx = await commands.Context.from_interaction(interaction)
        if serverStats[interaction.user.guild.name]["activeRaid"] == True:
            #await interaction.response.send_message("突袭正在进行时无法发起突袭！")
            await interaction.response.send_message("Cannot start a raid while one is in progress!")
            return
        if mode.value == "classic":
            serverStats[interaction.user.guild.name]["activeRaid"] = True
            view = JoinRaidButton(interaction.user.name)
            raid = RaidState(list(view.players), mode.value, interaction.user.guild.name)
            embed = discord.Embed(title=bossCounts[raid.boss.split(".")[0]]["wakeMessage"], color=discord.Color.gold())
            image = f'{script_directory}/assets/classic.png'
            file = discord.File(image, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
            #embed.add_field(name="主持人：", value=view.players[0])
            embed.add_field(name="Host:", value=view.players[0])
            view.embed = embed
            await interaction.response.send_message(view=view, embed=embed, file=file)
            while not view.children[1].disabled:
                await asyncio.sleep(5)
            raid.playerList = list(view.players)
            #if len(raid.playerList) == 4:
            #    raid.boss_health *= 1.5
            #    raid.hardmode =  True
            #elif len(raid.playerList) > 4:
            #    raid.boss_health *= 2.0
            #    raid.nightmare = True
            await ctx.invoke(bot.get_command('raidResults'), raid, mode.value)
        elif mode.value == "campaign":
            serverStats[interaction.user.guild.name]["activeRaid"] = True
            view = JoinRaidButton(interaction.user.name)
            raid = RaidState(list(view.players), mode.value, interaction.user.guild.name)
            embed = discord.Embed(title=bossCounts[raid.boss.split(".")[0]]["wakeMessage"], color=discord.Color.gold())
            image = f'{script_directory}/assets/campaign.png'
            file = discord.File(image, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
            #embed.add_field(name="主持人：", value=interaction.user.name)
            embed.add_field(name="Host:", value=view.players[0])
            view.embed = embed
            await interaction.response.send_message(view=view, embed=embed, file=file)
            while not view.children[1].disabled:
                await asyncio.sleep(5)
            raid.playerList = list(view.players)
            #if len(raid.playerList) > 4:
            #    raid.boss_health *= 1.5
            #    raid.hardmode =  True
            await ctx.invoke(bot.get_command('raidResults'), raid, mode.value)
    except Exception as e:
        print("\nSomething went wrong:\n", e)
        await ctx.interaction.response.send_message("An error occured during the raid instance.")
        #await ctx.interaction.response.send_message("raid 实例期间发生错误。")
        activeRaid = False
    

@bot.command() #Uses OS Name
async def raidResults(ctx, RaidState: RaidState, mode: str):
    #try:
        await RaidState.draw_cards()
        totalDamage = 0
        hand = []
        groups = []
        for p,data in RaidState.playerData.items():
            if p == "evolutions_FLAG":
                await ctx.send(f"{data[1]} and {data[2]} have evolved!", file=discord.File(f"{script_directory}/evolutions/{data[0]}.gif"))
                totalDamage *= toolStats[data[0]]["Default"]
                break
            else:
                newCounts[data["character"].split(".")[0].casefold()]["raidsCompleted"] += 1
                hand.append(discord.File(f"{script_directory}/images/{data['character']}"))
                hand.append(discord.File(f"{script_directory}/tools/{data['tool']}"))

                if newCounts[data["character"].split(".")[0].casefold()]["group"] != "_unsorted":
                    groups.append(newCounts[data["character"].split(".")[0].casefold()]["group"])

                if data['tool'] == 'backup.jpg':
                    try:
                        bhand = await RaidState.backup_hand()
                        hand.append(discord.File(f"{script_directory}/images/{bhand['character']}"))
                        hand.append(discord.File(f"{script_directory}/tools/{bhand['tool']}"))
                        data['damageIndex'] += bhand['damageIndex']
                    except:
                        print("Backup tool didnt work")
                elif data['tool'] == 'convoy.jpg':
                    try:
                        for i in range(1, 6):
                            chand = await RaidState.convoy()
                            hand.append(discord.File(f"{script_directory}/images/{chand['character']}"))
                            data['damageIndex'] += chand['damageIndex']
                    except:
                        print("convoy tool didnt work")
                elif data['tool'] == 'Call of the wild.png':
                    try:
                        for i in range(1,6):
                            chand = await RaidState.callotw()
                            hand.append(discord.File(f"{script_directory}/images/{chand['character']}"))
                            data['damageIndex'] += chand['damageIndex']
                    except:
                        print("CALL did not work!")
                if RaidState.boss_weakness == newCounts[data["character"].split(".")[0].casefold()]["group"] or RaidState.boss_weakness == data["character"].split('.')[0].casefold() or RaidState.boss_weakness == data['tool'].split('.')[0]:
                    #await ctx.send(f'"{RaidState.boss_weakness} 是我的弱点！”')
                    await ctx.send(f'"{RaidState.boss_weakness} is my weakness!"')
                    data['damageIndex'] *= 2
                await ctx.send(f"{p}'s hand, dealing {round(data['damageIndex'], 2)} damage:", files = hand)
                #await ctx.send(f"{p} 的手，交易 {round(data['damageIndex'], 2)} 损害", files = hand)
                addUserStat(p, 'damage', round(data['damageIndex'], 2))
                totalDamage += round(data['damageIndex'], 0)
                hand.clear()
                await asyncio.sleep(5)
        if len(groups) != len(set(groups)):
            combo = len(groups) - len(set(groups))
            combo *= 2
            try:
                groupscheck = set()
                comboGroups = []
                for g in groups:
                    if g in groupscheck:
                        comboGroups.append(g)
                    else:
                        groupscheck.add(g)

                groupsstring = ", ".join(comboGroups)
                #await ctx.send(f'{groupsstring} 已组合为 {combo}x 团体组合！额外伤害已解锁！')
                await ctx.send(f'{groupsstring} HAVE COMBINED FOR A {combo}x GROUP COMBO(s)! BONUS DAMAGE UNLOCKED!')
            except:
                await ctx.send(f'{combo} GROUP COMBO(s)! BONUS DAMAGE UNLOCKED!')
            totalDamage *= combo
        await ctx.send(file = discord.File(f"{script_directory}/bosses/{RaidState.boss}"))
        addServerStats(ctx.author.guild.name, "Raid")
        if RaidState.boss_health > totalDamage:
            if RaidState.boss.split(".")[0] == "death":
                await ctx.send("It wasn't enough...")
                #file = discord.File(unlock, filename="unlock.jpg")
                await ctx.invoke(bot.get_command('deathVotes'))
            else:
                #await ctx.send(f'你的队伍攻击并离开 {RaidState.boss.split(".")[0]} 在 {RaidState.boss_health - totalDamage} HP\n{RaidState.boss.split(".")[0]} 杀死你的队伍，没有人活着......')
                await ctx.send(f'Your party attacks and leaves {RaidState.boss.split(".")[0]} at {RaidState.boss_health - totalDamage} HP\n{RaidState.boss.split(".")[0]} slays your party, leaving no one alive....')

            bossCounts[RaidState.boss.split(".")[0]]["timesWon"] += 1
        elif RaidState.boss_health <= totalDamage:
            #await ctx.send(f'你们的政党宣布胜利 {RaidState.boss.split(".")[0]}, 交易 {totalDamage} 总伤害！')
            await ctx.send(f'Your party declares victory over {RaidState.boss.split(".")[0]}, dealing {totalDamage} total damage!')
            bossCounts[RaidState.boss.split(".")[0]]["timesDefeated"] += 1
            addServerStats(ctx.author.guild.name, "Win")
            addServerStats(ctx.author.guild.name, "Damage", totalDamage)
            if mode == "campaign":
                if RaidState.boss.split(".")[0] == "KRYPTIS ZYPHER":
                    await ctx.send(file = discord.File(f"{script_directory}/assets/demise.gif"))
                    addServerStats(ctx.author.guild.name, "Campaign", campaign="death")
                if bossCounts[RaidState.boss.split(".")[0]]["ID"] == "COMPLETE":
                    addServerStats(ctx.author.guild.name, "Campaign", campaign=bossCounts[RaidState.boss.split(".")[0]]["ID"])
                    addServerStats(ctx.author.guild.name, "Completed")
                    newGame()
                else:
                    addServerStats(ctx.author.guild.name, "Campaign", campaign=bossCounts[RaidState.boss.split(".")[0]]["ID"])
            for user in RaidState.playerList:
                addUserStat(user, 'raid', 1)
            for phand in RaidState.playerData.values():
                if type(phand) == tuple:
                    break
                name = phand["character"].split(".")[0]
                newCounts[name.casefold()]["raidsWon"] += 1
                tool = phand["tool"].split(".")[0]
                if RaidState.hardmode == False and RaidState.nightmare == False:
                    toolStats[tool][name] += 0.05
                elif RaidState.hardmode == True:
                    toolStats[tool][name] += 0.10
                elif RaidState.nightmare == True:
                    toolStats[tool][name] += 0.20
        serverStats[ctx.author.guild.name]["activeRaid"] = False
        print("RAID was completed successfully...\n\n")
        save_stats()
    #except Exception as e:
        #print("Raid did not complete, error occured: \n", e)
        #activeRaid = False

@bot.command() #Uses OS Name
async def deathVotes(ctx):
    embed2 = discord.Embed(title=f'Turn back now, or face the forces of death again if you dare...')
    brave = int(0)
    coward = int(0)
    simple_view = discord.ui.View()
    simple_button = discord.ui.Button(label="It's not over!", style=discord.ButtonStyle.success)
    embed2.add_field(name="Try again: ", value=brave)
    embed2.add_field(name="Leave now:", value=coward)

    async def simple_callback(button_inter: discord.Interaction):
        nonlocal brave
        nonlocal simple_view
        brave += 1
        #embed2.set_field_at(index=0, name="Try again: ", value=brave)
        simple_view = simple_view.clear_items()
        embed2.clear_fields()
        addServerStats(ctx.author.guild.name, "Campaign", campaign="death")
        embed2.color = discord.Colour.dark_blue()
        embed2.title=("Death awaits you yet again...")
        await button_inter.response.edit_message(embed=embed2, view=simple_view)
    simple_button.callback = simple_callback

    prev_button = discord.ui.Button(label="I'm not ready...", style=discord.ButtonStyle.danger)
    async def previous_callback(button_inter: discord.Interaction):
        nonlocal coward
        nonlocal simple_view
        coward += 1
        #embed2.set_field_at(index=1, name="Leave now: ", value=coward)
        simple_view = simple_view.clear_items()
        embed2.clear_fields()
        addServerStats(ctx.author.guild.name, "Campaign", campaign="COMPLETE")
        cowardice = f"{script_directory}/assets/coward.gif"
        file = discord.File(cowardice, filename="coward.gif")
        embed2.set_image(url=f"attachment://coward.gif")
        embed2.color = discord.Colour.dark_red()
        embed2.title=(" ")
        await button_inter.response.edit_message(embed=embed2, view=simple_view, attachments=[file])
    simple_button.callback = simple_callback
    prev_button.callback = previous_callback
    simple_view.add_item(item=simple_button)
    simple_view.add_item(item=prev_button)
    simple_view.timeout = 7
    ctx.interaction = await ctx.send(embed=embed2, view=simple_view)
    if brave == 0 and coward == 0:
        try:
            await previous_callback(button_inter= ctx.message.interaction)
        except:
            addServerStats(ctx.author.guild.name, "Campaign", campaign="COMPLETE")
    return
    #await tallyvotes()
#        
#
#MAIN AND UTILITIES ----------------------------------------------------------------------------------------------------------
#
#
@bot.command(name='sync', description='Owner only')
async def sync(ctx):
    if ctx.author.id == bot.owner_id:
        await bot.tree.sync(guild=discord.Object(id=240265833199173633))
        print('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')

@bot.event
async def on_ready():
    print("Bot ready")
    await bot.tree.sync()

if __name__ == "__main__":
    load_stats()
    newLoadAllImages()
    bot.run(DISCORD_TOKEN)