import fnf_data
import traceback
import os
import itertools
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# this is the last time the FnF Showdown Search database was updated
last_update = None

def timelog(text):
    now = datetime.datetime.now()
    now_text = now.strftime("%m/%d/%y %H:%M:%S")
    print(now_text + " - " + text) 

def create_command(command, tutorial=None, rand=False):
    timelog("A Command object was created.")
    command_object = Command(command, rand)
    command_object.run_command()
    response_text = ""
    if command_object.success:
        if tutorial == "ability" and command_object.command_type == "ability":
            response_text = "Good job!\nBy the way, to see a list of a command's arguments, type \"/help <command name>\".\nOr, to move on, view the \"moves\" tutorial."
        elif tutorial == "move" and command_object.command_type == "move":
            response_text = "Great!\nThe move command is capable of using more complex arguments than the ability command, so try out some of the other arguments sometime.\nOr, to continue, view the \"pokemon\" tutorial."
        elif tutorial == "pokemon" and command_object.command_type == "pokemon":
            response_text = "You now know enough to use my commands effectively. However, I truly shine when my commands are utilized to the fullest. To start learning advanced features, view the \"not operator\" tutorial."
        # the list comprehension serves a dual-purpose of finding if the ! operator was used in the command while also breaking PEP-8 style guide. 
        elif tutorial == "not operator" and command_object.command_type in ["ability", "move", "pokemon"] and len([command_part for command_part in command_object.command_parts if command_part.part_type == "operator" and command_part.contents == "!"]):
            response_text = "Great work! There are still some more operators you should know about. To keep going, see the \"and operator\" tutorial."
        elif tutorial == "and operator" and command_object.command_type in ["ability", "move", "pokemon"] and len([command_part for command_part in command_object.command_parts if command_part.part_type == "operator" and command_part.contents == "&"]):
            response_text = "Good! The next tutorial covers the OR operator, which functions similarly to the AND operator. It's called the \"or operator\" tutorial."
        elif tutorial == "or operator" and command_object.command_type in ["ability", "move", "pokemon"] and len([command_part for command_part in command_object.command_parts if command_part.part_type == "operator" and command_part.contents == "|"]):
            response_text = "You now have a solid understanding of how my commands work, but to become truly proficient there's still a few more things to learn. To continue, see the \"parentheses\" tutorial."
        elif tutorial == "parentheses" and command_object.command_type in ["ability", "move", "pokemon"] and len([command_part for command_part in command_object.command_parts if command_part.part_type == "operator" and command_part.contents == "("]):
            response_text = "You are almost finished! There's just one tutorial left, and it's about the most powerful feature I have. The last tutorial is the \"subcommands\" tutorial."
        elif tutorial == "subcommands" and command_object.command_type == "pokemon" and len([command_part for command_part in command_object.command_parts if command_part.part_type == "subcommand"]):
            response_text = "Congratulations! You now know all you need to filter data like a pro!"
    return command_object.output.replace("é", "e"), command_object.error_log, response_text

# SETUP
# from https://help.pythonanywhere.com/pages/NoSuchFileOrDirectory/
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    
CRED_FILE = os.path.join(THIS_FOLDER, 'credentials-sheets.json')
TYPE_FILE = os.path.join(THIS_FOLDER, 'fnf-types.csv')
HELP_BASIC_FILE = open(os.path.join(THIS_FOLDER, 'help-basic.txt'), "r").read()
HELP_ABILITY_FILE = open(os.path.join(THIS_FOLDER, 'help-ability.txt'), "r").read()
HELP_MOVE_FILE = open(os.path.join(THIS_FOLDER, 'help-move.txt'), "r").read()
HELP_POKEMON_FILE = open(os.path.join(THIS_FOLDER, 'help-pokemon.txt'), "r").read()

debug_mode = False

# a dict of pokemon that should be replaced, and what they should be replaced with (empty string if they should be removed with no replacement)
POKEMON_REPLACE = {
    "Basculin-Red": "Basculin",
    "Basculin-Blue": "",
    "Darmanitan-Zen": "",
    "Meloetta-Pirouette": "",
    "Greninja-Ash": "",
    "Zygarde-Complete": "",
    "Wishiwashi-School": "",
    "Minior-Meteor": "Minior",
    "Minior-Core": ""
    }

# this isn't used but maybe it will be?
KEYWORDS = {
    'HP': ['hp', 'health', 'health points', 'hit points'],
    'ATK': ['atk', 'attack'],
    'DEF': ['def', 'defense'],
    'SPA': ['spa', 'special attack', 'sp. attack', 'sp attack'],
    'SPD': ['spd', 'special defense' 'sp. defense', 'sp defense'],
    'SPE': ['spe', 'speed']}

# creates the type chart - I'm not sure how it works either and I hope I never have to remember
with open(TYPE_FILE, 'r') as in_file:
    lines = [];
    for line in in_file.readlines():
        line = line.split(',')
        l = []
        for value in line:
            value = value.strip()
            l.append(value)
        lines.append(l)

    types = {key: fnf_data.Type(key) for key in lines[0][1:]}
    for line in lines[1:]:
        for i, value in enumerate(line):
            if i == 0:
                continue
            types[line[0]].offensive[types[list(types.keys())[i-1]]] = float(value)

