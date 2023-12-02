from re import S
import fnf_data
import traceback
import random
import saurbot_functions
from hyphenate import hyphenate_word
POKEMON_SORT_METHODS = {"name": ["name"],
                        "dex": ["dex", "pokedex", "num", "number"],
                        "draft": ["draft", "draft tier"],
                        "ladder": ["ladder", "ladder tier", "tier"],
                        "hp": ["hp", "health", "health points", "hit points"],
                        "atk": ["attack", "atk"],
                        "def": ["defense", "def"],
                        "spa": ["special attack", "spa", "spatk", "sp. attack", "sp. atk"],
                        "spd": ["special defense", "spd", "spdef", "sp. defense", "sp. def"],
                        "spe": ["speed", "spe"],
                        "bst": ["bst", "base stat total", "base stat"],
                        "buff": ["buff"]}
MOVE_SORT_METHODS = {"name": ["name"],
                     "type": ["type"],
                     "pow": ["pow", "power"],
                     "cat": ["cat", "category"],
                     "acc": ["acc", "accuracy"],
                     "pp": ["pp", "power points"]}
ABILITY_SORT_METHODS = {"name": ["name"]}

debug_mode = False

class CommandPart:
    def __init__(self, part_type, contents, position):
        self.position = position
        self.part_type = part_type
        self.contents = contents
    def __str__(self):
        if self.part_type == "subcommand":
            return "[" + self.contents + "]"
        else:
            return self.contents

