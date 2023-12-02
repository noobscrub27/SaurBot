import fnf_data
import mkw_data
import discord
from discord.ext import commands
from discord import app_commands
import enum
import random

EVIL_PLAYER_EASTER_EGG = 0.01

class TrackType(enum.Enum):
    all_tracks = 0
    vanilla = 1
    vanilla_wii = 2
    vanilla_retro = 3
    ctgp = 4
    ctgp_custom = 5
    ctgp_retro = 6

class WeightClass(enum.Enum):
    no_preference = 0
    light = 1
    medium = 2
    heavy = 3

class VehicleType(enum.Enum):
    no_preference = 0
    kart = 1
    bike = 2

class MarioKartWiiCog(commands.GroupCog, group_name="mkw"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="random_character")
    async def command_random_character(self, interaction: discord.Interaction,
                                           weight: WeightClass=WeightClass.no_preference,
                                           vehicle: VehicleType=VehicleType.no_preference):
        """Get a random Mario Kart Wii character/vehicle combo.

        Parameters
        -----------
        weight: WeightClass
            Optional. Use this to guarantee you'll get a character of a certain weight class.
        vehicle: VehicleType
            Optional. Use this to guarnatee you'll get a vehicle of a certain type.
        """
        weight = weight.value
        vehicle = vehicle.value
        if weight == 0:
            weight = random.choice(["Light", "Medium", "Heavy"])
            character = random.choice(mkw_data.MKW_CHARACTERS[weight])
        elif weight == 1:
            weight = "Light"
            character = random.choice(mkw_data.MKW_CHARACTERS[weight])
        elif weight == 2:
            weight = "Medium"
            character = random.choice(mkw_data.MKW_CHARACTERS[weight])
        elif weight == 3:
            weight = "Heavy"
            character = random.choice(mkw_data.MKW_CHARACTERS[weight])
        if vehicle == 0:
            vehicle = random.choice(["Bike", "Kart"])
        elif vehicle == 1:
            vehicle = "Kart"
        elif vehicle == 2:
            vehicle = "Bike"
        if vehicle == "Kart":
            vehicle = random.choice(mkw_data.MKW_KARTS[weight])
        else:
            vehicle = random.choice(mkw_data.MKW_BIKES[weight])
        if random.random() < EVIL_PLAYER_EASTER_EGG:
            easter_egg = random.choice(mkw_data.MKW_EASTER_EGG)
            easter_egg = easter_egg.replace("<evilplayer>", random.choice(mkw_data.MKW_EVIL_PLAYERS))
            await interaction.response.send_message(easter_egg)
        else:
            await interaction.response.send_message(f"{character} on the {vehicle}.")

    @app_commands.command(name="random_track")
    async def command_random_track(self, interaction: discord.Interaction,
                                       track_type: TrackType=TrackType.vanilla):
        """Get a random Mario Kart Wii track.

        Parameters
        -----------
        track_type: TrackType
            Optional. Use this to guarantee you'll get a certain type of track. Defaults to Vanilla.
        """
        if random.random() < EVIL_PLAYER_EASTER_EGG:
            easter_egg = random.choice(mkw_data.MKW_EASTER_EGG)
            easter_egg = easter_egg.replace("<evilplayer>", random.choice(mkw_data.MKW_EVIL_PLAYERS))
            await interaction.response.send_message(easter_egg)
        else:
            if track_type.value == 0:
                track = random.choice(mkw_data.VANILLA_WII + mkw_data.VANILLA_RETRO + mkw_data.CTGP_CUSTOM + mkw_data.CTGP_RETRO)
            elif track_type.value == 1:
                track = random.choice(mkw_data.VANILLA_WII + mkw_data.VANILLA_RETRO)
            elif track_type.value == 2:
                track = random.choice(mkw_data.VANILLA_WII)
            elif track_type.value == 3:
                track = random.choice(mkw_data.VANILLA_RETRO)
            elif track_type.value == 4:
                track = random.choice(mkw_data.CTGP_CUSTOM + mkw_data.CTGP_RETRO)
            elif track_type.value == 5:
                track = random.choice(mkw_data.CTGP_CUSTOM)
            elif track_type.value == 6:
                track = random.choice(mkw_data.CTGP_RETRO)
            await interaction.response.send_message(f"{track}.")
 
async def setup(bot: commands.Bot):
    await bot.add_cog(MarioKartWiiCog(bot))