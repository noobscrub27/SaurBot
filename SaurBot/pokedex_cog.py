import fnf_data
import fnf_showdown
import showdown_scraper
import saurbot_functions
import discord
from discord.ext import commands
from discord import app_commands
import enum
import random

class FilterRules(enum.Enum):
    exclude = 0
    include = 1
    require = 2

    

with open("chatot.txt", "r") as f:
    CHATOT = f.read()

class PokedexCog(commands.GroupCog, group_name="pokedex"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Locks the usage of Saurbot commands. Devs only.")
    @app_commands.check(fnf_data.check_is_noob_or_nole)
    async def command_lock_pokedex(self, interaction: discord.Interaction):
        if fnf_data.commands_locked:
            fnf_data.commands_locked = False
            await interaction.response.send_message(f"Pokedex commands are now enabled.", ephemeral=True)
        else:
            fnf_data.commands_locked = True
            await fnf_data.destroy_all_command_views()
            await interaction.response.send_message(f"Pokedex commands are now disabled.", ephemeral=True)

    @command_lock_pokedex.error
    async def command_lock_pokedex_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @app_commands.command(name="debug", description="Toggles debug mode. Devs only.")
    @app_commands.check(fnf_data.check_is_noob)
    async def command_toggle_debug(self, interaction: discord.Interaction):
        if fnf_showdown.debug_mode:
            fnf_showdown.debug_mode = False
            await interaction.response.send_message(f"Debug mode is now disabled.", ephemeral=True)
        else:
            fnf_showdown.debug_mode = True
            await interaction.response.send_message(f"Debug mode is now enabled.", ephemeral=True)

    @app_commands.command(name="update", description="Updates the database. Devs only.")
    @app_commands.check(fnf_data.check_is_noob_or_nole)
    async def command_update(self, interaction: discord.Interaction,
                             revealing: bool=False,
                             update_sprites: bool=False):
        """Filter pokemon. Use /help for more info.

        Parameters
        -----------
        revealing: bool
            Optional. Reveals unrevealed pokemon, moves, and abilities.
        update_sprites: bool
            Optional. Updates the sprite list. Don't use this too often or I'll get rate-limited. :(
        """
        if fnf_data.currently_updating:
            await interaction.response.send_message(f"The database is already being updated. Please try again later.", ephemeral=True)
            return
        else:
            if revealing and fnf_data.check_is_nole(interaction) == False:
                await interaction.response.send_message(f"I'm sorry noob. I'm afraid I can't do that.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            text = saurbot_functions.timelog("Beginning manual update.", True)
            message = await interaction.followup.send(content=text, ephemeral=True)
            async for text_update in showdown_scraper.update_database(revealing, update_sprites):
                text += "\n" + text_update
                await message.edit(content=text)

    @command_update.error
    async def command_update_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @command_toggle_debug.error
    async def command_toggle_debug_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @app_commands.command(name="pokemon")
    async def command_pokemon(self, interaction: discord.Interaction,
                                    filters: str,
                                    base_forms: FilterRules=FilterRules.include,
                                    hypnomons: FilterRules=FilterRules.exclude,
                                    new_gen: FilterRules=FilterRules.exclude,
                                    ignored: FilterRules=FilterRules.exclude):
        """Filters pokemon. Use /help for more info.

        Parameters
        -----------
        filters: str
            Optional. The filters to apply.
        base_forms: FilterRules
            Optional. Include, exclude, or require base forms. Default: Include
        hypnomons: FilterRules
            Optional. Include, exclude, or require hypnomons. Default: Exclude
        new_gen: FilterRules
            Optional. Include, exclude, or require pokemon from games after USUM. Default: Exclude
        ignored: FilterRules
            Optional. Include, exclude, or require non-canon pokemon (eg. Pokestar pokemon). Default: Exclude
        """
        if fnf_data.commands_locked and (fnf_data.check_is_noob_or_nole(interaction) == False):
            await interaction.response.send_message(f"Pokedex commands are currently disabled. Please try again later.", ephemeral=True)
            return
        elif fnf_data.currently_updating:
            await interaction.response.send_message(f"The database is currently updating. Please try again later.", ephemeral=True)
            return
        filter_rules = {"base forms": base_forms.value,
                        "hypnomons": hypnomons.value,
                        "new gens": new_gen.value,
                        "ignored": ignored.value}
        command = fnf_showdown.Command("pokemon " + filters.strip(), filter_rules)
        command.run_command()
        if command.success:
            await fnf_data.create_pagination_view(interaction, self.bot, command)
        else:
            await interaction.response.send_message(command.output, ephemeral=True)
            await self.bot.dm_noob(command.error_log)
    
    @app_commands.command(name="move")
    async def command_move(self, interaction: discord.Interaction,
                                    filters: str,
                                    base_forms: FilterRules=FilterRules.include,
                                    hypnomons: FilterRules=FilterRules.exclude,
                                    new_gen: FilterRules=FilterRules.exclude,
                                    ignored: FilterRules=FilterRules.exclude):
        """Filters moves. Use /help for more info.

        Parameters
        -----------
        filters: str
            Optional. The filters to apply.
        base_forms: FilterRules
            Optional. Include, exclude, or require moves exclusive to base forms. Default: Include
        hypnomons: FilterRules
            Optional. Include, exclude, or require moves exclusive to hypnomons. Default: Exclude
        new_gen: FilterRules
            Optional. Include, exclude, or require moves from games after USUM. Default: Exclude
        ignored: FilterRules
            Optional. Include, exclude, or require moves exclusive to non-canon pokemon. Default: Exclude
        """
        if fnf_data.commands_locked and (fnf_data.check_is_noob_or_nole(interaction) == False):
            await interaction.response.send_message(f"Pokedex commands are currently disabled. Please try again later.", ephemeral=True)
            return
        elif fnf_data.currently_updating:
            await interaction.response.send_message(f"The database is currently updating. Please try again later.", ephemeral=True)
            return
        filter_rules = {"base forms": base_forms.value,
                        "hypnomons": hypnomons.value,
                        "new gens": new_gen.value,
                        "ignored": ignored.value}
        command = fnf_showdown.Command("move " + filters.strip(), filter_rules)
        command.run_command()
        if command.success:
            await fnf_data.create_pagination_view(interaction, self.bot, command)
        else:
            await interaction.response.send_message(command.output, ephemeral=True)
            await self.bot.dm_noob(command.error_log)
            
    @app_commands.command(name="ability")
    async def command_ability(self, interaction: discord.Interaction,
                                    filters: str,
                                    base_forms: FilterRules=FilterRules.include,
                                    hypnomons: FilterRules=FilterRules.exclude,
                                    new_gen: FilterRules=FilterRules.exclude,
                                    ignored: FilterRules=FilterRules.exclude):
        """Filters abilities. Use /help for more info.

        Parameters
        -----------
        filters: str
            Optional. The filters to apply.
        base_forms: FilterRules
            Optional. Include, exclude, or require abilities exclusive to base forms. Default: Include
        hypnomons: FilterRules
            Optional. Include, exclude, or require abilities exclusive to hypnomons. Default: Exclude
        new_gen: FilterRules
            Optional. Include, exclude, or require abilities from games after USUM. Default: Exclude
        ignored: FilterRules
            Optional. Include, exclude, or require abilities exclusive to non-canon pokemon. Default: Exclude
        """
        if fnf_data.commands_locked and (fnf_data.check_is_noob_or_nole(interaction) == False):
            await interaction.response.send_message(f"Pokedex commands are currently disabled. Please try again later.", ephemeral=True)
            return
        elif fnf_data.currently_updating:
            await interaction.response.send_message(f"The database is currently updating. Please try again later.", ephemeral=True)
            return
        filter_rules = {"base forms": base_forms.value,
                        "hypnomons": hypnomons.value,
                        "new gens": new_gen.value,
                        "ignored": ignored.value}
        command = fnf_showdown.Command("ability " + filters.strip(), filter_rules)
        command.run_command()
        if command.success:
            await fnf_data.create_pagination_view(interaction, self.bot, command)
        else:
            await interaction.response.send_message(command.output, ephemeral=True)
            await self.bot.dm_noob(command.error_log)

    @app_commands.command(name="fuse")
    async def command_fuse(self, interaction: discord.Interaction,
                                    first_pokemon: str,
                                    second_pokemon: str):
        """Fuses two pokemon.

        Parameters
        -----------
        first_pokemon: str
            The first pokemon to fuse.
        second_pokemon: str
            The second pokemon to fuse.
        """
        if fnf_data.commands_locked and (fnf_data.check_is_noob_or_nole(interaction) == False):
            await interaction.response.send_message(f"Pokedex commands are currently disabled. Please try again later.", ephemeral=True)
            return
        elif fnf_data.currently_updating:
            await interaction.response.send_message(f"The database is currently updating. Please try again later.", ephemeral=True)
            return
        fusion = fnf_showdown.fuse(first_pokemon, second_pokemon)
        if type(fusion) is list:
            await fnf_data.create_pagination_view(interaction, self.bot, fusion)
        else:
            await interaction.response.send_message(fusion, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PokedexCog(bot))





