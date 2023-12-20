from thefuzz import process
from PIL import Image, ImageFont, ImageDraw
import re
import os
import textwrap
import discord
from discord.ext import commands
import saurbot_functions
import math
from io import BytesIO
import random

SAURBOT_QUOTES = ["It's me!", "You're searching for me? Hello!", "Are you thinking of adding me to your team?", "I'll help with analysis and strategy, even if it's used against me.", "My stats are pretty good, huh?"]

# these are defined on startup, but they are defined in other files
NOEL_ID = None
DEV_ID = None
FRONT_SPRITES_URL = ""
FRONT_SHINY_SPRITES_URL = ""
BACK_SPRITES_URL = ""
BACK_SHINY_SPRITES_URL = ""
DEX_SPRITES_URL = ""
DEX_SHINY_SPRITES_URL = ""

MOBILE_IMAGE_WARNING = "Full results not shown. To see the rest, use a different view mode."

commands_locked = False
currently_updating = False

active_command_views = []

longest_pokemon_name = 0
longest_ability_name = 0
longest_move_name = 0

POKEMON_MAX_LENGTH = 23
MOVE_MAX_LENGTH = 30
ABILITY_MAX_LENGTH = 20
STAT_MAX_LENGTH = 30
TYPE_MAX_LENGTH = 12

guild_preferences = {}
# user_tutorial_state isn't used anymore
user_tutorial_state = {}
user_mkw_fc = {}

sprite_list = []
ignore_forms = ["Pokestar Giant-PropO1", "Pokestar Giant-PropO2", "Pokestar UFO-PropU1", "Hypno-Happyf"]
dex_forms = ["Vivillon-Archipelago", "Vivillon-Continental", "Vivillon-Archipelago", "Vivillon-Elegant", "Vivillon-Garden", "Vivillon-High Plains", "Vivillon-Icy Snow", "Vivillon-Jungle", "Vivillon-Marine", "Vivillon-Modern", "Vivillon-Monsoon", "Vivillon-Ocean", "Vivillon-Polar", "Vivillon-River", "Vivillon-Sandstorm", "Vivillon-Savanna", "Vivillon-Sun", "Vivillon-Tundra", "Furfrou-Dandy", "Furfrou-Debutante", "Furfrou-Diamond", "Furfrou-Heart", "Furfrou-Kabuki", "Furfrou-La Reine", "Furfrou-Matron", "Furfrou-Pharaoh", "Furfrou-Star", "Unown-Exclamation", "Unown-Question"]

POKEDEX_COLORS = {"red": "#e60033",
                  "blue": "#0095d9",
                  "yellow": "#ffd900",
                  "green": "#3eb370",
                  "black": "#2b2b2b",
                  "brown": "#965042",
                  "purple": "#884898",
                  "gray": "#7d7d7d",
                  "grey": "#7d7d7d",
                  "white": "#ffffff",
                  "pink": "#e38698"
                  }

# size: [rows, chars]

FONT_SIZES = {36: [27, 91],
              48: [22, 68],
              60: [18, 54],
              72: [15, 45]}

NOT_VERY_EFFECTIVE_TEXT = ["0.5", "x0.5", "*0.5", "1/2", "x1/2", "*1/2"]
DOUBLE_NOT_VERY_EFFECTIVE_TEXT = ["0.25", "x0.25", "*0.25", "1/4", "x1/4", "*1/4"]
NOT_EFFECTIVE_TEXT = ["0", "x0", "*0"]
SUPER_EFFECTIVE_TEXT = ["2", "x2", "*2"]
DOUBLE_SUPER_EFFECTIVE_TEXT = ["4", "x4", "*4"]
NEUTRAL_EFFECTIVE_TEXT = ["1", "x1", "*1"]

EMPTY_SAMPLE = "There are no sample sets at this time. Perhaps you could be the first to make one!"

STAT_ALIASES = {"hp": ["hp", "hit points", "health points", "health"],
                "atk": ["attack", "atk"],
                "def": ["defense", "def"],
                "spa": ["special attack", "sp. attack", "spattack", "sp.attack", "sp.atk", "spatk", "sp atk", "sp. atk", "spa"],
                "spd": ["special defense", "sp. defense", "spdefense", "sp.defense", "sp.def", "spdef", "sp def", "sp. def", "spd"],
                "spe": ["speed", "spe"],
                "evasion": ["evasion", "evasiveness", "eva"],
                "accuracy": ["accuracy", "acc"],
                "bst": ["bst", "base stat total", "total"]}

STATUS_ALIASES = {"brn": ["brn", "burn", "burned"],
                  "psn": ["psn", "poison", "poisoned"],
                  "tox": ["tox", "toxic poison", "toxic", "toxic poisoned", "badly poisoned", "toxic poison", "bad poison"],
                  "frz": ["frz", "freeze", "frozen", "frostbite", "frostbitten"],
                  "slp": ["slp", "sleep", "asleep", "sleeping", "mimir", "eepy"], 
                  "par": ["par", "paralysis", "paralyze", "paralyzed"]
                  }

# these lists are automatically updated along with the database
move_flags = ["authentic", "bite", "blade", "bone", "bullet", "charge", "contact", "dance", "defrost", "distance", "gravity", "heal", "kick", "nonsky", "powder", "protect", "pulse", "punch", "recharge", "reflectable", "snatch", "sound"]
move_targets = {"any": "Any",
                "all": "All",
                "adjacentAlly": "Adjacent ally",
                "allySide": "Ally side",
                "normal": "Normal",
                "scripted": "Special",
                "adjacentAllyOrSelf": "Self or adjacent ally",
                "foeSide": "Opposing side",
                "allyTeam": "Ally team",
                "allies": "Allies",
                "self": "Self",
                "allAdjacent": "All adjacent",
                "adjacentFoe": "Adjacent opponent",
                "allAdjacentFoes": "All adjacent opponents",
                "randomNormal": "Random"}
move_volatile_statuses = ['octolock', 'partiallytrapped', 'roost', 'laserfocus', 'foresight', 'protect', 'miracleeye', 'leechseed', 'curse', 'followme', 'ingrain', 'noretreat', 'powder', 'torment', 'destinybond', 'lockedmove', 'embargo', 'substitute', 'disable', 'focusenergy', 'aquaring', 'helpinghand', 'imprison', 'attract', 'charge', 'encore', 'bide', 'endure', 'minimize', 'powertrick', 'spikyshield', 'rage', 'nightmare', 'tarshot', 'taunt', 'uproar', 'gastroacid', 'ragepowder', 'obstruct', 'magnetrise', 'magiccoat', 'snatch', 'kingsshield', 'spotlight', 'smackdown', 'banefulbunker', 'healblock', 'flinch', 'yawn', 'mustrecharge', 'confusion', 'grudge', 'stockpile', 'telekinesis', 'throatchop', 'electrify', 'defensecurl']

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


