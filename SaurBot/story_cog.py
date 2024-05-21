import discord
from discord.ext import commands
from discord import app_commands
import json
import saurbot_functions
import math

with open("story_profiles.json") as f:
    story_profiles = json.load(f)
invalid_story_profiles = []

class InvalidStoryProfile(Exception):
    def __init__(self, profile, description, page_name=None):
        self.profile = profile
        self.page_name = page_name
        self.description = description

    def __str__(self):
        text = f"InvalidStoryProfile for {self.profile}: {self.description}"
        if self.page_name is not None:
            text += f" (Found in {self.page_name})"
        return text

async def story_autocomplete(interaction: discord.Interaction, current):
    return [app_commands.Choice(name=item, value=item)
            for item in story_profiles.keys() if item not in invalid_story_profiles
            and saurbot_functions.only_a_to_z(current) in saurbot_functions.only_a_to_z(item)]

async def create_story_view(interaction: discord.Interaction, profile_key, copy=False):
    story_view = StoryView(profile_key, None, copy)
    await story_view.send(interaction)

class StoryView(discord.ui.View):
    sep: int = 10
    def __init__(self, profile_key, old_view=None, copy=False):
        super().__init__()
        self.profile_name = profile_key
        self.profile_dict = story_profiles[profile_key]
        self.errors = []
        self.pages = [page_name for page_name in self.profile_dict]
        if len(self.pages) > 25:
            self.errors.append(InvalidStoryProfile(self.profile_name, "Each entry can have no more than 25 pages."))
        elif len(self.pages) == 0:
            self.errors.append(InvalidStoryProfile(self.profile_name, "Each entry must have at least 1 page."))
        self.current_page_index = 0
        self.related_pagination_page = 1
        try:
            self.current_page = self.pages[self.current_page_index]
            self.related = [item for item in self.get_related(self.current_page) if item not in invalid_story_profiles]
            self.related_pagination_page_amount = max(1, math.ceil(len(self.related)/self.sep))
        except (IndexError, AttributeError):
            self.current_page = None
            self.related = []
            self.related_pagination_page_amount = 1
        self.timeout = None
        self.page_menu = None
        self.related_menu = None
        if old_view is None:
            self.history = {"list": [self.profile_name], "index": 0}
            self.message_text = ""
            self.message = None
            self.command_user = None
            self.copy = copy
        else:
            self.history = old_view.history
            self.message_text = old_view.message_text
            self.message = old_view.message
            self.command_user = old_view.command_user
            self.copy = old_view.copy
            self.create_page_menu()
            self.create_related_menu()
        
    def create_embed(self, name):
        # I know discord provides a from_dict method
        # this is good practice tho, right? <- trying to justify wasted time
        page_data = self.profile_dict[name]
        errors = []
        if type(name) is not str:
            self.errors.append(InvalidStoryProfile(self.profile_name, "Page names must be strings."))
            embed = discord.Embed(title="error placeholder")
        elif len(name) > 256:
            self.errors.append(InvalidStoryProfile(self.profile_name, f"Page names must be at most 256 characters."))
            embed = discord.Embed(title="error placeholder")
        elif len(name) == 0:
            self.errors.append(InvalidStoryProfile(self.profile_name, f"Page names must be at least 1 character."))
            embed = discord.Embed(title="error placeholder")
        else:
            embed = discord.Embed(title=name)
        if "description" in page_data:
            if type(page_data["description"]) is not str:
                self.errors.append(InvalidStoryProfile(self.profile_name, f"Descriptions must be strings.", name))
            elif len(page_data["description"]) > 4096:
                self.errors.append(InvalidStoryProfile(self.profile_name, f"Descriptions must be at most 4096 characters.", name))
            if len(self.errors) == 0:
                embed.description = page_data["description"]
        if "image" in page_data and len(page_data["image"]):
            embed.set_image(url=page_data["image"])
        if "fields" in page_data:
            for key, value in page_data["fields"].items():
                if type(key) is not str:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field names must be strings.", name))
                elif len(key) > 256:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field names must be at most 256 characters. \"{key[:200]}...\" is too long.", name))
                elif len(key) == 0:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field names must be at least 1 character.", name))
                if type(value) is not str:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field values must be strings.", name))
                elif len(value) > 1024:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field values must be at most 1024 characters. \"{key}\" is too long.", name))
                elif len(value) == 0:
                    self.errors.append(InvalidStoryProfile(self.profile_name, f"Field values must be at least 1 character.", name))
                if len(self.errors) == 0:
                    embed.add_field(name=key, value=value, inline=False)
        if "footer" in page_data:
            if type(page_data["footer"]) is not str:
                self.errors.append(InvalidStoryProfile(self.profile_name, f"Footers must be strings.", name))
            elif len(page_data["footer"]) > 2048:
                self.errors.append(InvalidStoryProfile(self.profile_name, f"Footers must be at most 2048 characters.", name))
            if len(self.errors) == 0:
                embed.set_footer(text=page_data["footer"])
        if len(embed) > 6000:
            self.errors.append(InvalidStoryProfile(self.profile_name, f"Each page must have no more than 6000 characters.", name))
        return embed

    def get_related(self, name):
        page_data = self.profile_dict[name]
        related = []
        if "related" in page_data:
            if type(page_data["related"]) is not list:
                 self.errors.append(InvalidStoryProfile(self.profile_name, f"Related must be a list of strings.", name))
            else:
                for item in page_data["related"]:
                    if type(item) is not str:
                        self.errors.append(InvalidStoryProfile(self.profile_name, f"Related must be a list of strings.", name))
                    elif item not in story_profiles:
                        self.errors.append(InvalidStoryProfile(self.profile_name, f"{item} is not a valid entry.", name))
                    if len(self.errors) == 0:
                        related.append(item)
        return related

    async def send(self, interaction):
        self.command_user = interaction.user
        self.create_page_menu()
        self.create_related_menu()
        self.message = await interaction.followup.send(view=self, ephemeral=self.copy)
        await self.update_message()
        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] in ["StoryView:happy_ivy_button"]:
            if self.copy:
                await interaction.response.send_message("Ivysaur says hi!", ephemeral=True)
                return False
        elif interaction.user != self.command_user:
            await interaction.response.send_message("You can't interact with someone else's command. Press the Ivysaur button to create a personal copy of this command.", ephemeral=True)
            return False
        return True

    async def update_message(self):
        self.forward_button.disabled = False
        self.back_button.disabled = False
        if len(self.history["list"]) == self.history["index"] + 1:
            self.forward_button.disabled = True
        if self.history["index"] == 0:
            self.back_button.disabled = True
        await self.message.edit(content=f"**Entry for {self.profile_name}:**", embed=self.create_embed(self.current_page), attachments=[], view=self)

    def create_page_menu(self):
        if self.page_menu is not None:
            return
        if len(self.pages) < 2:
            return
        self.page_menu = StoryPageSelectMenu(self.pages, self.current_page)
        self.add_item(self.page_menu)

    def destroy_page_menu(self):
        if self.page_menu is not None:
            self.remove_item(self.page_menu)
            self.page_menu = None

    def create_related_menu(self):
        if self.related_menu is not None:
            return
        if len(self.related) == 0:
            return
        related_start = (self.sep * self.related_pagination_page) - self.sep
        related_end = min(len(self.related), related_start+self.sep)
        related = self.related[related_start:related_end]
        self.related_menu = RelatedSelectMenu(related, self.related_pagination_page, related_start != 0, related_end != len(self.related))
        self.add_item(self.related_menu)

    def destroy_related_menu(self):
        if self.related_menu is not None:
            self.remove_item(self.related_menu)
            self.related_menu = None

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, custom_id="StoryView:back_button")
    async def back_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.history["index"] -= 1
        profile_key = self.history["list"][self.history["index"]]
        new_view = StoryView(profile_key, self, False)
        await new_view.update_message()

    @discord.ui.button(label="", style=discord.ButtonStyle.green, emoji="<:happyivy:666673253414207498>", custom_id="StoryView:happy_ivy_button")
    async def happy_ivy_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await create_story_view(interaction, self.profile_name, True)

    @discord.ui.button(label="Forward", style=discord.ButtonStyle.blurple, custom_id="StoryView:forward_button")
    async def forward_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.history["index"] += 1
        profile_key = self.history["list"][self.history["index"]]
        new_view = StoryView(profile_key, self, False)
        await new_view.update_message()

    async def respond_to_story_page_select_menu(self, interaction: discord.Interaction, values):
        await interaction.response.defer()
        value = int(values[0])
        if value != self.current_page_index:
            self.current_page_index = value
            self.current_page = self.pages[self.current_page_index]
            self.related = [item for item in self.get_related(self.current_page) if item not in invalid_story_profiles]
            self.related_pagination_page = 1
            self.related_pagination_page_amount = max(1, math.ceil(len(self.related)/self.sep))
            self.destroy_related_menu()
            self.create_related_menu()
            self.destroy_page_menu()
            self.create_page_menu()
            await self.update_message()

    async def respond_to_related_select_menu(self, interaction: discord.Interaction, values):
        await interaction.response.defer()
        value = values[0]
        if value not in ["<nextpage>", "<lastpage>"]:
            self.history["index"] += 1
            # add the value to the history while removing the ability to click the forward button
            self.history["list"] = self.history["list"][:self.history["index"]]
            self.history["list"].append(value)
            profile_key = self.history["list"][self.history["index"]]
            new_view = StoryView(profile_key, self, False)
            await new_view.update_message()
            return
        elif value == "<nextpage>":
            self.related_pagination_page += 1
        elif value == "<lastpage>":
            self.related_pagination_page -= 1
        self.destroy_related_menu()
        self.create_related_menu()
        await self.update_message()
   

