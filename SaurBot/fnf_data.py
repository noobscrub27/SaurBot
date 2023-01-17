import re

POKEMON_MAX_LENGTH = 23
MOVE_MAX_LENGTH = 30
ABILITY_MAX_LENGTH = 20
STAT_MAX_LENGTH = 30
TYPE_MAX_LENGTH = 12

NOT_VERY_EFFECTIVE_TEXT = ["0.5", "x0.5", "*0.5", "1/2", "x1/2", "*1/2"]
DOUBLE_NOT_VERY_EFFECTIVE_TEXT = ["0.25", "x0.25", "*0.25", "1/4", "x1/4", "*1/4"]
NOT_EFFECTIVE_TEXT = ["0", "x0", "*0"]
SUPER_EFFECTIVE_TEXT = ["2", "x2", "*2"]
DOUBLE_SUPER_EFFECTIVE_TEXT = ["4", "x4", "*4"]
NEUTRAL_EFFECTIVE_TEXT = ["1", "x1", "*1"]

EMPTY_SAMPLE = "There are no sample sets at this time. Perhaps you could be the first to make one!"

TIERS = {
    "BANNED": 0,
    "M1": -1,
    "M2": -2,
    "M3": -3,
    "1A": 1,
    "1B": 1.1,
    "2A": 2,
    "2B": 2.1,
    "3A": 3,
    "3B": 3.1,
    "4A": 4,
    "4B": 4.1,
    "5A": 5,
    "5B": 5.1,
    "BUFFED": 6
    }

types = {}
pokemon = {}
abilities = {}
moves = {}
page_learnsets = {}

def multiply_list(l):
    result = 1
    for i in l:
        result *= i
    return result

class Pokemon:
    def __init__(self, name = "none", types = [], abilities = [], pokedex = 0, tier = "", stats = [0,0,0,0,0,0,0], buffs = "", moves = [], changes = "N/A", sets = []):
        self.name = name
        self.types = types
        if len(self.types):
            self.matchups = [{pkmn_type: multiply_list([self_type.defensive[pkmn_type] for self_type in self.types])} for pkmn_type in self.types[0].defensive]
        else:
            self.matchups = []
        self.abilities = abilities
        self.pokedex = pokedex
        self.tier = tier.replace("MT", "M")
        self.stats = {
            'HP': stats[0],
            'ATK': stats[1],
            'DEF': stats[2],
            'SPA': stats[3],
            'SPD': stats[4],
            'SPE': stats[5],
            'BST': stats[6]}
        self.alt_stats = {
            'HP': None,
            'ATK': None,
            'DEF': None,
            'SPA': None,
            'SPD': None,
            'SPE': None,
            'BST': None}
        self.alt_form = None
        self.buff = buffs
        self.moves = moves
        self.notes = ""
        self.sample_sets = sets
        self.changes = changes

    def to_string(self):
        # name
        result = self.name
        # dex number
        result += " " + f'#{self.pokedex:5.1f}'.replace(".0", "").replace(" ", "0").replace("-", "-0").replace("0-", "-0")
        # types
        result += "\nTypes: "
        for i in self.types:
            result += i.name + '/'
        result = result[:-1]
        # abilities
        result += "\nAbilities: "
        for i in self.abilities:
            result += i.name + ', '
        result = result[:-2]
        # stats
        result += "\n"
        for i in self.stats:
            if i != "BST":
                result += i + ": " + str(self.stats[i]) + ", "
        result = result[:-2] + "\nBST: " + str(self.stats["BST"])
        # notes
        if self.notes:
            result += "\n" + self.notes
        # matchups
        result += "\nType matchups:"
        mu_numbers = [4, 2, 1, 0.5, 0.25, 0]
        for num in mu_numbers:
            mu_list = [list(mu.keys())[0].name for mu in self.matchups if list(mu.values())[0] == num]
            if mu_list:
                result += "\n\tDamage x" + str(num) + (" " * (4 - len(str(num)))) + ": "
                for mu in mu_list:
                    result += (mu + ", ") if mu not in ["Shadow", "Typeless"] else ""
            if result [-2:] == ", ":
                result = result[:-2]
        # tier
        result += "\nTier: " + self.tier
        # buff
        if self.buff:
            result += "\nBuff: " + str(self.buff)
        # changes
        if self.changes != "N/A":
            result += "\nChanges:\n" + self.changes
        result += "\n\nRelated commands:"
        result += "\nView learnset: \"/learnset " + self.name + "\""
        result += "\nView sample sets: \"/sets " + self.name + "\""
        return result

    def to_string_moves(self):
        result = ""
        for i in self.moves:
            result += i.to_string_one_line() + "\n"
        return result[:-1]

    def to_string_sample_sets(self):
        result = ""
        if len(self.sample_sets):
            for i in self.sample_sets:
                result += i.to_string() + "\n"
        else:
            result += EMPTY_SAMPLE
        return result.strip()

    def to_string_one_line(self):
        # dex number
        result = "#"
        pokedex_string = f'{self.pokedex:5.1f}'.replace(".0", "").replace(" ", "0").replace("-", "-0").replace("0-", "-0")
        result += pokedex_string + (" " * (7 - len(pokedex_string)))
        # tier
        result += self.tier + (" " * (8 - len(self.tier)))
        # name
        result += self.name
        result += (" " * (POKEMON_MAX_LENGTH - len(self.name)))
        # types
        len_types = 0
        for i in self.types:
            len_types += len(i.name) + 1
            result += i.name + "/"
        result = result[:-1]
        len_types -= 1
        result += (" " * (TYPE_MAX_LENGTH * 2 - len_types))
        # abilities
        len_abilities = 0
        for i in self.abilities:
            len_abilities += len(i.name) + 2
            result += i.name + ", "
        result = result[:-2]
        len_abilities -= 2
        result += (" " * (ABILITY_MAX_LENGTH * 3 - len_abilities))
        # stats
        result += "("
        for i in self.stats:
            if i != "BST":
                if self.stats[i] < 10:
                    result += "00"
                elif self.stats[i] < 100:
                    result += "0"
                result += str(self.stats[i]) + "/"
        result = result[:-1] + ")"
        if self.alt_form:
            result += "* "
        else:
            result += "  "
        result += "BST: "
        result += str(self.stats['BST'])
        result += ("\n*" + self.notes) if self.notes else ""
        return result