# draft tiers for sorting
SORT_TIERS = {
    "BANNED": 0,
    "M1": 0.1,
    "M2": 0.2,
    "M3": 0.3,
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

LADDER_TIERS = {
    "UBERS": 0,
    "UBER": 0,
    "OU": 1,
    "UUBL": 1.5,
    "UU": 2,
    "RUBL": 2.5,
    "RU": 3,
    "NUBL": 3.5,
    "NU": 4,
    "PUBL": 4.5,
    "PU": 5,
    "ZUBL": 5.5,
    "ZU": 6,
    "NFE": 7,
    "LC": 8,
    "UNTIERED": 9}

class MoveEffect:
    def __init__(self, name, targets_self, chance, details, description):
        self.name = name
        self.targets_self = targets_self
        self.chance = chance
        self.details = details
        self.description = description
    def get_text_suffix(self):
        if self.targets_self:
            text = "Affects move user."
        else:
            text = "Affects move target."
        if self.chance != 100:
            text += f" {self.chance}% chance to occur."
        return text

    def __str__(self):
        return f"{self.name}: {self.description} " + self.get_text_suffix()
            

class BoostEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Boosts", targets_self, chance, details, "")
    def __str__(self):
        text = "Stat changes: "
        for stat in self.details:
            value = f"+{self.details[stat]}" if self.details[stat] > 0 else str(self.details[stat])
            text += f"{STAT_ALIASES[stat][0]}: {value}, "
        text = text.removesuffix(", ")
        return text + ". " + self.get_text_suffix()

class ZBoostEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Z-Boosts", targets_self, chance, details, "")
    def __str__(self):
        text = "Provides the following stat changes when powered up by a z-crystal: "
        for stat in self.details:
            value = f"+{self.details[stat]}" if self.details[stat] > 0 else str(self.details[stat])
            text += f"{STAT_ALIASES[stat][0]}: {value}, "
        text = text.removesuffix(", ")
        return text + ". " + self.get_text_suffix()    

class VolatileStatusEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Volatile Status", targets_self, chance, details, "")
    def __str__(self):
        if len(self.details) == 1:
            text = f"Inflicts {self.details[0]}. "
        else:
            text = "Inflicts the following volatile statuses: "
            for status in self.details:
                text += status + ", "
            text = text.removesuffix(", ") + ". "
        return text + self.get_text_suffix()

class NonvolatileStatusEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Nonvolatile Status", targets_self, chance, details, "")
    def __str__(self):
        text = f"Inflicts {STATUS_ALIASES[self.details][1]}. "
        return text + self.get_text_suffix()
    
class RecoilEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Recoil", targets_self, chance, details, "")
    def __str__(self):
        text = f"The user takes recoil damage equal to {self.details:.1f}% of the damage dealt. "
        return text + self.get_text_suffix()

class ZEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Z-Effect", targets_self, chance, details, "")
    def __str__(self):
        text = f"Has the following effect when powered up by a z-crystal: {self.details}. "
        return text + self.get_text_suffix()

class RandomStatusEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Random Status", targets_self, chance, details, "")
    def __str__(self):
        text = "Inflicts one of the following statuses: "
        for status in self.details:
            text += f"{STATUS_ALIASES[status][1]}, "
        text = text.removesuffix(", ")
        return text + ". " + self.get_text_suffix()

class CureStatusEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Cure Status", targets_self, chance, details, "")
    def __str__(self):
        if len(self.details["effects"]) == 1:
            text = "Cures {self.details[0]}. "
        else:
            text = "Cures the following statuses: "
            for status in self.details:
                text += status + ", "
            text = text.removesuffix(", ") + ". "
        return text + self.get_text_suffix()

class FieldEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("Field Effect", targets_self, chance, details, "")
    def __str__(self):
        if len(self.details) == 1:
            text = "Sets {self.details}. "
        else:
            text = "Cures the following field effects: "
            for effect in self.details:
                text += effect + ", "
            text = text.removesuffix(", ") + ". "
        return text + self.get_text_suffix()

class PPChangeEffect(MoveEffect):
    def __init__(self, targets_self, chance, details):
        super().__init__("PP Change", targets_self, chance, details, "")
    def __str__(self):
        if self.details > 0:
            text = "Increases "
        else:
            text = "Decreases "
        text += f"the PP of the last used move by {self.details}. "
        return text + self.get_text_suffix()

def create_response_text(filter_name, pos, severity_type, text):
    return f"[{severity_type.upper()}] Ignoring {filter_name} filter at position {pos}: {text}"

def padding(text, total_chars, padding_char=" ", left_padding=False):
    text_len = len(text)
    if text_len >= total_chars:
        return text
    padding = padding_char * (total_chars - text_len)
    if left_padding:
        return padding + text
    return text + padding

types = {}
class Type:
    def __init__(self, name = ""):
        self.name = name
        self.defensive = {}
        self.offensive = {}

class DexDict(dict):
    data_type_str = ""

    def __init__(self, base_dict=None):
        super().__init__()
        # key will be a common name of a pokemon/move/ability
        # value will be the key used in the actual dictionary, aka internal_name
        self.aliases = {}
        if type(base_dict) is dict:
            for key in base_dict:
                self[key] = base_dict[key]

    def create_aliases(self):
        for key in self:
            for alias in self[key].aliases:
                if alias not in self.aliases:
                    self.aliases[alias] = key
                else:
                    if self.aliases[alias] != key:
                        print(f"WARNING: {alias} is an alias for multiple keys")

    def all_finish_setup(self):
        for item in self.values():
            item.create_text_values()
                  
    # takes the name of a pokemon/move/ability, returns the value of the DexDict
    def alias_search(self, name):
        return self[self.aliases[saurbot_functions.only_a_to_z(name)]]

    # takes the name of a pokemon/move/ability, returns the value of the DexDict, or None if there are no sufficient matches
    # also returns how alike name is to the returned value's alias
    def fuzzy_alias_search(self, name):
        MAX_NAME_LEN_DIFF = 3
        LIKENESS_THRESHOLD = 80
        name = saurbot_functions.only_a_to_z(name)
        valid_aliases = []
        for alias in self.aliases:
            if abs(len(alias)-len(name)) <= MAX_NAME_LEN_DIFF:
                valid_aliases.append(alias)
        if len(valid_aliases) == 0:
            return None, 0
        best_guess, likeness = process.extractOne(name, valid_aliases)
        if likeness >= LIKENESS_THRESHOLD:
            return self.alias_search(best_guess), likeness
        return None, likeness

    def all_after_scraping(self):
        for item in self.values():
            item.after_scraping()
        self.create_aliases()

    def all_calculate_filter_rules(self):
        for item in self.values():
            item.calculate_filter_rules()

    def filter_name_starts_with(self, pos, full_argument, stripped_argument):
        response_text_list = []
        stripped_argument = saurbot_functions.only_a_to_z(stripped_argument)
        results = set()
        for key in self.aliases:
            if key.startswith(stripped_argument):
                results.add(self.alias_search(key))
        results = list(results)
        return Argument(self.data_type_str, "name starts with", full_argument, results), response_text_list

    def filter_name_ends_with(self, pos, full_argument, stripped_argument):
        response_text_list = []
        stripped_argument = saurbot_functions.only_a_to_z(stripped_argument)
        results = set()
        for key in self.aliases:
            if key.endswith(stripped_argument):
                results.add(self.alias_search(key))
        results = list(results)
        return Argument(self.data_type_str, "name ends with", full_argument, results), response_text_list

    def filter_name_includes(self, pos, full_argument, stripped_argument):
        response_text_list = []
        stripped_argument = saurbot_functions.only_a_to_z(stripped_argument)
        results = set()
        for key in self.aliases:
            if stripped_argument in key:
                results.add(self.alias_search(key))
        results = list(results)
        return Argument(self.data_type_str, "name includes", full_argument, results), response_text_list

    def filter_name(self, pos, full_argument, stripped_argument, assumed=False):
        stripped_argument = remove_equals_operator(stripped_argument)
        results = []
        response_text_list = []
        if assumed:
            response_text_list.append(create_response_text("name", pos, "notice", f"Unknown filter \"{stripped_argument}\". Defaulting to name filter."))
        result, score = self.fuzzy_alias_search(stripped_argument)
        if result is not None:
            results.append(result)
            if score < 100:
                response_text_list.append(create_response_text("name", pos, "notice", f"Could not find \"{stripped_argument}\". Autocorrected to {result.name}."))
        else:
            response_text_list.append(create_response_text("name", pos, "notice", f"Could not find \"{stripped_argument}\"."))
        return Argument(self.data_type_str, "name", full_argument, results), response_text_list

    def filter_all(self):
        return Argument(self.data_type_str, "all", "all", list(self.values())), []

    def filter_pokedex(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("pokedex", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_draft(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("draft", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_ladder(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("ladder", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_buff(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("buff", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_nfe(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("nfe", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_stat(self, pos, full_argument, stripped_argument, stat):
        raise SearchError(create_response_text("name", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_has_ability(self, pos, ability_argument):
        raise SearchError(create_response_text("ability", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_has_move(self, pos, move_argument, new_gens):
        raise SearchError(create_response_text("move", pos, "error", f"{self.data_type_str} does not support this filter."))
        
    def filter_pp(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("pp", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_maxpp(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("max pp", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_accuracy(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("accuracy", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_power(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("power", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_zpower(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("zpower", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_priority(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("priority", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_crit_ratio(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("crit rate", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_category(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("category", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_trait(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("trait", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_target(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("target", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_type(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("type", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_effectiveness(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("effectiveness", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_secondary_chance(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("secondary chance", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_stage(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("stage", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_status(self, pos, full_argument, stripped_argument):
        raise SearchError(create_response_text("status", pos, "error", f"{self.data_type_str} does not support this filter."))

    def filter_learned_by(self, pos, full_argument, stripped_argument, new_gens):
        raise SearchError(create_response_text("learned by", pos, "error", f"{self.data_type_str} does not support this filter."))

class PokemonDict(DexDict):
    data_type_str = "pokemon"
    def all_check_whitelist(self, pokemon_hashes):
        for item in self.values():
            item.check_whitelist(pokemon_hashes)

    def all_after_scraping(self):
        super().all_after_scraping()
        for item in self.values():
            item.calculate_matchups()
            item.check_prevo_and_evos()
            
    def all_finish_setup(self):
        super().all_finish_setup()
        for item in self.values():
            item.check_learnset()
   
    def filter_pokedex(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("pokedex", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "pokedex", full_argument, results), response_text_list
        results = [mon for mon in self.values() if comparison_function(value, mon.dex)]
        return Argument(self.data_type_str, "pokedex", full_argument, results), response_text_list

    def filter_draft(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        tier, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        tier_check_result = check_tier("draft", pos, tier)
        if type(tier_check_result) == str:
            response_text_list.append(tier_check_result)
            return Argument(self.data_type_str, "draft", full_argument, results), response_text_list
        tier = TIERS[tier.upper()]
        if tier == 0:
            # if banned
            if comparison_operator == "==":
                results = [mon for mon in self.values() if mon.tier.lower() == "banned"]
            elif comparison_operator == ">=":
                results = [mon for mon in self.values() if mon.tier.lower() == "banned"]
            elif comparison_operator == "<=":
                results = [mon for mon in self.values()]
            elif comparison_operator == ">":
                results = []
            elif comparison_operator == "<":
                results = [mon for mon in self.values() if mon.tier.lower() != "banned"]
        elif tier > 0:
            results = [mon for mon in self.values() if (comparison_function((-tier), (-TIERS[mon.tier.upper()])) if ("M" not in mon.tier.upper()) else False)]
        else:
            results = [mon for mon in self.values() if (comparison_function(tier, TIERS[mon.tier.upper()]) if ("M" in mon.tier.upper()) else False)]
        return Argument(self.data_type_str, "draft", stripped_argument, results), response_text_list

    def filter_ladder(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        tier, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        ladder_check_result = check_ladder_tier("ladder", pos, tier)
        if type(ladder_check_result) == str:
            response_text_list.append(ladder_check_result)
            return Argument(self.data_type_str, "ladder", full_argument, results), response_text_list
        tier = LADDER_TIERS[tier.upper()]
        if tier == 0:
            # if banned
            if comparison_operator == "==":
                results = [mon for mon in self.values() if mon.tier.lower() == "ubers"]
            elif comparison_operator == ">=":
                results = [mon for mon in self.values() if mon.tier.lower() == "ubers"]
            elif comparison_operator == "<=":
                results = [mon for mon in self.values()]
            elif comparison_operator == ">":
                results = [mon for mon in self.values() if mon.tier.lower() == "ag"]
            elif comparison_operator == "<":
                results = [mon for mon in self.values() if mon.tier.lower() != "ubers"]
        elif tier > 0:
            results = [mon for mon in self.values() if (comparison_function((-tier), (-LADDER_TIERS[mon.ladder_tier.upper()])))]
        return Argument(self.data_type_str, "ladder", stripped_argument, results), response_text_list

    def filter_buff(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        results = [mon for mon in self.values() if mon.buff]
        return Argument(self.data_type_str, "pokedex", full_argument, results), response_text_list

    def filter_nfe(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        results = [mon for mon in self.values() if len(mon.evos)]
        return Argument(self.data_type_str, "pokedex", full_argument, results), response_text_list

    def filter_stat(self, pos, full_argument, stripped_argument, stat):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("stat", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "stat", full_argument, results), response_text_list
        results = [mon for mon in self.values() if comparison_function(value, mon.stats[stat.upper()])]
        return Argument(self.data_type_str, "stat", full_argument, results), response_text_list

    def filter_type(self, pos, full_argument, stripped_argument):
        results = self.values()
        response_text_list = []
        filter_types = set()
        type_finder_string = stripped_argument
        for pkmn_type in types:
            if type_finder_string.startswith(pkmn_type.lower()):
                found_type = pkmn_type
                filter_types.add(types[found_type])
                type_finder_string = type_finder_string.removeprefix(found_type.lower()).strip()
                break
        if type_finder_string.startswith("-"):
            type_finder_string = type_finder_string.removeprefix("-").strip()
            for pkmn_type in types:
                if type_finder_string.startswith(pkmn_type.lower()):
                    found_type = pkmn_type
                    filter_types.add(types[found_type])
                    type_finder_string = type_finder_string.removeprefix(found_type.lower()).strip()
                    break
        filter_types = list(filter_types)
        if len(filter_types) == 0:
            response_text_list.append(create_response_text("type", pos, "notice", f"Invalid type."))
        for t in filter_types:
            old_results = results
            results = set()
            for mon in old_results:
                if t in [mon_type for mon_type in mon.types]:
                    results.add(mon)
        return Argument(self.data_type_str, "type", full_argument, list(results)), response_text_list

    def filter_effectiveness(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        found_type = ""
        for pkmn_type in types:
            if stripped_argument.startswith(pkmn_type.lower()):
                found_type = types[pkmn_type.capitalize()]
                stripped_argument = stripped_argument.removeprefix(found_type.name.lower()).strip()
                break
        if found_type == "":
            response_text_list.append(create_response_text("effectiveness", pos, "notice", f"Invalid type."))
        else:
            value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
            effectiveness_check_result = check_effectiveness_text("effectiveness", pos, value)
            if type(effectiveness_check_result) == str:
                response_text_list.append(value)
                return Argument(self.data_type_str, "effectiveness", full_argument, results), response_text_list
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
            results = [mon for mon in self.values() if comparison_function(value, mon.matchups[found_type])]
        return Argument(self.data_type_str, "effectiveness", full_argument, results), response_text_list

    def filter_has_ability(self, pos, ability_argument):
        results = []
        response_text_list = []
        for mon in self.values():
            if len([ability for ability in mon.get_ability_list() if ability in ability_argument]):
                results.append(mon)
        return Argument(self.data_type_str, "ability", "", results), response_text_list

    def filter_has_move(self, pos, move_argument, new_gens):
        gen = 7
        if new_gens:
            gen = 8
        results = []
        response_text_list = []
        for mon in self.values():
            for move in move_argument:
                if mon.learns_move(move, gen):
                    results.append(mon)
                    break
        return Argument(self.data_type_str, "move", "", results), response_text_list

class MoveDict(DexDict):
    data_type_str = "move"

    def all_after_scraping(self):
        super().all_after_scraping()
        self["curse"].volatile_status.append(VolatileStatusEffect(False, 100, ["curse"]))
        self["curse"].self_effect.append(BoostEffect(True, 100, {"atk": 1, "def": 1, "spe": -1}))
        self["curse"].zeffect = [BoostEffect(True, 100, {"atk": 1}),
                                 ZEffect(True, 100, "heal")]

    def update_move_volatiles(self):
        new_move_volatile_statuses = set()
        for move in self.values():
            if move.filter_rule_unrevealed:
                continue
            for status in move.self_effect + move.volatile_status + move.secondary_effects_user + move.secondary_effects_target:
                if status.name == "volatile status":
                    new_move_volatile_statuses.update(status.details)
        for status in new_move_volatile_statuses:
            if status not in move_volatile_statuses:
                #print(f"A new volatile status {status} needs to be added to the status list. Remember to update the help doc!")
                print("A new volatile status needs to be added to the status list. Remember to update the help doc!")

    def filter_pp(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("pp", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "pp", full_argument, results), response_text_list
        if value % 8 == 0 and value % 5 != 0:
            response_text_list.append(create_response_text("pp", pos, "notice", f"Filtering by base pp. If you want to filter by max pp, use the maxpp filter."))
        results = [move for move in self.values() if comparison_function(value, move.pp)]
        return Argument(self.data_type_str, "pp", full_argument, results), response_text_list

    def filter_maxpp(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("maxpp", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "maxpp", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.max_pp)]
        return Argument(self.data_type_str, "pp", full_argument, results), response_text_list

    def filter_accuracy(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        if value.lower() in ["true", "fixed", "sure hit", "guaranteed", "guaranteed hit", "never miss", "missless", "always hits", "always lands"]:
            value = 101
        value = check_float("accuracy", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "accuracy", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.accuracy)]
        return Argument(self.data_type_str, "accuracy", full_argument, results), response_text_list

    def filter_power(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("power", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "power", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.power)]
        return Argument(self.data_type_str, "power", full_argument, results), response_text_list

    def filter_zpower(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("zpower", pos, value)
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "zpower", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.zpower)]
        return Argument(self.data_type_str, "zpower", full_argument, results), response_text_list

    def filter_priority(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("priority", pos, value.removeprefix("+").strip())
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "priority", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.priority)]
        return Argument(self.data_type_str, "priority", full_argument, results), response_text_list

    def filter_crit_ratio(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("crit rate", pos, value.removeprefix("+").strip())
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "crit rate", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.crit_ratio)]
        return Argument(self.data_type_str, "crit rate", full_argument, results), response_text_list

    def filter_category(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        cat = ""
        if stripped_argument in ["phys", "physical"]:
            cat = "Physical"
        elif stripped_argument in ["spec", "special"]:
            cat = "Special"
        elif stripped_argument in ["stat", "status"]:
            cat = "Status"
        else:
            response_text_list.append(create_response_text("category", pos, "notice", f"Unknown category \"{stripped_argument}\". Accepted categories are physical, special, and status."))
        results = [move for move in self.values() if move.category == cat]
        return Argument(self.data_type_str, "category", full_argument, results), response_text_list

    def filter_trait(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        traits = set()
        draining = False
        multihit = False
        recoil = False
        argument_list = stripped_argument.split(",")
        for item in argument_list:
            item = item.strip()
            if item in ["drain", "draining"]:
                draining = True
            elif item in ["multi-hit", "multihit"]:
                multihit = True
            elif item in ["recoil"]:
                recoil = True
            elif item in move_flags:
                traits.add(item)
        if (draining or multihit or recoil) == False and len(traits) == 0:
            response_text_list.append(create_response_text("trait", pos, "notice", f"Invalid traits. For a list of valid traits, see the Saurbot Guide by using /help."))
            return Argument(self.data_type_str, "trait", full_argument, results), response_text_list
        for move in self.values():
            add_move = True
            if draining == True and move.drain == False:
                add_move = False
            if multihit == True and move.multihit == False:
                add_move = False
            if recoil == True and len([effect for effect in move.self_effect if type(effect) is RecoilEffect]) == 0:
                add_move = False
            for trait in traits:
                if add_move == False:
                    break
                if trait not in move.flags:
                    add_move = False
            if add_move:
                results.append(move)
        return Argument(self.data_type_str, "trait", full_argument, results), response_text_list

    def filter_target(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        if saurbot_functions.only_a_to_z(stripped_argument) not in [saurbot_functions.only_a_to_z(item) for item in list(move_targets.keys()) + list(move_targets.values())]:
            response_text_list.append(create_response_text("target", pos, "notice", f"Invalid target. For a list of valid targets, see the Saurbot Guide by using /help."))
        results = [move for move in self.values() if saurbot_functions.only_a_to_z(move.target) == saurbot_functions.only_a_to_z(stripped_argument) or saurbot_functions.only_a_to_z(move_targets[move.target]) == saurbot_functions.only_a_to_z(stripped_argument) or (stripped_argument in ["randomnormal", "self", "random"] and move == "curse")]
        return Argument(self.data_type_str, "target", full_argument, results), response_text_list

    def filter_type(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        if stripped_argument.capitalize() not in types:
            response_text_list.append(create_response_text("type", pos, "notice", f"Unknown type \"{stripped_argument}\"."))
        results = [move for move in self.values() if move.type.name.lower() == stripped_argument]
        return Argument(self.data_type_str, "type", full_argument, results), response_text_list

    def filter_effectiveness(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        filter_types = set()
        type_finder_string = stripped_argument
        for pkmn_type in types:
            if type_finder_string.startswith(pkmn_type.lower()):
                found_type = pkmn_type
                filter_types.add(types[found_type])
                type_finder_string = type_finder_string.removeprefix(found_type.lower()).strip()
                break
        if type_finder_string.startswith("-"):
            type_finder_string = type_finder_string.removeprefix("-").strip()
            for pkmn_type in types:
                if type_finder_string.startswith(pkmn_type.lower()):
                    found_type = pkmn_type
                    filter_types.add(types[found_type])
                    type_finder_string = type_finder_string.removeprefix(found_type.lower()).strip()
                    break
        filter_types = list(filter_types)
        if len(filter_types) == 0:
            response_text_list.append(create_response_text("effectiveness", pos, "notice", f"Invalid type. Please provide a pokemon type, or two pokemon types joined by a hyphen (E.g. grass-poison)."))
            return Argument(self.data_type_str, "effectiveness", full_argument, []), response_text_list
        elif len(filter_types) == 1:
            filter_types.append(types["Typeless"])
        if type_finder_string == "":
            type_finder_string = "> 1"
        value, comparison_function, comparison_operator = determine_comparison(type_finder_string)
        # raise a search error if it's not a valid number
        effectiveness_check_result = check_effectiveness_text("effectiveness", pos, value)
        if type(effectiveness_check_result) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "effectiveness", full_argument, results), response_text_list
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
        results = [move for move in self.values() if (comparison_function(value, move.type.offensive[filter_types[0]] * move.type.offensive[filter_types[1]]) and move.category != "Status")]
        inverse_results = [move for move in self.values() if (comparison_function(value, move.type.offensive[filter_types[0]] * move.type.offensive[filter_types[1]]) == False and move.category != "Status")]
        return Argument(self.data_type_str, "effectiveness", full_argument, results, inverse_results), response_text_list

    def filter_secondary_chance(self, pos, full_argument, stripped_argument):
        results = []
        response_text_list = []
        if stripped_argument == "":
            stripped_argument = "> 0"
        value, comparison_function, comparison_operator = determine_comparison(stripped_argument)
        value = check_float("secondary chance", pos, value.removesuffix("%").strip())
        if type(value) == str:
            response_text_list.append(value)
            return Argument(self.data_type_str, "secondary chance", full_argument, results), response_text_list
        results = [move for move in self.values() if comparison_function(value, move.secondary_chance)]
        return Argument(self.data_type_str, "secondary chance", full_argument, results), response_text_list

    def filter_stage(self, pos, full_argument, stripped_argument):
        response_text_list = []
        modified_argument = stripped_argument
        # start off assuming the user doesnt care who gets boosted
        boost_target = "either"
        boosts = {}
        # if they specify user or target, change the recipient of the buff accordingly
        if modified_argument.startswith("user"):
            boost_target = "user"
            modified_argument = modified_argument.removeprefix("user").strip()
        elif modified_argument.startswith("target"):
            boost_target = "target"
            modified_argument = modified_argument.removeprefix("target").strip()
        modified_argument = modified_argument.split(",")
        if modified_argument == [""]:
            modified_argument = []
        # example filter might look like this:
        # boosts user atk +1, spe +1
        # comparison operators are also allowed, so "boosts user atk > 0" could work
        # if its just blank like "boosts atk" it'll return everything that changes attack
        # right now, we're looking at the "atk +1, spe +1" part of the command
        # we split it at the commas and look at each boost separately here
        if len(modified_argument) > 0:
            results = self.values()
            for current_boost in modified_argument:
                current_boost = current_boost.strip()
                # we go through our dictionary of stat names to see if any of them are at the start of the current boost
                matched_boost = False
                for stat in STAT_ALIASES:
                    if matched_boost:
                        break
                    for alias in STAT_ALIASES[stat]:
                        if matched_boost:
                            break
                        if current_boost.startswith(alias):
                            matched_boost = True
                            if stat == "hp":
                                # you can't boost hp unfortunately
                                response_text_list.append(create_response_text("stage", pos, "notice", f"Unfortunately, you can't boost HP. If it was possible, I would have done so already."))
                            elif stat == "bst":
                                response_text_list.append(create_response_text("stage", pos, "notice", f"You can't boost your base stat total. But that doesn't mean you don't have any room to grow!"))
                            else:
                                # this removes the stat name. now we're at "+1"
                                current_boost = current_boost.removeprefix(alias).strip()
                                # if everything has been removed, change it to "> -13"
                                if current_boost == "":
                                    current_boost = "> -13"
                                value, comparison_function, comparison_operator = determine_comparison(current_boost)
                                value = check_float("stage", pos, value.removeprefix("+").strip())
                                if type(value) == str:
                                    response_text_list.append(value)
                                else:
                                    # now we update the results
                                    new_results = set()
                                    for move in list(results):
                                        if boost_target != "target":
                                            # check self_effect, self secondary effects, and zeffects for the boost
                                            if len([effect for effect in move.self_effect + move.secondary_effects_user + move.zeffect if effect.name == "Boosts" and stat in effect.details and comparison_function(value, effect.details[stat])]):
                                                new_results.add(move)
                                            # check boosts for the boost
                                            elif move.target == "self" and len([effect for effect in move.boosts if effect.name == "Boosts" and stat in effect.details and comparison_function(value, effect.details[stat])]):
                                                new_results.add(move)
                                        if boost_target != "user":
                                            # check boosts for the boost
                                            if move.target == "self" and len([effect for effect in move.boosts if effect.name == "Boosts" and stat in effect.details and comparison_function(value, effect.details[stat])]):
                                                new_results.add(move)
                                            # check boosts if move has secondary effects
                                            elif len([effect for effect in move.secondary_effects_target if effect.name == "Boosts" and stat in effect.details and comparison_function(value, effect.details[stat])]):
                                                new_results.add(move)
                                    results = new_results
        # if the len is 0 we're looking for anything that boosts
        else:
            results = set()
            for move in self.values():
                if boost_target != "target":
                    # check self_effect for boosts
                    if len([effect for effect in move.self_effect if effect.name == "Boosts"]) > 0:
                        results.add(move)
                    # check boosts if move targets self
                    elif move.target == "self" and move.boosts != []:
                        results.add(move)
                    # check boosts if move has secondary effects that target self
                    elif len([effect for effect in move.secondary_effects_user if effect.name == "Boosts"]):
                        results.add(move)
                    # check boosts in the zeffect
                    elif len([effect for effect in move.zeffect if effect.name == "Boosts"]):
                        results.add(move)
                if boost_target != "user":
                    # check boosts if move doesnt target self
                    if move.target != "self" and move.boosts != []:
                        results.add(move)
                    # check boosts if move has secondary effects
                    elif len([effect for effect in move.secondary_effects_target if effect.name == "Boosts"]) > 0:
                        results.add(move)
        return Argument(self.data_type_str, "stage", full_argument, list(results)), response_text_list

    def filter_status(self, pos, full_argument, stripped_argument):
        response_text_list = []
        results = []
        modified_argument = stripped_argument
        # start off assuming the user doesnt care who gets statused
        status_target = "either"
        # if they specify user or target, change the recipient of the status accordingly
        if modified_argument.startswith("user"):
            status_target = "user"
            modified_argument = modified_argument.removeprefix("user")
        elif modified_argument.startswith("target"):
            status_target = "target"
            modified_argument = modified_argument.removeprefix("target")
        modified_argument = saurbot_functions.only_a_to_z(modified_argument)
        status_to_find = ""
        status_type = ""
        # checks to see if the status is in the list of volatiles
        if modified_argument in move_volatile_statuses:
            status_to_find = modified_argument
            status_type = "volatile"
        # checks to see if the status is in the list of nonvolatiles or their aliases
        else:
            for nonvolatile_status in STATUS_ALIASES:
                if status_to_find != "":
                    break
                for alias in STATUS_ALIASES[nonvolatile_status]:
                    if saurbot_functions.only_a_to_z(alias) == modified_argument:
                        status_to_find = nonvolatile_status
                        status_type = "nonvolatile"
                        break
        if status_to_find == "":
            response_text_list.append(create_response_text("status", pos, "notice", f"Unknown status {stripped_argument}. For a list of valid statuses, see the Saurbot Guide by using /help."))
        else:
            # we go through each move
            for move in list(self.values()):
                status_found = False
                # depending on what the user asked for, we check certain effect sources
                status_sort_lists = []
                if status_target in ["user", "either"]:
                    status_sort_lists += move.self_effect
                    status_sort_lists += move.secondary_effects_user
                    if move.target == "self":
                        status_sort_lists += move.secondary_effects_target
                        status_sort_lists += move.volatile_status
                        status_sort_lists += move.status
                if status_target in ["target", "either"]:
                    if move.secondary_effects_target not in status_sort_lists:
                        status_sort_lists += move.secondary_effects_target
                    if move.target != "self":
                        status_sort_lists += move.volatile_status
                        status_sort_lists += move.status
                # we go through each source in the list of sources and check to see if that status is caused by that source for this move
                for status_source in status_sort_lists:
                    if status_found:
                        break
                    if status_type == "nonvolatile":
                        if status_source.name == "Nonvolatile Status" and status_source.details == status_to_find:
                            results.append(move)
                            status_found = True
                            break
                        elif status_source.name == "Random Status" and status_to_find in status_source.details:
                            results.append(move)
                            status_found = True
                            break
                    elif status_type == "volatile" and status_source.name == "Volatile Status" and status_to_find in status_source.details:
                        results.append(move)
                        status_found = True
                        break
        return Argument(self.data_type_str, "status", full_argument, results), response_text_list

    def filter_learned_by(self, pos, full_argument, stripped_argument, new_gens):
        gen = 7
        if new_gens:
            gen = 8
        results = []
        response_text_list = []
        result, score = pokemon.fuzzy_alias_search(stripped_argument)
        if result is not None:
            results = [move for move in result.learnset.keys() if result.learns_move(move, gen)]
            if score < 100:
                response_text_list.append(create_response_text("learned by", pos, "notice", f"Could not find \"{stripped_argument}\". Autocorrected to {result.name}."))
        else:
            response_text_list.append(create_response_text("learned by", pos, "notice", f"Could not find \"{stripped_argument}\"."))
        return Argument(self.data_type_str, "learned by", full_argument, results), response_text_list

class AbilityDict(DexDict):
    data_type_str = "ability"


pokemon = PokemonDict()
moves = MoveDict()
abilities = AbilityDict()

class DexData:
    def __init__(self, internal_name):
        self.internal_name = internal_name
        self.name = ""
        self.aliases = set()
        self.filter_rule_base_forms = False # must be a base form or exclusive to a base form
        self.filter_rule_hypnomons = False # must be a hypnomon or exclusive to a hypnomon
        self.filter_rule_new_gens = False # gen 8+
        self.filter_rule_ignored = True # non-fnf customs/non-canon vanilla stuff 
        self.filter_rule_unrevealed = False # unrevealed fnf stuff
        
    def add_alias(self, name):
        if type(name) is str:
            self.aliases.add(saurbot_functions.only_a_to_z(name))
        elif type(name) is list:
            for item in name:
                self.aliases.add(saurbot_functions.only_a_to_z(item))

    def after_scraping(self):
        self.add_alias([self.name, self.internal_name])

    # default filter rules:
    # base_forms: Include
    # hypnomons: Exclude
    # new_gens: Exclude
    # ignored: Exclude
    # unrevealed: Exclude (cannot be changed)
    # 0 (exclude) = do not include if this trait is true
    # 1 (include) = include this trait in the search results
    # 2 (require) = exclusively filter for this trait
    def check_filter_rules(self, base_forms=1, hypnomons=0, new_gens=0, ignored=0):
        if self.filter_rule_unrevealed:
            return False
        if new_gens == 0 and self.filter_rule_new_gens:
            return False
        if new_gens == 2 and self.filter_rule_new_gens == False:
            return False
        if hypnomons == 0 and self.filter_rule_hypnomons:
            return False
        if hypnomons == 2 and self.filter_rule_hypnomons == False:
            return False
        if base_forms == 0 and self.filter_rule_base_forms:
            return False
        if base_forms == 2 and self.filter_rule_base_forms == False:
            return False
        if ignored == 0 and self.filter_rule_ignored:
            return False
        if ignored == 2 and self.filter_rule_ignored == False:
            return False
        return True

    def create_text_values(self):
        pass

    def get_name_and_summary(self):
        return self.name, ""

    def to_text_one_line(self):
        return self.name

    def to_embed(self):
        return discord.Embed(title=self.name), []

    def to_text(self):
        return ""

    def to_image_text(self):
        return self.to_text()

class Ability(DexData):
    def __init__(self, internal_name):
        super().__init__(internal_name)
        self.description = "Description not available"

    def calculate_filter_rules(self):
        self.filter_rule_ignored = False
        pokemon_with_this_ability = [mon for mon in pokemon.values() if self in mon.get_ability_list()]
        hypnomon_pokemon_with_this_ability = [mon for mon in pokemon_with_this_ability if mon.filter_rule_hypnomons]
        base_form_pokemon_with_this_ability = [mon for mon in pokemon_with_this_ability if mon.filter_rule_base_forms]
        new_gen_pokemon_with_this_ability = [mon for mon in pokemon_with_this_ability if mon.filter_rule_new_gens]
        ignored_pokemon_with_this_ability = [mon for mon in pokemon_with_this_ability if mon.filter_rule_ignored]
        unrevealed_pokemon_with_this_ability = [mon for mon in pokemon_with_this_ability if mon.filter_rule_unrevealed]
        if len(pokemon_with_this_ability) == len(hypnomon_pokemon_with_this_ability):
            self.filter_rule_hypnomons = True
        if len(pokemon_with_this_ability) == len(base_form_pokemon_with_this_ability):
            self.filter_rule_base_forms = True
        if len(pokemon_with_this_ability) == len(new_gen_pokemon_with_this_ability):
            self.filter_rule_new_gens = True
        if len(pokemon_with_this_ability) == len(ignored_pokemon_with_this_ability):
            self.filter_rule_ignored = True
        if len(pokemon_with_this_ability) == len(unrevealed_pokemon_with_this_ability):
            self.filter_rule_unrevealed = True

    def get_name_and_summary(self):
        return self.name, self.description

    def to_text_one_line(self):
        return f"{padding(self.name, longest_ability_name+1)}: {self.description}" 

    def to_embed(self):
        embed = discord.Embed(title=self.name)
        embed.add_field(name="Description", value=self.description)
        return embed, []

    def to_text(self):
        return f"{self.name}\n{self.description}"

class Move(DexData):
    def __init__(self, internal_name):
        super().__init__(internal_name)
        self.type = ""
        self.category = ""
        self.power = 0
        self.zpower = 0
        self.accuracy = 0
        self.pp = 0
        self.max_pp = 0
        self.description = ""
        self.flags = []
        self.target = ""
        self.crit_ratio = 0
        self.priority = 0
        self.multihit = False
        self.drain = False
        self.description = ""
        self.zeffect = []
        self.self_effect = []
        self.boosts = []
        self.volatile_status = []
        self.status = []
        self.secondary_chance = 0
        self.secondary_effects_user = []
        self.secondary_effects_target = []
        self.unresolved_secondaries = False

    def calculate_zpower(self):
        if self.category == "Status":
            self.zpower = 0
        elif self.power >= 140:
            self.zpower = 200
        elif self.power >= 130:
            self.zpower = 195
        elif self.power >= 120:
            self.zpower = 190
        elif self.power >= 110:
            self.zpower = 185
        elif self.power >= 100:
            self.zpower = 180
        elif self.power >= 90:
            self.zpower = 175
        elif self.power >= 80:
            self.zpower = 160
        elif self.power >= 70:
            self.zpower = 140
        elif self.power >= 60:
            self.zpower = 120
        elif self.power > 0:
            self.zpower = 100

    def after_scraping(self):
        super().after_scraping()
        if self.zpower == 0:
            self.calculate_zpower()
        for effect in self.status + self.volatile_status + self.boosts:
            if self.target == "self":
                effect.targets_self = True

    def calculate_filter_rules(self):
        self.filter_rule_ignored = False
        pokemon_with_this_move = [mon for mon in pokemon.values() if self in mon.learnset]
        hypnomon_pokemon_with_this_move = [mon for mon in pokemon_with_this_move if mon.filter_rule_hypnomons]
        base_form_pokemon_with_this_move = [mon for mon in pokemon_with_this_move if mon.filter_rule_base_forms]
        new_gen_pokemon_with_this_move = [mon for mon in pokemon_with_this_move if mon.learns_move(self, 7) == False]
        ignored_pokemon_with_this_move = [mon for mon in pokemon_with_this_move if mon.filter_rule_ignored]
        unrevealed_pokemon_with_this_move = [mon for mon in pokemon_with_this_move if mon.filter_rule_unrevealed]
        if len(pokemon_with_this_move) == len(hypnomon_pokemon_with_this_move):
            self.filter_rule_hypnomons = True
        if len(pokemon_with_this_move) == len(base_form_pokemon_with_this_move):
            self.filter_rule_base_forms = True
        if len(pokemon_with_this_move) == len(new_gen_pokemon_with_this_move):
            self.filter_rule_new_gens = True
        if len(pokemon_with_this_move) == len(ignored_pokemon_with_this_move):
            self.filter_rule_ignored = True
        if len(pokemon_with_this_move) == len(unrevealed_pokemon_with_this_move):
            self.filter_rule_unrevealed = True
        if self.filter_rule_unrevealed == False and self.unresolved_secondaries == True:
            saurbot_functions.timelog(f"WARNING: {self.internal_name} has multiple secondary effects that need to be added manually.")
        if self.name in ["Red Rush", "Blue Bites", "Regroup2"]:
            self.filter_rule_hypnomons = False
            self.filter_rule_base_forms = False
            self.filter_rule_new_gens = False
            self.filter_rule_ignored = False
            self.filter_rule_unrevealed = False

    def create_text_values(self):
        self.text_values = {}
        self.text_values["padded type"] = padding(self.type.name, 9)
        self.text_values["padded power"] = padding(str(self.power), 3, " ", True)
        self.text_values["padded category"] = padding(self.category, 8)
        self.text_values["padded accuracy"] = "---" if self.accuracy == 101 else padding(str(self.accuracy), 3, " ", True)
        self.text_values["padded pp"] = f"{padding(str(self.pp), 2)} ({self.max_pp})"
        self.text_values["pp"] = f"{self.pp} ({self.max_pp})"
        self.text_values["flags"] = ""
        self.text_values["priority"] = f"+{self.priority}" if self.priority > 0 else str(self.priority)
        self.text_values["crit rate"] = f"+{self.crit_ratio}"
        if self.multihit:
            self.text_values["flags"] += "multihit, "
        if self.drain:
            self.text_values["flags"] += "drain, "
        for flag in self.flags:
            self.text_values["flags"] += flag + ", "
        self.text_values["flags"] = self.text_values["flags"].removesuffix(", ")

    def get_name_and_summary(self):
        summary_text = f"{self.text_values['padded type']} CAT: {self.text_values['padded category']} POW: {self.text_values['padded power']} ACC: {self.text_values['padded accuracy']} PP: {self.text_values['padded pp']}"
        if self.description != "":
            summary_text += "\n" + self.description
        return self.name, summary_text

    def to_text_one_line(self):
        summary_text = f"{self.text_values['padded type']} CAT: {self.text_values['padded category']} POW: {self.text_values['padded power']} ACC: {self.text_values['padded accuracy']} PP: {self.text_values['padded pp']}"
        name = padding(self.name, longest_move_name)
        return f"{name} {summary_text}"

    def to_embed(self):
        color = discord.Color.from_str(self.type.color)
        embed = discord.Embed(title=f"{self.name}", color=color)
        attachments = []
        embed.add_field(name="Type", value=self.type.name, inline=False)
        embed.add_field(name="Category", value=self.category, inline=False)
        embed.add_field(name="Power", value=self.power, inline=False)
        embed.add_field(name="Accuracy", value=self.text_values["padded accuracy"].strip(), inline=False)
        embed.add_field(name="PP (Max)", value=self.text_values["pp"], inline=False)
        if self.priority != 0:
            embed.add_field(name="Priority", value=self.text_values["priority"], inline=False)
        if self.crit_ratio != 0:
            embed.add_field(name="Crit rate", value=self.text_values["crit rate"], inline=False)
        if self.text_values["flags"] != "":
            embed.add_field(name="Flags", value=self.text_values["flags"], inline=False)
        embed.add_field(name="Target", value=self.target, inline=False)
        secondary_effects = self.secondary_effects_user + self.secondary_effects_target
        if len(secondary_effects) > 0:
            text = ""
            for effect in secondary_effects:
                text += str(effect) + "\n"
            embed.add_field(name="Secondary effects", value=text.strip(), inline=False)
        other_effects = self.status + self.volatile_status + self.boosts + self.self_effect + self.zeffect
        if len(other_effects) > 0:
            text = ""
            for effect in other_effects:
                text += str(effect) + "\n"
            embed.add_field(name="Move effects", value=text.strip(), inline=False)
        embed.add_field(name="Description", value=self.description)
        return embed, attachments

    def to_text(self):
        text = f"{self.name}\n"
        text += f"Type: {self.type.name}\n"
        text += f"Category: {self.category}\n"
        text += f"Power: {self.power}\n"
        text += f"Accuracy: {self.text_values['padded accuracy'].strip()}\n"
        text += f"PP (Max): {self.text_values['pp']}\n"
        if self.priority != 0:
            text += f"Priority: {self.text_values['priority']}\n"
        if self.crit_ratio != 0:
            text += f"Crit rate: {self.text_values['crit rate']}\n"
        if self.text_values["flags"] != "":
            text += f"Flags: {self.text_values['flags']}\n"
        secondary_effects = self.secondary_effects_user + self.secondary_effects_target
        text += f"Target: {self.target}\n"
        if len(secondary_effects) > 0:
            text += "Secondary effects:\n"
            for effect in secondary_effects:
                text += f"\t{effect}\n"
        other_effects = self.status + self.volatile_status + self.boosts + self.self_effect + self.zeffect
        if len(other_effects) > 0:
            text += "Move effects:\n"
            for effect in other_effects:
                text += f"{effect}\n"
        text += f"Description: {self.description}"
        return text
        
class Pokemon(DexData):
    def __init__(self, internal_name):
        super().__init__(internal_name)
        self.sprites = {}
        self.base_species = ""
        self.required_item = ""
        self.required_ability = ""
        self.required_move = ""
        self.num = 0
        self.dex = 0
        self.heightm = 0
        self.weightkg = 0
        self.types = []
        self.evos = []
        self.egg_groups = []
        self.color = ""
        self.prevo = None
        self.stats = {"HP": 0, "ATK": 0, "DEF": 0, "SPA": 0, "SPD": 0, "SPE": 0, "BST": 0}
        self.gender_ratio = {"M": 0, "F": 0, "N": 0}
        # S is special ability, which is only used by rockruff to my knowledge
        self.abilities = {"0": None, "1": None, "H": None, "S": None}
        self.form = ""
        self.related = set()
        self.moves = {}
        self.tier = "BANNED"
        self.ladder_tier = "UNTIERED"
        self.learnset = {}
        self.matchups = {}
        self.learnset_checked = False
        self.changes_from = ""
        self.buff = ""
        self.sample_sets = []
        self.changes = ""
        self.cosmetic_forms = []

    def check_learnset(self):
        if self.learnset_checked:
            return
        prevo = None
        base_form = None
        if self.prevo is not None:
            self.prevo.check_learnset()
        if self.changes_from != "":
            base_form = pokemon.alias_search(self.changes_from)
            base_form.check_learnset()
        if self.prevo is not None:
            for move in self.prevo.learnset:
                for method in self.prevo.learnset[move]:
                    evo_method = method[0] + "evo"
                    if move in self.learnset and (method[0] in self.learnset[move] or evo_method in self.learnset[move]):
                        continue
                    if move not in self.learnset:
                        self.learnset[move] = []
                    self.learnset[move].append(evo_method)
        if base_form is not None:
            for move in base_form.learnset:
                for method in base_form.learnset[move]:
                    evo_method = method[0] + "form"
                    if move in self.learnset and (method[0] in self.learnset[move] or evo_method in self.learnset[move]):
                        continue
                    if move not in self.learnset:
                        self.learnset[move] = []
                    self.learnset[move].append(evo_method)
        self.learnset_checked = True

    def get_ability_list(self):
        return [ability for ability in self.abilities.values() if ability is not None]

    def get_weight_attributes(self):
        weightkg = self.weightkg
        if weightkg >= 200:
            self.grass_knot_power = 120
        elif weightkg >= 100:
            self.grass_knot_power = 100
        elif weightkg >= 50:
            self.grass_knot_power = 80
        elif weightkg >= 25:
            self.grass_knot_power = 60
        elif weightkg >= 10:
            self.grass_knot_power = 40
        else:
            self.grass_knot_power = 20
        if weightkg > 200 or self.form == "Gmax":
            self.immune_to_sky_drop = True
        else:
            self.immune_to_sky_drop = False
        self.heavy_slam_thresholds = {"outgoing": {"120": weightkg / 5, "100": weightkg / 4, "80": weightkg / 3, "60": weightkg / 2},
                                      "incoming": {"120": weightkg * 5, "100": weightkg * 4, "80": weightkg * 3, "60": weightkg * 2}}
        if self.form == "Gmax":
            self.weightkg = 10000


    def check_sprites(self):
        sprites_found = 0
        if self.name == "Toxtricity-Low-Key-Gmax":
            self.sprites = {"Base Front": FRONT_SPRITES_URL + "toxtricity-gmax.png",
                            "Base Back": BACK_SPRITES_URL + "toxtricity-gmax.png",
                            "Shiny Front": FRONT_SHINY_SPRITES_URL + "toxtricity-gmax.png",
                            "Shiny Back": BACK_SHINY_SPRITES_URL + "toxtricity-gmax.png"}
            return 4
        # split into 4 dicts to ensure a consistent order is shown to the user
        male_sprites_dict = {}
        female_sprites_dict = {}
        # other_sprites_dict is a dict of dicts: {cosmetic form name: {sprite name: sprite url}}
        other_sprites_dict = {}
        has_gender_difference = False
        simplified_cosmetic_forms = [saurbot_functions.only_a_to_z(form) for form in self.cosmetic_forms]
        for img_file in sprite_list:
            simplified_img_file = saurbot_functions.only_a_to_z(img_file.removesuffix(".png"))
            found_sprite = False
            for alias in [name for name in self.aliases if name not in simplified_cosmetic_forms]:
                if (simplified_img_file == alias+"f" or simplified_img_file+"totem" == alias+"f") and self.name not in ["Unown", "Pyroar", "Nidoran", "Unfezant"]:
                    has_gender_difference = True
                    female_sprites_dict["Female Front"] = FRONT_SPRITES_URL + img_file
                    female_sprites_dict["Female Back"] = BACK_SPRITES_URL + img_file
                    female_sprites_dict["Shiny Female Front"] = FRONT_SHINY_SPRITES_URL + img_file
                    female_sprites_dict["Shiny Female Back"] = BACK_SHINY_SPRITES_URL + img_file
                    sprites_found += 4
                    found_sprite = True
                    break
                elif simplified_img_file == alias or simplified_img_file+"totem" == alias:
                    male_sprites_dict["Male Front"] = FRONT_SPRITES_URL + img_file
                    male_sprites_dict["Male Back"] = BACK_SPRITES_URL + img_file
                    male_sprites_dict["Shiny Male Front"] = FRONT_SHINY_SPRITES_URL + img_file
                    male_sprites_dict["Shiny Male Back"] = BACK_SHINY_SPRITES_URL + img_file
                    sprites_found += 4
                    found_sprite = True
                    break
            if found_sprite:
                continue
            for form in self.cosmetic_forms:
                if form in ignore_forms:
                    pass
                elif simplified_img_file == saurbot_functions.only_a_to_z(form):
                    if form not in other_sprites_dict:
                        other_sprites_dict[form] = {}
                    if form in dex_forms:
                        other_sprites_dict[form][f"{form}"] = DEX_SPRITES_URL + img_file
                        other_sprites_dict[form][f"Shiny {form}"] = DEX_SHINY_SPRITES_URL + img_file
                        sprites_found += 2
                        break
                    other_sprites_dict[form][f"{form} Front"] = FRONT_SPRITES_URL + img_file
                    other_sprites_dict[form][f"{form} Back"] = BACK_SPRITES_URL + img_file
                    other_sprites_dict[form][f"Shiny {form} Front"] = FRONT_SHINY_SPRITES_URL + img_file
                    other_sprites_dict[form][f"Shiny {form} Back"] = BACK_SHINY_SPRITES_URL + img_file
                    sprites_found += 4
                    break
        for key in male_sprites_dict:
            if has_gender_difference == False:
                if key == "Male Front":
                    self.sprites["Base Front"] = male_sprites_dict["Male Front"]
                    continue
                elif key == "Male Back":
                    self.sprites["Base Back"] = male_sprites_dict["Male Back"]
                    continue
                elif key == "Shiny Male Front":
                    self.sprites["Shiny Front"] = male_sprites_dict["Shiny Male Front"]
                    continue
                elif key == "Shiny Male Back":
                    self.sprites["Shiny Back"] = male_sprites_dict["Shiny Male Back"]
                    continue
            self.sprites[key] = male_sprites_dict[key]
        for key in female_sprites_dict:
            self.sprites[key] = female_sprites_dict[key]
        sorted_other_sprites_keys = list(other_sprites_dict.keys())
        sorted_other_sprites_keys.sort()
        for key in sorted_other_sprites_keys:
            for subkey in other_sprites_dict[key]:
                self.sprites[subkey] = other_sprites_dict[key][subkey]
        return sprites_found

    def after_scraping(self):
        super().after_scraping()
        self.get_weight_attributes()
        for key in self.gender_ratio:
            self.gender_ratio[key] *= 100
        if self.form in ["Galar", "Alola", "FnF", "Delta"]:
            self.base_species = self.name
        if self.required_item.endswith("Armor"):
            self.base_species = self.name.removesuffix("-Armored")
            self.form = "Armored"
        if self.gender_ratio == {"M": 0, "F": 0, "N": 0}:
            self.gender_ratio = {"M": 50, "F": 50, "N": 0}

    def check_prevo_and_evos(self):
        if self.prevo is not None:
            self.prevo = pokemon.alias_search(self.prevo)
        new_evos = []
        for evo in self.evos:
            new_evos.append(pokemon.alias_search(evo))
        self.evos = new_evos

    def calculate_filter_rules(self):
        if self.base_species == self.name:
            self.filter_rule_base_forms = True
        if -1000 < self.num <= -500:
            self.filter_rule_ignored = False
        elif -5000 < self.num <= -1000:
            self.filter_rule_hypnomons = True
            self.filter_rule_ignored = False
        elif 1 <= self.num <= 807:
            self.filter_rule_ignored = False
        elif 807 < self.num <= 898:
            self.filter_rule_ignored = False
            self.filter_rule_new_gens = True
        if self.form in ["Gmax", "Galar"]:
            self.filter_rule_ignored = False
            self.filter_rule_new_gens = True

    def get_learnset_text(self):
        text = ""
        for move in self.learnset:
            text += f"{move.name}: {move}\n"
        return text

    def check_whitelist(self, pokemon_hashes):
        if saurbot_functions.hash256(self.internal_name) in pokemon_hashes:
            self.filter_rule_unrevealed = False
        else:
            self.filter_rule_unrevealed = True

    def calculate_matchups(self):
        for current_type in types:
            type_matchups = []
            for pkmntype in self.types:
                type_matchups.append(pkmntype.defensive[types[current_type]])
            self.matchups[types[current_type]] = multiply_list_of_numbers(type_matchups)

    def learns_move(self, move, gen):
        if type(move) == str:
            move = moves.alias_search(move)
        if move in self.learnset:
            for learn_method in self.learnset[move]:
                if int(learn_method[0]) <= gen:
                    return True
        return False

    def create_text_values(self):
        self.text_values = {}
        self.text_values["type"] = self.types[0].name
        if len(self.types) > 1:
            self.text_values["type"] += f"-{self.types[1].name}"
        self.text_values["stats"] = ""
        for stat in self.stats:
            if stat != "BST":
                self.text_values["stats"] += padding(str(self.stats[stat]), 3, "0", True)
                if stat != "SPE":
                    self.text_values["stats"] += "/"
            else:
                self.text_values["stats"] += " (BST " + padding(str(self.stats[stat]), 3, "0", True) + ")"
        self.text_values["embed stats"] = ""
        self.text_values["file stats"] = ""
        for stat in self.stats:
            self.text_values["embed stats"] += f"**{stat}**: {self.stats[stat]}"
            self.text_values["file stats"] += f"{stat}: {self.stats[stat]}"
            if stat != "BST":
                self.text_values["embed stats"] += ", "
                self.text_values["file stats"] += ", "
        self.text_values["padded dex"] = padding(str(self.dex), 5)
        ladder_tier = "NONE" if self.ladder_tier == "UNTIERED" else self.ladder_tier
        draft_tier = "BAN" if self.tier == "BANNED" else self.tier
        draft_tier = f"({draft_tier})"
        self.text_values["padded tiers"] = f"{padding(ladder_tier, 5)} {padding(draft_tier, 8)}"
        self.text_values["padded type"] = padding(self.text_values["type"], 18)
        weakness_text = ""
        resistance_text = ""
        immunity_text = ""
        for t in self.matchups:
            if t.name in ["Typeless", "Shadow"] or self.matchups[t] == 1:
                continue
            elif self.matchups[t] == 2:
                weakness_text += f"{t.name}, "
            elif self.matchups[t] == 4:
                weakness_text = f"**{t.name}!**, " + weakness_text
            elif self.matchups[t] == 0.5:
                resistance_text += f"{t.name}, "
            elif self.matchups[t] == 0.25:
                resistance_text = f"**{t.name}!**, " + resistance_text
            elif self.matchups[t] == 0:
                immunity_text += f"{t.name}, "
        # for the embed, the ! will be removed
        # for the text, the * will be removed, and the ! will be come a *
        self.text_values["embed weakness"] = weakness_text.removesuffix(", ").replace("!", "")
        self.text_values["embed resistance"] = resistance_text.removesuffix(", ").replace("!", "")
        self.text_values["embed immunity"] = immunity_text.removesuffix(", ").replace("!", "")
        self.text_values["weakness"] = weakness_text.removesuffix(", ").replace("*", "").replace("!", "*")
        self.text_values["resistance"] = resistance_text.removesuffix(", ").replace("*", "").replace("!", "*")
        self.text_values["immunity"] = immunity_text.removesuffix(", ").replace("*", "").replace("!", "*")
        ability_text = ""
        hidden_ability_text = ""
        for key in self.abilities:
            if self.abilities[key] is None:
                continue
            if key == "H":
                hidden_ability_text = self.abilities[key].name
            else:
                ability_text += f"{self.abilities[key].name}, "
        if hidden_ability_text != "":
            self.text_values["abilities"] = f"{ability_text}{hidden_ability_text} (hidden)"
            self.text_values["embed abilities"] = f"{ability_text}*{hidden_ability_text}*"
        else:
            self.text_values["abilities"] = ability_text.removesuffix(", ")
            self.text_values["embed abilities"] = ability_text.removesuffix(", ")
        other_commands = f"/pokedex move filters: learned by {self.name}"
        '''
        Sample sets are super outdated so they are removed from saurbot until they become useful
        if len(self.sample_sets) > 0:
            other_commands += f"\n/pokedex sets {self.name}"
        '''
        self.text_values["related commands"] = other_commands
        if self.form == "Gmax":
            self.text_values["heavy slam outgoing"] = f"This Pokemon cannot use Heavy Slam."
            self.text_values["heavy slam incoming"] = "Immune to moves that depend on weight."
        else:
            heavy_slam_list = self.heavy_slam_thresholds["outgoing"]
            self.text_values["heavy slam outgoing"] = f"120BP: {heavy_slam_list['120']: .1f}kg, 100BP: {heavy_slam_list['100']: .1f}kg, 80BP: {heavy_slam_list['80']: .1f}kg, 60BP: {heavy_slam_list['60']: .1f}kg"
            heavy_slam_list = self.heavy_slam_thresholds["incoming"]
            self.text_values["heavy slam incoming"] = f"120BP: {heavy_slam_list['120']: .1f}kg, 100BP: {heavy_slam_list['100']: .1f}kg, 80BP: {heavy_slam_list['80']: .1f}kg, 60BP: {heavy_slam_list['60']: .1f}kg"
        evo_text = ""
        for evo in self.evos:
            evo_text += f"{evo.name}, "
        self.text_values["evos"] = evo_text[:-2]
        prevo_text = ""
        if self.prevo is not None:
            prevo_text = self.prevo.name
        self.text_values["prevo"] = prevo_text
        egg_group_text = ""
        for egg_group in self.egg_groups:
            egg_group_text += egg_group + ", "
        self.text_values["egg groups"] = egg_group_text[:-2]
        if self.gender_ratio["N"] == 100:
            self.text_values["gender"] = "Genderless"
        else:
            self.text_values["gender"] = f"M: {self.gender_ratio['M']}%, F: {self.gender_ratio['F']}%"
        if self.form == "Gmax":
            weight_text = "???kg (Immune to moves that depend on weight)"
        else:
            weight_text = f"{self.weightkg}kg (Low Kick BP: {self.grass_knot_power}"
            if self.immune_to_sky_drop:
                weight_text += ", Immune to Sky Drop"
            weight_text += ")"
        self.text_values["weight"] = weight_text

    def get_name_and_summary(self):
        summary_text = f"{self.text_values['padded tiers']} {self.text_values['padded type']} {self.text_values['stats']}\nAbilities: {self.text_values['embed abilities']}"
        name = f"#{self.dex}: {self.name}"
        return name, summary_text

    def to_text_one_line(self):
        summary_text = f"{self.text_values['padded tiers']} {self.text_values['padded type']} {self.text_values['stats']} {self.text_values['abilities']}"
        name = f"#{self.text_values['padded dex']}: {self.name}"
        name = padding(name, longest_pokemon_name+8)
        return f"{name}{summary_text}"

    def to_embed(self, sprite_to_show="<default>"):
        color = discord.Color.from_str(POKEDEX_COLORS[self.color.lower()])
        embed = discord.Embed(title=f"#{self.dex}: {self.name}", color=color)
        sprites_list = []
        if len(self.sprites):
            sprites_list = [key for key in self.sprites]
            if sprite_to_show == "<default>":
                embed.set_thumbnail(url=list(self.sprites.values())[0])
            else:
                embed.set_thumbnail(url=self.sprites[sprite_to_show])
        embed.add_field(name="Tier", value=f"Ladder: {self.ladder_tier}, Draft: {self.tier}", inline=False)
        embed.add_field(name="Type", value=self.text_values["type"], inline=False)
        if self.text_values["embed weakness"] != "":
            embed.add_field(name="Weaknesses", value=self.text_values["embed weakness"], inline=False)
        if self.text_values["embed resistance"] != "":
            embed.add_field(name="Resistances", value=self.text_values["embed resistance"], inline=False)
        if self.text_values["embed immunity"] != "":
            embed.add_field(name="Immunities", value=self.text_values["embed immunity"], inline=False)
        embed.add_field(name="Stats", value=self.text_values["embed stats"], inline=False)
        embed.add_field(name="Abilities", value=self.text_values["embed abilities"], inline=False)
        if len(self.evos) > 0:
            embed.add_field(name="Evolves into", value=self.text_values["evos"], inline=False)
        if self.prevo is not None:
            embed.add_field(name="Evolves from", value=self.text_values["prevo"], inline=False)
        embed.add_field(name="Gender ratio", value=self.text_values["gender"], inline=False)
        embed.add_field(name="Egg groups", value=self.text_values["egg groups"], inline=False)
        embed.add_field(name="Height", value=f"{self.heightm}m", inline=False)
        embed.add_field(name="Weight", value=self.text_values["weight"], inline=False)
        embed.add_field(name=f"Power of {self.name}'s Heavy Slam (Base Power: opponent's weight)",value=self.text_values["heavy slam outgoing"], inline=False)
        embed.add_field(name=f"Power of foe's Heavy Slam (Base Power: opponent's weight)",value=self.text_values["heavy slam incoming"], inline=False)
        if self.changes != "":
            embed.add_field(name="Changes made in FnF", value=self.changes, inline=False)
        embed.add_field(name="Related commands", value=f"*{self.text_values['related commands']}*",inline=False)
        if type(self) == Pokemon and self.name == "Saurbot":
            embed.set_footer(text=random.choice(SAURBOT_QUOTES))
        return embed, sprites_list

    def to_text(self):
        text = f"#{self.dex}: {self.name}\n"
        text += f"Ladder tier: {self.ladder_tier}, Draft tier: {self.tier}\n"
        text += f"Type: {self.text_values['type']}\n"
        if self.text_values["weakness"] != "":
            text += f"Weaknesses: {self.text_values['weakness']}\n"
        if self.text_values["resistance"] != "":
            text += f"Resistances: {self.text_values['resistance']}\n"
        if self.text_values["immunity"] != "":
            text += f"Immunities: {self.text_values['immunity']}\n"
        text += self.text_values["file stats"] + "\n"
        text += f"Abilities: {self.text_values['abilities']}\n"
        text += f"Gender ratio: {self.text_values['gender']}\n"
        text += f"Egg groups: {self.text_values['egg groups']}\n"
        text += f"Height: {self.heightm}m\n"
        text += f"Weight: {self.text_values['weight']}\n"
        text += f"Power of Heavy Slam used by {self.name} (Base Power: opponent's weight):\n\t{self.text_values['heavy slam outgoing']}\n"
        text += f"Power of Heavy Slam used against {self.name} (Base Power: opponent's weight):\n\t{self.text_values['heavy slam incoming']}\n"
        if self.changes != "":
            text += f"Changes made in FnF:\n{self.changes}\n"
        text += f"Related commands:\n{self.text_values['related commands']}"
        return text

class Fusion:
    def __init__(self, name=""):
        self.name = name
        self.possible_types = ""
        self.color = ""
        self.stats_text = ""
        self.possible_abilities = ""
        self.text_learnset = ""
        self.embed_learnset = ""
        self.image_learnset = ""

    def get_stats_text(self):
        for stat in self.stats:
            self.stats_text += f"{stat}: {self.stats[stat]}"
            if stat != "BST":
                self.stats_text += "\n"

    def to_embed(self):
        color = discord.Color.from_str(POKEDEX_COLORS[self.color.lower()])
        embed = discord.Embed(title=f"{self.name}", color=color)
        attachments = []
        embed.add_field(name="Possible types", value=self.possible_types, inline=False)
        embed.add_field(name="Possible abilities", value=self.possible_abilities, inline=False)
        embed.add_field(name="Stats", value=self.stats_text, inline=False)
        embed.add_field(name="Learnset", value=self.embed_learnset, inline=False)
        return embed, attachments

    def to_text_base(self):
        text = f"{self.name}\n"
        text += f"Possible types: {self.possible_types}\n"
        text += f"Possbile abilities: {self.possible_abilities}\n"
        text += f"Stats: {self.stats_text}\n"
        text += f"Learnset (New gen only marked with asterisk):\n"
        return text

    def to_text(self):
        return self.to_text_base() + self.text_learnset

    def to_image_text(self):
        return self.to_text_base() + self.image_learnset

    def get_name_and_summary(self):
        return "", ""

    def to_text_one_line(self):
        return ""


class PkmnType:
    def __init__(self, name = ""):
        self.name = name
        self.defensive = {}
        self.offensive = {}

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

class SampleSet:
    def __init__(self, sample_set = "", description = ""):
        self.sample_set = re.sub("\n+", "\n", re.sub(" +", " ", sample_set.strip()))
        self.description = re.sub("\n+", "\n", re.sub(" +", " ", description.strip()))

    def to_string(self):
        return (self.sample_set + "\n" + self.description)

    def to_image(self):
        return make_image(self.to_string())

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

def determine_comparison(command):
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
        comparison_operator = "=="
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

def check_float(filter_name, pos, value):
    try:
        return float(value)
    except ValueError:
        return create_response_text(filter_name, pos, "error", "Expected a number.")

def check_effectiveness_text(filter_name, pos, value):
    if value not in NOT_VERY_EFFECTIVE_TEXT + DOUBLE_NOT_VERY_EFFECTIVE_TEXT + NOT_EFFECTIVE_TEXT + SUPER_EFFECTIVE_TEXT + DOUBLE_SUPER_EFFECTIVE_TEXT + NEUTRAL_EFFECTIVE_TEXT:
        return check_float(filter_name, pos, value)
    return True

def check_tier(filter_name, pos, value):
    if value.upper() not in TIERS.keys():
        return create_response_text(filter_name, pos, "error", "Expected a draft tier.")
    return True

def check_ladder_tier(filter_name, pos, value):
    if value.upper() not in LADDER_TIERS.keys():
        return create_response_text(filter_name, pos, "error", "Expected a ladder tier (i.e. OU, UUBL, etc.).")
    return True

def multiply_list_of_numbers(l):
    result = 1
    for item in l:
        result *= item
    return result

def remove_equals_operator(text):
    return text.removeprefix("==").removeprefix("=").strip()

def wrap(text, font_size=36, mobile=False):
    initial_lines = text.split("\n")
    output = []
    for line in initial_lines:
        split_lines = textwrap.wrap(line, width=FONT_SIZES[font_size][1], break_long_words=False, replace_whitespace=False)
        for split_line in split_lines:
            output.append(split_line)
    if len(output) > FONT_SIZES[font_size][0] and mobile:
        output = output[:FONT_SIZES[font_size][0]-1]
        output.append(f"{MOBILE_IMAGE_WARNING}\n")
    result = ""
    for line in output:
        result += line + "\n"
    return result

def make_image(text, font_size=60, reduce_if_needed=True):
    img = Image.open("blank_image1920x1080.png")
    if reduce_if_needed:
        sizes = [72,60,48,36]
        for size in sizes:
            if size > font_size:
                del size
        for size in sizes:
            if wrap(text, size, True).strip().endswith(MOBILE_IMAGE_WARNING) == False:
                break

    font = ImageFont.truetype("cascadia-code/Cascadia.ttf", size)

    draw = ImageDraw.Draw(img)
    draw.text((0,0), wrap(text, size, True).strip(), (255, 255, 255), font=font)
    return img

def ready_image(img_input): 
    with BytesIO() as image:
        img_input.save(image, "PNG")
        image.seek(0)
        return discord.File(fp=image, filename='image.png')

def make_mobile_list(data):
    result = ""
    for thing in data:
        result += thing.name + ", "
    return saurbot_functions.asciinator(result[:-2])

with open("chatot.txt", "r") as f:
    CHATOT = f.read()

async def create_pagination_view(interaction: discord.Interaction, bot, command, copy=False):
    pagination_view = PaginationView()
    await pagination_view.send(interaction, bot, command, copy)
    active_command_views.append(pagination_view)

class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 10
    async def send(self, interaction: discord.Interaction, bot, command, copy):
        # fuse commands pass a list in the format of [str, fnf_data.Fusion] as the command paramenter
        if type(command) is list:
            self.command = command
            self.command_type = "fuse"
            self.message_text = command[0]
            self.data = [command[1]]
        else:
            self.command = command
            self.command_type = command.command_type
            self.message_text = self.command.get_message_text()
            self.data = self.command.results
        self.cosmetic_form_select_menu = None
        self.selected_cosmetic_form = "<default>"
        self.selected_form_options_start = 0
        self.selected_form_options_end = 0
        self.next_form_list_option_name = None
        self.bot = bot
        self.copy = copy
        self.select_result_menu = None
        self.sort_select_menu = None
        self.reverse_sort = False
        if self.command_type == "pokemon":
            self.current_sort_method = "pokedex"
        else:
            self.current_sort_method = "name"
        self.create_sort_select_menu()
        if self.command_type in ["pokemon", "move"]:
            self.current_sort_function, self.reverse_sort_by_default = self.sort_select_menu.get_sort_function(self.current_sort_method)
        else:
            self.current_sort_function = lambda x: x.name
            self.reverse_sort_by_default = False
        self.view_mode = "embed"
        if len(self.data) == 1:
            self.selected_index = 0
            self.set_selected_results()
            self.set_cosmetic_forms_menu_options_indexes(True)
        else:
            self.selected_index = None
            self.selected_results = {}
        self.command_user = interaction.user
        self.timeout = 43200
        self.number_of_pages = max(math.ceil(len(self.data) / self.sep), 1)
        await interaction.response.defer()
        self.create_select_result_menu()
        self.message = await interaction.followup.send(view=self, ephemeral=self.copy)
        await self.sort()

    async def sort(self):
        reverse = self.reverse_sort_by_default
        if self.reverse_sort:
            reverse = not reverse
        self.data = sorted(self.data, key=self.current_sort_function, reverse=reverse)
        self.update_data()
        await self.update_message()

    def update_data(self):
        file_text = ""
        for item in self.data:
            file_text += item.to_text_one_line() + "\n"
        file_text = file_text.strip()
        self.results_file = self.bot.turn_into_file(file_text)
        self.results_image = ready_image(make_image(make_mobile_list(self.data)))

    def create_select_result_menu(self):
        if self.select_result_menu is not None:
            return
        options = []
        from_item, until_item = self.get_data_slices()
        for i, value in enumerate(self.data[from_item:until_item]):
            index = i + from_item
            options.append(discord.SelectOption(label=value.name, value=str(index)))
        options.append(discord.SelectOption(label="Random", value="random"))
        self.select_result_menu = ResultsSelectMenu(options)
        self.add_item(self.select_result_menu)

    def destroy_select_result_menu(self):
        if self.select_result_menu is not None:
            self.remove_item(self.select_result_menu)
            self.select_result_menu = None

    def create_sort_select_menu(self):
        if self.command_type not in ["pokemon", "move"]:
            return
        if self.sort_select_menu is not None:
            return
        self.sort_select_menu = SortSelectMenu(self.command_type)
        self.add_item(self.sort_select_menu)

    def destroy_sort_select_menu(self):
        if self.sort_select_menu is not None:
            self.remove_item(self.sort_select_menu)
            self.sort_select_menu = None

    def create_cosmetic_form_select_menu(self):
        if self.command_type != "pokemon":
            return
        if self.cosmetic_form_select_menu is not None:
            return
        if len(self.selected_results["cosmetic forms"]) == 0:
            return
        self.cosmetic_form_select_menu = CosmeticFormSelectMenu(self.selected_results["cosmetic forms"], self.selected_form_options_start, self.selected_form_options_end, self.next_form_list_option_name)
        self.add_item(self.cosmetic_form_select_menu)

    def destroy_cosmetic_form_select_menu(self):
        if self.cosmetic_form_select_menu is not None:
            self.remove_item(self.cosmetic_form_select_menu)
            self.cosmetic_form_select_menu = None

    async def on_timeout(self):
        await self.destroy()

    async def destroy(self):
        active_command_views.remove(self)
        for item in self.children:
            item.disabled = True
        await self.update_message(True)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] in ["happyIvy_button"]:
            if interaction.user == self.command_user:
                await interaction.response.send_message("Ivysaur says hi!", ephemeral=True)
                return False
            elif commands_locked:
                await interaction.response.send_message("This command can't be copied right now.", ephemeral=True)
                return False
            return True
        if interaction.user != self.command_user:
            await interaction.response.send_message("You can't interact with someone else's command. Press the Ivysaur button to create your own copy of this command.", ephemeral=True)
            return False
        return True

    def create_embed(self):
        title = f"Data (Page {self.current_page} of {self.number_of_pages})"
        embed = discord.Embed(title=title)
        for item in self.get_current_page_data():
            name, summary = item.get_name_and_summary()
            embed.add_field(name=name, value=summary, inline=False)
        return embed

    async def update_message(self, skip_button_update=False):
        if skip_button_update == False:
            self.update_buttons()
        self.update_data()
        if self.selected_index is None:
            if self.view_mode == "embed":
                await self.message.edit(content=self.message_text, embed=self.create_embed(), attachments=[], view=self)
            elif self.view_mode == "file":
                await self.message.edit(content=self.message_text, embed=None, attachments=[self.results_file], view=self)
            elif self.view_mode == "image":
                await self.message.edit(content=self.message_text, embed=None, attachments=[self.results_image], view=self)
        else:
            self.set_selected_results()
            if self.view_mode == "embed":
                await self.message.edit(content=self.message_text, embed=self.selected_results["embed"], attachments=[], view=self)
            elif self.view_mode == "file":
                await self.message.edit(content=self.message_text, embed=None, attachments=[self.selected_results["file"]], view=self)
            elif self.view_mode == "image":
                await self.message.edit(content=self.message_text, embed=None, attachments=[self.selected_results["image"]], view=self)

    def update_buttons(self):
        self.destroy_select_result_menu()
        if self.selected_index is not None:
            self.destroy_sort_select_menu()
            self.reverse_sort_button.disabled = True
            self.back_to_results_button.disabled = False
            self.last_page_button.disabled = True
            self.next_page_button.disabled = True
            self.first_page_button.disabled = True
            self.previous_page_button.disabled = True
            if self.view_mode == "image":
                self.destroy_cosmetic_form_select_menu()
                self.image_view_button.disabled = True
                self.file_view_button.disabled = False
                self.embed_view_button.disabled = False
            elif self.view_mode == "file":
                self.destroy_cosmetic_form_select_menu()
                self.image_view_button.disabled = False
                self.file_view_button.disabled = True
                self.embed_view_button.disabled = False
            elif self.view_mode == "embed":
                self.create_cosmetic_form_select_menu()
                self.image_view_button.disabled = False
                self.file_view_button.disabled = False
                self.embed_view_button.disabled = True
        else:
            self.create_sort_select_menu()
            self.create_select_result_menu()
            self.destroy_cosmetic_form_select_menu()
            self.back_to_results_button.disabled = True
            self.reverse_sort_button.disabled = False
            if self.view_mode == "image":
                self.image_view_button.disabled = True
                self.last_page_button.disabled = True
                self.next_page_button.disabled = True
                self.first_page_button.disabled = True
                self.previous_page_button.disabled = True
            else:
                self.image_view_button.disabled = False
            if self.view_mode == "file":
                self.file_view_button.disabled = True
                self.last_page_button.disabled = True
                self.next_page_button.disabled = True
                self.first_page_button.disabled = True
                self.previous_page_button.disabled = True
            else:
                self.file_view_button.disabled = False
            if self.view_mode == "embed":
                self.embed_view_button.disabled = True
                self.last_page_button.disabled = False
                self.next_page_button.disabled = False
                self.first_page_button.disabled = False
                self.previous_page_button.disabled = False
                if self.current_page == 1:
                    self.first_page_button.disabled = True
                    self.previous_page_button.disabled = True
                if self.current_page == self.number_of_pages:
                    self.last_page_button.disabled = True
                    self.next_page_button.disabled = True
            else:
                self.embed_view_button.disabled = False
        if self.command_type == "fuse":
            self.back_to_results_button.disabled = True
            self.reverse_sort_button.disabled = True

    def get_data_slices(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == self.number_of_pages:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return from_item, until_item

    def get_current_page_data(self):
        from_item, until_item = self.get_data_slices()
        return self.data[from_item:until_item]

    def set_cosmetic_forms_menu_options_indexes(self, start_at_zero=False):
        if start_at_zero:
            self.selected_form_options_start = 0
        else:
            self.selected_form_options_start += 24
        if self.selected_form_options_start >= len(self.selected_results["cosmetic forms"]):
            self.selected_form_options_start = 0
        self.selected_form_options_end = self.selected_form_options_start + 24
        if self.selected_form_options_end > len(self.selected_results["cosmetic forms"]):
            self.selected_form_options_end = len(self.selected_results["cosmetic forms"])
        next_page_start = self.selected_form_options_start + 24
        if next_page_start >= len(self.selected_results["cosmetic forms"]):
            next_page_start = 0
        next_page_end = next_page_start + 24
        if next_page_end > len(self.selected_results["cosmetic forms"]):
            next_page_end = len(self.selected_results["cosmetic forms"])
        if next_page_start == 0 and self.selected_form_options_start == 0:
            self.next_form_list_option_name = None
        else:
            self.next_form_list_option_name = f"(View sprites {next_page_start+1}-{next_page_end})"
        self.destroy_cosmetic_form_select_menu()
        self.create_cosmetic_form_select_menu()

    def set_selected_results(self):
        if self.command_type == "pokemon":
            embed, cosmetic_forms = self.data[self.selected_index].to_embed(self.selected_cosmetic_form)
        else:
            embed, cosmetic_forms = self.data[self.selected_index].to_embed()
        self.selected_results = {"embed": embed,
                                 "cosmetic forms": cosmetic_forms,
                                 "file": self.bot.turn_into_file(self.data[self.selected_index].to_text()),
                                 "image": ready_image(make_image(self.data[self.selected_index].to_image_text()))}

    @discord.ui.button(label=" |< ", style=discord.ButtonStyle.blurple, custom_id="first_page_button")
    async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        await self.update_message()

    @discord.ui.button(label="  <  ", style=discord.ButtonStyle.blurple, custom_id="previous_page_button")
    async def previous_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message()

    @discord.ui.button(label="", style=discord.ButtonStyle.green, emoji="<:happyivy:666673253414207498>", custom_id="happyIvy_button")
    async def happy_ivy_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await create_pagination_view(interaction, self.bot, self.command, True)
        await self.update_message()
        
    @discord.ui.button(label="  >  ", style=discord.ButtonStyle.blurple, custom_id="next_page_button")
    async def next_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message()

    @discord.ui.button(label=" >| ", style=discord.ButtonStyle.blurple, custom_id="last_page_button")
    async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.number_of_pages
        await self.update_message()

    @discord.ui.button(label="Reverse sort", style=discord.ButtonStyle.blurple, custom_id="reverse_sort_button")
    async def reverse_sort_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.reverse_sort = not self.reverse_sort
        await self.sort()
        
    @discord.ui.button(label="Embed", style=discord.ButtonStyle.grey, custom_id="view_embed_button")
    async def embed_view_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "embed"
        await self.update_message()

    @discord.ui.button(label="File", style=discord.ButtonStyle.grey, custom_id="view_file_button")
    async def file_view_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "file"
        await self.update_message()

    @discord.ui.button(label="Image", style=discord.ButtonStyle.grey, custom_id="view_image_button")
    async def image_view_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "image"
        await self.update_message()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, custom_id="back_to_results_button")
    async def back_to_results_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.selected_index = None
        self.selected_results = {}
        self.selected_cosmetic_form = "<default>"
        self.selected_form_options_start = 0
        self.selected_form_options_end = 0
        await self.update_message()

    async def respond_to_results_select_menu(self, interaction: discord.Interaction, select_item: discord.ui.select):
        await interaction.response.defer()
        selected = select_item[0]
        if len(self.data) > 0:
            if selected == "random":
                self.selected_index = random.randint(0, len(self.data)-1)
            else:
                self.selected_index = int(selected)
        self.set_selected_results()
        self.set_cosmetic_forms_menu_options_indexes(True)
        await self.update_message()

    async def respond_to_sort_select_menu(self, interaction: discord.Interaction, select_item: discord.ui.select):
        await interaction.response.defer()
        self.current_sort_method = select_item[0]
        self.current_sort_function, self.reverse_sort_by_default = self.sort_select_menu.get_sort_function(self.current_sort_method)
        await self.sort()

    async def respond_to_cosmetic_form_select_menu(self, interaction: discord.Interaction, select_item: discord.ui.select):
        await interaction.response.defer()
        if select_item[0] == "<nextpage>":
            self.set_cosmetic_forms_menu_options_indexes()
        else:
            self.selected_cosmetic_form = select_item[0]
            self.set_selected_results()
        await self.update_message()

class ResultsSelectMenu(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Select an option to view details.", min_values=0)
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_results_select_menu(interaction, self.values)

class SortSelectMenu(discord.ui.Select):
    def __init__(self, command_type):
        super().__init__(placeholder="Select a sort method.")
        if command_type == "pokemon":
            options = [discord.SelectOption(label="Dex", value="pokedex"),
                       discord.SelectOption(label="Name", value="name"),
                       discord.SelectOption(label="Ladder tier", value="ladder"),
                       discord.SelectOption(label="Draft tier", value="draft"),
                       discord.SelectOption(label="HP", value="hp"),
                       discord.SelectOption(label="Attack", value="atk"),
                       discord.SelectOption(label="Defense", value="def"),
                       discord.SelectOption(label="Special attack", value="spa"),
                       discord.SelectOption(label="Special defense", value="spd"),
                       discord.SelectOption(label="Speed", value="spe"),
                       discord.SelectOption(label="BST", value="bst"),
                       discord.SelectOption(label="Height", value="height"),
                       discord.SelectOption(label="Weight", value="weight")]
        elif command_type == "move":
            options = [discord.SelectOption(label="Name", value="name"),
                       discord.SelectOption(label="Power", value="power"),
                       discord.SelectOption(label="Accuracy", value="accuracy"),
                       discord.SelectOption(label="PP", value="pp"),
                       discord.SelectOption(label="Crit Rate", value="crit rate"),
                       discord.SelectOption(label="Priority", value="priority"),
                       discord.SelectOption(label="Z-Power", value="zpower")]
        self.options = options
        self.sort_functions = {"name": [lambda x: x.name, False],
                               "pokedex": [lambda x: self.dex_sort(x), False],
                               "ladder": [lambda x: LADDER_TIERS[x.ladder_tier], False],
                               "draft": [lambda x: SORT_TIERS[x.tier.upper()], False],
                               "hp": [lambda x: x.stats["HP"], True],
                               "atk": [lambda x: x.stats["ATK"], True],
                               "def": [lambda x: x.stats["DEF"], True],
                               "spa": [lambda x: x.stats["SPA"], True],
                               "spd": [lambda x: x.stats["SPD"], True],
                               "spe": [lambda x: x.stats["SPE"], True],
                               "bst": [lambda x: x.stats["BST"], True],
                               "height": [lambda x: x.heightm, False],
                               "power": [lambda x: x.power, True],
                               "accuracy": [lambda x: x.accuracy, True],
                               "pp": [lambda x: x.pp, True],
                               "crit rate": [lambda x: x.crit_ratio, True],
                               "priority": [lambda x: x.priority, True],
                               "zpower": [lambda x: x.zpower, True]}

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_sort_select_menu(interaction, self.values)

    def get_sort_function(self, value):
        value = self.sort_functions[value]
        return value[0], value[1]

    def dex_sort(self, mon):
        # fnf custommons
        if mon.filter_rule_ignored == False and mon.dex < 0:
            return abs(mon.dex) + 1000
        if mon.filter_rule_new_gens:
            return mon.dex + 1000
        if mon.filter_rule_ignored:
            return abs(mon.dex) + 2500
        return mon.dex

class CosmeticFormSelectMenu(discord.ui.Select):
    def __init__(self, forms, start, end, next_page_name):
        super().__init__(placeholder="Select a cosmetic form.")
        options = [discord.SelectOption(label=form, value=form) for form in forms]
        if len(options) == 0:
            options = [discord.SelectOption(label="Default", value="<default>")]
        else:
            options = options[start:end]
        if next_page_name is not None:
            options.append(discord.SelectOption(label=next_page_name, value="<nextpage>"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_cosmetic_form_select_menu(interaction, self.values)


# saurbot check functions go here
def check_saurbot_permissions(interaction: discord.Interaction):
    return interaction.user.id in guild_preferences[interaction.guild.id].saurbot_managers or interaction.user.guild_permissions.administrator

# DEV_ID and NOEL_ID are initialized in SaurBot.py when the program starts
def check_is_noob(interaction: discord.Interaction):
    return interaction.user.id == DEV_ID

def check_is_nole(interaction: discord.Interaction):
    return interaction.user.id == NOEL_ID

def check_is_noob_or_nole(interaction: discord.Interaction):
    return check_is_noob(interaction) or check_is_nole(interaction)

async def ephemeral_error_message(interaction: discord.Interaction, error):
    saurbot_functions.timelog(str(error))
    await interaction.response.send_message(f"Something went wrong. Make sure you have permission to use this command.", ephemeral=True)

async def destroy_all_command_views():
    for item in active_command_views:
        await item.destroy()