import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import copy
import replay_analyzer
import datetime
import discord
import fnf_data
import fnf_showdown
from io import BytesIO
import math
from discord.ext import commands
from discord import app_commands
import saurbot_functions
import matplotlib

# credit omosh
# https://stackoverflow.com/questions/69924881/userwarning-starting-a-matplotlib-gui-outside-of-the-main-thread-will-likely-fa
matplotlib.use('agg')

def adaptive_round(x):
    if x < 1:
        digits = 3
    elif x < 10:
        digits = 2
    else:
        digits = 1
    return round(x, digits)

class AnalyzerResultView(discord.ui.View):
    sep: int = 10
    def __init__(self, bot, tier, command1, command2, results_list1, results_list2, single_pokemon1, single_pokemon2, copy):
        super().__init__()
        self.bot = bot
        self.timeout = 900
        self.message_text = ""
        self.message = None
        self.command_user = None
        self.copy = copy
        self.primary_select_menu = None
        self.secondary_select_menu = None
        self.primary_option = "wins"
        self.secondary_option = "total"
        self.secondary_selection = None
        self.results_dict1 = None
        self.winning_results_dict1 = None
        self.losing_results_dict1 = None
        self.results_dict2 = None
        self.winning_results_dict2 = None
        self.losing_results_dict2 = None
        self.command1 = command1
        self.command2 = command2
        self.results_list1 = results_list1
        self.results_list2 = results_list2
        self.single_pokemon1 = single_pokemon1
        self.single_pokemon2 = single_pokemon2
        self.tier = tier
        self.attachments = []
        self.now = datetime.datetime.now()
        self.pokemon_results()

    def pokemon_results(self):
        self.results_dict1 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
        self.winning_results_dict1 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
        self.losing_results_dict1 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
        results_list1 = sorted(self.results_list1, key=lambda x: x.timestamp)
        for mon in results_list1:
            self.results_dict1 = replay_analyzer.update_pokemon_stats(self.results_dict1, mon)
            if mon.winner:
                self.winning_results_dict1 = replay_analyzer.update_pokemon_stats(self.winning_results_dict1, mon)
            else:
                self.losing_results_dict1 = replay_analyzer.update_pokemon_stats(self.losing_results_dict1, mon)
        if len(self.results_list2):
            results_list2 = sorted(self.results_list2, key=lambda x: x.timestamp)
            self.results_dict2 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
            self.winning_results_dict2 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
            self.losing_results_dict2 = copy.deepcopy(replay_analyzer.POKEMON_ATTRIBUTES)
            for mon in results_list2:
                self.results_dict2 = replay_analyzer.update_pokemon_stats(self.results_dict2, mon)
                if mon.winner:
                    self.winning_results_dict2 = replay_analyzer.update_pokemon_stats(self.winning_results_dict2, mon)
                else:
                    self.losing_results_dict2 = replay_analyzer.update_pokemon_stats(self.losing_results_dict2, mon)
        else:
            results_list2 = None
            self.results_dict2 = None
            self.winning_results_dict2 = None
            self.losing_results_dict2 = None

    @saurbot_functions.to_thread
    def calculate_results(self):
        all_species_in_tier = self.tier.get_species_with_sufficient_data()
        sns.set(style="darkgrid", context="notebook", font_scale=1.25)
        plt.style.use("dark_background")
        plt.rcParams.update({"grid.linewidth":0.5, "grid.alpha":0.5, "figure.figsize": [12,6]})
        # this is programmed in a way that supports multiple plots, but right now only one is displayed at a time
        figure, axe = plt.subplots(1, 1, figsize=(12,8))
        for tier_update in [datetime.datetime.fromtimestamp(timestamp) for timestamp in self.tier.update_timestamps]:
            axe.axvline(tier_update, ymin=0, ymax=1, linewidth = 1.5, color="pink", alpha=0.75)
        if self.secondary_option.startswith("per"):
            title = f"{self.primary_option.capitalize()} {self.secondary_option}"
        else:
            title = f"{self.secondary_option.capitalize()} {self.primary_option}"
        ylim = False
        if self.primary_option in ["wins", "faints"] and self.secondary_option == "average":
            ylim = True
        y_function = lambda x: x[self.primary_option][self.secondary_option]
        axe = self.create_subplot(axe, title, "Time", "Value", all_species_in_tier, y_function, [0, 1] if ylim else None)
        axe.legend(loc="upper left", fontsize="x-small")
        axe.autoscale(tight=True)
        axe.tick_params(labelrotation=60)
        figure.tight_layout()
        with BytesIO() as image:
            figure.savefig(image, format="png")
            image.seek(0)
            self.attachments = [discord.File(fp=image, filename='image.png')]
        sorted_all_species_in_tier = {key: y_function(all_species_in_tier[key].stats)[-1] for key in all_species_in_tier}
        sorted_all_species_in_tier = {key: value for key, value in sorted(sorted_all_species_in_tier.items(), key=lambda x: x[1])}
        reverse_sorted_all_species_in_tier = {key: value for key, value in sorted(sorted_all_species_in_tier.items(), reverse=True, key=lambda x: x[1])}
        text = title
        average_value = adaptive_round(sum(sorted_all_species_in_tier.values()) / len(sorted_all_species_in_tier))
        if len(sorted_all_species_in_tier) % 2 == 0:
            upper_median = list(sorted_all_species_in_tier.values())[math.ceil(len(sorted_all_species_in_tier)-1)]
            lower_median = list(sorted_all_species_in_tier.values())[math.floor(len(sorted_all_species_in_tier)-1)]
            median_value = adaptive_round((upper_median + lower_median) / 2)
        else:
            median_value = adaptive_round(list(sorted_all_species_in_tier.values())[(len(sorted_all_species_in_tier)-1)//2])
        command1_value = y_function(self.results_dict1)[-1]
        command1_percentile = round(self.get_percentile(command1_value, list(sorted_all_species_in_tier.values()), self.single_pokemon1), 1)
        text += f"\n{self.command1}: {adaptive_round(command1_value)} (greater than {command1_percentile}% of the tier)"
        if self.results_dict2 is not None:
            command2_value = y_function(self.results_dict2)[-1]
            command2_percentile = round(self.get_percentile(command2_value, list(sorted_all_species_in_tier.values()), self.single_pokemon2), 1)
            text += f"\n{self.command2}: {adaptive_round(command2_value)} (greater than {command2_percentile}% of the tier)"
        text += f"\n\nTier average: {average_value}"
        text += f"\nTier median: {median_value}"
        text += "\n\nTier leaders:"
        count = 5
        for key, value in reverse_sorted_all_species_in_tier.items():
            text += f"\n{key}: {adaptive_round(value)}"
            count -= 1
            if count == 0:
                break
        self.message_text = text

    def get_percentile(self, value, tier_values, single_species):
        # binary search to find where value fits in
        lower_index = 0
        upper_index = len(tier_values) - 1
        if value > tier_values[upper_index] and single_species == False:
            return 100.0
        elif value <= tier_values[lower_index]:
            return 0.0
        else:
            while True:
                index = math.ceil((lower_index + upper_index) / 2)
                if tier_values[index] >= value:
                    upper_index = index
                elif tier_values[index] < value:
                    if tier_values[index+1] >= value:
                        # single_species = True if the filter is is_species: <a single pokemon's name>
                        # in that case, don't include that species in the size of the tier for percentile purposes
                        pokemon_in_tier = len(tier_values)-int(single_species)
                        number_of_pokemon_lower_than_value = index+1
                        return 100*(number_of_pokemon_lower_than_value/pokemon_in_tier)
                    lower_index = index

    def create_subplot(self, axe, title, xlabel, ylabel, tier_data, y_function, ylim=None):
        for i, mon in enumerate(sorted(tier_data.values(), key=lambda x: y_function(x.stats)[-1])):
            green = (i/(4*len(tier_data))) + 0.5
            data = {
                "x": mon.stats["date"]+[self.now],
                "y": duplicate_last_entry(y_function(mon.stats))
                }
            sns.lineplot(data=data, x="x", y="y", color=(1,green,0.25), alpha=0.3, ax=axe)
        results_data1 = {
            "x": self.results_dict1["date"]+[self.now],
            "y": duplicate_last_entry(y_function(self.results_dict1))
            }
        sns.lineplot(data=results_data1, x="x", y="y", linewidth = 2, color=(0,1,1), label=self.command1, linestyle="solid", ax=axe)
        if self.results_dict2 is not None:
            results_data2 = {
                "x": self.results_dict2["date"]+[self.now],
                "y": duplicate_last_entry(y_function(self.results_dict2))
                }
            sns.lineplot(data=results_data2, x="x", y="y", linewidth = 2, color=(1,0.5,1), label=self.command2, linestyle="solid", ax=axe)
        axe.set(title=title, xlabel=xlabel, ylabel=ylabel)
        if ylim is not None:
            axe.set_ylim(ylim)
        return axe

    async def send(self, interaction):
        self.command_user = interaction.user
        self.create_primary_select_menu()
        self.create_secondary_select_menu()
        await self.calculate_results()
        self.message = await interaction.followup.send(view=self, ephemeral=self.copy)
        await self.update_message()
        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] in ["AnalyzerResultView:happy_ivy_button"]:
            if self.copy:
                await interaction.response.send_message("Ivysaur says hi!", ephemeral=True)
                return False
        elif interaction.user != self.command_user:
            await interaction.response.send_message("You can't interact with someone else's command. Press the Ivysaur button to create a personal copy of this command.", ephemeral=True)
            return False
        return True

    async def update_message(self):
        await self.message.edit(content=self.message_text, attachments=self.attachments, view=self)

    def get_primary_select_menu_options(self):
        return [item for item in replay_analyzer.POKEMON_ATTRIBUTES.keys() if item not in ["timestamps", "date"]]

    def get_secondary_select_menu_options(self):
        if type(replay_analyzer.POKEMON_ATTRIBUTES[self.primary_option]) is not dict:
            return []
        else:
            return [item for item in replay_analyzer.POKEMON_ATTRIBUTES[self.primary_option].keys()]

    def create_primary_select_menu(self):
        if self.primary_select_menu is not None:
            return
        self.primary_select_menu = AnalyzerSelectMenu("primary", self.get_primary_select_menu_options(), self.primary_option)
        self.add_item(self.primary_select_menu)

    def destroy_primary_select_menu(self):
        if self.primary_select_menu is not None:
            self.remove_item(self.primary_select_menu)
            self.primary_select_menu = None

    def create_secondary_select_menu(self):
        if self.secondary_select_menu is not None:
            return
        self.secondary_select_menu = AnalyzerSelectMenu("secondary", self.get_secondary_select_menu_options(), self.secondary_option)
        self.add_item(self.secondary_select_menu)

    def destroy_secondary_select_menu(self):
        if self.secondary_select_menu is not None:
            self.remove_item(self.secondary_select_menu)
            self.secondary_select_menu = None

    @discord.ui.button(label="", style=discord.ButtonStyle.green, emoji="<:happyivy:666673253414207498>", custom_id="AnalyzerResultView:happy_ivy_button")
    async def happy_ivy_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await create_pokemon_analysis_view(interaction, self.bot, self.tier, self.command1, self.command2, self.results_list1, self.results_list2, self.single_pokemon1, self.single_pokemon2, True)

    async def respond_to_select_menu(self, interaction: discord.Interaction, callback_id, values):
        await interaction.response.defer()
        value = values[0]
        if callback_id == "primary":
            self.primary_option = value
        elif callback_id == "secondary":
            self.secondary_option = value
        await self.calculate_results()
        self.destroy_primary_select_menu()
        self.destroy_secondary_select_menu()
        self.create_primary_select_menu()
        self.create_secondary_select_menu()
        await self.update_message()
   

class AnalyzerSelectMenu(discord.ui.Select):
    def __init__(self, callback_id, pages, current_page_name):
        super().__init__(placeholder=current_page_name)
        self.timeout = 900
        self.callback_id = callback_id
        options = []
        for page in pages:
            if page == current_page_name:
                continue
            options.append(discord.SelectOption(label=page, value=page))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_select_menu(interaction, self.callback_id, self.values)

COMBATANT_ATTRIBUTES = {
    "differential": "differential",
    "turns": "turns",
    "active turns": "active_turns",
    "active turns per turn": "active_turns_per_turn",
    "damage dealt": "total_damage_dealt",
    "damage dealt per game turn": "total_damage_dealt_per_turn",
    "active damage": "active_damage",
    "active damage per game turn": "active_damage_per_turn",
    "active damage per active turn": "active_damage_per_active_turn",
    "direct damage dealt": "direct_damage_dealt",
    "direct damage dealt per game turn": "direct_damage_dealt_per_turn",
    "direct damage dealt per active turn": "direct_damage_dealt_per_active_turn",
    "indirect damage dealt": "indirect_damage_dealt",
    "indirect damage dealt per game turn": "indirect_damage_dealt_per_turn",
    "damage taken": "damage_taken",
    "damage taken per game turn": "damage_taken_per_turn",
    "damage taken per active turn": "damage_taken_per_active_turn",
    "healing given": "healing_given",
    "healing given per game turn": "healing_given_per_turn",
    "healing given per active turn": "healing_given_per_active_turn",
    "healing received": "healing_received",
    "healing received per game turn": "healing_received_per_turn",
    "healing received per active turn": "healing_received_per_active_turn"}

class InvalidReplayAnalysisRequest(Exception):
    def __init__(self, errors):
        self.errors = errors
    def __str__(self):
        text = ""
        for error in self.errors:
            text += error + "\n"
        return text.strip()
    
# for when the requested data is pokemon
def parse_pokemon_arguments(bot, interaction, tier, command):
    # arguments are individual filters given by the user, deliminated by semicolins
    arguments = command.split(";")
    all_pokemon_in_tier = tier.get_all_pokemon_instances()
    errors = []
    single_pokemon_search = "Maybe"
    if command != "all":
        # the check_date filter is unique and will always be run
        before = 253402322399 # 12/31/9999 23:59:59
        after = 1
        # this goes through each argument and matches it with the filter function that needs to be called
        if len(arguments) != 1:
            single_pokemon_search = "False"
        for argument in arguments:
            arg = argument.strip()
            inverse = False
            if arg.startswith("!"):
                arg = arg.removeprefix("!")
                inverse = True
                single_pokemon_search = "False"
            if arg.startswith("is_species"):
                arg = arg.removeprefix("is_species")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "is_species", arg, "species", "pokemon")
                if len(filter_args) == 1 and single_pokemon_search == "Maybe":
                    single_pokemon_search = "True"
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_species(filter_args, inverse)]

            elif arg.startswith("has_move"):
                arg = arg.removeprefix("has_move")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "has_move", arg, "moves", "move")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_move(filter_args, False, inverse)]

            elif arg.startswith("has_ability"):
                arg = argument.removeprefix("has_ability")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "has_ability", arg, "abilities", "ability")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_ability(filter_args, inverse)]

            elif arg.startswith("has_item"):
                arg = arg.removeprefix("has_item")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "has_item", arg, "items")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_item(filter_args, inverse)]

            elif arg == "won":
                all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_win()]
            elif arg == "lost":
                all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_win(True)]
            elif arg == "lived":
                all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.fainted(True)]
            elif arg == "fainted":
                all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.fainted()]
            
            elif arg.startswith("ko_amount"):
                arg = arg.removeprefix("ko_amount")
                arg = arg.strip()
                comparison_operator, value, formatting_errors = prepare_comparison_arg_filter("ko_amount", arg)
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_number_of_kos(value, comparison_operator)]
            
            elif arg.startswith("koed_by"):
                arg = arg.removeprefix("koed_by")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "koed_by", arg, "species", "pokemon")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_knocked_out_by(filter_args, inverse)]
        
            elif arg.startswith("koed_species"):
                arg = arg.removeprefix("koed_species")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "koed_species", arg, "species", "pokemon")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_knocked_out_opponent(filter_args, False, inverse)]
        
            elif arg.startswith("before"):
                arg = arg.removeprefix("before")
                arg = arg.strip()
                date, formatting_errors = validate_date("before", arg)
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    before = date
                
            elif arg.startswith("after"):
                arg = arg.removeprefix("after")
                arg = arg.strip()
                date, formatting_errors = validate_date("after", arg)
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    after = date

            elif arg.startswith("used_by_trainer"):
                arg = arg.removeprefix("used_by_trainer")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "used_by_trainer", arg, "trainer", None, interaction)
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_team_trainer(filter_args, interaction.guild_id, inverse)]

            elif arg.startswith("fought_trainer"):
                arg = arg.removeprefix("fought_trainer")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "fought_trainer", arg, "trainer", None, interaction)
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_opponent_trainer(filter_args, interaction.guild_id, inverse)]

            elif arg.startswith("has_teammates"):
                arg = arg.removeprefix("has_teammates")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "has_teammates", arg, "species", "pokemon")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_teammates(filter_args, False, inverse)]

            elif arg.startswith("fought_species"):
                arg = arg.removeprefix("fought_species")
                arg = arg.strip()
                filter_args, formatting_errors = prepare_two_arg_basic_filter(bot, "fought_species", arg, "species", "pokemon")
                if len(formatting_errors):
                    errors += formatting_errors
                    continue
                else:
                    all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_opponents(filter_args, False, inverse)]          
            else:
                combatant_attribute_flag = False
                for k, v in COMBATANT_ATTRIBUTES.items():
                    combatant_attribute_flag = True
                    if arg.startswith(k):
                        arg = arg.removeprefix(k)
                        arg = arg.strip()
                        comparison_operator, value, formatting_errors = prepare_comparison_arg_filter(k, arg)
                        if len(formatting_errors):
                            errors += formatting_errors
                            continue
                        else:
                            all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_performance_stat(v, value, comparison_operator)]
                if combatant_attribute_flag == False:
                    errors.append(f"Unknown argument {arg}.")
            
        all_pokemon_in_tier = [mon for mon in all_pokemon_in_tier if mon.check_date(after, before)]
    if len(all_pokemon_in_tier) < replay_analyzer.SUFFICIENT_DATA_SIZE:
        errors.append("Not enough results.")
    if len(errors) != 0:
         raise InvalidReplayAnalysisRequest(errors)
    return all_pokemon_in_tier, True if single_pokemon_search == "True" else False