for pkmn_type in types:
    types[pkmn_type].defensive = {types[key]: types[key].offensive[types[pkmn_type]] for key in types.keys()}


# connects to the google sheet
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, scope)
client = gspread.authorize(credentials)
sheet = client.open('FnF Showdown')


def add_move(row):
    name = row["Move"]
    pkmn_type = types[row['Type']]
    category = row["Category"]
    power = row["Power"]
    accuracy = row["Accuracy"]
    accuracy = accuracy.replace("%", "")
    try:
        accuracy = int(accuracy)
    except ValueError:
        pass
    pp = int(row["PP"].split(" (max")[0])
    description = row["Description"]
    fnf_data.moves[name] = fnf_data.Move(name, pkmn_type, category, power, accuracy, pp, description)


def add_ability(row):
    name = row['Ability']
    if name == "-":
        return
    description = row['Description']
    fnf_data.abilities[name] = fnf_data.Ability(name, description)

def add_pokemon(row):
    buff = row['Buff']
    dex = row['Dex']
    name = row['Pokémon']
    tier = row['Tier']
    pkmn_types = []
    for i in [row['Type 1'], row['Type 2']]:
        if i in list(types.keys()):
            pkmn_types.append(types[i])
    pkmn_abilities = []
    for i in [row['Ability 1'], row['Ability 2'], row['Ability 3']]:
        try:
            pkmn_abilities.append(fnf_data.abilities[i])
        except KeyError:
            if i != "-":
                print("WARNING: Could not find ability", ('"' + str(i) + '".'), "(Occurred while processing abilities for", str(name) + ")")
    stats = [row['HP'],
             row['ATK'],
             row['DEF'],
             row['SP.ATK'],
             row['SP.DEF'],
             row['SPEED'],
             row['BST']]

    pkmn_moves = []
    try:
        for move in fnf_data.page_learnsets[name]:
            pkmn_moves.append(fnf_data.moves[move])
    except KeyError:
        print("WARNING: Could not find move or learnset. (Occurred while processing moves for", str(name) + ")")
    changes = row["Changes"]
    sets = []
    for i in [[row["Set 1"], row["1D"]], [row["Set 2"], row["2D"]], [row["Set 3"], row["3D"]]]:
        if i[0] != fnf_data.EMPTY_SAMPLE:
            sets.append(fnf_data.Sample_Set(i[0], i[1]))

    if name in POKEMON_REPLACE:
        if POKEMON_REPLACE[name] == "":
            return
        else:
            name = POKEMON_REPLACE[name]
    fnf_data.pokemon[name] = fnf_data.Pokemon(name, pkmn_types, pkmn_abilities, dex, tier, stats, buff, pkmn_moves, changes, sets)