class StoryPageSelectMenu(discord.ui.Select):
    def __init__(self, pages, current_page_name):
        super().__init__(placeholder=current_page_name, custom_id="StoryView:StoryPageSelectMenu")
        options = []
        for i, page in enumerate(pages):
            if page == current_page_name:
                continue
            options.append(discord.SelectOption(label=page, value=i))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_story_page_select_menu(interaction, self.values)

class RelatedSelectMenu(discord.ui.Select):
    def __init__(self, related, page_number, show_last_page, show_next_page):
        super().__init__(placeholder="Browse related entries", custom_id="StoryView:RelatedSelectMenu")
        options = [discord.SelectOption(label=item, value=item) for item in related]
        if show_last_page:
            options = [discord.SelectOption(label=f"(To page {page_number-1})", value="<lastpage>")] + options
        if show_next_page:
            options += [discord.SelectOption(label=f"(To page {page_number+1})", value="<nextpage>")]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_related_select_menu(interaction, self.values)

class StoryCog(commands.GroupCog, group_name="story"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View the profile of a character, location, or event from the story.")
    @app_commands.autocomplete(profile=story_autocomplete)
    async def command_profile(self, interaction: discord.Interaction,
                                    profile: str):
        """
        Parameters
        -----------
        profile: str
            The character, location, or event to view the profile of.
        """
        if profile not in story_profiles or profile in invalid_story_profiles:
            await interaction.response.send_message("This profile doesn't exist or isn't able to be viewed.", ephemeral=True)
        else:
            await interaction.response.defer()
            await create_story_view(interaction, profile)

    @app_commands.command(name="list", description="Lists all profiles.")
    async def command_list(self, interaction: discord.Interaction):
        text = ""
        for profile in sorted(list(story_profiles.keys()), key=lambda x: x.lower()):
            text += profile + ", "
        text = text.removesuffix(", ")
        await interaction.response.send_message(text)

for key in story_profiles:
    test_profile = StoryView(key)
    for page in test_profile.pages:
        test_profile.create_embed(page)
    for error in test_profile.errors:
        saurbot_functions.timelog(str(error))
    if len(test_profile.errors):
        invalid_story_profiles.append(key)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(StoryCog(bot))
