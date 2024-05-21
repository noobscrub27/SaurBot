import discord
from discord import ui, app_commands
from discord.ext import commands, tasks
import fnf_data
import showdown_scraper
import fnf_showdown
import saurbot_functions
import replay_analyzer
import cookie_types
import datetime
import time
import threading
import pickle
import random
import os
from io import StringIO
import logging
import enum
from quest_cog import Quest04Paths
import datetime
from humanfriendly import format_timespan
import asyncio

BATTLES_PER_POINT = 5
# Module descriptions:
# SaurBot.py - this is the main module. It creates the discord bot object and runs it.
# X_cog.py - All of the cog module are where the code for the commands are.
# fnf_showdown.py - The code for FnF Pokedex Search Command objects are contained here.
# showdown_scraper.py - The code used to obtain data for Saurbot's database is here. This is not on the Saurbot github at Noel's request.
# fnf_data.py - All of the classes necessary for storing data are defined here. It also contains functions for discord command checks, as well as the PaginationView.
# saurbot_functions.py - This module contains commonly used functions that need to be accessed by every other module in the project.
# cookie_types.py - This a meme. I don't know why I spent time on this.

DONT_LOAD_COGS = ["quest_cog"]
class SaurbotCogs(enum.Enum):
    tasks_cog = 0
    profile_cog = 1
    config_cog = 2
    mkw_cog = 3
    pokedex_cog = 4
    quest_cog = 5
    story_cog = 6
    analyze_cog = 7

class CogActions(enum.Enum):
    cog_load = 0
    cog_unload = 1
    cog_reload = 2

with open("token.txt", "r") as f:
    lines = f.readlines()
    fnf_data.DEV_ID = int(lines[0].strip())
    fnf_data.NOEL_ID = int(lines[1].strip())
    fnf_data.PIKA_ID = int(lines[2].strip())
    fnf_data.SHOWDOWN_INSTRUCTIONS_FILE = lines[3].strip()
    fnf_data.REPLAY_FOLDER = lines[4].strip()
    TOKEN = lines[5].strip()
    
DEFAULT_MAX_LINES = 10
DEFAULT_MAX_CHARS = 1000
DEFAULT_FUN = 0
MIN_TRIGGER_LEN = 3