class Move:
    def __init__(self, name = "", pkmn_type = None, category = "Status", power = 0, accuracy = 0, pp = 0, description = 0, buff = 0):
        self.name = name
        self.type = pkmn_type
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.pp = pp
        self.max_pp = int(pp * 8/5) if pp >= 5 else pp
        self.description = description

    def to_string(self):
        return self.to_string_one_line() + "\n" + self.description

    def to_string_one_line(self):
        # name
        result = self.name + (" " * (MOVE_MAX_LENGTH - len(self.name)))
        # type
        result += self.type.name + (" " * (TYPE_MAX_LENGTH - len(self.type.name)))
        # category
        result += "CAT: " + self.category + (" " * (12 - len(self.category)))
        # power
        result += "POW: " + str(self.power) + (" " * (7 - len(str(self.power))))
        # accuracy
        result += "ACC: " + str(self.accuracy) + "%" + (" " * (7 - len(str(self.accuracy))))
        # PP
        result += "PP: " + str(self.pp)
        result += " " if self.pp < 10 else ""
        result += " (max: " + str(self.max_pp) + ")"

        return result

class Ability:
    def __init__(self, name = "", description = ""):
        self.name = name
        self.description = description

    def to_string_one_line(self):
        return self.name + ":" + (" " * (ABILITY_MAX_LENGTH - len(self.name))) + self.description

    def to_string(self):
        return self.to_string_one_line()

class Type:
    def __init__(self, name = ""):
        self.name = name
        self.defensive = {}
        self.offensive = {}

class Sample_Set:
    def __init__(self, sample_set = "", description = ""):
        self.sample_set = re.sub("\n+", "\n", re.sub(" +", " ", sample_set.strip()))
        self.description = re.sub("\n+", "\n", re.sub(" +", " ", description.strip()))

    def to_string(self):
        return (self.sample_set + "\n" + self.description)

