from random import gammavariate
import fnf_data
import discord
from discord.ext import commands
from discord import app_commands
import enum

@app_commands.guild_only()
class ConfigCog(commands.GroupCog, group_name="config"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    trigger_group = app_commands.Group(name="trigger", description="Manage the likelihood that Saurbot will respond to certain triggers. Requires permission.")

    @app_commands.command(name="promote")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_promote(self, interaction: discord.Interaction,
                              member: discord.Member):
        """Give a member the ability to use Saurbot commands that require permission. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to promote.
        """
        guild_id = interaction.guild_id
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        user = self.bot.get_user(user_id)
        if user_id in fnf_data.guild_preferences[guild_id].saurbot_managers:
            await interaction.response.send_message(f"{user.name} already has Saurbot management permissions.", ephemeral=True)
            return
        fnf_data.guild_preferences[guild_id].saurbot_managers.append(user_id)
        self.bot.write_preferences()
        await interaction.response.send_message(f"{user.name} can now use commands that require permission.", ephemeral=True)

    @command_promote.error
    async def command_promote_error(self, interaction: discord.Interaction, error):
        fnf_data.timelog("An error was caused by a command.")
        print(error)
        await fnf_data.ephemeral_error_message(interaction, error)

    @app_commands.command(name="demote")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_demote(self, interaction: discord.Interaction,
                              member: discord.Member):
        """Revoke a member's ability to use Saurbot commands that require permission. Requires permission.

        Parameters
        -----------
        member: discord.Member
            The member to demote.
        """
        guild_id = interaction.guild_id
        user_id = member.id
        if user_id is None or self.bot.create_guild_user_profile(interaction.guild, user_id) == False:
            await interaction.response.send_message(f"That user is not a member of this server.", ephemeral=True)
            return
        user = self.bot.get_user(user_id)
        if user_id not in fnf_data.guild_preferences[guild_id].saurbot_managers:
            await interaction.response.send_message(f"{user.name} doesn't have management permissions. If this user is an admin, they can use all Saurbot commands without permission.", ephemeral=True)
            return
        fnf_data.guild_preferences[guild_id].saurbot_managers.remove(user_id)
        self.bot.write_preferences()
        await interaction.response.send_message(f"{user.name} can no longer use commands that require permission.", ephemeral=True)

    @command_demote.error
    async def command_demote_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @trigger_group.command(name="set_odds")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_set_odds(self, interaction: discord.Interaction,
                             trigger: str,
                             odds: float):
        """Set the likelihood that Saurbot will respond to an existing trigger. Requires permission.

        Parameters
        -----------
        trigger: str
            The trigger to set the odds for.
        odds: float
            The likelihood Saurbot will respond to the trigger.
        """
        guild_id = interaction.guild_id
        trigger =  trigger.lower().strip()
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
            await interaction.response.send_message(f"Could not find trigger \"{trigger}\".", ephemeral=True)
        elif trigger not in fnf_data.guild_preferences[guild_id].fun:
            await interaction.response.send_message(f"Could not find trigger \"{trigger}\".", ephemeral=True)
        elif odds > 100 or odds < 0:
            await interaction.response.send_message(f"Odds must be a number between 0 and 100.", ephemeral=True)
        else:
            fnf_data.guild_preferences[guild_id].fun[trigger][0] = odds
            self.bot.write_preferences()
            await interaction.response.send_message(f"Set the response odds to {odds}% for trigger \"{trigger}\".", ephemeral=True)

    @command_trigger_set_odds.error
    async def command_trigger_set_odds_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @trigger_group.command(name="set_all_odds")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_set_all_odds(self, interaction: discord.Interaction,
                                           odds: float):
        """Set the likelihood that Saurbot will respond to any existing trigger. Requires permission.

        Parameters
        -----------
        odds: float
            The likelihood Saurbot will respond to triggers.
        """
        guild_id = interaction.guild_id
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
            await interaction.response.send_message(f"No triggers to update.", ephemeral=True)
        elif len(fnf_data.guild_preferences[guild_id].fun) == 0:
            await interaction.response.send_message(f"No triggers to update.", ephemeral=True)
        elif odds > 100 or odds < 0:
            await interaction.response.send_message(f"Odds must be a number between 0 and 100.", ephemeral=True)
        else:
            counter = 0
            for trigger in fnf_data.guild_preferences[guild_id].fun.values():
                trigger[0] = odds
                counter += 1
            self.bot.write_preferences()
            await interaction.response.send_message(f"Set the response odds to {odds}% for {counter} trigger(s).", ephemeral=True)

    @command_trigger_set_all_odds.error
    async def command_trigger_set_all_odds_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @trigger_group.command(name="cap_odds")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_cap_all_odds(self, interaction: discord.Interaction,
                                           odds: float):
        """Cap the likelihood that Saurbot will respond to any existing trigger. Requires permission.

        Parameters
        -----------
        odds: float
            Any trigger with a response likelihood higher this will have its likelihood reduced to this.
        """
        guild_id = interaction.guild_id
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
            await interaction.response.send_message(f"No triggers to update.", ephemeral=True)
        elif len(fnf_data.guild_preferences[guild_id].fun) == 0:
            await interaction.response.send_message(f"No triggers to update.", ephemeral=True)
        elif odds > 100 or odds < 0:
            await interaction.response.send_message(f"Odds must be a number between 0 and 100.", ephemeral=True)
        else:
            counter = 0
            for trigger in fnf_data.guild_preferences[guild_id].fun.values():
                if trigger[0] > odds:
                    trigger[0] = odds
                    counter += 1
            self.bot.write_preferences()
            await interaction.response.send_message(f"Set the response odds to {odds}% for {counter} trigger(s).", ephemeral=True)

    @command_trigger_cap_all_odds.error
    async def command_trigger_cap_all_odds_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)


    @trigger_group.command(name="add")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_add(self, interaction: discord.Interaction,
                                  trigger: str,
                                  response: str,
                                  odds: float):
        """Add a new trigger, or add a new response for an existing trigger. Requires permission.

        Parameters
        -----------
        trigger: str
            The phrase that might trigger a response.
        response: str
            What Saurbot will say when the it decides to respond to a trigger.
        odds: float
            The likelihood Saurbot will respond to the trigger.
        """
        guild_id = interaction.guild_id
        trigger = trigger.strip().lower()
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
        if odds > 100 or odds < 0:
            await interaction.response.send_message(f"Odds must be a number between 0 and 100.", ephemeral=True)
            return
        elif len(response) > 2000:
            await interaction.response.send_message(f"Response must be 2000 characters or less.", ephemeral=True)
            return
        elif trigger not in fnf_data.guild_preferences[guild_id].fun:
            fnf_data.guild_preferences[guild_id].fun[trigger] = [odds, response]
        else:
            fnf_data.guild_preferences[guild_id].fun[trigger][0] = odds
            fnf_data.guild_preferences[guild_id].fun[trigger].append(response)
        self.bot.write_preferences()
        await interaction.response.send_message(f"Added \"{response}\" to the responses for the phrase \"{trigger}\".\nSet the response odds to {odds}% for the phrase \"{trigger}\".", ephemeral=True)

    @command_trigger_add.error
    async def command_trigger_add_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)


    @trigger_group.command(name="remove")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_remove(self, interaction: discord.Interaction,
                                  trigger: str):
        """Remove a trigger and all of its responses. Requires permission.

        Parameters
        -----------
        trigger: str
            The trigger phrase to remove.
        """
        guild_id = interaction.guild_id
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
            await interaction.response.send_message(f"There are no triggers to remove.", ephemeral=True)
        elif trigger.strip().lower() not in fnf_data.guild_preferences[guild_id].fun:
            await interaction.response.send_message(f"Could not find trigger \"{trigger}\".", ephemeral=True)
        else:
            del fnf_data.guild_preferences[guild_id].fun[trigger.strip().lower()]
            self.bot.write_preferences()
            await interaction.response.send_message(f"Removed trigger \"{trigger}\" and all of its responses.", ephemeral=True)

    @command_trigger_remove.error
    async def command_trigger_remove_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)

    @trigger_group.command(name="list", description="Get a file listing all of the triggers and responses for this server.")
    @app_commands.check(fnf_data.check_saurbot_permissions)
    async def command_trigger_list(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if guild_id not in fnf_data.guild_preferences:
            fnf_data.guild_preferences[guild_id] = self.bot.create_guild_preferences(guild_id)
            self.bot.write_preferences()
            await interaction.response.send_message(f"There are no triggers to view.", ephemeral=True)
        elif len(fnf_data.guild_preferences[guild_id].fun) == 0:
            await interaction.response.send_message(f"There are no triggers to view.", ephemeral=True)
        else:
            text = "Triggers and responses (tabs and linebreaks are omitted)\n\n"
            for trigger in fnf_data.guild_preferences[guild_id].fun:
                stripped_trigger = trigger.replace("\t", " ").replace("\n", " ")
                odds = fnf_data.guild_preferences[guild_id].fun[trigger][0]
                text += f"{stripped_trigger} ({odds}%)\n"
                for response in fnf_data.guild_preferences[guild_id].fun[trigger][1:]:
                    stripped_response = response.replace("\t", " ").replace("\n", " ")
                    text += f"\t{stripped_response}\n"
            await interaction.response.send_message(file=self.bot.turn_into_file(text), ephemeral=True)

    @command_trigger_list.error
    async def command_trigger_list_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)
            
async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigCog(bot))