class Client(commands.Bot):
    def __init__(self):
        self.my_name = ["saurbot", "sorebob", "saurbob", "sorebot"]
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.last_gspread_api_call_timestamp = 0
        self.GSPREAD_API_CALL_COOLDOWN = 60

    def check_gspread_api_cooldown(self):
        return True
        # api costs are not a concern for the foreseeable future
        now = datetime.datetime.now().timestamp()
        if now >= self.last_gspread_api_call_timestamp + self.GSPREAD_API_CALL_COOLDOWN:
            self.last_gspread_api_call_timestamp = now
            return True
        return False

    async def on_ready(self):
        saurbot_functions.timelog(f"Syncing commands...")
        await self.tree.sync()
        saurbot_functions.timelog(f"Logged in as {self.user}")

    async def setup_hook(self):
        for ext in SaurbotCogs:
            if ext.name not in DONT_LOAD_COGS:
                await self.load_extension(ext.name)
        #self.add_view(fnf_data.PaginationView())
        #self.add_view(ChallengeView())

    async def on_message(self, message):
        if message.author == self.user:
            return
        lowered_content = message.content.lower()
        if message.author == await self.fetch_user(fnf_data.DEV_ID):
            if isinstance(message.channel, discord.channel.DMChannel):
                if message.content.startswith("react"):
                    await self.react_to_message(message.content.removeprefix("react").strip())      
                elif message.content.startswith("unreact"):
                    await self.react_to_message(message.content.removeprefix("unreact").strip(), True)
                elif message.content.startswith("custom react"):
                    await self.custom_react_to_message(message.content.removeprefix("custom react").strip())
                elif message.content.startswith("custom unreact"):
                    await self.custom_react_to_message(message.content.removeprefix("custom unreact").strip(), True)
                elif message.content.startswith("reply"):
                    await self.reply_to_message(message.content.removeprefix("reply").strip(), message.attachments)
                elif message.content.startswith("silent reply"):
                    await self.reply_to_message(message.content.removeprefix("silent reply").strip(), message.attachments, False)
                elif message.content.startswith("say"):
                    await self.send_to_channel(message.content.removeprefix("say").strip(), message.attachments)
                elif message.content == "debug":
                    if fnf_showdown.debug_mode:
                        fnf_showdown.debug_mode = False
                        await message.reply("Debug mode is now off.")
                    else:
                        fnf_showdown.debug_mode = True
                        await message.reply("Debug mode is now on.")
        else:
            for alias in self.my_name:
                if alias in lowered_content:
                    if isinstance(message.channel, discord.channel.DMChannel) == False:
                        text = f"I was mentioned at {message.jump_url}. Full text: \"{message.content}\""
                        if len(text) > 2000:
                            text = text[:1996] + "...\""
                        await self.dm_noob(text, False)
                        return
            
        try:
            if message.guild.id in fnf_data.guild_preferences:
                for trigger in fnf_data.guild_preferences[message.guild.id].fun:
                    if trigger in lowered_content:
                        roll = random.random() * 100
                        if fnf_data.guild_preferences[message.guild.id].fun[trigger][0] > roll:
                            response = random.choice(fnf_data.guild_preferences[message.guild.id].fun[trigger][1:])
                            await message.reply(response)
                            saurbot_functions.timelog("Easter egg!")
        except AttributeError:
            return

    async def dm_noob(self, message, send_as_file=True):
        user = await self.fetch_user(fnf_data.DEV_ID)
        if user.dm_channel is None: 
            await user.create_dm()
        if send_as_file:
            await user.dm_channel.send(file=self.turn_into_file(message))
        else:
            await user.dm_channel.send(message)

    def get_guild_channel_message(self, text):
        guild_channel_message = text.split(";")[0]
        text = text.removeprefix(guild_channel_message+";").strip()
        guild_channel_message = guild_channel_message.strip().removeprefix("https://discord.com/channels/")
        guild_channel_message = guild_channel_message.split("/")
        try:
            guild_id = int(guild_channel_message[0])
        except IndexError:
            guild_id = 0
        try:
            channel_id = int(guild_channel_message[1])
        except IndexError:
            channel_id = 0
        try:
            message_id = int(guild_channel_message[2])
        except IndexError:
            message_id = 0
        return guild_id, channel_id, message_id, text

    async def send_to_channel(self, message, attachments):
        try:
            guild_id, channel_id, message_id, text = self.get_guild_channel_message(message)
            channel = self.get_channel(channel_id)
            await channel.send(text, files=[await attachment.to_file() for attachment in attachments])
        except Exception as e:
             print("Exception in send_to_channel:", e)

    async def reply_to_message(self, message, attachments, mention=True):
        try:
            guild_id, channel_id, message_id, text = self.get_guild_channel_message(message)
            channel = self.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.reply(text, files=[await attachment.to_file() for attachment in attachments], mention_author=mention)
        except Exception as e:
             print("Exception in reply_to_message:", e)

    async def react_to_message(self, message, remove=False):
        try:
            guild_id, channel_id, message_id, emoji = self.get_guild_channel_message(message)
            channel = self.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            if remove:
                await message.remove_reaction(emoji, self.user)
            else:
                await message.add_reaction(emoji)
        except Exception as e:
             print("Exception in react_to_message:", e)

    async def custom_react_to_message(self, message, remove=False):
        try:
            guild_id, channel_id, message_id, emoji_name = self.get_guild_channel_message(message)
            guild = self.get_guild(guild_id)
            channel = self.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            emoji = discord.utils.get(guild.emojis, name = emoji_name)
            if remove:
                await message.remove_reaction(emoji, self.user)
            else:
                await message.add_reaction(emoji)
        except Exception as e:
             print("Exception in custom_react_to_message:", e)

    def create_guild_preferences(self, guild):
        if guild.id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild.id] = Guild_Preferences(guild.id)
        self.write_preferences()

    def create_guild_user_profile(self, guild, user_id):
        self.create_guild_preferences(guild)
        if guild.get_member(user_id) is None:
            return False
        if user_id not in fnf_data.guild_preferences[guild.id].user_profiles:
            fnf_data.guild_preferences[guild.id].user_profiles[user_id] = User_Profile(user_id, fnf_data.guild_preferences[guild.id])
        return True

    def write_preferences(self, guild_file='guild_preferences.pickle', user_file='user_preferences.pickle', battle_file='battle_data.pickle'):
        with open(guild_file, 'wb') as f:
            pickle.dump(fnf_data.guild_preferences, f, protocol=pickle.HIGHEST_PROTOCOL)
        with open(user_file, 'wb') as f:
            pickle.dump([fnf_data.user_tutorial_state, fnf_data.user_mkw_fc], f, protocol=pickle.HIGHEST_PROTOCOL)
        with open(battle_file, 'wb') as f:
            pickle.dump([fnf_data.analyzed_replays, fnf_data.formats], f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_preferences(self):
        with open('guild_preferences.pickle', 'rb') as f:
            fnf_data.guild_preferences = pickle.load(f)
        with open('user_preferences.pickle', 'rb') as f:
            data = pickle.load(f)
        with open('battle_data.pickle', 'rb') as f:
            battle_data = pickle.load(f)
            fnf_data.analyzed_replays = battle_data[0]
            fnf_data.analyzed_replays = []
            fnf_data.formats = battle_data[1]
            fnf_data.formats = {}
        for guild in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild].update()

    def update_point_log(self, guild_id, user, old_points, new_points, change_type):
        file_name = os.path.join("point logs", str(guild_id) + ".txt")
        with open(file_name, "a", encoding="utf-8") as f:
            text = f"{user.id} ({user.display_name}): {old_points} -> {new_points} ({change_type})\n"
            f.write(text)

    def bointa_rng(self):
        return True if random.random() <= 0.01 else False

    def turn_into_file(self, message):
        return discord.File(StringIO(message), filename="results.txt")

    def create_guild_preferences(self, guild_id):
        return Guild_Preferences(guild_id)

