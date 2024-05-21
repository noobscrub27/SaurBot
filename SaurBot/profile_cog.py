import fnf_data
import discord
from discord.ext import commands
from discord import app_commands
import datetime
import saurbot_functions
import random

MAX_LINKED_SHOWDOWN_ACCOUNTS = 10

async def create_profile_view(interaction: discord.Interaction, bot, user_profile, copy=False):
    profile_view = ProfileView(bot, user_profile, copy)
    await profile_view.send(interaction)

PROFILE_PAGES = ["Overview", "Pokemon", "Battle Data", "Gym Challenge", "Mario Kart Wii"]

class ProfileView(discord.ui.View):
    sep: int = 10
    def __init__(self, bot, user_profile, copy):
        super().__init__()
        self.bot = bot
        self.bointa = True if random.random() > 0.99 else False
        self.user_profile = user_profile
        self.embed = None
        self.current_page = PROFILE_PAGES[0]
        self.timeout = 900
        self.message_text = ""
        self.message = None
        self.command_user = None
        self.copy = copy
        self.primary_select_menu = None

    async def create_overview_embed(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        embed = discord.Embed(color=(profile_user.accent_color if profile_user.accent_color is not None else discord.Color.default()),title=self.current_page)
        embed.set_thumbnail(url=profile_user.display_avatar.url)
        embed.add_field(name=("Bointa" if self.bointa else "Points"), value=str(self.user_profile.bointa), inline=False)
        embed.add_field(name="Treasures", value=self.user_profile.get_treasure_text(), inline=False)
        self.embed = embed

    async def create_pokemon_embed(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        embed = discord.Embed(color=(profile_user.accent_color if profile_user.accent_color is not None else discord.Color.default()),title=self.current_page)
        if self.user_profile.trainer_sprite_url is not None:
            embed.set_thumbnail(url=self.user_profile.trainer_sprite_url)
        else:
            embed.set_thumbnail(url=profile_user.display_avatar.url)
        embed.add_field(name="Favorite Pokemon", value=str(self.user_profile.favorite_mon), inline=False)
        embed.add_field(name="Favorite Buff/Rework", value=str(self.user_profile.favorite_buff), inline=False)
        embed.add_field(name="Favorite Custom Pokemon", value=str(self.user_profile.favorite_custom_mon), inline=False)
        embed.add_field(name="Favorite Story Character", value=str(self.user_profile.favorite_story_char), inline=False)
        if self.user_profile.shadowmon is not None:
            embed.add_field(name="Shadowmon", value=f'{self.user_profile.shadowmon["nickname"]} ({"Purified" if self.user_profile.shadowmon["purified"] else "Shadow"} {self.user_profile.shadowmon["species"]})\n*/pokedex pokemon name {self.user_profile.shadowmon["command_name"]}*')
        else:
            embed.add_field(name="Shadowmon", value="None")
        if len(self.user_profile.showdown_accounts):
            showdown_accounts_text = ""
            for account in self.user_profile.showdown_accounts:
                showdown_accounts_text += account + ", "
            showdown_accounts_text = showdown_accounts_text.removesuffix(", ")
            embed.add_field(name="Showdown Accounts", value=showdown_accounts_text)
        else:
            embed.add_field(name="Showdown Accounts", value="None linked")
        self.embed = embed

    async def create_battle_data_embed(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        embed = discord.Embed(color=(profile_user.accent_color if profile_user.accent_color is not None else discord.Color.default()),title=self.current_page)
        if self.user_profile.trainer_sprite_url is not None:
            embed.set_thumbnail(url=self.user_profile.trainer_sprite_url)
        else:
            embed.set_thumbnail(url=profile_user.display_avatar.url)
        if self.user_profile.public_trainer_data == False:
            embed.add_field(name="Trainer data is not public", value="If this is your profile and you would like to share trainer data, link your Showdown account with */profile showdown link*, then use */profile share_trainer_data*.", inline=False)
            self.embed = embed
        else:
            embed.add_field(name="Not ready yet!", value="This section of the profile is under construction.", inline=False)
        self.embed = embed

    async def create_gym_challenge_embed(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        embed = discord.Embed(color=(profile_user.accent_color if profile_user.accent_color is not None else discord.Color.default()),title=self.current_page)
        if self.user_profile.trainer_sprite_url is not None:
            embed.set_thumbnail(url=self.user_profile.trainer_sprite_url)
        else:
            embed.set_thumbnail(url=profile_user.display_avatar.url)
        embed.add_field(name="Badges obtained", value=str(self.user_profile.badges_obtained), inline=False)
        embed.add_field(name="More coming soon!", value="This section of the profile is under construction.", inline=False)
        self.embed = embed

    async def create_mario_kart_wii_embed(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        embed = discord.Embed(color=(profile_user.accent_color if profile_user.accent_color is not None else discord.Color.default()),title=self.current_page)
        embed.set_thumbnail(url=profile_user.display_avatar.url)
        if self.user_profile.favorite_mkw_char is not None:
            embed.add_field(name="Favorite Character", value=str(self.user_profile.favorite_mkw_char), inline=False)
        if self.user_profile.favorite_mkw_vehicle is not None:
            embed.add_field(name="Favorite Vehicle", value=str(self.user_profile.favorite_mkw_vehicle), inline=False)
        if self.user_profile.favorite_course is not None:
            embed.add_field(name="Favorite Course", value=str(self.user_profile.favorite_course), inline=False)
        # friend codes being stored seperately from the rest of the profile is a holdover from when saurbot was first made and the profile system was less organized
        # it was done this way so that mkw friend codes are shared across multiple servers
        # however, I've since moved away from this approach and make every profile different from server to server when I can
        mkw_profile = True if self.user_profile.id in fnf_data.user_mkw_fc and len(fnf_data.user_mkw_fc[self.user_profile.id]) else False
        if mkw_profile:
            text = ""
            for i, code in enumerate(fnf_data.user_mkw_fc[self.user_profile.id]):
                text += f"{i+1}: {code}\n"
            embed.add_field(name="Friend Codes", value=text, inline=False)
        else:
            embed.add_field(name="Friend Codes", value="None", inline=False)
        self.embed = embed

    async def send(self, interaction):
        self.command_user = interaction.user
        self.create_primary_select_menu()
        self.current_page = PROFILE_PAGES[0]
        await self.create_overview_embed()
        self.message = await interaction.followup.send(view=self, ephemeral=self.copy)
        await self.update_message()
        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] in ["ProfileView:happy_ivy_button"]:
            if self.copy:
                await interaction.response.send_message("Ivysaur says hi!", ephemeral=True)
                return False
        elif interaction.user != self.command_user:
            await interaction.response.send_message("You can't interact with someone else's command. Press the Ivysaur button to create a personal copy of this command.", ephemeral=True)
            return False
        return True

    async def update_message(self):
        profile_user = await self.bot.fetch_user(self.user_profile.id)
        await self.message.edit(content=f"**{profile_user.display_name}'s Profile**", embed=self.embed, attachments=[], view=self)

    def create_primary_select_menu(self):
        if self.primary_select_menu is not None:
            return
        self.primary_select_menu = ProfilePrimarySelectMenu(PROFILE_PAGES, self.current_page)
        self.add_item(self.primary_select_menu)

    def destroy_primary_select_menu(self):
        if self.primary_select_menu is not None:
            self.remove_item(self.primary_select_menu)
            self.primary_select_menu = None

    # use related menu code from story cog for the secondary menu when its implemented

    @discord.ui.button(label="", style=discord.ButtonStyle.green, emoji="<:happyivy:666673253414207498>", custom_id="ProfileView:happy_ivy_button")
    async def happy_ivy_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await create_profile_view(interaction, self.bot, self.user_profile, True)

    async def respond_to_primary_select_menu(self, interaction: discord.Interaction, values):
        await interaction.response.defer()
        new_page = values[0]
        self.current_page = new_page
        if self.current_page == "Overview":
            await self.create_overview_embed()
        elif self.current_page == "Pokemon":
            await self.create_pokemon_embed()
        elif self.current_page == "Battle Data":
            await self.create_battle_data_embed()
        elif self.current_page == "Gym Challenge":
            await self.create_gym_challenge_embed()
        elif self.current_page == "Mario Kart Wii":
            await self.create_mario_kart_wii_embed()
        self.destroy_primary_select_menu()
        self.create_primary_select_menu()
        await self.update_message()
   

class ProfilePrimarySelectMenu(discord.ui.Select):
    def __init__(self, pages, current_page_name):
        super().__init__(placeholder=current_page_name, custom_id="ProfileView:ProfilePrimarySelectMenu")
        self.timeout = None
        options = []
        for page in pages:
            if page == current_page_name:
                continue
            options.append(discord.SelectOption(label=page, value=page))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_primary_select_menu(interaction, self.values)

'''
class ProfileSecondarySelectMenu(discord.ui.Select):
    def __init__(self, related, page_number, show_last_page, show_next_page):
        super().__init__(placeholder="Browse related entries", custom_id="ProfileView:ProfilePSecondarySelectMenu")
        options = [discord.SelectOption(label=item, value=item) for item in related]
        if show_last_page:
            options = [discord.SelectOption(label=f"(To page {page_number-1})", value="<lastpage>")] + options
        if show_next_page:
            options += [discord.SelectOption(label=f"(To page {page_number+1})", value="<nextpage>")]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_related_select_menu(interaction, self.values)
'''

async def unlink_autocomplete(interaction: discord.Interaction, current):
    guild_id = interaction.guild_id
    user_id = interaction.user.id
    return [app_commands.Choice(name=item, value=item)
            for item in fnf_data.guild_preferences[guild_id].user_profiles[user_id].showdown_accounts
            if saurbot_functions.only_a_to_z(current) in saurbot_functions.only_a_to_z(item)]

@app_commands.guild_only()
class ProfileCog(commands.GroupCog, group_name="profile"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    points_group = app_commands.Group(name="points", description="Manage the number of points each user has. Requires permission.")
    shadowmon_group = app_commands.Group(name="shadowmon", description="Manage each user's shadowmon. Requires permission.")
    mkw_group = app_commands.Group(name="mkw", description="Manage your Mario Kart Wii friend codes.")
    showdown_group = app_commands.Group(name="showdown", description="Link or unlink a Pokemon Showdown account to your Saurbot profile.")
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
                             trainer_sprite_url: str="",
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
        trainer_sprite_url: str
            Optional. The url for the member's custom trainer sprite. Type "none" to reset.
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
        if trainer_sprite_url != "":
            fnf_data.guild_preferences[guild_id].user_profiles[user_id].trainer_sprite_url = None if trainer_sprite_url == "none" else trainer_sprite_url
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
                           member: discord.Member):
        """View a member's profile.

        Parameters
        -----------
        member: discord.Member
            The member whose profile you want to view.
        """
        await interaction.response.defer(thinking=True)
        self.bot.create_guild_preferences(interaction.guild)
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.followup.send(content=f"That user is not a member of this server.", ephemeral=True)
            return
        await create_profile_view(interaction, self.bot, fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id])

    @app_commands.command(name="share_trainer_data", description="If you have a Showdown account linked, your battle data will be made visible to others.")
    async def command_share_trainer_data(self, interaction: discord.Interaction):
        self.bot.create_guild_user_profile(interaction.guild, interaction.user.id)
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if fnf_data.guild_preferences[guild_id].user_profiles[user_id].public_trainer_data:
            await interaction.response.send_message(f"Your battle data is already visible to others.", ephemeral=True)
            return
        fnf_data.guild_preferences[guild_id].user_profiles[user_id].public_trainer_data = True
        self.bot.write_preferences()
        await interaction.response.send_message(f"Your battle data is now visible to others. Use */profile hide_trainer_data* if you would like to undo this. Note that this setting does nothing if you don't have a Showdown account linked. To link a Showdown account, use */profile showdown link*.", ephemeral=True)
    
    @app_commands.command(name="hide_trainer_data", description="Your battle data will be hidden from others.")
    async def command_hide_trainer_data(self, interaction: discord.Interaction):
        self.bot.create_guild_user_profile(interaction.guild, interaction.user.id)
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if fnf_data.guild_preferences[guild_id].user_profiles[user_id].public_trainer_data == False:
            await interaction.response.send_message(f"Your battle data is already hidden from others.", ephemeral=True)
            return
        fnf_data.guild_preferences[guild_id].user_profiles[user_id].public_trainer_data = False
        self.bot.write_preferences()
        await interaction.response.send_message(f"Your battle data is now hidden from others.", ephemeral=True)

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

    @showdown_group.command(name="link")
    async def command_link(self, interaction: discord.Interaction,
                          account: str):
        """Link a Pokemon Showdown account to your Saurbot profile.

        Parameters
        -----------
        account: str
            The Showdown account to link. Ensure that you own this account and it is password-protected!
        """
        await interaction.response.defer(thinking=True,ephemeral=True)
        self.bot.create_guild_user_profile(interaction.guild, interaction.user.id)
        now = datetime.datetime.now().timestamp()
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        not_a_number = False
        try:
            int(account)
        except ValueError:
            not_a_number = True
        if not_a_number == False or len(account) > 18:
            await interaction.followup.send(content=f"This is not a valid Showdown account name.", ephemeral=True)
            return
        if saurbot_functions.only_a_to_z(account) in [item.lower() for item in fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].showdown_accounts]:
            await interaction.followup.send(content=f"You've already linked this account.", ephemeral=True)
            return
        if fnf_data.guild_preferences[interaction.guild_id].get_user_from_showdown(account) is not None:
            await interaction.followup.send(content=f"Someone else has already linked this account.", ephemeral=True)
            return
        pending_len = len(list(fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].pending_showdown_account_links))
        account_len = len(list(fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].showdown_accounts))
        if pending_len + account_len + 1 > MAX_LINKED_SHOWDOWN_ACCOUNTS:
            await interaction.followup.send(content=f"You cannot have more than {MAX_LINKED_SHOWDOWN_ACCOUNTS} Showdown accounts linked. Please unlink an account before linking another.",ephemeral=True)
            return
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].pending_showdown_account_links[saurbot_functions.only_a_to_z(account)] = now
        self.bot.write_preferences()
        await interaction.followup.send(content=f"Step one complete. Please log into Pokemon Showdown as {account} and DM Saurbot the word \"link\" within five minutes to continue.", ephemeral=True)

    @showdown_group.command(name="unlink")
    @app_commands.autocomplete(account=unlink_autocomplete)
    async def command_unlink(self, interaction: discord.Interaction,
                          account: str):
        """Unlink a linked Pokemon Showdown account from your Saurbot profile.

        Parameters
        -----------
        account: str
            The Showdown account to unlink. It will be removed from your Saurbot profile.
        """
        self.bot.create_guild_user_profile(interaction.guild, interaction.user.id)
        now = datetime.datetime.now().timestamp()
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if account not in fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].showdown_accounts:
            await interaction.response.send_message(f"You don't have a linked Showdown account named {account}.", ephemeral=True)
            return
        fnf_data.guild_preferences[interaction.guild_id].user_profiles[user_id].showdown_accounts.remove(account)
        self.bot.write_preferences()
        await interaction.response.send_message(f"Successfully unlinked {account} from your profile.", ephemeral=True)

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