# this function just converts a string date provided by the user to something usable
def validate_date(filter_name, arg):
    errors = []
    if "-" in arg:
        month_day_year = arg.split("-")
    elif "/" in arg:
        month_day_year = arg.split("/")
    if len(month_day_year) != 3:
        errors.append(f"Improper formatting for {filter_name}. Please format dates like MM/DD/YYYY or MM-DD-YYYY.")
        return None, errors
    month = convert_int(month_day_year[0])
    day = convert_int(month_day_year[1])
    year = convert_int(month_day_year[2])
    date = None
    if month is None or month < 1 or month > 12:
        errors.append(f"Invalid month provided for {filter_name}.")
    if day is None:
        errors.append(f"Invalid day provided for {filter_name}.")
    if year is None:
        errors.append(f"Invalid year provided for {filter_name}.")
    if len(errors) == 0:
        try:
            timestamp = datetime.timestamp(datetime.date(year, month, day))
        except ValueError as e:
            errors.append(f"Invalid formatting for {filter_name}: {e}.")
    return timestamp, errors
    

def prepare_comparison_arg_filter(filter_name, arg):
    errors = []
    subargs = arg.strip()
    if subargs.startswith(">="):
        comparison_operator = ">="
    elif subargs.startswith("<="):
        comparison_operator = "<="
    elif subargs.startswith(">"):
        comparison_operator = ">"
    elif subargs.startswith("<"):
        comparison_operator = "<"
    elif subargs.startswith("="):
        comparison_operator = "="
    else:
        errors.append(f"Invalid comparison operator for {filter_name}.")
        return None, None, errors
    value = subargs.removeprefix(comparison_operator)
    value = value.strip()
    value = convert_int(value)
    if value is None:
        errors.append(f"Invalid value for {filter_name}.")
        return None, None, errors
    return comparison_operator, value, errors
    