class HelpView(discord.ui.View):
    async def send(self, interaction):
        self.timeout = None
        fnf_showdown_client_button = discord.ui.Button(label="FnF Showdown Client", style=discord.ButtonStyle.url, url="https://fnf-showdown-client.herokuapp.com/", row=0)
        self.add_item(fnf_showdown_client_button)
        fnf_showdown_calc_button = discord.ui.Button(label="Damage Calculator", style=discord.ButtonStyle.url, url="https://noobscrub27.github.io/fnf-damage-calc", row=0)
        self.add_item(fnf_showdown_calc_button)
        fnf_showdown_doc_button = discord.ui.Button(label="FnF Showdown Doc", style=discord.ButtonStyle.url, url="https://docs.google.com/spreadsheets/d/1olW_CgttMCgvR3LYIMndMfNDH18lqQAOf3ylPoosf_k/edit?usp=sharing", row=0)
        self.add_item(fnf_showdown_doc_button)
        point_and_spriting_guide_button = discord.ui.Button(label="Custom Pokemon Information Doc", style=discord.ButtonStyle.url, url="https://docs.google.com/document/d/1XsNuFZW2UskqCGv3pbdxDM8YRf7ou-iYT14zT1VrZOY/edit?usp=sharing", row=1)
        self.add_item(point_and_spriting_guide_button)
        hypnomons_doc_button = discord.ui.Button(label="Hypnomons Doc", style=discord.ButtonStyle.url, url="https://docs.google.com/spreadsheets/d/1SeKw1jYmnKmNUGKDQ7b8ZiR6c21bOOWhw1YJfax_YXg/edit?usp=sharing", row=1)
        self.add_item(hypnomons_doc_button)
        saurbot_guide_button = discord.ui.Button(label="Saurbot Guide", style=discord.ButtonStyle.url, url="https://docs.google.com/document/d/13SDdfcPebgQNadCTgHCheVKdhF4eCME-YjUgX4q96Ko/edit?usp=sharing", row=1)
        self.add_item(saurbot_guide_button)

        text = "***Help and resources:***\n"
        text += "- **The FnF Showdown Client** is where you can play FnF Showdown.\n"
        text += "- Find all of the data on the FnF Showdown changes with the **FnF Showdown Doc**. Type into the blue bar in the PokeViewer tab to view a specific pokemon in detail. You could also view the custom pokedex and keep track of points in this doc.\n"
        text += "- Plan your next move using the **Damage Calculator**. *The damage calculator is now fully functional. Please report any errors to noobscrub*.\n"
        text += "- View all the spriting procedures with the **Custom Pokemon Information Doc**\, as well as custom pokemon creation processes and a guide on how to use points.\n"
        text += "- View all information on Hypnomons in depth with the **Hypnomons Doc**, including sprites and custom dex entries!\n"
        text += "- Get help with Saurbot Commands and a guide on how to use the Pokedex Search commands with the **Saurbot Guide**.\n"
        text += "If you have questions about FnF Showdown not answered by the provided links, reach out to noel5229 on Discord.\n"
        text += "If you have questions about Saurbot not answered by the Saurbot Guide, reach out to noobscrub on Discord."
        await interaction.response.send_message(text, view=self, ephemeral=False)

