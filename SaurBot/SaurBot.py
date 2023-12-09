import discord
from discord.ext import commands
import fnf_data
import showdown_scraper
import fnf_showdown
import saurbot_functions
import cookie_types
import datetime
import time
import schedule
import threading
import pickle
import random
import os
from io import StringIO
# Module descriptions:
# SaurBot.py - this is the main module. It creates the discord bot object and runs it.
# X_cog.py - All of the cog module are where the code for the commands are.
# fnf_showdown.py - The code for FnF Pokedex Search Command objects are contained here.
# showdown_scraper.py - The code used to obtain data for Saurbot's database is here. This is not on the Saurbot github at Noel's request.
# fnf_data.py - All of the classes necessary for storing data are defined here. It also contains functions for discord command checks, as well as the PaginationView.
# saurbot_functions.py - This module contains commonly used functions that need to be accessed by every other module in the project.
# cookie_types.py - This a meme. I don't know why I spent time on this.

with open("token.txt", "r") as f:
    lines = f.readlines()
    fnf_data.DEV_ID = int(lines[0].strip())
    fnf_data.NOEL_ID = int(lines[1].strip())
    TOKEN = lines[2].strip()

DEFAULT_MAX_LINES = 10
DEFAULT_MAX_CHARS = 1000
DEFAULT_FUN = 0
MIN_TRIGGER_LEN = 3