class Command:
    def __init__(self, command, filter_rules):
        self.filter_rules = filter_rules
        self.output = ""
        self.success = False
        self.error_log = None
        # for commands that call other commands, root command is the first command called.
        # used to ensure that each chained command writes logs in the same string
        self.root_command = self
        self.command = command
        # command_text is the version of the command that will be displayed to the user at the end
        self.command_text = "/pokedex " + self.command
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
        self.raw_results = []
        self.all_response_texts = []
        # if this is a subcommand, the subcommand position will be used for displaying error messages to the user
        self.subcommand_position = 0

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

    def create_child_command(self, command, filters, position):
        self.log_function_call("create_child_command")
        # creates a child command and sets its root_command
        child_command = Command(command, filters)
        child_command.subcommand_position = position
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


    def identify_command(self, pos, full_argument):
        argument = full_argument.lower().strip()
        data_list = None
        if self.command_type == "pokemon":
            data_list = fnf_data.pokemon
        elif self.command_type == "move":
            data_list = fnf_data.moves
        elif self.command_type == "ability":
            data_list = fnf_data.abilities
        self.log_function_call(f"identify_command (argument: {argument}, pos: {pos})")
        # when adding a new command, don't just mindlessly copy-paste the "for prefix in list" loop
        # it's important that the shorter items in the list are at the end
        # for example, for the argument "end saur", "end", "ends", "endswith", and "ends with" all are valid prefixes
        # we want to remove as much text as possible from the command, so start by checking the longer prefixes
        if saurbot_functions.only_a_to_z(argument) in data_list.aliases:
            return data_list.filter_name(pos, full_argument, argument.strip(), True)
        for prefix in ["name starts with", "name startswith", "name starts", "name start", "startswith", "starts with", "starts", "start"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_name_starts_with(pos, full_argument, argument.strip())
        for prefix in ["endswith", "ends with", "name ends with", "name endswith", "name ends", "name end", "ends", "end"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_name_ends_with(pos, full_argument, argument.strip())
        for prefix in ["includes", "include", "name includes", "name include"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_name_includes(pos, full_argument, argument.strip())
        for prefix in ["name"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_name(pos, full_argument, argument.strip())
        for prefix in ["tier", "ladder tier", "ladder"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_ladder(pos, full_argument, argument.strip())
        for prefix in ["draft tier", "draft"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_draft(pos, full_argument, argument.strip())
        for prefix in ["buffed", "buff", "changed", "change"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_buff(pos, full_argument, argument.strip())
        for prefix in ["nfe"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_nfe(pos, full_argument, argument.strip())
        for prefix in fnf_data.STAT_ALIASES["hp"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "hp")
        for prefix in fnf_data.STAT_ALIASES["atk"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "atk")
        for prefix in fnf_data.STAT_ALIASES["def"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "def")
        for prefix in fnf_data.STAT_ALIASES["spa"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "spa")
        for prefix in fnf_data.STAT_ALIASES["spd"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "spd")
        for prefix in fnf_data.STAT_ALIASES["spe"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "spe")
        for prefix in fnf_data.STAT_ALIASES["bst"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stat(pos, full_argument, argument.strip(), "bst")
        for prefix in ["pp", "power points"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_pp(pos, full_argument, argument.strip())
        for prefix in ["maxpp", "max power points", "max pp", "maximumpp", "maximum power points", "maximum pp"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_maxpp(pos, full_argument, argument.strip())
        for prefix in ["accuracy", "acc"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_accuracy(pos, full_argument, argument.strip())
        for prefix in ["power", "pow"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_power(pos, full_argument, argument.strip())
        for prefix in ["zpower", "z-power", "zpow", "z-pow"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_zpower(pos, full_argument, argument.strip())
        for prefix in ["priority"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_priority(pos, full_argument, argument.strip())
        for prefix in ["crit ratio", "critratio", "critrate", "crit rate", "critical ratio", "critical rate", "critical", "crit"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_crit_ratio(pos, full_argument, argument.strip())
        for prefix in ["traits", "flags", "trait", "flag"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_trait(pos, full_argument, argument.strip())
        for prefix in ["targets", "target"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_target(pos, full_argument, argument.strip())
        for prefix in ["type"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_type(pos, full_argument, argument.strip())
        for prefix in ["effectiveness", "vs", "matchup"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_effectiveness(pos, full_argument, argument.strip())
        for prefix in ["secondary chance", "effect chance", "secondary", "chance"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_secondary_chance(pos, full_argument, argument.strip())
        for prefix in ["stage", "stat change"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_stage(pos, full_argument, argument.strip())
        for prefix in ["status condition", "status", "condition"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                return data_list.filter_status(pos, full_argument, argument.strip())
        for prefix in ["learned by"]:
            if argument.startswith(prefix):
                argument = argument.removeprefix(prefix)
                new_gens = False
                if self.filter_rules["new gens"] != 0:
                    new_gens = True
                return data_list.filter_learned_by(pos, full_argument, argument.strip(), new_gens)
        if argument == "all":
            return data_list.filter_all()
        return data_list.filter_name(pos, full_argument, argument.strip(), True)

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
            command_number = 0
            for character in self.answer:
                if in_brackets:
                    if character == "]":
                        # close bracket signifies the end of a subcommand. the subcommand is added to the list and the string is reset
                        in_brackets = False
                        if len(current_argument.strip()):
                            command_number += 1
                            self.command_parts.append(CommandPart("subcommand", current_argument.strip(), command_number))
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
                            command_number += 1
                            self.command_parts.append(CommandPart("argument", current_argument.strip(), command_number))
                            current_argument = ""
                        self.command_parts.append(CommandPart("operator", character, 0))
                    else:
                        current_argument += character
            if len(current_argument.strip()):
                command_number += 1
                self.command_parts.append(CommandPart("argument", current_argument.strip(), command_number))
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
                    position = command_part.position
                    if self.subcommand_position != 0:
                        position = self.subcommand_position
                    argument_results, response_text = self.identify_command(position, command_part.contents)
                    self.all_response_texts += response_text
                    result = fnf_data.Argument_Container(self.command_type, inverse, merge, [argument_results])
                    self.results = self.delve_and_append(self.results, result, depth)
                elif command_part.part_type == "subcommand":
                    position = command_part.position
                    # currently subcommand_position should always be 0 here
                    if self.subcommand_position != 0:
                        position = self.subcommand_position
                    # create a child command with the current argument
                    subcommand = self.create_child_command(command_part.contents, self.filter_rules, position)
                    # turns the subcommand results into an argument
                    if subcommand.command_type == "move":
                        new_gens = False
                        if self.filter_rules["new gens"] != 0:
                            new_gens = True
                        argument_results, response_text = fnf_data.pokemon.filter_has_move(position, subcommand.results, new_gens)
                        self.all_response_texts += subcommand.all_response_texts
                        result = fnf_data.Argument_Container(self.command_type, inverse, merge, [argument_results])
                        self.results = self.delve_and_append(self.results, result, depth)
                    elif subcommand.command_type == "ability":
                        argument_results, response_text = fnf_data.pokemon.filter_has_ability(position, subcommand.results)
                        self.all_response_texts += subcommand.all_response_texts
                        result = fnf_data.Argument_Container(self.command_type, inverse, merge, [argument_results])
                        self.results = self.delve_and_append(self.results, result, depth)
                    else:
                        raise fnf_data.SearchError(f"Invalid subcommand of type {subcommand.command_type}.", True)
                last_command_part = command_part
            # this does all the combining logic and brings us to just one final list of results
            self.results.combine()
            self.results = self.results.arguments[0]
            '''
            for result in self.results.data:
                print(result.name)
                print(f"base form {result.filter_rule_base_forms}")
                print(f"hypnomons {result.filter_rule_hypnomons}")
                print(f"new gens  {result.filter_rule_new_gens}")
                print(f"ignored   {result.filter_rule_ignored}")
                print(f'check     {result.check_filter_rules(self.filter_rules["base forms"],self.filter_rules["hypnomons"],self.filter_rules["new gens"],self.filter_rules["ignored"])}')
            '''
            self.results = [result for result in self.results.data if result.check_filter_rules(self.filter_rules["base forms"],
                                                                                                self.filter_rules["hypnomons"],
                                                                                                self.filter_rules["new gens"],
                                                                                                self.filter_rules["ignored"])]
            if len(self.results) == 0:
                self.all_response_texts.append("No results found.")
            self.success = True
            self.log_function_end()
            return
        except fnf_data.SearchError as e:
            return self.handle_search_error(e)
        except Exception as e:
            return self.create_and_send_error_log(e)

    def get_message_text(self):
        text = self.command_text + "\n\n"
        for item in self.all_response_texts:
            text += item + "\n"
        if len(text) > 2000:
            text = text[:1997] + "..."
        return text

    def handle_search_error(self, e):
        if e.send_error_log:
            self.create_and_send_error_log(e)
        # sets the output to a description of the exception if this is the root command
        elif self is self.root_command:
            if debug_mode:
                self.create_and_send_error_log(e, True)
            else:
                self.output += e.description
                saurbot_functions.timelog("An exception was raised intentionally.")
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
                saurbot_functions.timelog("An exception was raised intentionally while in debug mode.")
            else:
                self.output = "An unhandled exception occurred and the command could not be executed. Information about this error is being logged so it can be prevented in the future."
                saurbot_functions.timelog("An exception went unhandled.")
            self.error_log = text
        # otherwise, the exception is passed to the root command
        else:
            self.root_command.create_and_send_error_log(e)

#HYPHEN_MONS = ["Ho-oh", "Jangmo-o", "Kakamo-o", "Kommo-o"]
def fuse(pokemon1, pokemon2):
    command_text = f"/pokedex fuse {pokemon1} {pokemon2}"
    pokemon1, score = fnf_data.pokemon.fuzzy_alias_search(pokemon1)
    pokemon2, score = fnf_data.pokemon.fuzzy_alias_search(pokemon2)
    if (pokemon1 is None or pokemon2 is None) or (pokemon1.filter_rule_unrevealed or pokemon2.filter_rule_unrevealed):
        return "Could not find one or both Pokemon."
    if pokemon1 is pokemon2:
        return "You can't fuse two identical Pokemon."
    name1 = hyphenate_word(pokemon1.base_species)
    name2 = hyphenate_word(pokemon2.base_species)
    if len(name1) == 1:
        start = name1[0]
    else:
        stop_syllable = random.randint(1, len(name1)-1)
        start = "".join(name1[:-stop_syllable])
    if len(name2) == 1:
        end = name2[0]
    else:
        start_syllable = random.randint(1, len(name2)-1)
        end = "".join(name2[start_syllable:])
    name = f"{start+end.lower()} ({pokemon1.name} + {pokemon2.name})"
    fusion = fnf_data.Fusion(name)
    possible_types = []
    possible_abilities = set()
    for a in pokemon1.get_ability_list() + pokemon2.get_ability_list():
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
    fusion.stats = {"HP": (pokemon1.stats["HP"] + pokemon2.stats["HP"]) * 0.5,
                    "ATK": (pokemon1.stats["ATK"] + pokemon2.stats["ATK"]) * 0.5,
                    "DEF": (pokemon1.stats["DEF"] + pokemon2.stats["DEF"]) * 0.5,
                    "SPA": (pokemon1.stats["SPA"] + pokemon2.stats["SPA"]) * 0.5,
                    "SPD": (pokemon1.stats["SPD"] + pokemon2.stats["SPD"]) * 0.5,
                    "SPE": (pokemon1.stats["SPE"] + pokemon2.stats["SPE"]) * 0.5,
                    "BST": (pokemon1.stats["BST"] + pokemon2.stats["BST"]) * 0.5}
    types_text = ""
    for i in possible_types:
        if len(i) == 1:
            types_text += i[0].name + ", "
        else:
            types_text += i[0].name + "-" + i[1].name + ", "
    fusion.possible_types = types_text.removesuffix(", ")
    ability_text = ""
    for i in possible_abilities:
        ability_text += i.name + ", "
    fusion.possible_abilities = ability_text.removesuffix(", ")
    embed_text = ""
    image_text = ""
    file_text = ""
    len_counter = 0
    for move in sorted(set(list(pokemon1.learnset.keys()) + list(pokemon2.learnset.keys())), key=lambda move: move.name.lower()):
        move_name = move.name
        if (pokemon1.learns_move(move, 7) or pokemon2.learns_move(move, 7)) == False:
            move_name = move_name + "*"
        image_text += move_name + ", "
        len_counter += len(move_name) + 2
        if len_counter > 72:
            move_name = "\n" + move_name
            len_counter = 0
        file_text += move_name + ", "
    fusion.text_learnset = file_text.strip().removesuffix(",")
    fusion.image_learnset = image_text.strip().removesuffix(",")
    fusion.embed_learnset = f"*/pokedex move filters: learned by {pokemon1.name} | learned by {pokemon2.name}*"
    fusion.color = pokemon1.color
    fusion.get_stats_text()
    return [command_text, fusion]