# yeah idk why I named these with an underscore I like UpperCamelCase more for classes
# too late to change it now tho
class Guild_Preferences:
    def __init__(self, identifier, max_lines = DEFAULT_MAX_LINES, max_chars = DEFAULT_MAX_CHARS, fun = None):
        if fun is None:
            self.fun = {}
        else:
            self.fun = fun
        self.id = identifier,
        self.max_lines = max_lines
        self.max_chars = max_chars
        self.user_profiles = {}
        # member for member in bot.get_guild(self.id).members if member.guild_permissions.administrator
        self.saurbot_managers = []
        # trigger structure:
        # {trigger: [response_odds, response1, response2, etc.]}
        self.suggestion_settings = {"channel_id": 0, "anonymous": True, "autoreport": True}
        self.suggestion_box = []
        self.points_channel_id = None

    def update(self):
        # to see how to use this function, check User_Profile
        for user in self.user_profiles.values():
            user.update()
        if hasattr(self, "bot"):
            del self.bot

    def get_user_from_showdown(self, showdown):
        showdown = saurbot_functions.only_a_to_z(showdown)
        for user in self.user_profiles.values():
            if showdown in [saurbot_functions.only_a_to_z(account) for account in user.showdown_accounts]:
                return user
        return None

class User_Profile:
    def __init__(self, identifier, guild):
        self.guild = guild
        self.id = identifier
        self.shadowmon = None # {purified:bool, species:str, nickname:str, command_name:str}
        self.favorite_mon = None
        self.favorite_story_char = None
        self.favorite_buff = None
        self.favorite_custom_mon = None
        self.bointa = 0
        self.favorite_mkw_char = None
        self.favorite_mkw_vehicle = None
        self.favorite_course = None
        self.badges_obtained = 0
        self.quest_data = {4: {"boxes seen": [[], []]}}
        self.reset_treasure_collection()
        self.showdown_accounts = []
        self.pending_showdown_account_links = {}
        self.public_trainer_data = False
        self.trainer_sprite_url = None
        # key: tier name (str), trainer data (replay analyzer Trainer)
        self.trainer_data = {}
        self.gym_box = []
        self.battles_until_next_point = BATTLES_PER_POINT
        self.elo = {}

    def update(self):
        # pending_showdown_account_links should reset after every restart, so don't delete this
        self.pending_showdown_account_links = {}
        # when changing classes with the update function, since class data is pickled, you need to update old versions of the class using this update method before you can change the rest of the class
        # for example, to add a "foo" attribute, first put this in the update function:
        # if hasattr(self, "foo") == False:
        #     self.foo = <whatever the default value for foo will be>
        # after running SaurBot at least once like this, you can add self.foo = <default value> to the init function and ignore the update function until you need it again
        self.elo = {}
        self.battles_until_next_point = BATTLES_PER_POINT

    def get_elo(self, game_format):
        if game_format not in self.elo:
            self.elo[game_format] = 1000
        return self.elo[game_format]

    def set_elo(self, game_format, elo):
        self.elo[game_format] = elo

    async def battle_completed(self):
        self.battles_until_next_point -= 1
        username = bot.get_user(self.id).display_name
        if self.battles_until_next_point == 0:
            self.battles_until_next_point = BATTLES_PER_POINT
            old_points = self.bointa
            #self.bointa += 1
            #bot.update_point_log(self.guild.id, self.id, old_points, self.bointa, "ADD")
            bot.write_preferences()
            if self.guild.points_channel_id is not None:
                channel = bot.get_channel(self.guild.points_channel_id)
                #await channel.send(f"<@{self.id}> has earned a point from battling.")
            
    def reset_treasure_collection(self):
        self.quest_data[4]["treasure collection"] = {"Faisca Hollow": {"Common": [0 for i in range(6)], "Uncommon": [0 for i in range(9)], "Rare": [0,0]},
                                                     "Iris Cavern": {"Common": [0 for i in range(6)], "Uncommon": [0 for i in range(9)], "Rare": [0,0]},
                                                     "Both": {"Common": [], "Uncommon": [], "Rare": [0]},
                                                     "timestamp": 0,
                                                     "cookiestamp": 0}

    def get_treasure_text(self):
        treasures = self.quest_data[4]["treasure collection"]
        common_treasures_found = {"Faisca Hollow": sum(treasures["Faisca Hollow"]["Common"]+treasures["Both"]["Common"]),
                                  "Iris Cavern": sum(treasures["Iris Cavern"]["Common"]+treasures["Both"]["Common"]),
                                  "Total": sum(treasures["Faisca Hollow"]["Common"]+treasures["Iris Cavern"]["Common"]+treasures["Both"]["Common"])}
        uncommon_treasures_found = {"Faisca Hollow": sum(treasures["Faisca Hollow"]["Uncommon"]+treasures["Both"]["Uncommon"]),
                                    "Iris Cavern": sum(treasures["Iris Cavern"]["Uncommon"]+treasures["Both"]["Uncommon"]),
                                    "Total": sum(treasures["Faisca Hollow"]["Uncommon"]+treasures["Iris Cavern"]["Uncommon"]+treasures["Both"]["Uncommon"])}
        rare_treasures_found = {"Faisca Hollow": sum(treasures["Faisca Hollow"]["Rare"]+treasures["Both"]["Rare"]),
                                "Iris Cavern": sum(treasures["Iris Cavern"]["Rare"]+treasures["Both"]["Rare"]),
                                "Total": sum(treasures["Faisca Hollow"]["Rare"]+treasures["Iris Cavern"]["Rare"]+treasures["Both"]["Rare"])}
        treasures_found = {"Faisca Hollow": common_treasures_found["Faisca Hollow"]+uncommon_treasures_found["Faisca Hollow"]+rare_treasures_found["Faisca Hollow"],
                           "Iris Cavern": common_treasures_found["Iris Cavern"]+uncommon_treasures_found["Iris Cavern"]+rare_treasures_found["Iris Cavern"],
                           "Total": common_treasures_found["Total"]+uncommon_treasures_found["Total"]+rare_treasures_found["Total"]}
        unique_common_treasures_found = {"Faisca Hollow": sum([1 for item in treasures["Faisca Hollow"]["Common"]+treasures["Both"]["Common"] if item > 0]),
                                         "Iris Cavern": sum([1 for item in treasures["Iris Cavern"]["Common"]+treasures["Both"]["Common"] if item > 0]),
                                         "Total": sum([1 for item in treasures["Faisca Hollow"]["Common"]+treasures["Iris Cavern"]["Common"]+treasures["Both"]["Common"] if item > 0])}
        unique_uncommon_treasures_found = {"Faisca Hollow": sum([1 for item in treasures["Faisca Hollow"]["Uncommon"]+treasures["Both"]["Uncommon"] if item > 0]),
                                           "Iris Cavern": sum([1 for item in treasures["Iris Cavern"]["Uncommon"]+treasures["Both"]["Uncommon"] if item > 0]),
                                           "Total": sum([1 for item in treasures["Faisca Hollow"]["Uncommon"]+treasures["Iris Cavern"]["Uncommon"]+treasures["Both"]["Uncommon"] if item > 0])}
        unique_rare_treasures_found = {"Faisca Hollow": sum([1 for item in treasures["Faisca Hollow"]["Rare"]+treasures["Both"]["Rare"] if item > 0]),
                                        "Iris Cavern": sum([1 for item in treasures["Iris Cavern"]["Rare"]+treasures["Both"]["Rare"] if item > 0]),
                                        "Total": sum([1 for item in treasures["Faisca Hollow"]["Rare"]+treasures["Iris Cavern"]["Rare"]+treasures["Both"]["Rare"] if item > 0])}
        unique_treasures_found = {"Faisca Hollow": unique_common_treasures_found["Faisca Hollow"]+unique_uncommon_treasures_found["Faisca Hollow"]+unique_rare_treasures_found["Faisca Hollow"],
                                  "Iris Cavern": unique_common_treasures_found["Iris Cavern"]+unique_uncommon_treasures_found["Iris Cavern"]+unique_rare_treasures_found["Iris Cavern"],
                                  "Total": unique_common_treasures_found["Total"]+unique_uncommon_treasures_found["Total"]+unique_rare_treasures_found["Total"]}
        text = f"Faisca Hollow: {unique_common_treasures_found['Faisca Hollow']}/6 Common, {unique_uncommon_treasures_found['Faisca Hollow']}/9 Uncommon, {unique_rare_treasures_found['Faisca Hollow']}/3 Rare ({unique_treasures_found['Faisca Hollow']}/18)\n"
        text += f"Iris Cavern: {unique_common_treasures_found['Iris Cavern']}/6 Common, {unique_uncommon_treasures_found['Iris Cavern']}/9 Uncommon, {unique_rare_treasures_found['Iris Cavern']}/3 Rare ({unique_treasures_found['Iris Cavern']}/18)\n"
        text += f"All Treasures: {unique_common_treasures_found['Total']}/12 Common, {unique_uncommon_treasures_found['Total']}/18 Uncommon, {unique_rare_treasures_found['Total']}/5 Rare ({unique_treasures_found['Total']}/35)\n"
        text += f"Treasures Found: {common_treasures_found['Total']} Common, {uncommon_treasures_found['Total']} Uncommon, {rare_treasures_found['Total']} Rare (Total: {treasures_found['Total']})\n"
        return text