class Client(commands.Bot):
    def __init__(self):
        self.my_name = ["saurbot", "sorebob", "saurbob", "sorebot"]
        self.cogslist = ["profile_cog", "mkw_cog", "config_cog", "pokedex_cog"]
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        async for text in showdown_scraper.update_database():
            pass
        saurbot_functions.timelog(f"Syncing commands...")
        await self.tree.sync()
        saurbot_functions.timelog(f"Logged in as {self.user}")
    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

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
            fnf_data.guild_preferences[guild.id].user_profiles[user_id] = User_Profile(user_id)
        return True

    def write_preferences(self, guild_file='guild_preferences.pickle', user_file='user_preferences.pickle'):
        with open(guild_file, 'wb') as f:
            pickle.dump(fnf_data.guild_preferences, f, protocol=pickle.HIGHEST_PROTOCOL)
        with open(user_file, 'wb') as f:
            pickle.dump([fnf_data.user_tutorial_state, fnf_data.user_mkw_fc], f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_preferences(self):
        try:
            with open('guild_preferences.pickle', 'rb') as f:
                fnf_data.guild_preferences = pickle.load(f)
        except FileNotFoundError:
            pass
        try:
            with open('user_preferences.pickle', 'rb') as f:
                data = pickle.load(f)
                fnf_data.user_tutorial_state, fnf_data.user_mkw_fc = data[0], data[1]
        except FileNotFoundError:
            pass
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
        self.timeout = 300
        fnf_showdown_client_button = discord.ui.Button(label="FnF Showdown Client", style=discord.ButtonStyle.url, url="https://fnf-showdown-client.herokuapp.com/")
        self.add_item(fnf_showdown_client_button)
        fnf_showdown_doc_button = discord.ui.Button(label="FnF Showdown Doc", style=discord.ButtonStyle.url, url="https://docs.google.com/spreadsheets/d/1olW_CgttMCgvR3LYIMndMfNDH18lqQAOf3ylPoosf_k/edit?usp=sharing")
        self.add_item(fnf_showdown_doc_button)
        point_and_spriting_guide_button = discord.ui.Button(label="Points & Spriting Guide", style=discord.ButtonStyle.url, url="https://docs.google.com/spreadsheets/d/1mXYqbtdAfKr4fBcHyj4BOJ6xypQaxkHqmAiHQgzEo2Q/edit?usp=sharing")
        self.add_item(point_and_spriting_guide_button)
        hypnomons_doc_button = discord.ui.Button(label="Hypnomons Doc", style=discord.ButtonStyle.url, url="https://docs.google.com/spreadsheets/d/1SeKw1jYmnKmNUGKDQ7b8ZiR6c21bOOWhw1YJfax_YXg/edit?usp=sharing")
        self.add_item(hypnomons_doc_button)
        saurbot_guide_button = discord.ui.Button(label="Saurbot Guide", style=discord.ButtonStyle.url, url="https://docs.google.com/document/d/13SDdfcPebgQNadCTgHCheVKdhF4eCME-YjUgX4q96Ko/edit?usp=sharing")
        self.add_item(saurbot_guide_button)

        text = "***Help and resources:***\n"
        text += "- **The FnF Showdown Client** is where you can play FnF Showdown.\n"
        text += "- Find all of the data on the FnF Showdown changes with the **FnF Showdown Doc**. Type into the blue bar in the PokeViewer tab to view a specific pokemon in detail.\n"
        text += "- Keep track of points and spriting with the **Points & Spriting Guide**, while also viewing the FnF Showdown custom pokedex.\n"
        text += "- View all information on Hypnomons in depth with the **Hypnomons Doc**, including sprites and custom dex entries!\n"
        text += "- Get help with Saurbot Commands and a guide on how to use the Pokedex Search commands with the **Saurbot Guide**.\n"
        text += "If you have questions about FnF Showdown not answered by the provided links, reach out to noel5229 on Discord.\n"
        text += "If you have questions about Saurbot not answered by the Saurbot Guide, reach out to noobscrub on Discord."
        await interaction.response.send_message(text, view=self, ephemeral=True)


bot = Client()

@bot.tree.command(name="help", description="Get help with FnF Showdown and Saurbot.")
async def help_command(interaction: discord.Interaction):
    help_view = HelpView()
    await help_view.send(interaction)

@bot.tree.command(name="dadave", description="Was he right all along?")
async def dadave_command(interaction: discord.Interaction):
    await interaction.response.send_message(fnf_data.CHATOT)

# yeah idk why I named these with an underscore I like UpperCamelCase more for classes
# too late to change it now tho
class User_Profile:
    def __init__(self, identifier, shadowmon = None, favorite_mon = None, favorite_story_char = None, favorite_buff = None, favorite_custom_mon = None, bointa = 0, favorite_mkw_char = None, favorite_mkw_vehicle = None, favorite_course = None, badges_obtained = 0):
        self.id = identifier
        self.shadowmon = shadowmon # {purified:bool, species:str, nickname:str, command_name:str}
        self.favorite_mon = favorite_mon
        self.favorite_story_char = favorite_story_char
        self.favorite_buff = favorite_buff
        self.favorite_custom_mon = favorite_custom_mon
        self.bointa = bointa
        self.favorite_mkw_char = favorite_mkw_char
        self.favorite_mkw_vehicle = favorite_mkw_vehicle
        self.favorite_course = favorite_course
        self.badges_obtained = badges_obtained
    def update(self):
        pass
        # when changing classes with the update function, since class data is pickled, you need to update old versions of the class using this update method before you can change the rest of the class
        # for example, to add a "foo" attribute, first put this in the update function:
        # if hasattr(self, "foo") == False:
        #     self.foo = <whatever the default value for foo will be>
        # after running SaurBot at least once like this, you can add self.foo = <default value> to the init function and ignore the update function until you need it again
    async def get_embed(self, profile_type):
        point_text_rng = bot.bointa_rng()
        mkw_profile = True if self.id in fnf_data.user_mkw_fc and len(fnf_data.user_mkw_fc[self.id]) else False
        user = await bot.fetch_user(self.id)
        if user is None:
            return None
        results_embed = discord.Embed(color=(user.accent_color if user.accent_color is not None else discord.Color.default()),title=user.display_name)
        results_embed.set_thumbnail(url=user.display_avatar.url)
        text = ""
        if profile_type == "pkmn":
            if self.bointa is not None:
                results_embed.add_field(name=("Bointa" if point_text_rng else "Points"), value=str(self.bointa))
            if self.favorite_mon is not None:
                results_embed.add_field(name="Favorite Pokemon", value=self.favorite_mon)
            if self.favorite_buff is not None:
                results_embed.add_field(name="Favorite Buff/Rework", value=self.favorite_buff)
            if self.favorite_custom_mon is not None:
                results_embed.add_field(name="Favorite Custom Pokemon", value=self.favorite_custom_mon)
            if self.favorite_story_char is not None:
                results_embed.add_field(name="Favorite FnF Character", value=self.favorite_story_char)
            results_embed.add_field(name="Badges obtained", value=str(self.badges_obtained))
            if self.shadowmon is not None:
                results_embed.add_field(name="Shadowmon", value=self.shadowmon["nickname"] + (" (Purified " if self.shadowmon["purified"] else " (Shadow ") + self.shadowmon["species"] + ")\n*/pokedex pokemon name " + self.shadowmon["command_name"] + "*")
        elif profile_type == "mkw":
            if self.favorite_mkw_char is not None:
                results_embed.add_field(name="Favorite MKW Character", value=self.favorite_mkw_char)
            if self.favorite_mkw_vehicle is not None:
                results_embed.add_field(name="Favorite MKW Vehicle", value=self.favorite_mkw_vehicle)
            if self.favorite_course is not None:
                results_embed.add_field(name="Favorite MKW Course", value=self.favorite_course)
            if mkw_profile:
                text = ""
                for i, code in enumerate(fnf_data.user_mkw_fc[self.id]):
                    text += str(i+1) + ": " + code + "\n"
                results_embed.add_field(name="MKW Friend Codes", value=text)
        if len(results_embed.fields) == 0:
            results_embed.add_field(name="No data to display",value="Use */profile set* to set up your profile.")
        return results_embed

@bot.tree.command(name="cookie", description="Cookie analysis.")
async def cookie_command(interaction: discord.Interaction):
        cookies_list = [cookie_types.MoonCookie(),
                        cookie_types.ChocolateMoonCookie(),
                        cookie_types.HerbalMoonCookie(),
                        cookie_types.RoyalMoonCookie(),
                        cookie_types.DenseMoonCookie(),
                        cookie_types.BerryliciousMoonCookie()]
        await interaction.response.send_message(str(random.choice(cookies_list)))

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
    def update(self):
        # to see how to use this function, check User_Profile
        pass

def backup():
    saurbot_functions.timelog("Creating backup")
    now = datetime.datetime.now()
    now_text = now.strftime("%m-%d-%y")
    guild_file_name = 'guild_preferences_backup - ' + now_text + '.pickle'
    guild_file_path = os.path.join("backups", "guild_preferences", guild_file_name)
    user_file_name = 'user_preferences_backup - ' + now_text + '.pickle'
    user_file_path = os.path.join("backups", "user_preferences", user_file_name)
    bot.write_preferences(guild_file_path, user_file_path)


schedule.every().day.at("00:00").do(backup)
def schedule_backup_save():
    print("Schedule started")
    while True:
        schedule.run_pending()
        time.sleep(60)

bot.load_preferences()

thread = threading.Thread(target=schedule_backup_save)
thread.start()
bot.run(TOKEN)