# This class contains one or more Arguments.
# It is responsible for keeping track of how the contained Arguments should be combined with other Arguments
# It keeps track of whether it use an AND or OR operator, as well as whether to use a NOT operator
# If parenetheses were used, it will hold other Argument_Containers.
class Argument_Container:
    def __init__(self, command_type, inverse, merge, arguments=None):
        self.command_type = command_type
        # if inverse is true, True and False are flipped
        self.inverse = inverse
        # if merge is true, this argument will merge with the argument behind it (caused by OR)
        self.merge = merge
        self.arguments = arguments or []
        # when self.analyzed is true, it means that there is no more work to be done on self.arguments
        # all of the arguments have been condensed into a single Argument object
        # at this point, it's safe to replace the Argument_Container object with the argument it contains
        self.analyzed = False
    def combine(self):
        while self.analyzed == False:
            # there will always be at least 1 argument in self.arguments
            try:
                arg_1 = self.arguments[0]
            except IndexError:
                raise SearchError("IndexError occurred while combining arguments. No arguments were found while at least one was expected.", True)
            # if there is more than one argument, that means that they still need to be combined
            if len(self.arguments) > 1:
                # this code ensures that the first 2 arguments are ready to be combined. If they aren't, it preps them to be combined.
                if arg_1.analyzed == False:
                    arg_1.combine()
                    continue
                arg_2 = self.arguments[1]
                if arg_2.analyzed == False:
                    arg_2.combine()
                    continue
                # now that the first two arguments are combined, it's time to merge them
                if arg_1.command_type != arg_2.command_type:
                    # this should never happen... I think
                    raise SearchError("Cannot combine arguments with non-matching command types.", True)
                if self.command_type == "ability":
                    lst = abilities.values()
                elif self.command_type == "move":
                    lst = moves.values()
                elif self.command_type == "pokemon":
                    lst = pokemon.values()
                arg_1_argument, arg_2_argument = arg_1.arguments[0], arg_2.arguments[0]
                if arg_2.merge:
                    data = [val for val in lst if (val in arg_1_argument.data) or (val in arg_2_argument.data)]
                    inverse_data = [val for val in lst if (val in arg_1_argument.inverse_data) and (val in arg_2_argument.inverse_data)]
                else:
                    data = [val for val in lst if (val in arg_1_argument.data) and (val in arg_2_argument.data)]
                    inverse_data = [val for val in lst if (val in arg_1_argument.inverse_data) or (val in arg_2_argument.inverse_data)]
                arg_1.arguments[0].data = data
                arg_1.arguments[0].inverse_data = inverse_data
                # after merging everything into arg_1, arg_2 is no longer needed
                del self.arguments[1]
            # if the contained argument is an Argument and not an Argument_Container, the Argument_Container is ready to be combined by its parent
            elif type(arg_1) is Argument:
                if self.inverse:
                    arg_1.inverse()
                self.analyzed = True
            else:
                if arg_1.analyzed:
                    # this if statement takes care of parentheses
                    # if there's only one Argument_Container in self.arguments, and it is analyzed, take its Argument
                    # do not take it's merge value
                    self.arguments = arg_1.arguments
                else:
                    arg_1.combine()

# this contains the results of a single argument in a list.
# after the whole command has been parsed, it is combined with the other arguments until just one argument remains
class Argument:
    def __init__(self, command_type, keyword, argument, data, inverse_data = None):
        self.command_type = command_type
        self.keyword = keyword
        self.argument = argument
        self.data = data
        # inverse_data is used instead of taking the reverse of data for specific scenarios
        # for example, the inverse of the move vs keyword still excludes status moves
        self.inverse_data = inverse_data
        if self.inverse_data is None:
            if self.command_type == "ability":
                lst = abilities.values()
            elif self.command_type == "move":
                lst = moves.values()
            elif self.command_type == "pokemon":
                lst = pokemon.values()
            self.inverse_data = [val for val in lst if val not in self.data]
    def inverse(self):
        temp = self.data
        self.data = self.inverse_data
        self.inverse_data = temp


class SearchError(Exception):
    def __init__(self, description = "An unknown error occurred", send_error_log=False):
        self.description = description
        self.send_error_log = send_error_log

