import discord
import fnf_showdown
import pickle
import random
from io import StringIO
import mkw_data
import schedule
import time
import datetime
import os
import threading

with open("token.txt", "r") as f:
    lines = f.readlines()
    DEV_ID = int(lines[0].strip())
    TOKEN = lines[1].strip()

EVIL_PLAYER_EASTER_EGG = 0.01
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
bot = discord.Bot(intents=intents)

guild_preferences = {}
guid_user_profiles = {}
user_tutorial_state = {}
user_mkw_fc = {}
DEFAULT_MAX_LINES = 10
DEFAULT_MAX_CHARS = 1000
DEFAULT_FUN = 0
MIN_TRIGGER_LEN = 3
# number of seconds to wait between /update commands
UPDATE_COOLDOWN = 60

def backup():
    fnf_showdown.timelog("Creating backup")
    now = datetime.datetime.now()
    now_text = now.strftime("%m-%d-%y")
    guild_file_name = 'guild_preferences_backup - ' + now_text + '.pickle'
    guild_file_path = os.path.join("backups", "guild_preferences", guild_file_name)
    user_file_name = 'user_preferences_backup - ' + now_text + '.pickle'
    user_file_path = os.path.join("backups", "user_preferences", user_file_name)
    write_preferences(guild_file_path, user_file_path)


def load_preferences():
    global guild_preferences, user_tutorial_state, user_mkw_fc
    try:
        with open('guild_preferences.pickle', 'rb') as f:
            guild_preferences = pickle.load(f)
    except FileNotFoundError:
        pass
    try:
        with open('user_preferences.pickle', 'rb') as f:
            data = pickle.load(f)
            user_tutorial_state, user_mkw_fc = data[0], data[1]
    except FileNotFoundError:
        pass
    for guild in guild_preferences:
        guild_preferences[guild].update()
    