def prepare_one_arg_basic_filter(filter_name, arg, filter_type):
    errors = []
    inverse_arg = arg.split
    if inverse_arg == "true":
        inverse = True
    elif inverse_arg == "false":
        inverse = False
    else:
        errors.append(f"Invalid value for inverse in {filter_name}.")
    return inverse_arg, errors
    
# oh god I have to explain how this works
# (this code hasnt been run, so let's be real, it doesn't)
# these filters are formatted like this:
# filter_name, inverse, {fnf showdown search command}
# or
# filter_name, inverse, thing_to_filter_for_1, thing_to_filter_for_2, thing_to_filter_for_3, etc.
# where inverse is a boolean, and when True, it inverses the results of the filter (True becomes False and vice versa)
# where fnf showdown search command is an fnf showdown search command
# and where things_to_filter_by are just strings
# arguments:
# bot - the bot object
# arg - the current filter argument
# filter_type - the name of the filter, for the purpose of having a nice looking error message if the user fucks up
# fnf_showdown_search_type - if this filter allows a saurbot command to be run, what kind of command is it? (pokemon, ability, or move)
# if this command deals with checking trainer data, the command_user is equal to the user of the command to see if they're allowed to see what they're asking to see
def prepare_two_arg_basic_filter(bot, filter_name, arg, filter_type, fnf_showdown_search_type=None, interaction=None):
    errors = []
    subargs = arg.split(",")
    showdown_search = False
    # if there's only 2 argument, this is *maybe* a showdown search command
    if fnf_showdown_search_type is not None and len(subargs) == 1:
        search_query = subargs[0].strip()
        # showdown search commands will always be inside {}. check if they are, and run the command if so
        if search_query.startswith("{") and search_query.endswith("}"):
            showdown_search = True
            search_output, search_results, search_error = run_search_query(search_query, fnf_showdown_search_type)
            if search_error:
                errors.append(f"Invalid argument for {filter_name}. FnF Showdown Search error log: {search_output}")
            filter_args = search_results
    # if it wasn't a showdown search command, every argument for this filter is just the name of something to filter by
    if showdown_search == False:
        filter_args = [thing.strip() for thing in subargs]
    # if command_user was provided, that means check to see if they have permission to view other trainer's stats
    if interaction is not None:
        for trainer in filter_args:
            if has_permission(interaction.guild_id, interaction.user.id, trainer) == False:
                errors.append(f"You either do not have permission to view {bot.get_user(trainer).name}'s battles, or they are not yet in the database.")
    return filter_args, errors
    