async def update_database():
    async for text in showdown_scraper.update_database():
        pass

asyncio.run(asyncio.wait_for(update_database(), timeout=None))
bot = Client()

@bot.tree.command(name="help", description="Get help with FnF Showdown and Saurbot.")
async def help_command(interaction: discord.Interaction):
    help_view = HelpView()
    await help_view.send(interaction)

@bot.tree.command(name="dadave", description="Was he right all along?")
async def dadave_command(interaction: discord.Interaction):
    await interaction.response.send_message(fnf_data.CHATOT)

@app_commands.guild_only()
@bot.tree.command(name="cookie", description="Cookie analysis.")
async def command_cookie(interaction: discord.Interaction):
    if random.random() < 0.02:
        cookie = cookie_types.DigitalCookieView()
        await cookie.send(interaction)
    else:
        cookies_list = [cookie_types.MoonCookie(),
                        cookie_types.ChocolateMoonCookie(),
                        cookie_types.HerbalMoonCookie(),
                        cookie_types.RoyalMoonCookie(),
                        cookie_types.DenseMoonCookie(),
                        cookie_types.BerryliciousMoonCookie()]
        text = str(random.choice(cookies_list))
        if random.random() < 0.25:
            bot.create_guild_user_profile(interaction.guild, interaction.user.id)
            now = datetime.datetime.now().timestamp()
            if fnf_data.guild_preferences[interaction.guild_id].user_profiles[interaction.user.id].quest_data[4]["treasure collection"]["cookiestamp"] + 21600 <= now:
                fnf_data.guild_preferences[interaction.guild_id].user_profiles[interaction.user.id].quest_data[4]["treasure collection"]["cookiestamp"] = now
                text += "\nHuh? The cookie came with something else.\n" + spelunk(random.choice(["Faisca Hollow","Iris Cavern"]), interaction.guild_id, interaction.user.id)
        await interaction.response.send_message(text)