def update_database():
    global last_update
    fnf_data.pokemon = {}
    fnf_data.abilities = {}
    fnf_data.moves = {}
    fnf_data.page_learnsets = {}
    print("Getting Pokemon data...")
    page_pokedex = sheet.worksheet("misc3").get_all_records()
    print("Getting Ability data...")
    page_abilities = sheet.worksheet("misc1").get_all_records()
    print("Getting Move data...")
    page_moves = sheet.worksheet("misc2").get_all_records()
    print("Getting Learnset data...")
    page_learnsets_list = sheet.worksheet("Learnsets").get_all_values()

    page_learnsets_list = list(map(list, itertools.zip_longest(*page_learnsets_list, fillvalue="")))
    fnf_data.page_learnsets = {}
    for i in page_learnsets_list:
        fnf_data.page_learnsets[i[0]] = [x for x in i[1:] if x != ""]

    for row in page_moves:
        add_move(row)
    for row in page_abilities:
        add_ability(row)
    for row in page_pokedex:
        add_pokemon(row)

    # pokemon with data overrides:
    try:
        fnf_data.pokemon["Basculin"].abilities = [fnf_data.abilities["Adaptability"], fnf_data.abilities["Mold Breaker"], fnf_data.abilities["Rock Head"], fnf_data.abilities["Reckless"]]
        fnf_data.pokemon["Basculin"].notes = "Reckless is exclusive to Red-Striped Basculin. Rock Head is exclusive to Blue-Striped Basculin."
    except:
        print("WARNING: Could not find pokemon \"Basculin\".", "(Occurred while adding Reckless and Rock Head.)")
    try:
        fnf_data.pokemon["Rockruff"].abilities = [fnf_data.abilities["Keen Eye"], fnf_data.abilities["Steadfast"], fnf_data.abilities["Vital Spirit"], fnf_data.abilities["Own Tempo"]]
        fnf_data.pokemon["Rockruff"].notes = "Rockruff gets Own Tempo as a forth ability. This ability lets it evolve into Lycanrock Dusk and lets it learn Happy Hour."
    except:
        print("WARNING: Could not find pokemon \"Rockruff\".", "(Occurred while adding Own Tempo.)")
    try:
        fnf_data.pokemon["Darmanitan"].stats = {"HP": 105, "ATK": 140, "DEF": 55, "SPA": 30, "SPD": 55, "SPE": 95, "BST": 480}
        fnf_data.pokemon["Darmanitan"].alt_stats = {"HP": 105, "ATK": 30, "DEF": 105, "SPA": 140, "SPD": 105, "SPE": 55, "BST": 540}
        fnf_data.pokemon["Darmanitan"].alt_form = "Darmanitan Zen Mode"
        fnf_data.pokemon["Darmanitan"].notes = "Darmanitan's stats change in Zen Mode to 105/30/105/140/105/55 (BST: 540)"
    except:
        print("WARNING: Could not find pokemon \"Darmanitan\".", "(Occurred while adding Darmanitan Zen Mode.)")
    try:
        fnf_data.pokemon["Meloetta"].stats = {"HP": 100, "ATK": 77, "DEF": 77, "SPA": 128, "SPD": 128, "SPE": 90, "BST": 600}
        fnf_data.pokemon["Meloetta"].alt_stats = {"HP": 100, "ATK": 128, "DEF": 90, "SPA": 77, "SPD": 77, "SPE": 128, "BST": 600}
        fnf_data.pokemon["Meloetta"].notes = "Meloetta's stats change in Pirouette forme to 100/128/90/77/77/128 (BST: 600)"
        fnf_data.pokemon["Meloetta"].alt_form = "Meloetta Pirouette forme"
    except:
        print("WARNING: Could not find pokemon \"Meloetta\".", "(Occurred while adding Meloetta Pirouette.)")
    try:
        fnf_data.pokemon["Greninja"].stats = {"HP": 72, "ATK": 95, "DEF": 67, "SPA": 103, "SPD": 71, "SPE": 122, "BST": 530}
        fnf_data.pokemon["Greninja"].alt_stats = {"HP": 72, "ATK": 145, "DEF": 67, "SPA": 153, "SPD": 71, "SPE": 132, "BST": 640}
        fnf_data.pokemon["Greninja"].notes = "Greninja's stats change as Ash-Greninja to 72/145/67/153/71/132 (BST: 640)"
        fnf_data.pokemon["Greninja"].alt_form = "Ash-Greninja"
    except:
        print("WARNING: Could not find pokemon \"Greninja\".", "(Occurred while adding Ash-Greninja.)")
    try:
        fnf_data.pokemon["Aegislash"].stats = {"HP": 60, "ATK": 50, "DEF": 150, "SPA": 50, "SPD": 150, "SPE": 60, "BST": 520}
        fnf_data.pokemon["Aegislash"].alt_stats = {"HP": 60, "ATK": 150, "DEF": 50, "SPA": 150, "SPD": 50, "SPE": 60, "BST": 520}
        fnf_data.pokemon["Aegislash"].notes = "Aegislash's stats change in Blade forme to 60/150/50/150/50/60 (BST: 520)"
        fnf_data.pokemon["Aegislash"].alt_form = "Aegislash Blade forme"
    except:
        print("WARNING: Could not find pokemon \"Aegislash\".", "(Occurred while adding Aegislash Shield.)")
    try:
        fnf_data.pokemon["Zygarde"].stats = {"HP": 108, "ATK": 100, "DEF": 121, "SPA": 81, "SPD": 95, "SPE": 95, "BST": 600}
        fnf_data.pokemon["Zygarde"].alt_stats = {"HP": 261, "ATK": 100, "DEF": 121, "SPA": 91, "SPD": 95, "SPE": 85, "BST": 708}
        fnf_data.pokemon["Zygarde"].notes = "Zygardes's stats change in Complete form to 261/100/121/91/95/85 (BST: 708)"
        fnf_data.pokemon["Zygarde"].alt_form = "Zygarde Complete forme"
    except:
        print("WARNING: Could not find pokemon \"Zygarde\".", "(Occurred while adding Zygarde Complete.)")
    try:
        fnf_data.pokemon["Zygarde-10%"].stats = {"HP": 54, "ATK": 100, "DEF": 71, "SPA": 61, "SPD": 85, "SPE": 115, "BST": 486}
        fnf_data.pokemon["Zygarde-10%"].alt_stats = {"HP": 261, "ATK": 100, "DEF": 121, "SPA": 91, "SPD": 95, "SPE": 85, "BST": 708}
        fnf_data.pokemon["Zygarde-10%"].notes = "Zygardes-10%'s stats change in Complete form to 261/100/121/91/95/85 (BST: 708)"
        fnf_data.pokemon["Zygarde-10%"].alt_form = "Zygarde Complete forme"
    except:
        print("WARNING: Could not find pokemon \"Zygarde-10%\".", "(Occurred while adding Zygarde Complete.)")
    try:
        fnf_data.pokemon["Wishiwashi"].stats = {"HP": 45, "ATK": 20, "DEF": 20, "SPA": 25, "SPD": 25, "SPE": 40, "BST": 175}
        fnf_data.pokemon["Wishiwashi"].alt_stats = {"HP": 45, "ATK": 140, "DEF": 130, "SPA": 140, "SPD": 135, "SPE": 30, "BST": 620}
        fnf_data.pokemon["Wishiwashi"].notes = "Wishiwashi's stats change in School form to 45/140/130/140/135/30 (BST: 620)"
        fnf_data.pokemon["Wishiwashi"].alt_form = "Wishiwashi School form"
    except:
        print("WARNING: Could not find pokemon \"Wishiwashi\".", "(Occurred while adding Wishiwashi School.)")
    try:
        fnf_data.pokemon["Minior"].stats = {"HP": 60, "ATK": 60, "DEF": 100, "SPA": 60, "SPD": 100, "SPE": 60, "BST": 440}
        fnf_data.pokemon["Minior"].alt_stats = {"HP": 60, "ATK": 100, "DEF": 60, "SPA": 100, "SPD": 60, "SPE": 120, "BST": 500}
        fnf_data.pokemon["Minior"].notes = "Minior's stats change in Core form to 60/100/60/100/60/120 (BST: 500)"
        fnf_data.pokemon["Minior"].alt_form = "Minior Core form"
    except:
        print("WARNING: Could not find pokemon \"Minior\".", "(Occurred while adding Minior Core.)")
    last_update = datetime.datetime.now()
    return "Database updated!", None