# requester and trainer are both discord User.id
def has_permission(guild_id, requester_id, trainer_id):
    if requester_id in [trainer_id, fnf_data.NOEL_ID, fnf_data.DEV_ID]:
        return True
    return fnf_data.guild_preferences[guild_id].user_profiles[trainer_id].public_trainer_data
    
def convert_int(number_string):
    try:
        val = int(number_string)
        return val
    except ValueError:
        return None
        
# this runs the fnf showdown search command and tries to turn it into a list of pokemon/move/ability names
def run_search_query(search_query, command_type):
    error = ""
    results = []
    final_query = search_query.removeprefix("{").removesuffix("}")
    final_query = command_type + " " + search_query
    final_query = final_query.strip()
    command = fnf_showdown.Command(final_query)
    command.run_command()
    if command.success:
        results = [result.name for result in command.raw_results]
    else:
        error = command.output()
    return error, results, command.success

def duplicate_last_entry(l):
    return l + [l[-1]]

async def filter_pokemon(bot, interaction: discord.Interaction, tier: replay_analyzer.Tier, command1: str, command2: str):
    command1 = command1.strip()
    command2 = command2.strip()
    tier = copy.deepcopy(tier)
    try:
        # 10 can be anything, it's just set to this to keep the sample size decent
        if len(tier.get_species_with_sufficient_data()) < 10:
            raise InvalidReplayAnalysisRequest(["This tier does not have enough data yet."])
        results1, single_pokemon1 = parse_pokemon_arguments(bot, interaction, tier, command1)
        single_pokemon2 = False
        if len(command2):
            results2, single_pokemon2 = parse_pokemon_arguments(bot, interaction, tier, command2)
        else:
            results2 = []
        await create_pokemon_analysis_view(interaction, bot, tier, command1, command2, results1, results2, single_pokemon1, single_pokemon2)
        return None
    except InvalidReplayAnalysisRequest as e:
        return e