@app_commands.guild_only()

@bot.tree.command(name="spelunk", description="Find an artifact in a cave.")
async def command_spelunk(interaction: discord.Interaction, path: Quest04Paths):
    """
    Parameters
    -----------
    path: Quest04Paths
        The path to go search for treasure in.
    """
    guild_id = interaction.guild_id
    user_id = interaction.user.id
    bot.create_guild_user_profile(interaction.guild, user_id)
    now = datetime.datetime.now().timestamp()
    diff = fnf_data.guild_preferences[guild_id].user_profiles[user_id].quest_data[4]["treasure collection"]["timestamp"] + 21600 - now
    if diff > 0:
        await interaction.response.send_message(f"You can only find one artifact or fossil every six hours. Try again in {format_timespan(max(1, int(diff)))}.")
        return
    if path.name == "faisca_hollow":
        text = spelunk("Faisca Hollow", guild_id, user_id)
    elif path.name == "iris_cavern":
        text = spelunk("Iris Cavern", guild_id, user_id)
    else:
        await interaction.response.send_message("Something went wrong.")
        return
    fnf_data.guild_preferences[guild_id].user_profiles[user_id].quest_data[4]["treasure collection"]["timestamp"] = now
    await interaction.response.send_message(text)

def spelunk(path, guild_id, user_id):
    location, rarity, index, artifact = cookie_types.random_artifact(path)
    artifact_name = artifact[0]
    artifact_description = artifact[1]
    fnf_data.guild_preferences[guild_id].user_profiles[user_id].quest_data[4]["treasure collection"][location][rarity][index] += 1
    amount_found = fnf_data.guild_preferences[guild_id].user_profiles[user_id].quest_data[4]["treasure collection"][location][rarity][index]
    collection = fnf_data.guild_preferences[guild_id].user_profiles[user_id].quest_data[4]["treasure collection"]
    both_artifacts = collection["Both"]["Common"] + collection["Both"]["Uncommon"] +collection["Both"]["Rare"] 
    faisca_artifacts = collection["Faisca Hollow"]["Common"] + collection["Faisca Hollow"]["Uncommon"] +collection["Faisca Hollow"]["Rare"] 
    iris_artifacts = collection["Iris Cavern"]["Common"] + collection["Iris Cavern"]["Uncommon"] +collection["Iris Cavern"]["Rare"] 
    text = f"You found "
    if artifact_name.lower().startswith("a"):
        text += "an " + artifact_name + "."
    else:
        text += "a " + artifact_name + "."
    if amount_found == 1:
        text += " This is your first " + artifact_name + ".\n"
    else:
        text += f" You've found {amount_found} " + artifact_name
        if artifact_name.lower().endswith("s"):
            text += "es"
        else:
            text += "s"
        text += " so far.\n"
    text += "*" + artifact_description + "*\n"
    if path == "Faisca Hollow":
        location_artifacts_found = len([item for item in both_artifacts + faisca_artifacts if item > 0])
        location_total_artifacts = len([item for item in both_artifacts + faisca_artifacts])
    else:
        location_artifacts_found = len([item for item in both_artifacts + iris_artifacts if item > 0])
        location_total_artifacts = len([item for item in both_artifacts + iris_artifacts])
    total_artifacts_found = len([item for item in both_artifacts + iris_artifacts + faisca_artifacts if item > 0])
    total_artifacts = len([item for item in both_artifacts + iris_artifacts + faisca_artifacts])
    text += f"You've found {location_artifacts_found} out of {location_total_artifacts} artifacts and fossils in {path}.\n"
    text += f"Overall, you've found {total_artifacts_found} out of {total_artifacts} artifacts and fossils."
    bot.write_preferences()
    return text