def determine_comparison(keyword, command):
    if command.startswith("=="):
        comparison_operator = "=="
    elif command.startswith("="):
        comparison_operator = "="
    elif command.startswith(">="):
        comparison_operator = ">="
    elif command.startswith("<="):
        comparison_operator = "<="
    elif command.startswith(">"):
        comparison_operator = ">"
    elif command.startswith("<"):
        comparison_operator = "<"
    else:
        raise SearchError(f"Expected comparison operator in {keyword} argument.")
    value = command.removeprefix(comparison_operator).strip()
    if comparison_operator in ["==", "="]:
        lambda_func = lambda val, data: data == val
    elif comparison_operator == ">=":
        lambda_func = lambda val, data: data >= val
    elif comparison_operator == "<=":
        lambda_func = lambda val, data: data <= val
    elif comparison_operator == ">":
        lambda_func = lambda val, data: data > val
    elif comparison_operator == "<":
        lambda_func = lambda val, data: data < val
    return value, lambda_func, comparison_operator

def check_float(keyword, value):
    try:
        return float(value)
    except ValueError:
        raise SearchError(f"Expected a number in the {keyword} argument.")

def check_efficacy(keyword, value):
    if value not in NOT_VERY_EFFECTIVE_TEXT + DOUBLE_NOT_VERY_EFFECTIVE_TEXT + NOT_EFFECTIVE_TEXT + SUPER_EFFECTIVE_TEXT + DOUBLE_SUPER_EFFECTIVE_TEXT + NEUTRAL_EFFECTIVE_TEXT:
        check_float(keyword, value)

def check_tier(keyword, value):
    if value.upper() not in TIERS.keys():
        raise SearchError(f"Expected a tier in the {keyword} argument.")


# abilities
def ability_start(argument):
    results = [abilities[ability] for ability in abilities if abilities[ability].name.lower().startswith(argument)]
    return Argument("ability", "start", argument, results)

def ability_end(argument):
    results = [abilities[ability] for ability in abilities if abilities[ability].name.lower().endswith(argument)]
    return Argument("ability", "end", argument, results)

def ability_include(argument):
    results = [abilities[ability] for ability in abilities if argument in abilities[ability].name.lower()]
    return Argument("ability", "include", argument, results)


def ability_name(argument):
    results = [abilities[ability] for ability in abilities if argument == abilities[ability].name.lower()]
    return Argument("ability", "name", argument, results)

def ability_all():
    # deepcopying just in case
    results = [abilities[ability] for ability in abilities]
    return Argument("ability", "all", "", results)


# moves
def move_start(argument):
    results = [moves[move] for move in moves if moves[move].name.lower().startswith(argument)]
    return Argument("move", "start", argument, results)

def move_end(argument):
    results = [moves[move] for move in moves if moves[move].name.lower().endswith(argument)]
    return Argument("move", "end", argument, results)

def move_include(argument):
    results = [moves[move] for move in moves if argument in moves[move].name.lower()]
    return Argument("move", "include", argument, results)

def move_name(argument):
    results = [moves[move] for move in moves if argument == moves[move].name.lower()]
    return Argument("move", "name", argument, results)

def move_pp(argument):
    value, comparison_function, comparison_operator = determine_comparison("pp", argument)
    value = check_float("pp", value)
    results = [moves[move] for move in moves if comparison_function(value, moves[move].pp)]
    return Argument("move", "pp", argument, results)

def move_maxpp(argument):
    value, comparison_function, comparison_operator = determine_comparison("maxpp", argument)
    value = check_float("maxpp", value)
    results = [moves[move] for move in moves if comparison_function(value, moves[move].max_pp)]
    return Argument("move", "maxpp", argument, results)

def move_accuracy(argument):
    value, comparison_function, comparison_operator = determine_comparison("pp", argument)
    value = check_float("accuracy", value)
    results = [moves[move] for move in moves if (comparison_function(value, moves[move].accuracy) if (isinstance(moves[move].accuracy, int) or isinstance(moves[move].accuracy, float)) else comparison_function(value, 100))]
    return Argument("move", "accuracy", argument, results)

def move_power(argument):
    value, comparison_function, comparison_operator = determine_comparison("power", argument)
    value = check_float("power", value)
    results = [moves[move] for move in moves if (comparison_function(value, moves[move].power) if isinstance(moves[move].power, int) else comparison_function(value, 0))]
    return Argument("move", "power", argument, results)

