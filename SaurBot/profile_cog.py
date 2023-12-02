import fnf_data
import discord
from discord.ext import commands
from discord import app_commands
import enum

class ProfileType(enum.Enum):
    pokemon = 0
    mario_kart = 1

@app_commands.guild_only()
class ProfileCog(commands.GroupCog, group_name="profile"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    points_group = app_commands.Group(name="points", description="Manage the number of points each user has. Requires permission.")
    shadowmon_group = app_commands.Group(name="shadowmon", description="Manage each user's shadowmon. Requires permission.")
    mkw_group = app_commands.Group(name="mkw", description="Manage your Mario Kart Wii friend codes.")
    @app_commands.command(name="set")
    async def command_set(self, interaction: discord.Interaction,
                          favorite_pokemon: str="",
                          favorite_buff: str="",
                          favorite_custom_pokemon: str="",
                          favorite_story_character: str="",
                          mkw_character: str="",
                          mkw_vehicle: str="",
                          mkw_track: str=""):
        """Set up and manage your profile.

        Parameters
        -----------
        favorite_pokemon: str
            Optional. Your favorite Pokemon. Type "none" to reset.
        favorite_buff: str
            Optional. Your favorite balance change made in FnF. Type "none" to reset.
        favorite_custom_pokemon: str
            Optional. Your favorite Pokemon introduced in FnF. Type "none" to reset.
        favorite_story_character: str
            Optional. Your favorite character from the FnF story. Type "none" to reset.
        mkw_character: str
            Optional. Your favorite character to play as in Mario Kart. Type "none" to reset.
        mkw_vehicle: str
            Optional. Your favorite vehicle to use in Mario Kart. Type "none" to reset.
        mkw_track: str
            Optional. Your favorite track from Mario Kart. Type "none" to reset.
        """
        self.bot.create_guild_user_profile(interaction.guild, interaction.user.id)
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if favorite_pokemon != "":
            if len(favorite_pokemon) > 1024:
                favorite_pokemon = favorite_pokemon[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mon = None if favorite_pokemon == "none" else favorite_pokemon
        if favorite_buff != "":
            if len(favorite_buff) > 1024:
                favorite_buff = favorite_buff[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_buff = None if favorite_buff == "none" else favorite_buff
        if favorite_custom_pokemon != "":
            if len(favorite_custom_pokemon) > 1024:
                favorite_custom_pokemon = favorite_custom_pokemon[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_custom_mon = None if favorite_custom_pokemon == "none" else favorite_custom_pokemon
        if favorite_story_character != "":
            if len(favorite_story_character) > 1024:
                favorite_story_character = favorite_story_character[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_story_char = None if favorite_story_character == "none" else favorite_story_character
        if mkw_character != "":
            if len(mkw_character) > 1024:
                mkw_character = mkw_character[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_char = None if mkw_character == "none" else mkw_character
        if mkw_vehicle != "":
            if len(mkw_vehicle) > 1024:
                mkw_vehicle = mkw_vehicle[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_vehicle = None if mkw_vehicle == "none" else mkw_vehicle
        if mkw_track != "":
            if len(mkw_track) > 1024:
                mkw_track = mkw_track[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_course = None if mkw_track == "none" else mkw_track
        self.bot.write_preferences()
        await interaction.response.send_message(f"Your profile has been updated.", ephemeral=True)

    @app_commands.command(name="manage")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_manage(self, interaction: discord.Interaction,
                             member: discord.Member,
                             favorite_pokemon: str="",
                             favorite_buff: str="",
                             favorite_custom_pokemon: str="",
                             favorite_story_character: str="",
                             badge_amount: int=-1,
                             mkw_character: str="",
                             mkw_vehicle: str="",
                             mkw_track: str=""):
        """Manage a member's profile. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member whose profile you want to manage.
        favorite_pokemon: str
            Optional. The member's favorite Pokemon. Type "none" to reset.
        favorite_buff: str
            Optional. The member's favorite balance change made in FnF. Type "none" to reset.
        favorite_custom_pokemon: str
            Optional. The member's favorite Pokemon introduced in FnF. Type "none" to reset.
        favorite_story_character: str
            Optional. The member's favorite character from the FnF story. Type "none" to reset.
        badge_amount: int
            Optional. The amount of gym badges earned by the member.
        mkw_character: str
            Optional. The member's favorite character to play as in Mario Kart. Type "none" to reset.
        mkw_vehicle: str
            Optional. The member's favorite vehicle to use in Mario Kart. Type "none" to reset.
        mkw_track: str
            Optional. The member's favorite track from Mario Kart. Type "none" to reset.
        """
        self.bot.create_guild_user_profile(interaction.guild, member.id)
        guild_id = interaction.guild_id
        user_id = member.id
        if badge_amount < -1:
            await interaction.response.send_message(f"badge_amount cannot be less than 0.", ephemeral=True)
            return
        elif badge_amount != 1:
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].badges_obtained = badge_amount
        if favorite_pokemon != "":
            if len(favorite_pokemon) > 1024:
                favorite_pokemon = favorite_pokemon[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mon = None if favorite_pokemon == "none" else favorite_pokemon
        if favorite_buff != "":
            if len(favorite_buff) > 1024:
                favorite_buff = favorite_buff[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_buff = None if favorite_buff == "none" else favorite_buff
        if favorite_custom_pokemon != "":
            if len(favorite_custom_pokemon) > 1024:
                favorite_custom_pokemon = favorite_custom_pokemon[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_custom_mon = None if favorite_custom_pokemon == "none" else favorite_custom_pokemon
        if favorite_story_character != "":
            if len(favorite_story_character) > 1024:
                favorite_story_character = favorite_story_character[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_story_char = None if favorite_story_character == "none" else favorite_story_character
        if mkw_character != "":
            if len(mkw_character) > 1024:
                mkw_character = mkw_character[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_char = None if mkw_character == "none" else mkw_character
        if mkw_vehicle != "":
            if len(mkw_vehicle) > 1024:
                mkw_vehicle = mkw_vehicle[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_mkw_vehicle = None if mkw_vehicle == "none" else mkw_vehicle
        if mkw_track != "":
            if len(mkw_track) > 1024:
                mkw_track = mkw_track[:1024]
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].favorite_course = None if mkw_track == "none" else mkw_track
        self.bot.write_preferences()
        await interaction.response.send_message(f"{member.name}'s profile has been updated.", ephemeral=True)

    @command_manage.error
    async def command_manage_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @app_commands.command(name="view")
    async def command_view(self, interaction: discord.Interaction,
                           member: discord.Member,
                           profile_type: ProfileType):
        """View a member's profile.

        Parameters
        -----------
        member: discord.Member
            The member whose profile you want to view.
        profile_type: ProfileType
            The profile data you want to see. Options: pokemon, mario_kart
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if profile_type.value == 0:
            profile_type = "pkmn"
        elif profile_type.value == 1:
            profile_type = "mkw"
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        if profile_type not in ["pkmn", "mkw"]:
            await interaction.response.send_message(f"profile_type must be pokemon or mario_kart.", ephemeral=True)
            return
        embed = await fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].get_embed(profile_type)
        if embed == None:
            fnf_data.timelog("An unknown error occurred. (caused by /profile view)")
            await interaction.response.send_message(f"An unknown error occurred.", ephemeral=True)
            return
        await interaction.response.send_message(embed=embed)
    
    @points_group.command(name="add")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_point_add(self, interaction: discord.Interaction,
                                member: discord.Member,
                                amount: int):
        """Give a member points. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to give points to.
        amount: int
            The number of points to give. Must be a whole number greater than zero.
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        user = self.bot.get_user(user_id)
        if amount < 1:
            await interaction.response.send_message(f"Please provide a whole number greater than zero.", ephemeral=True)
            return
        if fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa is None:
            fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = 0
        old_points = fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa
        new_points = old_points + amount
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = new_points
        self.bot.update_point_log(interaction.guild_id, user, old_points, new_points, "ADD")
        self.bot.write_preferences()
        bointa_text = "bointa" if self.bot.bointa_rng() else "point(s)"
        await interaction.response.send_message(f"{user.display_name} now has {new_points} {bointa_text}.")

    @command_point_add.error
    async def command_point_add_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @points_group.command(name="subtract")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_point_subtract(self, interaction: discord.Interaction,
                                member: discord.Member,
                                amount: int):
        """Take points from a member. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to take points from.
        amount: int
            The number of points to take. Must be a whole number greater than zero.
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        user = self.bot.get_user(user_id)
        if fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa is None:
            fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = 0
        old_points = fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa
        if old_points < amount:
            await interaction.response.send_message(f"{user.display_name} does not have enough points. To set negative points, use /profile points override.", ephemeral=True)
            return
        new_points = old_points - amount
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = new_points
        self.bot.update_point_log(interaction.guild_id, user, old_points, new_points, "SUB")
        self.bot.write_preferences()
        bointa_text = "bointa" if self.bot.bointa_rng() else "point(s)"
        await interaction.response.send_message(f"{user.name} now has {new_points} {bointa_text}.")

    @command_point_subtract.error
    async def command_point_subtract_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @points_group.command(name="override")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_point_override(self, interaction: discord.Interaction,
                                member: discord.Member,
                                amount: int):
        """Take points from a member. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member whose points you want to set.
        amount: int
            The amount to set the member's points to.
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        user = self.bot.get_user(user_id)
        if fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa is None:
            fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = 0
        old_points = fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa
        new_points = amount
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].bointa = new_points
        self.bot.update_point_log(interaction.guild_id, user, old_points, new_points, "SET")
        self.bot.write_preferences()
        bointa_text = "bointa" if self.bot.bointa_rng() else "point(s)"
        await interaction.response.send_message(f"{user.name} now has {new_points} {bointa_text}.")

    @command_point_override.error
    async def command_point_override_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @shadowmon_group.command(name="assign")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_assign_shadowmon(self, interaction: discord.Interaction,
                                       member: discord.Member,
                                       species: str,
                                       nickname: str,
                                       purified: bool):
        """Assign a shadowmon to a member without one, or update an existing shadowmon. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to recieve a shadowmon.
        species: str
            The species of the shadowmon. (eg. Bulbasaur)
        nickname: str
            The nickname of the shadowmon.
        purified: bool
            Whether or not the shadowmon has been purified.
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        mon = {"species": species, "nickname": nickname, "purified": purified}
        if purified:
            mon["command_name"] = f"{species}-{nickname}"
        else:
            mon["command_name"] = f"{species}-Shadow"
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].shadowmon = mon
        self.bot.write_preferences()
        await interaction.response.send_message(f"{member.name}'s shadowmon has been updated.")

    @command_assign_shadowmon.error
    async def command_assign_shadowmon_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @shadowmon_group.command(name="unassign")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_unassign_shadowmon(self, interaction: discord.Interaction,
                                       member: discord.Member):
        """Removes a member's shadowmon. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to have their shadowmon removed.
        """
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.\nSince they aren't part of the server, their profile, and by extension, their shadowmon aren't visible anyway.", ephemeral=True)
            return
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].shadowmon = None
        self.bot.write_preferences()
        await interaction.response.send_message(f"{member.name}'s shadowmon has been removed.")

    @command_unassign_shadowmon.error
    async def command_assign_unshadowmon_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @mkw_group.command(name="add_fc")
    async def command_add_mkw_fc(self, interaction: discord.Interaction,
                                 friend_code: str):
        """Add a Mario Kart Wii friend code to your profile.

        Parameters
        -----------
        friend_code: str
            Your friend code.
        """
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
                # deals with invalid friend codes that are integers of the wrong length
                if len(friend_code) != 12:
                    error_flag = True
            except ValueError:
                error_flag = True
            if not error_flag:
                friend_code = friend_code[0:4] + "-" + friend_code[4:8] + "-" + friend_code[8:12]
        if error_flag:
            await interaction.response.send_message("Invalid friend code. Please provide a code formatted like XXXXXXXXXXXX or XXXX-XXXX-XXXX.")
        else:
            if interaction.user.id in fnf_data.user_mkw_fc:
                if len(fnf_data.user_mkw_fc[interaction.user.id]) >= 4:
                    await interaction.response.send_message("You cannot store more than four friend codes. Use /profile mkw remove_fc to delete one and try again.", ephemeral=True)
                    return
                else:
                    fnf_data.user_mkw_fc[interaction.user.id].append(friend_code)
            else:
                fnf_data.user_mkw_fc[interaction.user.id] = [friend_code]
            self.bot.write_preferences()
            await interaction.response.send_message(f"Added {friend_code} to your profile.", ephemeral=True)

    @mkw_group.command(name="remove_fc")
    async def command_add_mkw_fc(self, interaction: discord.Interaction,
                                 friend_code_index: int):
        """Remove a Mario Kart Wii friend code from your profile.

        Parameters
        -----------
        friend_code_index: int
            The index of the friend code you want to remove. Viewable in your profile by using /profile view.
        """
        if interaction.user.id not in fnf_data.user_mkw_fc:
            await interaction.response.send_message("You don't have any stored friend codes to remove.", ephemeral=True)
            return
        if friend_code_index < 1 or friend_code_index > 4:
            await interaction.response.send_message("Please input a whole number from one to four.", ephemeral=True)
            return
        if len(fnf_data.user_mkw_fc[interaction.user.id]) < friend_code_index:
            await interaction.response.send_message("You don't that many friend codes stored.", ephemeral=True)
            return
        del fnf_data.user_mkw_fc[interaction.user.id][friend_code_index-1]
        await interaction.response.send_message("Friend code removed successfully.", ephemeral=True)
            
async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))