def write_preferences(guild_file='guild_preferences.pickle', user_file='user_preferences.pickle'):
    with open(guild_file, 'wb') as f:
        pickle.dump(guild_preferences, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(user_file, 'wb') as f:
        pickle.dump([user_tutorial_state, user_mkw_fc], f, protocol=pickle.HIGHEST_PROTOCOL)

def update_point_log(guild_id, user, old_points, new_points, change_type):
    file_name = os.path.join("point logs", str(guild_id) + ".txt")
    with open(file_name, "a") as f:
        text = str(user.id) + " (" + user.display_name + "):"
        text += " " + str(old_points) + " -> " + str(new_points) + " (" + change_type + ")\n"
        f.write(text)


def check_message_size(context, message):
    # this function previously determined if a message was too long and should be uplodaded as a file. however, I now think that its unnecessary, but I dont want to lose the code in case I decide to bring it back
    # elsewhere, related code can be found commented out in similar ways
    '''
    message_lines = len(message.split("\n"))
    message_chars = len(message)
    if context.guild.id in guild_preferences.keys():
        max_lines = guild_preferences[context.guild.id].max_lines
        max_chars = guild_preferences[context.guild.id].max_chars
    else:
        max_lines = guild_preferences["DEFAULT"].max_lines
        max_chars = guild_preferences["DEFAULT"].max_chars
    if message_lines > max_lines or message_chars > max_chars:
        return False
    return True
    '''
    return False
    

def turn_into_file(message):
    return discord.File(StringIO(message), filename="results.txt")

async def dm_noob(message):
    user = await bot.fetch_user(DEV_ID)
    if user.dm_channel is None: 
        await user.create_dm()
    await user.dm_channel.send(file=turn_into_file(message))

def bointa_rng():
    return True if random.random() <= 0.01 else False

class User_Profile:
    def __init__(self, identifier, shadowmon = None, favorite_mon = None, favorite_story_char = None, favorite_buff = None, favorite_custom_mon = None, bointa = 0, favorite_mkw_char = None, favorite_mkw_vehicle = None, favorite_course = None):
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
    def update(self):
        # when changing classes with the update function, since class data is pickled, you need to update old versions of the class using this update method before you can change the rest of the class
        # for example, to add a "foo" attribute, first put this in the update function:
        # if has attr(self, "foo") == False:
        #     self.foo = <whatever the default value for foo will be>
        # after running SaurBot at least once like this, you can add self.foo = <default value> to the init function and ignore the update function until you need it again
        if hasattr(self, "shadowmon") == False:
            self.shadowmon = None
        if hasattr(self, "favorite_mon") == False:
            self.favorite_mon = None
        if hasattr(self, "favorite_story_char") == False:
            self.favorite_story_char = None
        if hasattr(self, "favorite_buff") == False:
            self.favorite_buff = None
        if hasattr(self, "favorite_custom_mon") == False:
            self.favorite_custom_mon = None
        if hasattr(self, "bointa") == False:
            self.bointa = 0
        if hasattr(self, "favorite_mkw_char") == False:
            self.favorite_mkw_char = None
        if hasattr(self, "favorite_mkw_vehicle") == False:
            self.favorite_mkw_vehicle = None
        if hasattr(self, "favorite_course") == False:
            self.favorite_course = None
    async def get_embed(self):
        point_text_rng = bointa_rng()
        mkw_profile = True if self.id in user_mkw_fc and len(user_mkw_fc[self.id]) else False
        user = await bot.fetch_user(self.id)
        if user is None:
            return None
        results_embed = discord.Embed(color=(user.accent_color if user.accent_color is not None else discord.Color.default()),title=user.display_name)
        results_embed.set_thumbnail(url=user.display_avatar.url)
        text = ""
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
        if self.shadowmon is not None:
            results_embed.add_field(name="Shadowmon", value=self.shadowmon["nickname"] + (" (Purified " if self.shadowmon["purified"] else " (Shadow ") + self.shadowmon["species"] + ")\n*/pokemon name " + self.shadowmon["command_name"] + "*")

        if self.favorite_mkw_char is not None:
            results_embed.add_field(name="Favorite MKW Character", value=self.favorite_mkw_char)
        if self.favorite_mkw_vehicle is not None:
            results_embed.add_field(name="Favorite MKW Vehicle", value=self.favorite_mkw_vehicle)
        if self.favorite_course is not None:
            results_embed.add_field(name="Favorite MKW Course", value=self.favorite_course)
        if mkw_profile:
            text = ""
            for i, code in enumerate(user_mkw_fc[self.id]):
                text += str(i+1) + ": " + code + "\n"
            results_embed.add_field(name="MKW Friend Codes", value=text)
        return results_embed
        
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
        for profile in self.user_profiles:
            self.user_profiles[profile].update()
        if hasattr(self, "saurbot_managers") == False:
            self.saurbot_managers = self.profile_managers
            delattr(self, "profile_managers")
     
def get_user_tutorial_state(ctx):
    try:
        user_pref = user_tutorial_state[ctx.author.id]
    except KeyError:
        user_tutorial_state[ctx.author.id] = None
    return user_tutorial_state[ctx.author.id]

def create_guild_preferences(guild):
    global guild_preferences
    if guild.id not in guild_preferences:
        guild_preferences[guild.id] = Guild_Preferences(guild.id)
    write_preferences()

def create_guild_user_profile(guild, user_id):
    create_guild_preferences(guild)
    if guild.get_member(user_id) is None:
        return False
    if user_id not in guild_preferences[guild.id].user_profiles:
        guild_preferences[guild.id].user_profiles[user_id] = User_Profile(user_id)
    return True

def check_saurbot_permissions(ctx):
    return ctx.author.id in guild_preferences[ctx.guild.id].saurbot_managers

ABOUT_SAURBOT_EMBED = discord.Embed(title="Help", color=discord.Colour.green())
ABOUT_SAURBOT_EMBED.add_field(name="About", value="SaurBot is a bot created specifically for FnF. SaurBot's biggest feature is FnF Showdown Search, which can be used to filter data from our Gen 7 Draft pet mod. However, SaurBot has other commands for Mario Kart and more. For help using FnF Showdown Search, type /tutorial, or use the other /help commands.")
ABOUT_SAURBOT_EMBED.add_field(name="Contact and Special Thanks", value="If you need help, have a question or suggestion, or find a bug, please feel free to DM noobscrub#5659. Special thanks to Noel, without his continued hard work on both FnF Showdown and the Google Document that all the data is stored in, FnF Showdown Search would not be possible. And of course, thanks to the FnF community for helping FnF Showdown thrive.")

'''
LARGE_MESSAGE_EMBED = discord.Embed(color=discord.Colour.green())
LARGE_MESSAGE_EMBED.add_field(name="Large message", value="Because of the size of this message, SaurBot will instead upload it as a file to reduce server clutter.")
LARGE_MESSAGE_EMBED.set_footer(text="Server mods: If you have the manager server user permission, you can use \"/config spam\" to adjust how SaurBot handles large messages.")
'''

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

help_commands = bot.create_group("help", "Commands to learn more about SaurBot")
config_commands = bot.create_group("config", "Commands to configure general bot behavior (SaurBot management permission required)")
pkmn_commands = bot.create_group("pkmn", "Utility commands for FnF Showdown")
mkw_commands = bot.create_group("mkw", "Utility commands for Mario Kart Wii")
profile_commands = bot.create_group("profile", "Commands for viewing and changing user profiles")

@config_commands.command(description="Give a user permission to manage SaurBot settings for this server. (Server owner only)")
async def promote(ctx, member: discord.Option(discord.Member, "The member to promote.", name="member")):
    try:
        if ctx.author.guild_permissions.administrator:
            user_id = member.id
            if ctx.guild.get_member(user_id) is None:
                await ctx.respond(f"This user is not a part of this server.")
                return
            if user_id in guild_preferences[ctx.guild.id].saurbot_managers:
                await ctx.respond(f"This user already has SaurBot management permissions.")
                return
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            guild_preferences[ctx.guild.id].saurbot_managers.append(user_id)
            write_preferences()
            await ctx.respond(f"{user.display_name} was given permission to manage SaurBot settings.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Remove a user's permission to manage SaurBot settings. (Server owner only)")
async def demote(ctx, member: discord.Option(discord.Member, "The member to demote.", name="member")):
    try:
        if ctx.author.guild_permissions.administrator:
            user_id = member.id
            if ctx.guild.get_member(user_id) is None:
                await ctx.respond(f"This user is not a part of this server.")
                return
            if user_id not in guild_preferences[ctx.guild.id].saurbot_managers:
                await ctx.respond(f"This user doesn't have SaurBot management permissions.")
                return
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            guild_preferences[ctx.guild.id].saurbot_managers.remove(user_id)
            write_preferences()
            await ctx.respond(f"{user.display_name} can no longer manage profiles.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")


@profile_commands.command(description="Set up your SaurBot user profile")
async def set(ctx, favorite_mon: discord.Option(str, "Your favorite Pokemon. Type 'none' to reset.", name="pokemon", default="", max_length=1024),
              favorite_buff: discord.Option(str, "Your favorite FnF Showdon buff/change/rework. Type 'none' to reset.", name="buff", default="", max_length=1024),
              favorite_custom_mon: discord.Option(str, "Your favorite FnF Showdon custom Pokemon. Type 'none' to reset.", name="custom_pokemon", default="", max_length=1024),
              favorite_story_char: discord.Option(str, "Your favorite FnF Showdon story character. Type 'none' to reset.", name="fnf_character", default="", max_length=1024),
              mkw_character: discord.Option(str, "Your favorite Mario Kart Wii character. Type 'none' to reset.", name="mkw_character", default="", max_length=1024),
              mkw_vehicle: discord.Option(str, "Your favorite Mario Kart Wii vehicle. Type 'none' to reset.", name="mkw_vehicle", default="", max_length=1024),
              mkw_track: discord.Option(str, "Your favorite Mario Kart Wii track. Type 'none' to reset.", name="mkw_track", default="", max_length=1024)):
    create_guild_user_profile(ctx.guild, ctx.author.id)
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    if favorite_mon != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_mon = None if favorite_mon == "none" else favorite_mon
    if favorite_buff != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_buff = None if favorite_buff == "none" else favorite_buff
    if favorite_custom_mon != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_custom_mon = None if favorite_custom_mon == "none" else favorite_custom_mon
    if favorite_story_char != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_story_char = None if favorite_story_char == "none" else favorite_story_char
    if mkw_character != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_char = None if mkw_character == "none" else mkw_character
    if mkw_vehicle != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_vehicle = None if mkw_vehicle == "none" else mkw_vehicle
    if mkw_track != "":
        guild_preferences[guild_id].user_profiles[user_id].favorite_course = None if mkw_track == "none" else mkw_track
    write_preferences()
    await ctx.respond(f"Your profile has been updated.")

@config_commands.command(description="Manage a member's SaurBot profile.")
async def manage_profile(ctx, member: discord.Option(discord.Member, "The server member whos profile you'd like to manage.", name="member"),
                 favorite_mon: discord.Option(str, "Favorite Pokemon. Type 'none' to reset.", name="pokemon", default="", max_length=1024),
                 favorite_buff: discord.Option(str, "Favorite FnF Showdon buff/change/rework. Type 'none' to reset.", name="buff", default="", max_length=1024),
                 favorite_custom_mon: discord.Option(str, "Favorite FnF Showdon custom Pokemon. Type 'none' to reset.", name="custom_pokemon", default="", max_length=1024),
                 favorite_story_char: discord.Option(str, "Favorite FnF Showdon story character. Type 'none' to reset.", name="fnf_character", default="", max_length=1024),
                 mkw_character: discord.Option(str, "Favorite Mario Kart Wii character. Type 'none' to reset.", name="mkw_character", default="", max_length=1024),
                 mkw_vehicle: discord.Option(str, "Favorite Mario Kart Wii vehicle. Type 'none' to reset.", name="mkw_vehicle", default="", max_length=1024),
                 mkw_track: discord.Option(str, "Favorite Mario Kart Wii track. Type 'none' to reset.", name="mkw_track", default="", max_length=1024)):
    create_guild_preferences(ctx.guild)
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            user_id = member.id
            if create_guild_user_profile(ctx.guild, user_id) == False:
                await ctx.respond(f"That user is not a member of this server.")
                return
            guild_id = ctx.guild.id
            if favorite_mon != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_mon = None if favorite_mon == "none" else favorite_mon
            if favorite_buff != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_buff = None if favorite_buff == "none" else favorite_buff
            if favorite_custom_mon != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_custom_mon = None if favorite_custom_mon == "none" else favorite_custom_mon
            if favorite_story_char != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_story_char = None if favorite_story_char == "none" else favorite_story_char
            if mkw_character != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_char = None if mkw_character == "none" else mkw_character
            if mkw_vehicle != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_vehicle = None if mkw_vehicle == "none" else mkw_vehicle
            if mkw_track != "":
                guild_preferences[guild_id].user_profiles[user_id].favorite_course = None if mkw_track == "none" else mkw_track
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            write_preferences()
            await ctx.respond(f"{user.display_name}'s profile has been updated.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Assign a user their shadowmon.")
async def assign_shadowmon(ctx, member: discord.Option(discord.Member, "The member to receive the shadowmon.", name="member"),
                    species: discord.Option(str, "The species of the shadowmon.", name="species"),
                    nickname: discord.Option(str, "The nickname of the shadowmon.", name="nickname"),
                    purified: discord.Option(bool, "Whether the shadowmon has been purified.", name="purified"),
                    command_name: discord.Option(str, "The name of the shadowmon as it appears in the FnF Showdown Search database. (ex. Bulbasaur-Saur)", name="database_name")):
    create_guild_preferences(ctx.guild)
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            user_id = member.id
            if create_guild_user_profile(ctx.guild, user_id) == False:
                await ctx.respond(f"That user is not a member of this server.")
                return
            mon = {"species": species, "nickname": nickname, "purified": purified, "command_name": command_name}
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            guild_preferences[ctx.guild.id].user_profiles[user_id].shadowmon = mon
            write_preferences()
            await ctx.respond(f"{user.display_name}'s shadowmon has been updated.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Give a user points.")
async def point_add(ctx, member: discord.Option(discord.Member, "The member to receive the points.", name="member"),
                    amount: discord.Option(int, "The amount of points to add.", name="amount", min_value=1)):
    create_guild_preferences(ctx.guild)
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            user_id = member.id
            if create_guild_user_profile(ctx.guild, user_id) == False:
                await ctx.respond(f"That user is not a member of this server.")
                return
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            if guild_preferences[ctx.guild.id].user_profiles[user_id].bointa is None:
                guild_preferences[ctx.guild.id].user_profiles[user_id].bointa = 0
            old_points = guild_preferences[ctx.guild.id].user_profiles[user_id].bointa
            guild_preferences[ctx.guild.id].user_profiles[user_id].bointa += amount
            update_point_log(ctx.guild.id, user, old_points, guild_preferences[ctx.guild.id].user_profiles[user_id].bointa, "ADD")
            write_preferences()
            await ctx.respond(f"{user.display_name} now has {guild_preferences[ctx.guild.id].user_profiles[user_id].bointa} {'bointa' if bointa_rng() else 'point(s)'}.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Take points from a user.")
async def point_subtract(ctx, member: discord.Option(discord.Member, "The member to lose the points.", name="member"),
                    amount: discord.Option(int, "The amount of points to remove.", name="amount", min_value=1)):
    create_guild_preferences(ctx.guild)
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            user_id = member.id
            if create_guild_user_profile(ctx.guild, user_id) == False:
                await ctx.respond(f"That user is not a member of this server.")
                return
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            if guild_preferences[ctx.guild.id].user_profiles[user_id].bointa is None:
                guild_preferences[ctx.guild.id].user_profiles[user_id].bointa = 0
            old_points = guild_preferences[ctx.guild.id].user_profiles[user_id].bointa
            if guild_preferences[ctx.guild.id].user_profiles[user_id].bointa < amount:
                await ctx.respond(f"{user.display_name} does not have enough points. To set negative points, use /profile point_override.")
                return
            guild_preferences[ctx.guild.id].user_profiles[user_id].bointa -= amount
            update_point_log(ctx.guild.id, user, old_points, guild_preferences[ctx.guild.id].user_profiles[user_id].bointa, "SUB")
            write_preferences()
            await ctx.respond(f"{user.display_name} now has {guild_preferences[ctx.guild.id].user_profiles[user_id].bointa} {'bointa' if bointa_rng() else 'point(s)'}.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Set a user's points.")
async def point_override(ctx, member: discord.Option(discord.Member, "The member that will have their points set.", name="member"),
                    amount: discord.Option(int, "The amount of points to set to.", name="amount")):
    create_guild_preferences(ctx.guild)
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            user_id = member.id
            if create_guild_user_profile(ctx.guild, user_id) == False:
                await ctx.respond(f"That user is not a member of this server.")
                return
            user = bot.get_user(user_id)
            if user is None:
                await ctx.respond(f"An unknown error occurred.")
                return
            if guild_preferences[ctx.guild.id].user_profiles[user_id].bointa is None:
                guild_preferences[ctx.guild.id].user_profiles[user_id].bointa = 0
            old_points = guild_preferences[ctx.guild.id].user_profiles[user_id].bointa
            guild_preferences[ctx.guild.id].user_profiles[user_id].bointa = amount
            update_point_log(ctx.guild.id, user, old_points, guild_preferences[ctx.guild.id].user_profiles[user_id].bointa, "SET")
            write_preferences()
            await ctx.respond(f"{user.display_name} now has {guild_preferences[ctx.guild.id].user_profiles[user_id].bointa} {'bointa' if bointa_rng() else 'point(s)'}.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

    
@profile_commands.command(description="View a user's profile.")
async def view(ctx, member: discord.Option(discord.Member, "The user whos profile you want to view.", name="member")):
    create_guild_preferences(ctx.guild)
    user_id = member.id
    if user_id is None:
        await ctx.respond(f"That user is not a member of this server.")
        return
    if create_guild_user_profile(ctx.guild, user_id) == False:
        await ctx.respond(f"That user is not a member of this server.")
        return
    embed = await guild_preferences[ctx.guild.id].user_profiles[user_id].get_embed()
    if embed == None:
        await ctx.respond(f"An unknown error occurred.")
        return
    await ctx.respond(embed=embed)

'''
@mod_commands.command(description="Configure SaurBot's self-moderation for large messages")
async def spam(ctx,
               max_lines: discord.Option(int, "Enter the (approximate) maximum amount of lines SaurBot will send before switching to a file.", name="max_lines", min_value=0),
               max_characters: discord.Option(int, "Enter the maximum amount of characters SaurBot will send before switching to a file.", name="min_lines", min_value=0, max_value=2000)):
    try:
        if ctx.author.guild_permissions.manage_guild:
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id, max_lines, max_characters)
            else:
                guild_preferences[ctx.guild.id].max_lines = max_lines
                guild_preferences[ctx.guild.id].max_chars = max_characters
            write_preferences()
            await ctx.respond(f"Updated self-moderation settings.\nMax lines: {max_lines}\nMax characters: {max_characters}\nNote: Depending on the circumstances (such as with long sentences or while viewing on mobile), it is possible for SaurBot to send messages that appear longer than max_lines.")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@mod_commands.command(description="View SaurBot's configuration settings")
async def settings(ctx):
    try:
        if ctx.author.guild_permissions.manage_guild:
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
            this_guild = guild_preferences[ctx.guild.id]
            text = f"Max lines: {this_guild.max_lines}\nMax characters: {this_guild.max_chars}"
            await ctx.respond(text)
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")
'''

@config_commands.command(description="Configure SaurBot's likelihood of responding to a given trigger.")
async def set_odds(ctx, trigger: discord.Option(str, "Enter an existing trigger", name="response_trigger"), odds: discord.Option(float, "Enter the likelihood SaurBot will respond to the trigger", name="odds", min_value=0, max_value=100)):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            trigger = trigger.lower().strip()
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
                write_preferences()
                await ctx.respond(f"Could not find trigger \"{trigger}\".")
            elif trigger not in guild_preferences[ctx.guild.id].fun:
                await ctx.respond(f"Could not find trigger \"{trigger}\".")
            else:
                guild_preferences[ctx.guild.id].fun[trigger][0] = odds
                write_preferences()
                await ctx.respond(f"Set the response odds to {odds}% for trigger \"{trigger}\".")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Configure SaurBot's likelihood of responding to all triggers.")
async def set_all_odds(ctx, odds: discord.Option(float, "Enter the likelihood SaurBot will respond to any trigger", name="odds", min_value=0, max_value=100)):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
                write_preferences()
                await ctx.respond("No triggers to update.")
            elif len(guild_preferences[ctx.guild.id].fun) == 0:
                await ctx.respond("No triggers to update.")
            else:
                counter = 0
                for trigger in guild_preferences[ctx.guild.id].fun:
                    guild_preferences[ctx.guild.id].fun[trigger][0] = odds
                    counter += 1
                write_preferences()
                await ctx.respond(f"Set the response odds to {odds}% for {counter} trigger(s).")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Lowers the likelihood to respond to all triggers that are higher than the value.")
async def cap_odds(ctx, odds: discord.Option(float, "Enter the max likelihood SaurBot will respond to any trigger", name="odds", min_value=0, max_value=100)):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
                write_preferences()
                await ctx.respond("No triggers to update.")
            elif len(guild_preferences[ctx.guild.id].fun) == 0:
                await ctx.respond("No triggers to update.")
            else:
                counter = 0
                for trigger in guild_preferences[ctx.guild.id].fun:
                    if guild_preferences[ctx.guild.id].fun[trigger][0] > odds:
                        guild_preferences[ctx.guild.id].fun[trigger][0] = odds
                        counter += 1
                write_preferences()
                await ctx.respond(f"Set the response odds to {odds}% for {counter} trigger(s).")
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Configure SaurBot's remove a trigger and its responses")
async def remove(ctx, trigger: discord.Option(str, "Enter the trigger to remove", name="response_trigger")):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            trigger = trigger.lower().strip()
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
                write_preferences()
                await ctx.respond("No triggers to remove.")
            elif trigger not in guild_preferences[ctx.guild.id].fun:
                await ctx.respond(f"Could not find trigger \"{trigger}\".")
            else:
                del guild_preferences[ctx.guild.id].fun[trigger]
                write_preferences()
                text = f"Removed the trigger \"{trigger}\" and all of its responses."
                await ctx.respond(text)
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Configure SaurBot's responses to a trigger. It can have multiple responses (add them one by one).")
async def add(ctx, trigger: discord.Option(str, "Enter the phrase that will trigger a response", name="response_trigger"), response: discord.Option(str, "Enter SaurBot's response.", name="response"), odds: discord.Option(float, "Enter the odds SaurBot will respond to the trigger. Overwrites previous odds for this trigger.", name="odds", min_value=0, max_value=100)):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id, DEFAULT_MAX_LINES, DEFAULT_MAX_CHARS, {trigger: [odds, response]})
            else:
                trigger = trigger.strip().lower()
                if len(trigger) < MIN_TRIGGER_LEN:
                    await ctx.respond(f"To prevent accidental spam, triggers must be at least {MIN_TRIGGER_LEN} characters long.")
                    return
                elif len(response) > 2000:
                    await ctx.respond("Responses cannot be more than 2000 characters.")
                    return
                elif trigger not in guild_preferences[ctx.guild.id].fun:
                    guild_preferences[ctx.guild.id].fun[trigger] = [odds, response]
                else:
                    guild_preferences[ctx.guild.id].fun[trigger][0] = odds
                    guild_preferences[ctx.guild.id].fun[trigger].append(response)
            write_preferences()
            text = f"\"{response}\" added to responses for the phrase \"{trigger}\".\nSet the response odds to {odds}% for trigger \"{trigger}\"."
            await ctx.respond(text)
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@config_commands.command(description="Lists all of SaurBot's triggers and responses")
async def list(ctx):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            if ctx.guild.id not in guild_preferences.keys():
                guild_preferences[ctx.guild.id] = Guild_Preferences(ctx.guild.id)
                write_preferences()
                await ctx.respond("No triggers found.")
            elif len(guild_preferences[ctx.guild.id].fun) == 0:
                await ctx.respond("No triggers found.")
            else:
                text = "Triggers and responses (tabs and line breaks are ommitted)\n\n"
                for trigger in guild_preferences[ctx.guild.id].fun:
                    text += trigger.replace("\t", " ").replace("\n", " ") + " (" + str(guild_preferences[ctx.guild.id].fun[trigger][0]) + "%)\n"
                    for response in guild_preferences[ctx.guild.id].fun[trigger][1:]:
                        text += "\t" + response.replace("\t", " ").replace("\n", " ") + "\n"
                await ctx.respond(file=turn_into_file(text))
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")


@config_commands.command(description="Refreshes the FnF Showdown Search database")
async def update(ctx):
    try:
        if ctx.author.guild_permissions.administrator or check_saurbot_permissions(ctx):
            if abs((datetime.datetime.now() - fnf_showdown.last_update).total_seconds()) < UPDATE_COOLDOWN:
                await ctx.respond("The database was updated recently. Please wait a bit and try again.")
                return
            await ctx.respond("Updating database. Commands won't work for a few seconds.")
            message, crash_text = fnf_showdown.update_database()
            await ctx.respond("Updated!")    
        else:
            await ctx.respond("You don't have permission to use this command.")
    except AttributeError:
        await ctx.respond("You don't have permission to use this command.")

@help_commands.command(description="Learn about SaurBot")
async def saurbot(ctx):
    print(ctx.guild.id)
    await ctx.respond(embed=ABOUT_SAURBOT_EMBED)
   
@help_commands.command(description="View basics on how to use FnF Showdown Search")
async def basics(ctx):
    message = fnf_showdown.HELP_BASIC_FILE
    if check_message_size(ctx, message):
        await ctx.respond(message)
    else:
        #await ctx.respond(embed=LARGE_MESSAGE_EMBED)
        #await ctx.send(file=turn_into_file(message))
        await ctx.respond(file=turn_into_file(message))

@help_commands.command(description="View in-depth help on /pkmn ability")
async def ability(ctx):
    message = fnf_showdown.HELP_ABILITY_FILE
    if check_message_size(ctx, message):
        await ctx.respond(message)
    else:
        #await ctx.respond(embed=LARGE_MESSAGE_EMBED)
        #await ctx.send(file=turn_into_file(message))
        await ctx.respond(file=turn_into_file(message))

@help_commands.command(description="View in-depth help on /pkmn move")
async def move(ctx):
    message = fnf_showdown.HELP_MOVE_FILE
    if check_message_size(ctx, message):
        await ctx.respond(message)
    else:
        #await ctx.respond(embed=LARGE_MESSAGE_EMBED)
        #await ctx.send(file=turn_into_file(message))
        await ctx.respond(file=turn_into_file(message))

@help_commands.command(description="View in-depth help on /pkmn pokemon")
async def pokemon(ctx):
    message = fnf_showdown.HELP_POKEMON_FILE
    if check_message_size(ctx, message):
        await ctx.respond(message)
    else:
        #await ctx.respond(embed=LARGE_MESSAGE_EMBED)
        #await ctx.send(file=turn_into_file(message))
        await ctx.respond(file=turn_into_file(message))

@pkmn_commands.command(description="DM-only. Learn how to use SaurBot commands.")
async def tutorial(ctx, tutorial: discord.Option(str, "Enter a tutorial name. If unsure, don't use this option. Type \"cancel\" to stop an ongoing tutorial.", name="tutorial_name", default="")):
    if ctx.channel.type is discord.ChannelType.private:
        arguments = tutorial.strip()
        if arguments in ["", "ability", "abilities"]:
            user_tutorial_state[ctx.author.id] = "ability"
            write_preferences()
            text = "In order to use the ability command, you need to use arguments. Arguments are instructions that tell me how to filter data. Try writing an ability command by typing \"/ability\" and adding an argument.\nIf you aren't sure what argument to write, try using the include argument by typing \"/ability include\" followed by some text. I will show you all of the abilities that have that text in their name."
            if arguments == "":
                text = "Let's start with the ability command.\n" + text
            await ctx.respond(text)
        elif arguments in ["move", "moves"]:
            user_tutorial_state[ctx.author.id] = "move"
            write_preferences()
            await ctx.respond("The move command uses arguments to filter data.\nTry writing a move command now.\nIf you aren't sure what to write, try using the type argument by typing \"/move type\" followed by any pokemon type.")
        elif arguments == "pokemon":
            user_tutorial_state[ctx.author.id] = "pokemon"
            write_preferences()
            await ctx.respond("The pokemon command uses arguments to filter data, and is my most important command.\nTry writing a pokemon command now.\nIf you aren't sure what to write, try using the bst argument. The bst argument is an argument that uses comparision operators, like, <, >=, and =.\nAn example of a pokemon command using the bst argument would be \"/pokemon bst >= 600\". This command filters by pokemon with a base stat total of at least 600.")
        elif arguments == "not operator":
            user_tutorial_state[ctx.author.id] = "not operator"
            write_preferences()
            await ctx.respond("\nSometimes, you'll want to find the reverse of what an argument would return. In these cases, you need the NOT operator.\nTo use the NOT operator, simply type \"!\".\nAn example is the command \"/move !type fire\". This command shows all moves that aren't fire-type. Try using the NOT operator in a command now.")
        elif arguments == "and operator":
            user_tutorial_state[ctx.author.id] = "and operator"
            write_preferences()
            await ctx.respond("If you've been following the previous tutorial commands, you now know how to use the ability, move, and pokemon commands with one argument.\nHowever, these commands can actually use multiple arguments. To do this, we need a way to combine multiple arguments into a single arguments.\nWe can use the AND operator, which takes the two arguments next to it and converts them into a single argument that only includes the data that satisfies both of the original arguments.\nThe AND operator is used in commands by typing an ampersand &. Try it now. If you need to see an example, try \"/move type grass & power > 120\". This command will show all grass-type moves with a base power of over 120.")
        elif arguments == "or operator":
            user_tutorial_state[ctx.author.id] = "or operator"
            write_preferences()
            await ctx.respond("To use the OR operator, you need to know how to use the AND operator. To learn about the AND operator, view the \"and operator\" tutorial.\nThe AND operator combines two arguments into a single argument that includes all data that would have been included in both of the original arguments.\nThe OR operator is similar, except the argument it creates includes all data that would have been included in EITHER of the original arguments.\nThe OR operator is used in command by typing a pipe |. An example of a command using the OR operator is \"/pokemon attack > 100 | speed > 100\". This will show all of the Pokemon that have an attack stat of over 100, a speed stat of over 100, or both.\nTry using a command with an OR operator now.")
        elif arguments == "parentheses":
            user_tutorial_state[ctx.author.id] = "parentheses"
            write_preferences()
            await ctx.respond("When evaluating commands that have multiple arguments, before giving the results, I combine all of the arguments into a single argument using the AND and OR operators.\nWhen doing this, I start from the left and work towards the right. However, sometimes you may want to change the order of operations.\nTo do this, you can place at least two arguments inside of parentheses to make them be evaluated first. You can even place parentheses inside of parentheses.\nTry writing a command with multiple arguments that uses parentheses.")
        elif arguments in ["subcommand", "subcommands"]:
            user_tutorial_state[ctx.author.id] = "subcommands"
            write_preferences()
            await ctx.respond("The subcommands feature is the most powerful tool I have, and it is exclusive to the pokemon command. Subcommands are used to filter pokemon based on what moves and abilities they have.\nSubcommands are used by surrounding any move or ability command in square brackets.\nThe command inside the brackets is run before the main command is evaluated. It is then turned into an argument that filters by all pokemon that have at least one move/ability that was returned by the subcommand.\nBecause the subcommand is turned into an argument after it's run, all of the things you can do with normal arguments (such as using the NOT/AND/OR operators and parentheses) work with subcommands.\nHere's an example command that uses a subcommand: \"/pokemon [ability name chlorophyll]\". This will show all Pokemon that can have Chlorophyll as an ability.\nTry writing a command with a subcommand now.")
        elif arguments == "cancel":
            current_tutorial = get_user_tutorial_state(ctx)
            user_tutorial_state[ctx.author.id] = None
            write_preferences()
            text = "Tutorial canceled." if current_tutorial is not None else "There's no ongoing tutorial to cancel."
            await ctx.respond(text)
        else:
            await ctx.respond("Tutorial could not be found. Is it spelled correctly?")
    else:
        await ctx.respond("This command is DM-only.")

@pkmn_commands.command(description="Search and filter abilities.")
async def ability(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command")):
    message, crash_text, response_text = fnf_showdown.create_command("ability " + arguments, get_user_tutorial_state(ctx), False)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Search and filter moves.")
async def move(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command")):
    #await ctx.respond("test")
    message, crash_text, response_text = fnf_showdown.create_command("move " + arguments, get_user_tutorial_state(ctx), False)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Search and filter Pokemon.")
async def pokemon(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command")):
    #await ctx.respond("test")
    message, crash_text, response_text = fnf_showdown.create_command("pokemon " + arguments, get_user_tutorial_state(ctx), False)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Search and filter abilities.")
async def random_ability(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command", default="all")):
    message, crash_text, response_text = fnf_showdown.create_command("ability " + arguments, get_user_tutorial_state(ctx), True)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Search and filter moves.")
async def random_move(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command", default="all")):
    message, crash_text, response_text = fnf_showdown.create_command("move " + arguments, get_user_tutorial_state(ctx), True)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Search and filter Pokemon.")
async def random_pokemon(ctx, arguments: discord.Option(str, "Enter the arguments for the command.", name="command", default="all")):
    message, crash_text, response_text = fnf_showdown.create_command("pokemon " + arguments, get_user_tutorial_state(ctx), True)
    if ctx.channel.type is discord.ChannelType.private and response_text != "":
        user_tutorial_state[ctx.author.id] = None
        write_preferences()
    else:
        response_text = ""
    await ctx.respond(response_text, file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Compare the learnsets of up to 12 Pokemon.")
async def compare(ctx, pokemon: discord.Option(str, "Enter the names of up to 12 Pokemon, separated by commas.", name="pokemon")):
    message, crash_text, response_text = fnf_showdown.create_command("compare " + pokemon)
    await ctx.respond(file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="View a Pokemon's learnset.")
async def learnset(ctx, pokemon: discord.Option(str, "Enter the name of a Pokemon.", name="pokemon")):
    message, crash_text, response_text = fnf_showdown.create_command("learnset " + pokemon)
    await ctx.respond(file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="View a Pokemon's learnset.")
async def fuse(ctx, pokemon1: discord.Option(str, "Enter the name the first Pokemon.", name="pokemon1"), pokemon2: discord.Option(str, "Enter the name the second Pokemon.", name="pokemon2"), learnset: discord.Option(bool, "Display the fused Pokemon's learnset.", name="learnset", default=False)):
    message = fnf_showdown.fuse(pokemon1, pokemon2, learnset)
    await ctx.respond(file=turn_into_file(message))

@pkmn_commands.command(description="View a Pokemon's sample sets.")
async def sets(ctx, pokemon: discord.Option(str, "Enter the name of a Pokemon.", name="pokemon")):
    message, crash_text, response_text = fnf_showdown.create_command("sets " + pokemon)
    await ctx.respond(file=turn_into_file(message))
    if crash_text is not None:
        await dm_noob(crash_text)

@pkmn_commands.command(description="Enables debug mode. Only usable by SaurBot's developer.")
async def debug(ctx):
    if ctx.author.id == DEV_ID:
        if fnf_showdown.debug_mode:
            fnf_showdown.debug_mode = False
            await ctx.respond("Debug mode is now disabled.")
        else:
            fnf_showdown.debug_mode = True
            await ctx.respond("Debug mode is now enabled.")
    else:
        await ctx.respond("You don't have permission to use this command.")

@mkw_commands.command(name="random", description="Generates a random character/vehicle combo.")
async def combo(ctx, weight: discord.Option(str, "Choose a weight class to get a character/vehicle combo of that weight class.", name="weight", default=""), vehicle: discord.Option(str, "Choose a vehicle type to get a character/vehicle combo with that vehicle type.", name="vehicle", default="")):
    if weight.strip().lower() == "light":
        weight = "Light"
    elif weight.strip().lower() == "medium":
        weight = "Medium"
    elif weight.strip().lower() == "heavy":
        weight = "Heavy"
    elif len(weight.strip()):
        await ctx.respond("Invalid weight. Valid options are \"light\", \"medium\", and \"heavy\". Or, if you want a character/vehicle combo of any weight class, do not use the weight option.")
        return
    else:
        weight = ""
    if vehicle.strip().lower() in ["bike", "bikes"]:
        vehicle = "Bike"
    elif vehicle.strip().lower() in ["cart", "carts", "kart", "karts"]:
        vehicle = "Kart"
    elif len(vehicle.strip()):
        await ctx.respond("Invalid vehicle. Valid options are \"bike\", and \"kart\". Or, if you want a character/vehicle combo of any vehicle type, do not use the vehicle option.")
        return
    else:
        vehicle = ""
    if weight == "":
        weight = random.choice(["Light", "Medium", "Heavy"])
    if vehicle == "":
        vehicle = random.choice(["Bike", "Kart"])
    character = random.choice(mkw_data.MKW_CHARACTERS[weight])
    if vehicle == "Bike":
        vehicle = random.choice(mkw_data.MKW_BIKES[weight])
    else:
        vehicle = random.choice(mkw_data.MKW_KARTS[weight])
    if random.random() < EVIL_PLAYER_EASTER_EGG:
        easter_egg = random.choice(mkw_data.MKW_EASTER_EGG)
        easter_egg = easter_egg.replace("<evilplayer>", random.choice(mkw_data.MKW_EVIL_PLAYERS))
        await ctx.respond(easter_egg)

@mkw_commands.command(description="Generates a random track.")
async def randomtrack(ctx, track_type: discord.Option(str, "Options: vanilla, wii, retro, ctgp, ctgp custom, ctgp retro, all. Vanilla is default.", name="track_type", default="vanilla")):
    track_type = track_type.lower().strip()
    if track_type not in ["vanilla", "wii", "retro", "ctgp", "ctgp custom", "ctgp retro", "all"]:
        await ctx.respond("Invalid track type. Valid options are \"vanilla\" for base game tracks, \"wii\" for tracks introduced in Mario Kart Wii, \"retro\" for returning tracks in vanilla MKW, \"ctgp\" for CTGP tracks, \"ctgp retro\" for CTGP retro tracks, \"ctgp custom\" for custom CTGP tracks, and \"all\" for all tracks.")
        return
    track_type = track_type.strip()
    if random.random() < EVIL_PLAYER_EASTER_EGG:
        easter_egg = random.choice(mkw_data.MKW_EASTER_EGG)
        easter_egg = easter_egg.replace("<evilplayer>", random.choice(mkw_data.MKW_EVIL_PLAYERS))
        await ctx.respond(easter_egg)
        return True
    if track_type == "vanilla":
        track = random.choice(mkw_data.VANILLA_WII + mkw_data.VANILLA_RETRO)
    elif track_type == "wii":
        track = random.choice(mkw_data.VANILLA_WII)
    elif track_type == "retro":
        track = random.choice(mkw_data.VANILLA_RETRO)
    elif track_type == "ctgp":
        track = random.choice(mkw_data.CTGP_CUSTOM + mkw_data.CTGP_RETRO)
    elif track_type == "ctgp custom":
        track = random.choice(mkw_data.CTGP_CUSTOM)
    elif track_type == "ctgp retro":
        track = random.choice(mkw_data.CTGP_RETRO)
    elif track_type == "all":
        track = random.choice(mkw_data.VANILLA_WII + mkw_data.VANILLA_RETRO + mkw_data.CTGP_CUSTOM + mkw_data.CTGP_RETRO)
    await ctx.respond(track)

@mkw_commands.command(description="Get the MKW friend codes of another member of the server.")
async def viewfc(ctx, user: discord.Option(str, "Type a username (eg. SaurBot#8585) to see their saved friend code. Case-sensitive!", name="username")):
    try:
        user = user.split("#")
        username = user[0].strip()
        disc = user[1].strip()
        print(username, disc)
    except IndexError:
        await ctx.respond("Invalid username. Please enter a username followed by the descriminator (eg. SaurBot#8585)")
        return
    if username == "SaurBot" and disc == "8585":
        await ctx.respond("You don't need a code to be my friend! :)")
        return
    fail_flag = 0
    user = discord.utils.get(ctx.guild.members, name=username, discriminator=disc)
    print(user)
    if user is None:
        fail_flag = 1
    else:
        user = user.id
        if user in user_mkw_fc and len(user_mkw_fc[user]):
            text = ""
            for i, code in enumerate(user_mkw_fc[user]):
                text += str(i+1) + ": " + code + "\n"
            await ctx.respond(f"{username}'s friend codes:\n{text[:-1]}")
        else:
            fail_flag = 2
    if fail_flag == 1:
        await ctx.respond("This user is not a member of this server.")
    elif fail_flag == 2:
        await ctx.respond("This user has not submitted a friend code.")

@mkw_commands.command(description="Add a MKW friend code to SaurBot's database so others can easily add you.")
async def addfc(ctx, friend_code: discord.Option(str, "Type your friend code.", name="friend_code")):
    error_flag = False
    # if the FC was formatted XXXX-XXXX-XXXX
    if "-" in friend_code:
        friend_code_list = friend_code.strip().split("-")
        for fc_part in friend_code_list:
            try:
                temp = int(fc_part)
                if len(fc_part) != 4:
                    error_flag = True
                    break
            except ValueError:
                error_flag = True
                break
    # if the FC was formatted XXXXXXXXXXXX
    else:
        try:
            temp = int(friend_code)
            # sneaky shortcut for dealing with invalid friend codes that are integers of the wrong length
            if len(friend_code) != 12:
                error_flag = True
        except ValueError:
            error_flag = True
        if not error_flag:
            friend_code = friend_code[0:4] + "-" + friend_code[4:8] + "-" + friend_code[8:12]
    if error_flag:
        await ctx.respond("Invalid friend code.")
    else:
        if ctx.author.id in user_mkw_fc:
            if len(user_mkw_fc[ctx.author.id]) > 8:
                await ctx.respond("You cannot store more than eight friend codes. Use /mkw removefc to delete one and try again.")
                return
            else:
                user_mkw_fc[ctx.author.id].append(friend_code)
        else:
            user_mkw_fc[ctx.author.id] = [friend_code]
        write_preferences()
        await ctx.respond(f"Added {friend_code}.")

@mkw_commands.command(description="Remove one of your MKW friend codes from SaurBot's database.")
async def removefc(ctx, fc_index: discord.Option(int, "Enter the number associated with the code to remove. (Viewed with /mkw viewfc) Default: 1", name="friend_code_index", default=1, max_value=8, min_value=1)):
    if ctx.author.id in user_mkw_fc:
        if len(user_mkw_fc[ctx.author.id]) < fc_index:
            await ctx.respond(f"You do not have {fc_index} friend codes stored.")
            return
        else:
            del user_mkw_fc[ctx.author.id][fc_index-1]
            write_preferences()
            await ctx.respond("Friend code removed sucessfully.")
    else:
        await ctx.respond("There isn't friend code stored for this user to remove.")

@bot.event
async def on_message(message): 
    if message.author == bot.user:
        return
    try:
        if message.guild.id in guild_preferences:
            for trigger in guild_preferences[message.guild.id].fun:
                if trigger in message.content.lower():
                    roll = random.random() * 100
                    if guild_preferences[message.guild.id].fun[trigger][0] > roll:
                        response = random.choice(guild_preferences[message.guild.id].fun[trigger][1:])
                        await message.reply(response)
                        fnf_showdown.timelog("Easter egg!")
    except AttributeError:
        return

schedule.every().day.at("00:00").do(backup)
def schedule_backup_save():
    print("Schedule started")
    while True:
        schedule.run_pending()
        time.sleep(60)

load_preferences()

thread = threading.Thread(target=schedule_backup_save)
thread.start()
bot.run(TOKEN)


# todo list:
# move certain classes and functions to a utilities file (the timelog function does not need to be in fnf_showdown.py for example)
# merge mkw friend code functionalities with the profile feature
# clean up the code and add more comments