@bot.tree.command(name="cogs", description="Manage a cog. Dev only.")
async def command_cogs(interaction: discord.Interaction,
                         action:CogActions,
                         cog:SaurbotCogs=None):
    """
    Parameters
    -----------
    action: CogActions
        The action to perform on the cog.
    cog: SaurbotCogs
        Optional. The cog to manage. Defaults to all cogs.
    """
    await interaction.response.defer(thinking=True,ephemeral=True)
    if fnf_data.check_is_noob(interaction) == False:
        await interaction.followup.send(content="Something went wrong. Make sure you have permission to use this command.",ephemeral=True)
        return
    cogs = list(SaurbotCogs) if cog is None else [cog]
    successes = 0
    failures = []
    for item in cogs:
        try:
            if action.name == "cog_load":
                await bot.load_extension(item.name)
            elif action.name == "cog_unload":
                await bot.unload_extension(item.name)
            elif action.name == "cog_reload":
                await bot.reload_extension(item.name)
            successes += 1
        except Exception as e:
            failures.append(str(e))
    await bot.tree.sync()
    text = f"Successfully {action.name.removeprefix('cog_')}ed {successes} cog(s)."
    text += f"\nCould not {action.name.removeprefix('cog_')} {len(failures)} cogs(s)."
    for failure in failures:
        text += "\n" + failure
    await interaction.followup.send(content=text,ephemeral=True)