def move_category(argument):
    if argument not in ["physical", "special", "status"]:
        raise SearchError(f"Could not parse category argument.")
    results = [moves[move] for move in moves if (argument == moves[move].category.lower())]
    return Argument("move", "category", argument, results)

def move_type(argument):
    results = [moves[move] for move in moves if (argument == moves[move].type.name.lower())]
    return Argument("move", "type", argument, results)

def move_efficacy(pkmn_types, argument):
    value, comparison_function, comparison_operator = determine_comparison("vs", argument)
    check_efficacy("vs", value)
    value = str(value)
    if value in NOT_VERY_EFFECTIVE_TEXT:
        value = 0.5
    elif value in DOUBLE_NOT_VERY_EFFECTIVE_TEXT:
        value = 0.25
    elif value in SUPER_EFFECTIVE_TEXT:
        value = 2
    elif value in DOUBLE_SUPER_EFFECTIVE_TEXT:
        value = 4
    elif value in NOT_EFFECTIVE_TEXT:
        value = 0
    elif value in NEUTRAL_EFFECTIVE_TEXT:
        value = 1
    else:
        value = float(value)
    results = [moves[move] for move in moves if (comparison_function(value, moves[move].type.offensive[pkmn_types[0]] * moves[move].type.offensive[pkmn_types[1]]) and moves[move].category != "Status")]
    inverse_results = [moves[move] for move in moves if (comparison_function(value, moves[move].type.offensive[pkmn_types[0]] * moves[move].type.offensive[pkmn_types[1]]) == False and moves[move].category != "Status")]
    return Argument("move", "vs", argument, results, inverse_results)

def move_all():
    # deepcopying just in case
    results = [moves[move] for move in moves]
    return Argument("move", "all", "", results)


# pokemon
def pokemon_start(argument):
    results = [pokemon[mon] for mon in pokemon if pokemon[mon].name.lower().startswith(argument)]
    return Argument("pokemon", "start", argument, results)

def pokemon_end(argument):
    results = [pokemon[mon] for mon in pokemon if pokemon[mon].name.lower().endswith(argument)]
    return Argument("pokemon", "end", argument, results)

def pokemon_include(argument):
    results = [pokemon[mon] for mon in pokemon if argument in pokemon[mon].name.lower()]
    return Argument("pokemon", "include", argument, results)

def pokemon_name(argument):
    results = [pokemon[mon] for mon in pokemon if argument == pokemon[mon].name.lower()]
    return Argument("pokemon", "name", argument, results)

def pokemon_pokedex(argument):
    value, comparison_function, comparison_operator = determine_comparison("pokedex", argument)
    value = check_float("pokedex", value)
    results = [pokemon[mon] for mon in pokemon if comparison_function(value, pokemon[mon].pokedex)]
    return Argument("pokemon", "pokedex", argument, results)

def pokemon_tier(argument):
    tier, comparison_function, comparison_operator = determine_comparison("tier", argument)
    check_tier("tier", tier)
    tier = TIERS[tier.upper()]
    if tier == 0:
        # if banned
        if comparison_operator == "==":
            results = [pokemon[mon] for mon in pokemon if pokemon[mon].tier.lower() == "banned"]
        elif comparison_operator == ">=":
            results = [pokemon[mon] for mon in pokemon if pokemon[mon].tier.lower() == "banned"]
        elif comparison_operator == "<=":
            results = [pokemon[mon] for mon in pokemon]
        elif comparison_operator == ">":
            results = []
        elif comparison_operator == "<":
            results = [pokemon[mon] for mon in pokemon if pokemon[mon].tier.lower() != "banned"]
    elif tier > 0:
        results = [pokemon[mon] for mon in pokemon if (comparison_function((-tier), (-TIERS[pokemon[mon].tier.upper()])) if ("M" not in pokemon[mon].tier.upper()) else False)]
    else:
        results = [pokemon[mon] for mon in pokemon if (comparison_function(tier, TIERS[pokemon[mon].tier.upper()]) if ("M" in pokemon[mon].tier.upper()) else False)]
    return Argument("pokemon", "tier", argument, results)

def pokemon_buff():
    results = [pokemon[mon] for mon in pokemon if pokemon[mon].buff]
    return Argument("pokemon", "buff", "", results)