class CommandPart:
    def __init__(self, part_type, contents):
        self.part_type = part_type
        self.contents = contents
    def __str__(self):
        if self.part_type == "subcommand":
            return "[" + self.contents + "]"
        else:
            return self.contents

class Command:
    def __init__(self, command, rand):
        self.output = ""
        self.success = False
        self.error_log = None
        # for commands that call other commands, root command is the first command called.
        # used to ensure that each chained command writes logs in the same string
        self.root_command = self
        self.command = command
        # when random is true a random pokemon that fits the command output is returned.
        self.random = rand
        # command_text is the version of the command that will be displayed to the user at the end
        self.command_text = "/" + self.command + "\n\n"
        # answer is the version of the command that is used for the bulk of the work
        self.answer = self.command.lower().strip()
        # command type (pokemon, move, ability, etc.)
        self.command_type = ""
        # call log is a log of all the calls made within this class to make debugging easier, since there will be some recursion going on
        self.call_log = ""
        self.call_depth = 0
        # these are the main variables that this class will be using
        self.operators = None
        self.results = None
        self.command_parts = []
        self.results = fnf_data.Argument_Container(None, False, False)

    def log_function_call(self, function_name):
        # makes sure that the root command is the one doing the logging
        if self.root_command is not self:
            self.root_command.log_function_call(function_name)
        else:
            self.call_log += "\t" * self.call_depth + function_name + "\n"
            self.call_depth += 1

    def log_function_end(self):
        # makes sure that the root command is the one doing the logging
        if self.root_command is not self:
            self.root_command.log_function_end()
        else:
            self.call_depth -= 1

    def create_child_command(self, command):
        self.log_function_call("create_child_command")
        # creates a child command and sets its root_command
        child_command = Command(command)
        child_command.root_command = self.root_command
        child_command.run_command()
        self.log_function_end()
        return child_command

    def check_command_type(self):
        # finds the starting word of the command, sets the command_type to it, and removes it
        prefix = ""
        # normal commands
        if self.answer.startswith("ability"):
            self.command_type = "ability"
            prefix = "ability"
        elif self.answer.startswith("abilities"):
            self.command_type = "ability"
            prefix = "abilities"
        elif self.answer.startswith("move"):
            self.command_type = "move"
            prefix = "move"
        elif self.answer.startswith("moves"):
            self.command_type = "move"
            prefix = "moves"
        elif self.answer.startswith("pokemon"):
            self.command_type = "pokemon"
            prefix = "pokemon"
        # special commands start here
        elif self.answer.startswith("compare"):
            self.command_type = "compare"
            prefix = "compare"
        elif self.answer.startswith("learnset"):
            self.command_type = "learnset"
            prefix = "learnset"
        elif self.answer.startswith("sets"):
            self.command_type = "sets"
            prefix = "sets"
        else:
            raise fnf_data.SearchError("Unknown command. Use /help to see a list of commands.")
        return prefix

    def delve_and_append(self, results, result, depth):
        # appends a result to the end of a list.
        # if the last item in the list is a list, it will put the result at the end of it
        # it will recurisvely call itself to do this as many times as it needs
        self.log_function_call("delve_and_append")
        if depth > 0:
            results.arguments[-1] = self.delve_and_append(results.arguments[-1], result, depth-1)
            self.log_function_end()
            return results
        if depth == 0:
            results.arguments.append(result)
            self.log_function_end()
            return results


    def identify_command(self, argument):
        argument = argument.lower().strip()
        result = None
        if self.command_type == "ability":
            if argument.startswith("start"):
                self.log_function_call("identify_command - fnf_data.ability_start")
                result = fnf_data.ability_start(argument.removeprefix("start").strip())
            elif argument.startswith("end"):
                self.log_function_call("identify_command - fnf_data.ability_end")
                result = fnf_data.ability_end(argument.removeprefix("end").strip())
            elif argument.startswith("include"):
                self.log_function_call("identify_command - fnf_data.ability_include")
                result = fnf_data.ability_include(argument.removeprefix("include").strip())
            elif argument.startswith("name"):
                self.log_function_call("identify_command - fnf_data.ability_name")
                result = fnf_data.ability_name(argument.removeprefix("name").strip())
            elif argument.startswith("all"):
                self.log_function_call("identify_command - fnf_data.ability_all")
                result = fnf_data.ability_all()
            else:
                raise fnf_data.SearchError(f"Unable to parse argument {argument}.")

        elif self.command_type == "move":
            if argument.startswith("start"):
                self.log_function_call("identify_command - fnf_data.move_start")
                result = fnf_data.move_start(argument.removeprefix("start").strip())
            elif argument.startswith("end"):
                self.log_function_call("identify_command - fnf_data.move_end")
                result = fnf_data.move_end(argument.removeprefix("end").strip())
            elif argument.startswith("include"):
                self.log_function_call("identify_command - fnf_data.move_include")
                result = fnf_data.move_include(argument.removeprefix("include").strip())
            elif argument.startswith("name"):
                self.log_function_call("identify_command - fnf_data.move_name")
                result = fnf_data.move_name(argument.removeprefix("name").strip())
            elif argument.startswith("pp"):
                self.log_function_call("identify_command - fnf_data.move_pp")
                result = fnf_data.move_pp(argument.removeprefix("pp").strip())
            elif argument.replace(" ", "").startswith("maxpp"):
                self.log_function_call("identify_command - fnf_data.move_maxpp")
                result = fnf_data.move_maxpp(argument.replace(" ", "").removeprefix("maxpp").strip())
            elif argument.startswith("accuracy"):
                self.log_function_call("identify_command - fnf_data.move_accuracy")
                result = fnf_data.move_accuracy(argument.replace(" ", "").removeprefix("accuracy").strip())
            elif argument.startswith("acc"):
                self.log_function_call("identify_command - fnf_data.move_accuracy")
                result = fnf_data.move_accuracy(argument.replace(" ", "").removeprefix("acc").strip())
            elif argument.startswith("power"):
                self.log_function_call("identify_command - fnf_data.move_power")
                result = fnf_data.move_power(argument.replace(" ", "").removeprefix("power").strip())
            elif argument.startswith("pow"):
                self.log_function_call("identify_command - fnf_data.move_pow")
                result = fnf_data.move_power(argument.replace(" ", "").removeprefix("pow").strip())
            elif argument.startswith("category"):
                self.log_function_call("identify_command - fnf_data.move_category")
                result = fnf_data.move_category(argument.replace(" ", "").removeprefix("category").strip())
            elif argument.startswith("cat"):
                self.log_function_call("identify_command - fnf_data.move_category")
                result = fnf_data.move_category(argument.replace(" ", "").removeprefix("cat").strip())
            elif argument.startswith("type"):
                self.log_function_call("identify_command - fnf_data.move_type")
                result = fnf_data.move_type(argument.replace(" ", "").removeprefix("type").strip())
            elif argument.startswith("vs"):
                self.log_function_call("identify_command - fnf_data.move_efficacy")
                argument_types = []
                untouched_arg = argument
                argument = argument.removeprefix("vs").strip()
                result = None
                while True:
                    found_type = False
                    for pkmn_type in types:
                        if argument.startswith(pkmn_type.lower()):
                            found_type = pkmn_type
                            break
                    if found_type:
                        argument_types.append(types[found_type])
                        argument = argument.removeprefix(found_type.lower()).strip()
                        if argument.startswith(",") and len(argument_types) < 2:
                            argument = argument.removeprefix(",").strip()
                            found_type = False
                        else:
                            if len(argument_types) == 1:
                                argument_types.append(types["Typeless"])
                            result = fnf_data.move_efficacy(argument_types, argument)
                    elif result is not None:
                        break
                    else:
                        raise fnf_data.SearchError(f"Unable to parse argument {untouched_arg}.")
            elif argument.startswith("all"):
                self.log_function_call("identify_command - fnf_data.move_all")
                result = fnf_data.move_all()
            else:
                raise fnf_data.SearchError(f"Unable to parse argument {argument}.")

        elif self.command_type == "pokemon":
            if argument.startswith("start"):
                self.log_function_call("identify_command - fnf_data.pokemon_start")
                result = fnf_data.pokemon_start(argument.removeprefix("start").strip())
            elif argument.startswith("end"):
                self.log_function_call("identify_command - fnf_data.pokemon_end")
                result = fnf_data.pokemon_end(argument.removeprefix("end").strip())
            elif argument.startswith("include"):
                self.log_function_call("identify_command - fnf_data.pokemon_include")
                result = fnf_data.pokemon_include(argument.removeprefix("include").strip())
            elif argument.startswith("name"):
                self.log_function_call("identify_command - fnf_data.pokemon_name")
                result = fnf_data.pokemon_name(argument.removeprefix("name").strip())
            elif argument.startswith("dex"):
                self.log_function_call("identify_command - fnf_data.pokemon_pokedex")
                result = fnf_data.pokemon_pokedex(argument.replace(" ", "").removeprefix("dex").strip())
            elif argument.startswith("pokedex"):
                self.log_function_call("identify_command - fnf_data. pokemon_pokedex")
                result = fnf_data.pokemon_pokedex(argument.replace(" ", "").removeprefix("pokedex").strip())
            elif argument.startswith("tier"):
                self.log_function_call("identify_command - fnf_data.pokemon_tier")
                result = fnf_data.pokemon_tier(argument.replace(" ", "").removeprefix("tier").strip())
            elif argument.startswith("buff"):
                self.log_function_call("identify_command - fnf_data.pokemon_buff")
                result = fnf_data.pokemon_buff()
            elif argument.startswith("hp"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('HP', argument.replace(" ", "").removeprefix("hp").strip())
            elif argument.startswith("attack"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('ATK', argument.replace(" ", "").removeprefix("attack").strip())
            elif argument.startswith("defense"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('DEF', argument.replace(" ", "").removeprefix("defense").strip())
            elif argument.startswith("special attack"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPA', argument.replace(" ", "").removeprefix("specialattack").strip())
            elif argument.startswith("special defense"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPD', argument.replace(" ", "").removeprefix("specialdefense").strip())
            elif argument.startswith("speed"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPE', argument.replace(" ", "").removeprefix("speed").strip())
            elif argument.startswith("atk"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('ATK', argument.replace(" ", "").removeprefix("atk").strip())
            elif argument.startswith("def"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('DEF', argument.replace(" ", "").removeprefix("def").strip())
            elif argument.startswith("spa"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPA', argument.replace(" ", "").removeprefix("spa").strip())
            elif argument.startswith("spd"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPD', argument.replace(" ", "").removeprefix("spd").strip())
            elif argument.startswith("spe"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('SPE', argument.replace(" ", "").removeprefix("spe").strip())
            elif argument.startswith("bst"):
                self.log_function_call("identify_command - fnf_data.pokemon_stat")
                result = fnf_data.pokemon_stat('BST', argument.replace(" ", "").removeprefix("bst").strip())
            elif argument.startswith("type"):
                self.log_function_call("identify_command - fnf_data.pokemon_type")
                result = fnf_data.pokemon_type(argument.replace(" ", "").removeprefix("type").strip())
            elif argument.startswith("vs"):
                for pkmn_type in types:
                    if argument.replace(" ", "").startswith("vs" + types[pkmn_type].name.lower()):
                        self.log_function_call("identify_command - fnf_data.pokemon_efficacy")
                        result = fnf_data.pokemon_efficacy(types[pkmn_type], argument.removeprefix("vs").strip().removeprefix(types[pkmn_type].name.lower()).strip())
            elif argument.startswith("all"):
                self.log_function_call("identify_command - fnf_data.pokemon_all")
                result = fnf_data.pokemon_all()
            else:
                raise fnf_data.SearchError(f"Unable to parse argument {argument}.")
        if result is None:
            raise fnf_data.SearchError(f"Unable to parse argument {argument}.")
        else:
            return result

    def format_results(self):
        self.log_function_call("format_results")
        text = self.command_text
        if len(self.results.data) == 1:
            if self.command_type == "ability":
                text += self.results.data[0].to_string_one_line()
            else:
                text += self.results.data[0].to_string()
        elif len(self.results.data) > 1:
            if self.command_type == "pokemon":
                self.results.data = sorted(self.results.data, key=lambda data: data.pokedex)
            elif self.command_type in ["ability", "move"]:
                self.results.data = sorted(self.results.data, key=lambda data: data.name.lower())
            for i in self.results.data:
                text += i.to_string_one_line() + "\n"
            text = text[:-1]
        else:
            text += "No results found."
        self.log_function_end()
        return text
        
    def run_command(self):
        self.log_function_call("run_command")
        try:
            self.operators = ["&"]
            for character in self.answer:
                if character in ["!", "&", "|", "(", ")", "[", "]"]:
                    self.operators.append(character)
            
            prefix = self.check_command_type()
            self.answer = self.answer.removeprefix(prefix).strip()
            if prefix == "compare":
                self.log_function_call("fnf_data.compare_learnsets")
                self.results = fnf_data.compare_learnsets(self.answer)
                self.log_function_end()
                self.output = self.command_text + self.results
                self.log_function_end()
                return
            elif prefix == "learnset":
                self.log_function_call("fnf_data.find_one_pokemon")
                self.results = fnf_data.find_one_pokemon(self.answer)
                self.log_function_end()
                self.output = self.command_text + self.results.to_string_moves()
                self.log_function_end()
                return
            elif prefix == "sets":
                self.log_function_call("fnf_data.find_one_pokemon")
                self.results = fnf_data.find_one_pokemon(self.answer)
                self.log_function_end()
                self.output = self.command_text + self.results.to_string_sample_sets()
                self.log_function_end()
                return
            # make sure that parentheses are even
            parentheses_count = 0
            for operator in self.operators:
                if operator == "(":
                    parentheses_count += 1
                elif operator == ")":
                    parentheses_count -= 1
                if parentheses_count < 0:
                    raise fnf_data.SearchError("Found a closing parentheses without an opening parentheses.")
            if parentheses_count < 0:
                raise fnf_data.SearchError("There are more closing parentheses than opening parentheses.")
            elif parentheses_count > 0:
                raise fnf_data.SearchError("There are more opening parentheses than closing parentheses.")

            # make sure that brackets are even
            bracket_count = 0
            for operator in self.operators:
                if operator == "[":
                    bracket_count += 1
                elif operator == "]":
                    bracket_count -= 1
                if bracket_count < 0:
                    raise fnf_data.SearchError("Found a closing bracket without an opening bracket.")
            if bracket_count < 0:
                raise fnf_data.SearchError("There are more closing brackets than opening brackets.")
            elif bracket_count > 0:
                raise fnf_data.SearchError("There are more opening brackets than closing brackets.")
            # make sure that brackets are being used correctly
            elif self.command_type != "pokemon" and ("[" in self.operators):
                raise fnf_data.SearchError("Only pokemon commands can use brackets.")
            elif self is not self.root_command and self.root_command.command_type == "pokemon" and self.command_type not in ["move", "ability"]:
                raise fnf_data.SearchError("Only move and ability commands can be placed in bracket operators.")
            
            # now its time to set the operators list (for real this time)
            # the argument list and subcommand list will also be made
            in_brackets = False
            current_argument = ""
            # loops through each character in the answer
            for character in self.answer:
                if in_brackets:
                    if character == "]":
                        # close bracket signifies the end of a subcommand. the subcommand is added to the list and the string is reset
                        in_brackets = False
                        if len(current_argument.strip()):
                            self.command_parts.append(CommandPart("subcommand", current_argument.strip()))
                        else:
                            raise fnf_data.SearchError("Brackets must contain a move or ability command.")
                        current_argument = ""
                    elif character == "[":
                        raise fnf_data.SearchError("Brackets cannot be placed inside of brackets.")
                    else:
                        current_argument += character
                else:
                    if character == "[":
                        # open bracket signifies the start of a new subcommand.
                        in_brackets = True
                    elif character in ["&", "|", "(", ")", "!"]:
                        if len(current_argument.strip()):
                            self.command_parts.append(CommandPart("argument", current_argument.strip()))
                            current_argument = ""
                        self.command_parts.append(CommandPart("operator", character))
                    else:
                        current_argument += character
            if len(current_argument.strip()):
                self.command_parts.append(CommandPart("argument", current_argument.strip()))
                current_argument = ""
            # search loop
            
            self.results.command_type = self.command_type
            inverse = False
            merge = False
            depth = 0
            last_command_part = None
            for command_part in self.command_parts:
                if command_part.part_type == "operator":
                    # the OR and AND operators always signify the start of a new argument
                    if command_part.contents in ["|", "&"]:
                        if command_part.contents == "|":
                            merge = True
                        else:
                            merge = False
                        inverse = False
                        if last_command_part is not None and last_command_part.part_type == "operator" and last_command_part.contents in ["(", "[", "!", "&", "|"]:
                            raise fnf_data.SearchError("AND and OR operators must not come directly after other operators with the exception of closing brackets/parentheses.")
                    # NOT operators can be used once per arguments to reverse the results
                    elif command_part.contents == "!":
                        inverse = True
                        if last_command_part is not None and last_command_part.part_type == "operator" and last_command_part.contents in [")", "]", "!"]:
                            raise fnf_data.SearchError("NOT operators must not come directly after closing brackets/parentheses or other NOT operators.")
                    # parentheses can be used to change the order of operations
                    elif command_part.contents == "(":
                        self.delve_and_append(self.results, fnf_data.Argument_Container(self.command_type, inverse, merge, []), depth)
                        depth += 1
                        merge = False
                        inverse = False
                    elif command_part.contents == ")":
                        if last_command_part == "(":
                            raise fnf_data.SearchError("Parentheses must contain at least one argument.")
                        depth -= 1
                elif command_part.part_type == "argument":
                    result = fnf_data.Argument_Container(self.command_type, inverse, merge, [self.identify_command(command_part.contents)])
                    self.results = self.delve_and_append(self.results, result, depth)
                elif command_part.part_type == "subcommand":
                    # create a child command with the current argument
                    subcommand = self.create_child_command(command_part.contents)
                    # turns the subcommand results into an argument
                    if subcommand.command_type == "move":
                        result = fnf_data.Argument_Container(self.command_type, inverse, merge, [fnf_data.pokemon_has_move(subcommand.results)])
                        self.results = self.delve_and_append(self.results, result, depth)
                    elif subcommand.command_type == "ability":
                        result = fnf_data.Argument_Container(self.command_type, inverse, merge, [fnf_data.pokemon_has_ability(subcommand.results)])
                        self.results = self.delve_and_append(self.results, result, depth)
                    else:
                        raise fnf_data.SearchError(f"Invalid subcommand of type {subcommand.command_type}.", True)
                last_command_part = command_part
            self.results.combine()
            self.results = self.results.arguments[0]
            if self.random:
                self.results.data = [random.choice(self.results.data)]
            results_text = self.format_results()
            self.output = results_text
            self.success = True
            self.log_function_end()
            return
        except fnf_data.SearchError as e:
            return self.handle_search_error(e)
        except Exception as e:
            return self.create_and_send_error_log(e)

    def handle_search_error(self, e):
        if e.send_error_log:
            self.create_and_send_error_log(e)
        # sets the output to a description of the exception if this is the root command
        elif self is self.root_command:
            if debug_mode:
                self.create_and_send_error_log(e, True)
            else:
                self.output += e.description
                timelog("An exception was raised intentionally.")
        # otherwise, the exception is passed to the root command
        else:
            self.root_command.create_and_send_error_log(e)

    def create_and_send_error_log(self, e, debug_mode_error=False):
        # sets the output to a description of the exception if this is the root command
        if self is self.root_command:
            # debug_mode_error is True for errors caused by SearchError exceptions that were raised during testing mode.
            if debug_mode and debug_mode_error:
                text = "While debug mode was on, a SearchError was raised:"
            else:
                text = "An unhandled exception occurred:"
            text += "\n" + traceback.format_exc()
            text += "\nVariable states:"
            text += "\ncommand_type             : " + str(self.command_type)
            text += "\nanswer                   : " + str(self.answer)
            text += "\noperators                : " + str(self.operators)
            text += "\ncommand_parts            : " + str([str(part) for part in self.command_parts])
            text += "\nresults                  : " + str(self.results)
            text += "\nCall log:\n" + self.call_log
            if debug_mode and debug_mode_error:
                # debug_mode_error is True for errors caused by SearchError exceptions that were raised during testing mode.
                self.output = "DEBUG MODE IS ON - this exception will generate an error log despite being raised intentionally\n"
                self.output += e.description
                timelog("An exception was raised intentionally while in debug mode.")
            else:
                self.output = "An unhandled exception occurred and the command could not be executed. Information about this error is being logged so it can be prevented in the future."
                timelog("An exception went unhandled.")
            self.error_log = text
        # otherwise, the exception is passed to the root command
        else:
            self.root_command.create_and_send_error_log(e)


def fuse(pokemon1, pokemon2, learnset):
    pokemon1 = Command("pokemon name " + pokemon1)
    pokemon2 = Command("pokemon name " + pokemon2)
    pokemon1.run_command()
    pokemon2.run_command()
    if len(pokemon1.results.data) != 1 or len(pokemon2.results.data) != 1:
        return "Could not find one or both Pokemon."
    pokemon1 = pokemon1.results.data[0]
    pokemon2 = pokemon2.results.data[0]
    if pokemon1 is pokemon2:
        return "You can't fuse two identical Pokemon."
    alt_form = False
    if pokemon1.alt_form is not None or pokemon2.alt_form is not None:
        alt_form = True
    possible_types = []
    possible_abilities = set()
    for a in pokemon1.abilities + pokemon2.abilities:
        possible_abilities.add(a)
    if set(pokemon1.types) == set(pokemon2.types):
        possible_types.append(pokemon1.types)
    else:
        for t1 in pokemon1.types:
            for t2 in pokemon2.types:
                current_combo = [t1, t2]
                if t1 == t2:
                    continue
                add_flag = True
                for combo in possible_types:
                    if set(current_combo) == set(combo):
                        add_flag = False
                        break
                if add_flag:
                    possible_types.append(current_combo)
    stats = [(pokemon1.stats["HP"] + pokemon2.stats["HP"]) * 0.5,
             (pokemon1.stats["ATK"] + pokemon2.stats["ATK"]) * 0.5,
             (pokemon1.stats["DEF"] + pokemon2.stats["DEF"]) * 0.5,
             (pokemon1.stats["SPA"] + pokemon2.stats["SPA"]) * 0.5,
             (pokemon1.stats["SPD"] + pokemon2.stats["SPD"]) * 0.5,
             (pokemon1.stats["SPE"] + pokemon2.stats["SPE"]) * 0.5]
    bst = 0
    for i in stats:
        bst += i
    stats.append(bst)
    text = pokemon1.name + " + " + pokemon2.name
    for i, stat_name in enumerate(["HP", "ATK", "DEF", "SPA", "SPD", "SPE", "BST"]):
        text += "\n" + stat_name + (":  " if i == 0 else ": ") + str(stats[i])
    text += "\nPossible types: "
    for i in possible_types:
        if len(i) == 1:
            text += i[0].name + ", "
        else:
            text += i[0].name + "/" + i[1].name + ", "
    text = text[:-2]
    text += "\nPossible abilities: "
    for i in possible_abilities:
        text += i.name + ", "
    text = text[:-2]
    if learnset:
        text += "\nLearnset:"
        for i in sorted(set(pokemon1.moves + pokemon2.moves), key=lambda move: move.name.lower()):
            text += "\n" + i.to_string_one_line()
    return text

update_database()