FUN_PLACEHOLDERS = ["Your great idea goes here!",
                    "We should buff Saurbot.",
                    "We should start doing Free Bointa Fridays."]

class SuggestionModal(ui.Modal, title="Suggestion"):
    def __init__(self, anonymous, channel_id):
        super().__init__()
        self.add_item(ui.TextInput(label="Enter your suggestion", placeholder=random.choice(FUN_PLACEHOLDERS), style=discord.TextStyle.long, max_length=1000))
        self.submit_anonymously = anonymous
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
        now = datetime.datetime.now()
        now_text = now.strftime("%Y-%m-%d %H:%M:%S")
        display_name = "Anonymous User" if self.submit_anonymously else interaction.user.name
        fnf_data.guild_preferences[interaction.guild_id].suggestion_box.append({"username": display_name, "suggestion": self.children[0].value, "time": now_text})
        bot.write_preferences()
        if self.channel_id != 0:
            channel = bot.get_channel(self.channel_id)
            await channel.send(f"Suggestion from {display_name}:\n{self.children[0].value}")

class NonAnonymousSuggestionConfirmView(discord.ui.View):
    async def send(self, interaction, channel_id):
        await interaction.response.defer()
        self.timeout = None
        self.channel_id = channel_id
        self.message_text = "You have chosen to suggest anonymously. However, this server has anonymous suggestions disabled.\nWould you like to continue? Your suggestion will not be anonymous."
        self.message = await interaction.followup.send(content=self.message_text, view=self, ephemeral=True)
        
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.blurple, custom_id="NonAnonymousSuggestionConfirmView:continue_button")
    async def continue_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestionModal(False, self.channel_id))
        await self.destroy()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="NonAnonymousSuggestionConfirmView:cancel_button")
    async def cancel_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.destroy()

    async def destroy(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(content=self.message_text, view=self)
        self.stop()

@bot.tree.command(name="suggest", description="Suggest a change to the moderators.")
async def command_suggest(interaction: discord.Interaction,
                          anonymous: bool):
    """
    Parameters
    -----------
    anonymous: bool
        When set to True, your suggestion will be anonymous if the server allows it.
    """
    guild_id = interaction.guild_id
    user_id = interaction.user.id
    bot.create_guild_user_profile(interaction.guild, user_id)
    suggestion_settings = fnf_data.guild_preferences[guild_id].suggestion_settings
    if suggestion_settings["channel_id"] == 0:
        await interaction.response.send_message(f"Suggestions are not enabled for this server.", ephemeral=True)
    else:
        if suggestion_settings["anonymous"] == False and anonymous == True:
            confirm_view = NonAnonymousSuggestionConfirmView()
            await confirm_view.send(interaction, suggestion_settings["channel_id"] if suggestion_settings["autoreport"] else 0)
        else:
            await interaction.response.send_modal(SuggestionModal(anonymous, suggestion_settings["channel_id"] if suggestion_settings["autoreport"] else 0))

bot.load_preferences()
# this ensures that the update method for the preferences objects gets applied
bot.write_preferences()

bot.run(TOKEN, log_level=logging.WARN)