async def create_pokemon_analysis_view(interaction: discord.Interaction, bot, tier, command1, command2, results_list1, results_list2, single_pokemon1, single_pokemon2, copy=False):
    analysis_view = AnalyzerResultView(bot, tier, command1, command2, results_list1, results_list2, single_pokemon1, single_pokemon2, copy)
    await analysis_view.send(interaction)

async def tier_autocomplete(interaction: discord.Interaction, current):
    return [app_commands.Choice(name=item, value=item)
            for item in sorted(fnf_data.formats) if saurbot_functions.only_a_to_z(current) in saurbot_functions.only_a_to_z(item)]

@app_commands.guild_only()
class AnalyzeCog(commands.GroupCog, group_name="analyze"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pokemon", description="View the performance of a pokemon in a given tier. To use this, view the documentation using /help.")
    @app_commands.autocomplete(tier=tier_autocomplete)
    async def command_pokemon(self, interaction: discord.Interaction,
                                    tier: str,
                                    filters1: str,
                                    filters2: str=""):
        """
        Parameters
        -----------
        tier: str
            The tier to search.
        filters1: str
            The main filters to apply.
        filters2: str
            The comparison filters to apply.
        """
        await interaction.response.defer()
        if tier not in fnf_data.formats:
            await interaction.followup.send(content="This tier is not being tracked.")
        errors = await filter_pokemon(self.bot, interaction, fnf_data.formats[tier], filters1, filters2)
        if errors is not None:
            await interaction.followup.send(content=f"The following errors occurred:\n{errors}\nUse /help for details on how to use this command.")
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AnalyzeCog(bot))