def pokemon_stat(stat, argument):
    value, comparison_function, comparison_operator = determine_comparison(stat, argument)
    value = check_float(stat, value)
    results = [pokemon[mon] for mon in pokemon if (comparison_function(value, pokemon[mon].stats[stat]) or (comparison_function(value, pokemon[mon].alt_stats[stat]) if pokemon[mon].alt_form else False))]
    return Argument("pokemon", stat, argument, results)

def pokemon_type(argument):
    results = [pokemon[mon] for mon in pokemon if (argument in [t.name.lower() for t in pokemon[mon].types])]
    return Argument("pokemon", "type", argument, results)

def pokemon_efficacy(pkmn_type, argument):
    value, comparison_function, comparison_operator = determine_comparison("vs", argument.replace(" ", ""))
    check_efficacy("vs", value)
    value = str(value)
    if value in NOT_VERY_EFFECTIVE_TEXT:
        value = 0.5
    elif value in SUPER_EFFECTIVE_TEXT:
        value = 2
    elif value in NOT_EFFECTIVE_TEXT:
        value = 0
    elif value in NEUTRAL_EFFECTIVE_TEXT:
        value = 1
    elif value in DOUBLE_NOT_VERY_EFFECTIVE_TEXT:
        value = 0.25
    elif value in DOUBLE_SUPER_EFFECTIVE_TEXT:
        value = 4
    else:
        value = float(value)
    results = [pokemon[mon] for mon in pokemon if (comparison_function(value, multiply_list([t.defensive[pkmn_type] for t in pokemon[mon].types])))]
    return Argument("pokemon", "vs", argument, results)

def pokemon_all():
    # deepcopying just in case
    results = [pokemon[mon] for mon in pokemon]
    return Argument("pokemon", "all", "", results)

def pokemon_has_move(move_argument):
    results = [pokemon[mon] for mon in pokemon if len([move for move in pokemon[mon].moves if move in move_argument.data])]
    return Argument("pokemon", "move", "", results)

def pokemon_has_ability(ability_argument):
    results = [pokemon[mon] for mon in pokemon if len([ability for ability in pokemon[mon].abilities if ability in ability_argument.data])]
    return Argument("pokemon", "ability", "", results)


def compare_learnsets(command):
    command = command.strip().split(",")
    command_len = len(command)
    if command_len > 12 or command_len < 2:
        raise SearchError("Expected two to twelve unique pokemon names separated by commas.")
    command_len = len(command)
    pokemon_list = []
    for i in command:
        pokemon_list.append([pokemon[mon] for mon in pokemon if i.strip() == pokemon[mon].name.lower()])
    # remove empty lists (created when a pokemon is not recognized)
    try:
        pokemon_list.remove([])
    except ValueError:
        pass
    # flatten
    pokemon_list = list(set([item for sublist in pokemon_list for item in sublist]))
    # check if the command is still valid
    if len(pokemon_list) < 2:
        raise SearchError("Not enough unique pokemon names were recognized to compare movesets.")
    elif len(pokemon_list) != command_len:
        output_text = "INFO: At least one pokemon name was not recognized and will be excluded from the comparison.\n"
    else:
        output_text = ""
    # a list of all the moves pokemon in pokemon_list can learn
    all_moves = list(set([item for sublist in [mon.moves for mon in pokemon_list] for item in sublist]))
    all_moves = sorted(all_moves, key=lambda move: move.name.lower())
    # create the output
    output_text += "Move name" + (" " * (MOVE_MAX_LENGTH - 9))
    for mon in pokemon_list:
        output_text += mon.name + (" " * (POKEMON_MAX_LENGTH - len(mon.name)))
    output_text += "\n"
    for move in all_moves:
        output_text += move.name + (" " * (MOVE_MAX_LENGTH - len(move.name)))
        for mon in pokemon_list:
            if move in mon.moves:
                output_text += "LEARNS"
            else:
                output_text += "      "
            output_text += " " * (POKEMON_MAX_LENGTH - 6)
        output_text += "\n"
    return output_text[:-1]

def find_one_pokemon(command):
    command = command.strip()
    pokemon_list = [pokemon[mon] for mon in pokemon if command == pokemon[mon].name.lower()]
    if len(pokemon_list) == 1:
        return pokemon_list[0]
    else:
        raise SearchError("Could not recognize that Pokemon name.")