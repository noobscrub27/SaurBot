import fnf_data
import re
import copy
import math
import os
import datetime
import html
import saurbot_functions

SUFFICIENT_DATA_SIZE = 4

NATURES = ["Hardy","Lonely","Brave","Adamant","Naughty",
           "Bold","Docile","Relaxed","Impish","Lax",
           "Timid","Hasty","Serious","Jolly","Naive",
           "Modest","Mild","Quiet","Bashful","Rash",
           "Calm","Gentle","Sassy","Careful","Quirky"]

POKEMON_ATTRIBUTES = {
    "timestamps": [],
    "date": [],
    "wins": {"total": [], "average": []},
    "differential": {"total": [], "average": []},
    "kos": {"total": [], "average": []},
    "faints": {"total": [], "average": []},
    "turns": {"total": [], "average": []},
    "active turns": {"total": [], "average": [], "per game turn": []},
    "damage dealt": {"total": [], "average": [], "per game turn": []},
    "active damage": {"total": [], "average": [], "per game turn": [], "per active turn": []},
    "direct damage dealt": {"total": [], "average": [], "per game turn": [], "per active turn": []},
    "indirect damage dealt": {"total": [], "average": [], "per game turn": []},
    "damage taken": {"total": [], "average": [], "per game turn": [], "per active turn": []},
    "healing given": {"total": [], "average": [], "per game turn": [], "per active turn": []},
    "healing received": {"total": [], "average": [], "per game turn": [], "per active turn": []}
}

transformation_items = {"Abomasite": ["Abomasnow", "Abomasnow-Mega"],
                        "Absolite": ["Absol", "Absol-Mega"],
                        "Aerodactylite": ["Aerodactyl", "Aerodactyl-Mega"],
                        "Aggronite": ["Aggron", "Aggron-Mega"],
                        "Alakazite": ["Alakazam", "Alakazam-Mega"],
                        "Altarianite": ["Altaria", "Altaria-Mega"],
                        "Ampharosite": ["Ampharos", "Ampharos-Mega"],
                        "Audinite": ["Audino", "Audino-Mega"],
                        "Banettite": ["Banette", "Banette-Mega"],
                        "Beedrillite": ["Bedrill", "Bedrill-Mega"],
                        "Blastoisinite": ["Blastoise", "Blastoise-Mega"],
                        "Blazikenite": ["Blaziken", "Blaziken-Mega"],
                        "Cameruptite": ["Camerupt", "Camerupt-Mega"],
                        "Charizardite X": ["Charizard", "Charizard-Mega-X"],
                        "Charizardite Y": ["Charizard", "Charizard-Mega-Y"],
                        "Diancite": ["Diancie", "Diancie-Mega"],
                        "Galladite": ["Gallade", "Gallade-Mega"],
                        "Garchompite": ["Garchomp", "Garchomp-Mega"],
                        "Gardevoirite": ["Gardevoir", "Gardevoir-Mega"],
                        "Gengarite": ["Gengar", "Gengar-Mega"],
                        "Glalitite": ["Glalie", "Glalie-Mega"],
                        "Goodrite": ["Goodra", "Goodra-Mega"],
                        "Gyaradosite": ["Gyarados", "Gyarados-Mega"],
                        "Heracronite": ["Heracross", "Heracross-Mega"],
                        "Houndoominite": ["Houndoom", "Houndoom-Mega"],
                        "Kangaskhanite": ["Kangaskhan", "Kangaskhan-Mega"],
                        "Latiasite": ["Latias", "Latias-Mega"],
                        "Latiosite": ["Latios", "Latios-Mega"],
                        "Lopunnite": ["Lopunny", "Lopunny-Mega"],
                        "Lucarionite": ["Lucario", "Lucario-Mega"],
                        "Magnezite": ["Magnezone", "Magnezone-Mega"],
                        "Manectite": ["Manectric", "Manectric-Mega"],
                        "Mawilite": ["Mawile", "Mawile-Mega"],
                        "Medichamite": ["Medicham", "Medicham-Mega"],
                        "Metagrossite": ["Metagross", "Metagross-Mega"],
                        "Mewtwonite X": ["Mewtwo", "Mewtwo-Mega-X"],
                        "Mewtwonite Y": ["Mewtwo", "Mewtwo-Mega-Y"],
                        "Pidgeotite": ["Pidgeot", "Pidgeot-Mega"],
                        "Pinsirite": ["Pinsir", "Pinsir-Mega"],
                        "Sablenite": ["Sableye", "Sableye-Mega"],
                        "Salamencite": ["Salamence", "Salamence-Mega"],
                        "Sceptilite": ["Sceptile", "Sceptile-Mega"],
                        "Scizorite": ["Scizor", "Scizor-Mega"],
                        "Sharpedonite": ["Sharpedo", "Sharpedo-Mega"],
                        "Slowbronite": ["Slowbro", "Slowbro-Mega"],
                        "Steelixite": ["Steelix", "Steelix-Mega"],
                        "Swampertite": ["Swampert", "Swampert-Mega"],
                        "Tyranitarite": ["Tyranitar", "Tyranitar-Mega"],
                        "Venusaurite": ["Venusaur", "Venusaur-Mega"],
                        "Alarixite": ["Gyarados-Alarix", "Gyarados-Mega-Alarix"],
                        "Cofagrigite": ["Cofagrigus", "Cofagrigus-Mega"],
                        "Delta Lucarionite": ["Lucario-Delta", "Lucario-Delta-Mega"],
                        "Furretite": ["Furret", "Furret-Mega"],
                        "Starmite": ["Starmie", "Starmie-Mega"],
                        "Sunflorite": ["Sunflora", "Sunflora-Mega"],
                        "Cerise Orb": ["Cherrim", "Cherrim-Primal"],
                        "Blue Orb": ["Phione", "Phione-Primal"],
                        "Red Orb": ["Groudon", "Groudon-Primal"],
                        "Teal Orb": ["Kyogre", "Kyogre-Primal"],
                        "Bug Memory": ["Silvally", "Silvally-Bug"],
                        "Dark Memory": ["Silvally", "Silvally-Dark"],
                        "Dragon Memory": ["Silvally", "Silvally-Dragon"],
                        "Electric Memory": ["Silvally", "Silvally-Electric"],
                        "Fairy Memory": ["Silvally", "Silvally-Fairy"],
                        "Fighting Memory": ["Silvally", "Silvally-Fighting"],
                        "Fire Memory": ["Silvally", "Silvally-Fire"],
                        "Flying Memory": ["Silvally", "Silvally-Flying"],
                        "Ghost Memory": ["Silvally", "Silvally-Ghost"],
                        "Grass Memory": ["Silvally", "Silvally-Grass"],
                        "Ground Memory": ["Silvally", "Silvally-Ground"],
                        "Ice Memory": ["Silvally", "Silvally-Ice"],
                        "Poison Memory": ["Silvally", "Silvally-Poison"],
                        "Psychic Memory": ["Silvally", "Silvally-Psychic"],
                        "Rock Memory": ["Silvally", "Silvally-Rock"],
                        "Steel Memory": ["Silvally", "Silvally-Steel"],
                        "Water Memory": ["Silvally", "Silvally-Water"],
                        "Draco Plate": ["Arceus", "Arceus-Dragon"],
                        "Dread Plate": ["Arceus", "Arceus-Dark"],
                        "Earth Plate": ["Arceus", "Arceus-Ground"],
                        "Fist Plate": ["Arceus", "Arceus-Fighting"],
                        "Flame Plate": ["Arceus", "Arceus-Fire"],
                        "Icicle Plate": ["Arceus", "Arceus-Ice"],
                        "Insect Plate": ["Arceus", "Arceus-Bug"],
                        "Iron Plate": ["Arceus", "Arceus-Steel"],
                        "Meadow Plate": ["Arceus", "Arceus-Grass"],
                        "Mind Plate": ["Arceus", "Arceus-Psychic"],
                        "Pixie Plate": ["Arceus", "Arceus-Fairy"],
                        "Sky Plate": ["Arceus", "Arceus-Flying"],
                        "Splash Plate": ["Arceus", "Arceus-Water"],
                        "Spooky Plate": ["Arceus", "Arceus-Ghost"],
                        "Stone Plate": ["Arceus", "Arceus-Rock"],
                        "Toxic Plate": ["Arceus", "Arceus-Poison"],
                        "Zap Plate": ["Arceus", "Arceus-Electric"],
                        "Griseous Orb": ["Giritina", "Giritina-Origin"],
                        "Ultranecrozium Z": ["Necrozma", "Necrozma-Ultra"],
                        "Trevenantite": ["Trevenant", "Trevenant-Mega"],
                        "FnFSablenite X": ["Sableye-FnF", "Sableye-FnF-Mega-X"],
                        "FnFSablenite Y": ["Sableye-FnF", "Sableye-FnF-Mega-Y"],
                        "Rapidashite": ["Rapidash", "Rapidash-Mega"],
                        "Hypnite": ["Hypno", "Hypno-Mega"],
                        }

def replace_alias(species, allow_nicknames=False):
    try:
        return fnf_data.pokemon.alias_search(saurbot_functions.only_a_to_z(species)).name
    except KeyError:
        if allow_nicknames:
            return species
    raise ValueError(f"{species} is not a valid pokemon species.")

POKEMON_NAME_REGEX_1 = re.compile(r"[\|\s\[\]\,\u202e]+")
POKEMON_NAME_REGEX_2 = re.compile(r"[\u0300-\u036f\u0483-\u0489\u0610-\u0615\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06ED\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]{3,}")
POKEMON_NAME_REGEX_3 = re.compile(r"[\u239b-\u23b9]")
def pokemon_name_formatter(name):
    name = re.sub(POKEMON_NAME_REGEX_1, " ", name).strip()
    name = name[:18].strip()
    name = re.sub(POKEMON_NAME_REGEX_2, "", name)
    name = re.sub(POKEMON_NAME_REGEX_3, "", name)
    return name

def team_analyzer(text):
    text = text.split("\n")
    # because pokemon are counted as complete at empty lines this ensures that the last pokemon gets added
    text.append("")
    last_line = ""
    current_line = ""
    team = []
    stats_dict = {"HP": 0, "ATK": 0, "DEF": 0, "SPA": 0, "SPD": 0, "SPE": 0}
    empty_pokemon = {"nickname": "",
                     "species": "",
                     "evs": copy.deepcopy(stats_dict),
                     "ivs": copy.deepcopy(stats_dict),
                     "nature": "Serious",
                     "item": "",
                     "ability": "",
                     "moves": [],
                     "level": 100}
    current_pokemon = copy.deepcopy(empty_pokemon)
    header_has_been_read = False
    for l in text:
        # the header (aka the line with the pokemon species, nickname and item) is always the first line of each stat block
        # but, the header is the most convenient stopping point because each stat block always has one, and its always in the same convenient place (the start)
        # but if we stop at the header, we miss the rest of the stats
        # the solution is to have a variable that tracks whether the header has been seen yet
        # if True, that means we're actually at the next pokemon's header, and its time to stop reading the first pokemon's header
        line = l.strip()
        # if the line is blank
        if len(line) == 0:
            # ignore duplicate whitespace
            if last_line == "Whitespace":
                continue
            # set this line to whitespace
            current_line = "Whitespace"
            if header_has_been_read:
                team.append(copy.deepcopy(current_pokemon))
                current_pokemon = copy.deepcopy(empty_pokemon)
                header_has_been_read = False
        elif line.startswith("Shiny: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Shiny"
        elif line.startswith("Hidden Power: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Hidden Power"
        elif line.startswith("Tera Type: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Tera Type"
        elif line.startswith("Happiness: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Happiness"
        elif line.startswith("EVs: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "EVs"
            evs_line = "".join(line.split())
            evs_list = evs_line.removeprefix("EVs:").split("/")
            for e in evs_list:
                ev = e.upper()[-3:] if e.endswith("HP") == False else "HP"
                value = int(e.upper().removesuffix(ev))
                current_pokemon["evs"][ev] = value
        elif line.startswith("IVs: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "IVs"
            ivs_line = "".join(line.split())
            ivs_list = ivs_line.removeprefix("IVs:").split("/")
            for i in ivs_list:
                iv = i.upper()[-3:] if i.endswith("HP") == False else "HP"
                value = int(i.upper().removesuffix(iv))
                current_pokemon["ivs"][iv] = value
        elif line.endswith("Nature"):
            current_line = "Nature"
            nature = line.removesuffix("Nature").strip()
            if nature in NATURES:
                current_pokemon["nature"] = nature
        elif line.startswith("Ability: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Ability"
            current_pokemon["ability"] = line.removeprefix("Ability: ")
        elif line.startswith("Level: ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Level"
            current_pokemon["level"] = int(line.removeprefix("Level: ").strip())
        elif line.startswith("- ") and line.replace("(", "").replace(")", "") == line:
            current_line = "Move"
            current_pokemon["moves"].append(line.removeprefix("- "))
        else:
            item = re.search('(@ )[\w\-\' ]+$', line)
            if item is None:
                item = "(No item)"
            else:
                item = item.group(0).removeprefix("@ ")
            nick_and_species = line.removesuffix("@ "+ item).strip()
            nick_and_species = nick_and_species.removesuffix("(F)")
            nick_and_species = nick_and_species.removesuffix("(M)")
            nick_and_species = nick_and_species.strip()
            pokemon_species = re.search('\(.+\)$', nick_and_species)
            if pokemon_species is None:
                pokemon_species = nick_and_species
                pokemon_nickname = ""
            else:
                pokemon_species = pokemon_species.group(0)
                pokemon_nickname = nick_and_species.removesuffix(pokemon_species).strip()
                pokemon_species = pokemon_species.removeprefix("(").removesuffix(")")
            if item in transformation_items:
                if transformation_items[item][0] == pokemon_species:
                    pokemon_species = transformation_items[item][1]
            pokemon_species = replace_alias(pokemon_species)
            # weird stuff happens with some pokemon that have different forms, such as oricorio and rotom
            if pokemon_nickname == "":
                if pokemon_species.endswith("-Alola"):
                    pokemon_nickname = pokemon_species.removesuffix("-Alola")
                elif pokemon_species.startswith("Oricorio"):
                    pokemon_nickname = "Oricorio"
                elif pokemon_species.startswith("Rotom"):
                    pokemon_nickname = "Rotom"
            current_pokemon["nickname"] = pokemon_name_formatter(pokemon_nickname)
            current_pokemon["species"] = pokemon_species
            current_pokemon["item"] = item
            header_has_been_read = True
        last_line = current_line
        current_line = ""
    return team

pokemon = {}
replays = {}

# the lowest level the lowest-base HP non-shedinja pokemon is guaranteed to have 16 HP with 0 EVs and 0 IVs. important for rounding\
# use saurbot to get this data automatically in the future
LOWEST_LEVEL_FOR_16_HEALTH = 5
tracked_tier_names = ["[Gen 7] OU", "[Gen 7] UU", "[Gen 7] RU", "[Gen 7] NU", "[Gen 7] NFE", "[Gen 7] Draft"]
STATUS_SHORTHANDS = ["fnt", "psn", "tox", "par", "frz", "brn", "slp"]
PARTIAL_TRAPPING_MOVES = ["Bind", "Bubble Prison", "Clamp", "Fire Spin", "Infestation", "Magma Storm", "Sand Tomb", "Shadow Hold", "Silk Snare", "Spider Web", "Spore Slash", "Whirlpool", "Wrap"]
FUTURE_SIGHT_MOVES = ["Future Sight", "Doom Desire", "Prophetic Asteroid", "Shadow Doomsday"]
HEALING_WISH_MOVES = ["Healing Wish", "Lunar Dance"]
HEALING_WISH_Z_MOVES = ["Memento", "Parting Shot"]
LEECH_SEED_MOVES = ["Leech Seed", "Biddy Bud", "Shadow Seed", "Sappy Seed"]
HAZARD_MOVES = ["Stealth Rock", "Spikes", "Toxic Spikes"]
POISON_MOVES = ["Barb Barrage", "Cross Poison", "Dire Claw", "Fling", "G-Max Befuddle", "G-Max Malodor", "G-Max Stun Shock", "Gunk Shot", "Mortal Spin", "Noxious Torque", "Poison Fang", "Poison Gas", "Poison Jab", "Poison Powder", "Poison Sting", "Poison Tail", "Psycho Shift", "Secret Power", "Shell Side Arm", "Sludge", "Sludge Bomb", "Sludge Wave", "Smog", "Toxic", "Toxic Thread", "Twineedle", "Fallout", "Shadow Fumes", "Shadow Spell"]
FREEZE_MOVES = ["Blizzard", "Freeze-Dry", "Freezing Glare", "Ice Beam", "Ice Fang", "Ice Punch", "Powder Snow", "Psycho Shift", "Secret Power", "Shadow Chill", "Tri Attack", "Ice Drill", "Chilling Rime", "Icicle Crash", "Shadow Frost", "Shadow Spell"]
BURN_MOVES = ["Beak Blast", "Blaze Kick", "Blazing Torque", "Blue Flare", "Burning Jealousy", "Ember", "Fire Blast", "Fire Fang", "Fire Punch", "Flame Wheel", "Flamethrower", "Flare Blitz", "Fling", "Heat Wave", "Ice Burn", "Infernal Parade", "Inferno", "Lava Plume", "Psycho Shift", "Pyro Ball", "Sacred Fire", "Sandsear Storm", "Scald", "Scorching Sands", "Searing Shot", "Secret Power", "Shadow Fire", "Sizzly Slide", "Steam Eruption", "Tri Attack", "Will-O-Wisp", "Fiery Blossom", "Bombs Away", "Plasma Spin", "Shell Trap", "Shadow Cinder", "Shadow Fire", "Shadow Spell"]
SELF_HEALING_MOVES = ["Heal Order", "Lunar Blessing", "Milk Drink", "Moonlight", "Morning Sun", "Purify", "Recover", "Rest", "Roost", "Shore Up", "Slack Off", "Soft-Boiled", "Strength Sap", "Synthesis", "Kappo", "Aggregate", "Regroup", "Regroup2", "Parasitic Drain", "Present", "Shadow Bath", "Shadow Flame", "Shadow Glaze", "Shadow Glow", "Shadow Moon", "Shadow Moss", "Shadow Sprites", "Shadow Sun"]
TARGET_HEALING_MOVES = ["Floral Healing", "Heal Pulse", "Pollen Puff", "Present"]
SELF_HEALING_ITEMS = ["Leftovers", "Shell Bell", "Black Sludge"]
SELF_HEALING_ABILITIES = ["Baku Shield", "Cheek Pouch", "Ice Body", "Sunbathing", "Volt Absorb", "Poison Heal", "Rain Dish", "Water Absorb", "Flame Absorb", "Dream Feast", "Dry Skin", "Shadow Birch", "Shadow Conduction", "Shadow Convection", "Shadow Embers", "Shadow Hydraulics", "Shadow Ribbons", "Shadow Slush", "Shadow Sparks", "Dumpster Diving"]
SELF_HEALING_EFFECTS = ["drain", "Ingrain", "Aqua Ring", "[zeffect]"]
SELF_DESTRUCT_MOVES = ["Explosion", "Healing Wish", "Final Gambit", "Lunar Dance", "Z-Memento", "Misty Explosion", "Self-Destruct", "Shadow Roulette", "Present"]
POKEMON_SUFFIXES = ["-Alola"]
def invert(result, inverse):
    if inverse:
        if result == True:
            return False
        return True
    return result

def compare_value(val, target, comparison):
    if comparison == "=" and val == target:
        return True
    elif comparison == ">" and val > target:
        return True
    elif comparison == "<" and val < target:
        return True
    elif comparison == ">=" and val >= target:
        return True
    elif comparison == "<=" and val <= target:
        return True
    return False

class InvalidReplayError(Exception):
    def __init__(self, description = "An unknown error occurred", turn=0, halt=True):
        self.description = description
        self.turn = turn
        self.halt = halt
    def __str__(self):
        return f"InvalidReplayError: {self.description} (Occured on turn {self.turn})"


class Tier():
    def __init__(self):
        self.name = ""
        self.pokemon = {}
        self.battles = []
        self.trainers = {}
        #self.update_timestamps = [1714370961, 1714412061]
        self.update_timestamps = []

    def add_trainer(self, trainer):
        '''
        trainer_name = trainer.trainer
        if trainer_name not in self.trainers:
            self.trainers[trainer_name].append(Trainer(trainer_name))
        self.trainers[trainer_name].add_instance(trainer)
        '''
        for mon in trainer.team.values():
            self.add_pokemon(mon)

    def add_pokemon(self, mon):
        if mon.species not in self.pokemon:
            self.pokemon[mon.species] = Pokemon(mon.species)
        self.pokemon[mon.species].add_instance(mon)

    def add_battle(self, battle):
        self.battles.append(battle)
        for trainer in battle.teams:
            self.add_trainer(trainer)

    def get_species_with_sufficient_data(self):
        return {mon: self.pokemon[mon] for mon in self.pokemon if len(self.pokemon[mon].instances) >= SUFFICIENT_DATA_SIZE}

    def get_all_pokemon_instances(self):
        instances = []
        for mon in self.pokemon.values():
            instances += mon.instances
        return instances

class Entity():
    def __init__(self):
        self.tier = None
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.instances = []
        self.winning_instances = []
        self.losing_instances = []

    def get_winrate(self):
        if self.games_played == 0:
            return 1
        else:
            return self.games_won / self.games_played

    def add_instance(self, thing):
        self.instances.append(thing)
        if thing.winner:
            self.games_won += 1
            self.winning_instances.append(thing)
        else:
            self.games_lost += 1
            self.losing_instances.append(thing)
        self.games_played += 1

class Pokemon(Entity):
    def __init__(self, species):
        super().__init__()
        self.species = species
        self.stats = copy.deepcopy(POKEMON_ATTRIBUTES)
        self.winning_stats = copy.deepcopy(POKEMON_ATTRIBUTES)
        self.losing_stats = copy.deepcopy(POKEMON_ATTRIBUTES)

    def add_instance(self, thing):
        super().add_instance(thing)
        self.stats = update_pokemon_stats(self.stats, thing)
        if thing.winner:
            self.winning_stats = update_pokemon_stats(self.winning_stats, thing)
        else:
            self.losing_stats = update_pokemon_stats(self.losing_stats, thing)

def update_pokemon_stats(stats_dict, mon):
    new_len = len(stats_dict["differential"]["total"]) + 1
    stats_dict["timestamps"].append(mon.timestamp)
    stats_dict["date"].append(datetime.datetime.fromtimestamp(stats_dict["timestamps"][-1]))
    if new_len == 1:
        stats_dict["wins"]["total"].append(int(mon.winner))
        stats_dict["wins"]["average"].append(stats_dict["wins"]["total"][-1])
        stats_dict["differential"]["total"].append(mon.differential)
        stats_dict["differential"]["average"].append(stats_dict["differential"]["total"][-1])
        stats_dict["kos"]["total"].append(mon.get_number_of_kos())
        stats_dict["kos"]["average"].append(stats_dict["kos"]["total"][-1])
        stats_dict["faints"]["total"].append(int(mon.check_fainted()))
        stats_dict["faints"]["average"].append(stats_dict["faints"]["total"][-1])
        stats_dict["turns"]["total"].append(mon.team.battle.turns)
        stats_dict["turns"]["average"].append(stats_dict["turns"]["total"][-1])
        stats_dict["active turns"]["total"].append(mon.active_turns)
        stats_dict["active turns"]["average"].append(stats_dict["active turns"]["total"][-1])
        stats_dict["active turns"]["per game turn"].append(mon.active_turns_per_turn)
        stats_dict["damage dealt"]["total"].append(mon.total_damage_dealt)
        stats_dict["damage dealt"]["average"].append(stats_dict["damage dealt"]["total"][-1])
        stats_dict["damage dealt"]["per game turn"].append(mon.total_damage_dealt_per_turn)
        stats_dict["active damage"]["total"].append(mon.active_damage)
        stats_dict["active damage"]["average"].append(stats_dict["active damage"]["total"][-1])
        stats_dict["active damage"]["per game turn"].append(mon.active_damage_per_turn)
        stats_dict["active damage"]["per active turn"].append(mon.active_damage_per_active_turn)
        stats_dict["direct damage dealt"]["total"].append(mon.direct_damage_dealt)
        stats_dict["direct damage dealt"]["average"].append(stats_dict["direct damage dealt"]["total"][-1])
        stats_dict["direct damage dealt"]["per game turn"].append(mon.direct_damage_dealt_per_turn)
        stats_dict["direct damage dealt"]["per active turn"].append(mon.direct_damage_dealt_per_active_turn)
        stats_dict["indirect damage dealt"]["total"].append(mon.indirect_damage_dealt)
        stats_dict["indirect damage dealt"]["average"].append(stats_dict["indirect damage dealt"]["total"][-1])
        stats_dict["indirect damage dealt"]["per game turn"].append(mon.indirect_damage_dealt_per_turn)
        stats_dict["damage taken"]["total"].append(mon.damage_taken)
        stats_dict["damage taken"]["average"].append(stats_dict["damage taken"]["total"][-1])
        stats_dict["damage taken"]["per game turn"].append(mon.damage_taken_per_turn)
        stats_dict["damage taken"]["per active turn"].append(mon.damage_taken_per_active_turn)
        stats_dict["healing given"]["total"].append(mon.healing_given)
        stats_dict["healing given"]["average"].append(stats_dict["healing given"]["total"][-1])
        stats_dict["healing given"]["per game turn"].append(mon.healing_given_per_turn)
        stats_dict["healing given"]["per active turn"].append(mon.healing_given_per_active_turn)
        stats_dict["healing received"]["total"].append(mon.healing_received)
        stats_dict["healing received"]["average"].append(stats_dict["healing received"]["total"][-1])
        stats_dict["healing received"]["per game turn"].append(mon.healing_received_per_turn)
        stats_dict["healing received"]["per active turn"].append(mon.healing_received_per_active_turn)
    else:
        stats_dict["wins"]["total"].append(stats_dict["wins"]["total"][-1]+int(mon.winner))
        stats_dict["wins"]["average"].append(stats_dict["wins"]["total"][-1]/new_len)
        stats_dict["differential"]["total"].append(stats_dict["differential"]["total"][-1]+mon.differential)
        stats_dict["differential"]["average"].append(stats_dict["differential"]["total"][-1]/new_len)
        stats_dict["kos"]["total"].append(stats_dict["kos"]["total"][-1]+mon.get_number_of_kos())
        stats_dict["kos"]["average"].append(stats_dict["kos"]["total"][-1]/new_len)
        stats_dict["faints"]["total"].append(stats_dict["faints"]["total"][-1]+int(mon.check_fainted()))
        stats_dict["faints"]["average"].append(stats_dict["faints"]["total"][-1]/new_len)
        stats_dict["turns"]["total"].append(stats_dict["turns"]["total"][-1]+mon.team.battle.turns)
        stats_dict["turns"]["average"].append(stats_dict["turns"]["total"][-1]/new_len)
        stats_dict["active turns"]["total"].append(stats_dict["active turns"]["total"][-1]+mon.active_turns)
        stats_dict["active turns"]["average"].append(stats_dict["active turns"]["total"][-1]/new_len)
        # this next line and lines like it undoes the average, adds the new data, then averages it again
        stats_dict["active turns"]["per game turn"].append(((stats_dict["active turns"]["per game turn"][-1]*(new_len-1))+mon.active_turns_per_turn)/new_len)
        stats_dict["damage dealt"]["total"].append(stats_dict["damage dealt"]["total"][-1]+mon.total_damage_dealt)
        stats_dict["damage dealt"]["average"].append(stats_dict["damage dealt"]["total"][-1]/new_len)
        stats_dict["damage dealt"]["per game turn"].append(((stats_dict["damage dealt"]["per game turn"][-1]*(new_len-1))+mon.total_damage_dealt_per_turn)/new_len)
        stats_dict["active damage"]["total"].append(stats_dict["active damage"]["total"][-1]+mon.active_damage)
        stats_dict["active damage"]["average"].append(stats_dict["active damage"]["total"][-1]/new_len)
        stats_dict["active damage"]["per game turn"].append(((stats_dict["active damage"]["per game turn"][-1]*(new_len-1))+mon.active_damage_per_turn)/new_len)
        stats_dict["active damage"]["per active turn"].append(((stats_dict["active damage"]["per active turn"][-1]*(new_len-1))+mon.active_damage_per_active_turn)/new_len)
        stats_dict["direct damage dealt"]["total"].append(stats_dict["direct damage dealt"]["total"][-1]+mon.direct_damage_dealt)
        stats_dict["direct damage dealt"]["average"].append(stats_dict["direct damage dealt"]["total"][-1]/new_len)
        stats_dict["direct damage dealt"]["per game turn"].append(((stats_dict["direct damage dealt"]["per game turn"][-1]*(new_len-1))+mon.direct_damage_dealt_per_turn)/new_len)
        stats_dict["direct damage dealt"]["per active turn"].append(((stats_dict["direct damage dealt"]["per active turn"][-1]*(new_len-1))+mon.direct_damage_dealt_per_active_turn)/new_len)
        stats_dict["indirect damage dealt"]["total"].append(stats_dict["indirect damage dealt"]["total"][-1]+mon.indirect_damage_dealt)
        stats_dict["indirect damage dealt"]["average"].append(stats_dict["indirect damage dealt"]["total"][-1]/new_len)
        stats_dict["indirect damage dealt"]["per game turn"].append(((stats_dict["indirect damage dealt"]["per game turn"][-1]*(new_len-1))+mon.indirect_damage_dealt_per_turn)/new_len)
        stats_dict["damage taken"]["total"].append(stats_dict["damage taken"]["total"][-1]+mon.damage_taken)
        stats_dict["damage taken"]["average"].append(stats_dict["damage taken"]["total"][-1]/new_len)
        stats_dict["damage taken"]["per game turn"].append(((stats_dict["damage taken"]["per game turn"][-1]*(new_len-1))+mon.damage_taken_per_turn)/new_len)
        stats_dict["damage taken"]["per active turn"].append(((stats_dict["damage taken"]["per active turn"][-1]*(new_len-1))+mon.damage_taken_per_active_turn)/new_len)
        stats_dict["healing given"]["total"].append(stats_dict["healing given"]["total"][-1]+mon.healing_given)
        stats_dict["healing given"]["average"].append(stats_dict["healing given"]["total"][-1]/new_len)
        stats_dict["healing given"]["per game turn"].append(((stats_dict["healing given"]["per game turn"][-1]*(new_len-1))+mon.healing_given_per_turn)/new_len)
        stats_dict["healing given"]["per active turn"].append(((stats_dict["healing given"]["per active turn"][-1]*(new_len-1))+mon.healing_given_per_active_turn)/new_len)
        stats_dict["healing received"]["total"].append(stats_dict["healing received"]["total"][-1]+mon.healing_received)
        stats_dict["healing received"]["average"].append(stats_dict["healing received"]["total"][-1]/new_len)
        stats_dict["healing received"]["per game turn"].append(((stats_dict["healing received"]["per game turn"][-1]*(new_len-1))+mon.healing_received_per_turn)/new_len)
        stats_dict["healing received"]["per active turn"].append(((stats_dict["healing received"]["per active turn"][-1]*(new_len-1))+mon.healing_received_per_active_turn)/new_len)
    return stats_dict


class Trainer(Entity):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

class Battle():
    def __init__(self, teams, timestamp, game_format, turns):
        self.game_format = game_format
        self.timestamp = 0
        self.teams = teams
        self.turns = turns
        for team in self.teams:
            team.battle = self
        self.change_timestamp(timestamp)

    def change_timestamp(self, timestamp):
        self.timestamp = timestamp
        for i, team in enumerate(self.teams):
            team.timestamp = timestamp+(i/10)
            for teammate in team.team.values():
                teammate.timestamp = team.timestamp
    def check_number_of_turns(self, target, comparison):
        return compare_value(self.turns, target, comparison)

    # unix timestamps for 1/1/2000 and 1/1/3000
    def check_date(self, start_date=946706400, end_date=32503701600):
        if self.timestamp > start_date and self.timestamp < end_date:
            return True
        return False


class Team():
    def __init__(self, player_number, trainer_name):
        self.team_index = 0
        self.timestamp = 0
        self.battle = None
        self.player_number = player_number
        self.trainer_name = trainer_name
        self.team = {}
        self.winner = False
        self.active_illusion = None
        self.elo = 1000
        # variables for replay parsing
        self.hazards = {"Stealth Rock": [],
                        "Spikes": [],
                        "Toxic Spikes": []}

    def get_teammate_from_nickname(self, nickname):
        if self.active_illusion is not None:
            nickname = self.active_illusion
        for teammate in self.team.values():
            # first half of the if statement checks for nickname, the second half checks for species
            if nickname == teammate.nickname or self.get_teammate_from_species(replace_alias(nickname, True)) == teammate:
                return teammate
        # do the nexted loop after the regular loop, since most of this time all this extra work will be unnecessary
        # this checks for pokemon that might not be identified because they're technically an alternate form of another pokemon
        # examples are Alolan pokemon. In battle, Ninetales-Alola shows up as just Ninetales, even though the teambuilder will show it as Ninetales-Alola
        # rotom and oricorio are other pokemon like this
        for teammate in self.team.values():
            pass

    def get_teammate_from_species(self, species):
        for teammate in self.team.values():
            if species == teammate.species:
                return teammate
            elif teammate.item in transformation_items:
                transformations = transformation_items[teammate.item]
                if teammate.species == transformations[1] and species == transformations[0]:
                    return teammate    

    def read_team(self, paste):
        team_data = team_analyzer(paste)
        for teammate in team_data:
            self.team[teammate['species']] = Combatant(self, teammate)

    def exists(self, species):
        self.get_teammate_from_species(species).exists = True

    def all_verify_existance(self):
        for teammate in self.team:
            self.team[teammate].verify_existance()

    def on_win(self):
        self.winner = True
        for teammate in self.team:
            self.team[teammate].winner = True

    def check_species(self, species, inverse=False):
        party = [mon.species.lower() for mon in self.team.values()]
        for s in species:
            if s.lower() in party:
                return invert(True, inverse)
        return invert(False, inverse)

    def check_win(self, inverse=False):
        return invert(self.winner, inverse)

    # this gets the number of pokemon that the opponent controls that have fainted
    def check_number_of_kos(self, target, comparison):
        for team in self.team.battle.teams:
            if team is not self:
                enemy_team = team
        number_of_kos = 0
        for mon in enemy_team.team.values():
            if mon.check_faint():
                number_of_kos += 1
        return compare_value(number_of_kos, target, comparison)

    # this gets the number of pokemon that the user controls that have fainted
    def check_number_of_faints(self, target, comparison):
        number_of_faints = 0
        for mon in self.team.values():
            if mon.check_fainted():
                number_of_faints += 1
        return compare_value(number_of_faints, target, comparison)

    def check_party_member(self, species, require_all=False, inverse=False):
        party = [mon.species.lower() for mon in self.team.values()]
        for s in species:
            if require_all:
                if s.lower() not in party:
                    return invert(False, inverse)
            else:
                if s.lower() in party:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_opponent_party_member(self, species, require_all=False, inverse=False):
        for team in self.battle.teams:
            if team is not self:
                enemy_team = team
        party = [mon.species.lower() for mon in enemy_team.team.values()]
        for s in species:
            if require_all:
                if s.lower() not in party:
                    return invert(False, inverse)
            else:
                if s.lower() in party:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_opponent_trainer(self, discord_ids, guild_id, inverse=False):
        for team in self.battle.teams:
            if team is not self:
                other_team_id = fnf_data.guild_preferences[guild_id].get_user_from_showdown(team.trainer_name).id
        for discord_id in discord_ids:
            if discord_id == other_team_discord_id:
                return invert(True, inverse)
        return invert(False, inverse)

    def check_number_of_turns(self, target, comparison):
        return self.battle.check_number_of_turns(target, comparison)

    def clean_up(self):
        self.active_disguise = None
        for mon in self.team:
            self.team[mon].clean_up()


class Combatant():
    def __init__(self, team, teammate_dict):
        self.team = team
        self.timestamp = 0
        self.nickname = teammate_dict["nickname"]
        self.species = teammate_dict["species"]
        self.evs = teammate_dict["evs"]
        self.ivs = teammate_dict["ivs"]
        self.nature = teammate_dict["nature"]
        self.item = teammate_dict["item"]
        self.ability = teammate_dict["ability"]
        self.moves = teammate_dict["moves"]
        self.level = teammate_dict["level"]
        self.kos = 0
        # differential rules:
        # tldr differential = kos - faints
        # fainting reduces differential by 1
        # KOing a pokemon increases differential by 1. if the effect that KOed the pokemon was caused by multiple pokemon (such as with multiple spike setters), the credit is split between the pokemon
        # if a pokemon faints to self-inflicted damage, the pokemon that damaged it last gets the differential increase
        # if a pokemon heals to full and then KOs itself with self inflicted damage without being damaged by an opponent, no opponent gets the differential increase (even if it was damaged by an opponent before healing)
        self.differential = 0
        # tracks the last opponent to damage the pokemon. reset if the pokemon heals to full. used for differentials in cases where the pokemon dies to self-inflicted damage
        self.last_damage_credit = None
        self.enemies_knocked_out = []
        self.knocked_out_by_combatant = None
        self.knocked_out_by_effect = None
        # For explaining situations that would seem impossible. Like if a Clefable KOs a pokemon using a shadow move, you can use the notes to explain if it was called by metronome.
        # currently unused
        self.knocked_out_notes = None
        # this is a basic check to see if this pokemon appears in the replay data as well as the team data.
        self.exists = False
        self.verification_failures = []
        self.mimicked_moves = []
        self.changed_abilities = []
        self.changed_items = []
        self.winner = False
        self.active_turns = 0
        self.direct_damage_dealt = 0
        self.indirect_damage_dealt = 0
        self.total_damage_dealt = 0
        self.active_damage = 0
        self.damage_taken = 0
        self.healing_given = 0
        self.healing_received = 0
        self.health = 100
        self.status = {'status': None, 'cause': []}
        self.volatile_status = {}

    def calculate_per_turn(self):
        self.turns = max(1, self.team.battle.turns)
        active_turns = max(1, self.active_turns)
        self.differential = self.get_number_of_kos() - int(self.check_fainted())
        self.active_turns_per_turn = self.active_turns / self.turns
        self.total_damage_dealt_per_turn = self.total_damage_dealt / self.turns
        self.active_damage_per_turn = self.active_damage / self.turns
        self.active_damage_per_active_turn = self.active_damage / active_turns
        self.direct_damage_dealt_per_turn = self.direct_damage_dealt / self.turns
        self.direct_damage_dealt_per_active_turn = self.direct_damage_dealt / active_turns
        self.indirect_damage_dealt_per_turn = self.indirect_damage_dealt / self.turns
        self.damage_taken_per_turn = self.damage_taken / self.turns
        self.damage_taken_per_active_turn = self.damage_taken / active_turns
        self.healing_given_per_turn = self.healing_given / self.turns
        self.healing_given_per_active_turn = self.healing_given / active_turns
        self.healing_received_per_turn = self.healing_received / self.turns
        self.healing_received_per_active_turn = self.healing_received / active_turns

    def verify_existance(self):
        if self.exists == False:
            self.verification_failures.append(f"{self.species} appears in the team file but not in the replay.")

    def verify_move(self, move):
        if move not in self.moves + self.mimicked_moves:
            self.verification_failures.append(f"{self.species} uses {move}, but does not know it according to the team file.")

    def verify_ability(self, ability):
        if ability != self.ability and ability not in self.changed_abilities:
            self.verification_failures.append(f"{self.species} reveals {ability}, but does not have it according to the team file.")

    def verify_item(self, item):
        if item != self.item and item not in self.changed_items:
            self.verification_failures.append(f"{self.species} has {item}, but does not hold it according to the team file.")

    def get_number_of_kos(self):
        return len(self.enemies_knocked_out)

    def faint(self, ko_credit, effect):
        self.knocked_out_by_combatant = ko_credit
        self.knocked_out_by_effect = effect
        # when this is updated for doubles, account for friendly fire!
        if ko_credit is not None and ko_credit.team != self.team:
            ko_credit.enemies_knocked_out.append({"combatant": self, "effect": effect})
            ko_credit.kos += 1
            ko_credit.differential += 1
        elif self.last_damage_credit is not None:
            self.last_damage_credit.differential += 1
        
    def do_damage(self, amount, direct):
        if direct:
            self.direct_damage_dealt += amount
        else:
            self.indirect_damage_dealt += amount

    # check functions are used for filtering
    # these functions can be used to narrow down the data a lot, but it can also be used to get an unfocused mess

    def check_species(self, species, inverse=False):
        for s in species:
            if s.lower() == self.species.lower():
                return invert(True, inverse)
        return invert(False, inverse)

    def check_move(self, moves, require_all=False, inverse=False):
        for move in moves:
            if require_all:
                if move not in moves:
                    return invert(False, inverse)
            else:
                if move in moves:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_ability(self, abilities, inverse=False):
        for ability in abilities:
            if ability == self.abilities:
                return invert(True, inverse)
        return invert(False, inverse)

    def check_item(self, items, inverse=False):
        for item in items:
            if item == self.item:
                return invert(True, inverse)
        return invert(False, inverse)

    def check_win(self, inverse=False):
        return invert(self.winner, inverse)

    def check_fainted(self, inverse=False):
        return invert(True if self.knocked_out_by_effect is not None else False, inverse)

    def check_number_of_kos(self, target, comparison):
        return compare_value(self.get_number_of_kos, target, comparison)

    def check_knocked_out_by(self, species, inverse=False):
        for opponent in species:
            if self.knocked_out_by_combatant.lower() == opponent.lower():
                return invert(True, inverse)
        return invert(False, inverse)

    def check_knocked_out_opponent(self, species, require_all=False, inverse=False):
        enemy_species_knocked_out = [enemy["combatant"].species.lower() for enemy in self.enemies_knocked_out]
        for opponent in species:
            if require_all:
                if opponent.lower() not in enemy_species_knocked_out:
                    return invert(False, inverse)
            else:
                if opponent.lower() in enemy_species_knocked_out:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_date(self, start_date=946706400, end_date=32503701600):
        return self.team.battle.check_date(start_date, end_date)
    
    # the function that calls this function should first check to make sure that the trainers being requested are viewable by the requester
    def check_team_trainer(self, discord_ids, guild_id, inverse=False):
        team_id = fnf_data.guild_preferences[guild_id].get_user_from_showdown(self.team.trainer_name).id
        for discord_id in discord_ids:
            if discord_id == team_id:
                return invert(True, inverse)
        return invert(False, inverse)

    def check_opponent_trainer(self, discord_ids, guild_id, inverse=False):
        return self.team.check_opponent_trainer(discord_ids, guild_id, inverse)

    def check_teammates(self, teammates, require_all=False, inverse=False):
        other_teammates = [member.species.lower() for member in self.team.team.values() if member is not self]
        for teammate in teammates:
            if require_all:
                if teammate.lower() not in other_teammates:
                    return invert(False, inverse)
            else:
                if teammate.lower() in other_teammates:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_opponents(self, opponents, require_all=False, inverse=False):
        for team in self.team.battle.teams:
            if team is not self:
                other_team = [member.species.lower() for member in team.team.values()]
        for opponent in opponents:
            if require_all:
                if opponent.lower() not in other_team:
                    return invert(False, inverse)
            else:
                if opponent.lower() in other_team:
                    return invert(True, inverse)
        if require_all:
            return invert(True, inverse)
        return invert(False, inverse)

    def check_number_of_turns(self, target, comparison):
        return self.team.battle.check_number_of_turns(target, comparison)

    def check_performance_stat(self, stat, target, comparison):
        return compare_value(getattr(self, stat), target, comparison)

    def clean_up(self):
        self.damage_dealt = self.direct_damage_dealt + self.indirect_damage_dealt
        self.calculate_per_turn()

class Replay():
    def __init__(self, file_name, player_dict, game_format, timestamp, check_teams=True, save_to_database=False, require_species_clause=True):
        self.file_name = file_name
        self.player_dict = player_dict
        self.game_format = game_format
        self.timestamp = timestamp
        # if check teams is False, the replay analyzer won't try to find inconsistencies in the Pokepaste.
        # a pokepaste containing each revealed Pokemon's nickname and species still must be provided, but the other info can be left out.
        self.check_teams = check_teams
        # if the battle has no errors, save it to the database. if ignore_errors is True, it will be saved even if errors are found.
        # PLEASE BE CAREFUL SETTING THIS TO TRUE IF CHECK_TEAMS IS FALSE OR IF SAVE_TO_DATABASE IS TRUE
        self.save_to_database = save_to_database
        self.require_species_clause = require_species_clause
        self.battle_log = ""
        self.errors = []
        self.halt = False
        self.complete = False
        # open the file
        with open(self.file_name, 'r') as f:
            self.lines = f.readlines()
            self.lines = self.lines[6:]
        self.teams = []
        self.tier = ""
        self.turn = 0
        self.player_number_regex = re.compile(r"p\da: ")
        self.health_regex = re.compile(r"\d+/\d+")
        self.last_move_used = {"move": None, "called by": None, "user": None, "target": None}
        self.fainted_this_turn = []
        self.upkeep = True
        self.active_pokemon = [None, None]
        self.active_post_switchin = [True, True]
        self.grassy_terrain_setter = None
        self.weather = {"weather": None, "setter": None}
        self.future_sight = [None, None]
        self.expect_silly_soda = False
        # the number of lines to expect a synchronize status
        self.expect_synchronize = 0
        self.synchronizer = None
        self.expect_leech_seed_start = {"target": None, "user": None}
        self.expect_leech_seed_heal_from_healer = []
        self.expect_retribution = 0
        self.mon_to_retribute = None
        self.healing_wish = [None, None]
        self.expect_nightmare = 0
        self.nightmare_credit = None
        self.expect_toxic_spikes_damage = 0
        self.expect_hazard_setup = 0
        self.hazard_credit = None
        self.baneful_bunker_active = [None, None]
        self.illusion_damage_credit = [None, None]
        self.expect_baneful_bunker_user = None
        self.expect_baneful_bunker = 0
        self.expect_poison = None
        self.expect_freeze = None
        self.expect_burn = None
        self.expect_z_move = False
        self.self_healing_move_user = None
        self.target_healing_move_user = None
        self.self_destructing_move_user = None
        self.self_destructing_move = None
        self.illusion_flag_data = ""
        self.battle = None
        self.pre_analysis()
        self.post_analysis_checks()

        if len(self.errors):
            saurbot_functions.timelog(f"A replay could not be read: {self.errors}")

    def log_append(self, text, turn_stamp = True):
        if turn_stamp:
            self.battle_log += f"Turn {self.turn}: "
        self.battle_log += text + "\n"

    def post_analysis_checks(self):
        if self.timestamp is None:
            if self.raise_exception(InvalidReplayError("Timestamp not found")):
                return

    def raise_exception(self, exception):
        try:
            raise exception
        except InvalidReplayError as e:
            self.errors.append(str(e))
            self.halt = e.halt
            self.log_append(str(e))
            return e.halt
        return True

    def is_ally(self, pokemon1, pokemon2):
        if pokemon1.team is pokemon2.team:
            return True
        return False
        
    def pre_analysis(self):
        # check for species clause
        species_clause = False
        for line in self.lines:
            if line.startswith("|rule|Species Clause"):
                species_clause = True
                break
        if species_clause == False and self.require_species_clause:
            if self.raise_exception(InvalidReplayError("Invalid rules (games without species clause cannot be analyzed)", self.turn)):
                return
        # get game data
        for line in self.lines:
            current_line = line.strip()
            # CHECK GAMETYPE
            if current_line.startswith('|gametype|'):
                gametype = current_line.removeprefix('|gametype|')
                if gametype != "singles":
                    if self.raise_exception(InvalidReplayError("Invalid gametype (only singles games can be analyzed)", self.turn)):
                        return
            # CHECK TIER
            elif current_line.startswith('|tier|'):
                tier = current_line.removeprefix('|tier|')
                if tier not in tracked_tier_names:
                    if self.raise_exception(InvalidReplayError("Invalid tier", self.turn)):
                        return
            # CHECK PLAYER
            elif current_line.startswith('|player|'):
                # lines starting with |player| in the replay look like this:
                # |player|p#|player_name|player_avatar|
                # for example
                # |player|p1|noobscrub|cheryl|
                player_data = current_line.removeprefix('|player|').split('|')
                pnum = self.get_player_number(player_data[0])
                player_name = player_data[1]
                self.teams.append(Team(pnum, player_name))
                self.teams[pnum-1].read_team(self.player_dict[player_name]["team"])
                self.teams[pnum-1].elo = self.player_dict[player_name]["elo"]
            elif current_line.startswith('|poke|'):
                if self.check_teams:
                    # this works similarly as the player code directly above
                    pokemon_data = current_line.removeprefix('|poke|').split('|')
                    species = pokemon_data[1].split(',')[0] if ',' in pokemon_data[1] else pokemon_data[1]
                    species = replace_alias(species)
                    pnum = self.get_player_number(pokemon_data[0])
                    self.teams[pnum-1].exists(species)
            # CHECK TEAM PREVIEW
            elif current_line == '|teampreview':
                for i, team in enumerate(self.teams):
                    if self.check_teams:
                        team.all_verify_existance()
                    team.team_index = i
                break
        self.analysis_loop()

    def line_move(self):
        self.expect_leech_seed_start = {"target": None, "user": None}
        self.expect_poison = None
        self.expect_freeze = None
        self.expect_burn = None
        self.self_healing_move_user = None
        self.self_destructing_move_user = None
        self.target_healing_move_user = None
        self.self_destructing_move = None
        # if check_move is True, the pokemon will be checked to see if it knows that move
        # it gets set to False if this move is called from a different source (moves like metronome and mimic and abilities like dancer)
        # except actually it doesnt do that and I never ended up using this variable
        self.check_move = True
        line_data = self.current_line.removeprefix('|move|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        user = self.teams[pindex].get_teammate_from_nickname(nickname)
        move = line_data[1].strip()
        target = None
        called_by = None
        mbounce = False
        counter = 0
        for l in line_data:
            counter += 1
            if counter < 3:
                # the first and second lines are already handled above, so skip them
                continue
            # if regex matches (this is the target)
            if re.match(self.player_number_regex, l):
                target_pindex, target_nickname = self.split_player_number_and_pokemon(l.strip())
                target = self.teams[target_pindex].get_teammate_from_nickname(target_nickname)
            elif l.startswith("[from]ability: Dancer"):
                called_by = "Dancer"
            elif l.startswith("[from]move: Metronome"):
                called_by = "Metronome"
            elif l.startswith("[from]move: Me First"):
                called_by = "Me First"
            elif l.startswith("[from]move: Copycat"):
                called_by = "Copycat"
            elif l.startswith("[from]move: Nature Power"):
                called_by = "Nature Power"
            elif l.startswith("[from]move: Mirror Move"):
                called_by = "Mirror Move"
            elif l.startswith("[from]ability: Magic Bounce"):
                mbounce = True
        # if this is a move that
        # 1. the user does not know
        # 2. the user has not mimicked
        # 3. is not called by a move the user knows or has mimicked
        # 4. is not a zmove
        if move not in user.moves + user.mimicked_moves and mbounce == False and (called_by is None or called_by not in user.moves + user.mimicked_moves) and self.expect_z_move == False:
            called_move = False
            if move in ["Biddy Bud", "Fiery Blossom", "Precipice Blades", "Splash"] and "Flora Power" in user.moves + user.mimicked_moves:
                called_move = True
            elif move in ["Red Rush", "Blue Bites", "Splash"] and "Stripe Style" in user.moves + user.mimicked_moves:
                called_move = True
            # if all of the qualifications are not met:
            # the move is hidden power
            # the user knows a move that starts with "Hidden Power"
            # the move was either not called by another move, or was called by a move the user knows or has mimicked
            # (this is because battles show hidden power as "Hidden Power" while the teambuilder shows it as "Hidden Power [type]")
            if called_move == False and (move == "Hidden Power" and len([hp_move for hp_move in user.moves + user.mimicked_moves if hp_move.startswith("Hidden Power")]) > 0 and (called_by is None or called_by in user.moves + user.mimicked_moves)) == False:
                if self.raise_exception(InvalidReplayError(f"{user.species} used {move} without knowing it.", self.turn)):
                    return
        self.last_move_used = {"move": move, "called by": called_by, "user": user, "target": target}
        if move in FUTURE_SIGHT_MOVES:
            self.future_sight[pindex] = user
        if move == "Nightmare":
            self.expect_nightmare = 2
            self.nightmare_credit = user
        if move in LEECH_SEED_MOVES:
            self.expect_leech_seed_start = {"target": target, "user": user}
        if move in HAZARD_MOVES:
            self.expect_hazard_setup = 2
            self.hazard_credit = user
        if move == "Baneful Bunker":
            self.baneful_bunker_active[pindex] = user
        if move in POISON_MOVES:
            self.expect_poison = user
        if move in FREEZE_MOVES:
            self.expect_freeze = user
        if move in BURN_MOVES:
            self.expect_burn = user
        if move in HEALING_WISH_MOVES:
            self.healing_wish[pindex] = user
        if move in SELF_HEALING_MOVES:
            self.self_healing_move_user = user
        if move in SELF_DESTRUCT_MOVES:
            self.self_destructing_move_user = user
            self.self_destructing_move = move
        if move in TARGET_HEALING_MOVES:
            self.target_healing_move_user = user
        self.expect_z_move = False
        self.log_append(f"{user.team.trainer_name}'s {user.species} used {move}.")

    def line_damage(self):
        line_data = self.current_line.removeprefix('|-damage|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        try:
            cause_data = line_data[2].strip()
            damage_credit, damage_type = [], "indirect"
            if cause_data == "[from] item: Life Orb":
                cause = {"attacker": None, "source": "Life Orb"}
            elif cause_data == "[from] Recoil":
                cause = {"attacker": None, "source": "Recoil"}
            elif cause_data == "[from] confusion":
                cause = {"attacker": None, "source": "Confusion"}
                damage_credit = target.volatile_status["Confusion"]
            elif cause_data == "[from] brn":
                cause = {"attacker": None, "source": "Burn"}
                damage_credit = target.status["cause"]
            elif cause_data == "[from] frz":
                cause = {"attacker": None, "source": "Freeze"}
                damage_credit = target.status["cause"]
            elif cause_data == "[from] psn":
                cause = {"attacker": None, "source": "Poison"}
                damage_credit = target.status["cause"]
            elif cause_data == "[from] item: Sticky Barb":
                cause = {"attacker": None, "source": "Sticky Barb"}
            elif cause_data == "[from] item: Black Sludge":
                cause = {"attacker": None, "source": "Black Sludge"}
            elif cause_data == "[from] Leech Seed":
                cause = {"attacker": None, "source": "Leech Seed"}
                damage_credit = target.volatile_status["Leech Seed"]
                self.expect_leech_seed_heal_from_healer.append(damage_credit[0])
            elif cause_data == "[from] Curse":
                damage_credit = target.volatile_status["Curse"]
            elif cause_data == "[from] Nightmare":
                damage_credit = target.volatile_status["Nightmare"]
            elif cause_data == "[from] Sandstorm":
                cause = {"attacker": None, "source": "Sandstorm"}
                if self.weather["setter"].team != target.team:
                    damage_credit = [self.weather["setter"]]
            elif cause_data == "[from] Hail":
                cause = {"attacker": None, "source": "Hail"}
                if self.weather["setter"].team != target.team:
                    damage_credit = [self.weather["setter"]]
            elif cause_data == "[from] Spikes":
                cause = {"attacker": None, "source": "Spikes"}
                damage_credit = target.team.hazards["Spikes"]
            elif cause_data == "[from] Stealth Rock":
                cause = {"attacker": None, "source": "Stealth Rock"}
                damage_credit = target.team.hazards["Stealth Rock"]
            elif cause_data in ["[from] item: Rocky Helmet", "[from] item: Jaboca Berry"]:
                cause = {"attacker": None, "source": cause_data.removeprefix("[from] item:").strip()}
            elif cause_data in ["[from] ability: Iron Barbs", "[from] ability: Rough Skin", "[from] ability: Reverberation"]:
                cause = {"attacker": None, "source": cause_data.removeprefix("[from] ability:").strip()}
            elif cause_data == ("[from] ability: Dry Skin"):
                cause = {"attacker": None, "source": "Dry Skin"}
            elif cause_data.removeprefix("[from] move: ") in PARTIAL_TRAPPING_MOVES:
                cause = {"attacker": None, "source": cause_data.removeprefix("[from] move: ")}
                damage_credit = target.volatile_status[cause_data.removeprefix("[from] move: ")]
            elif cause_data == ("[from] ability: Slow Digestion"):
                cause = {"attacker": None, "source": "Slow Digestion"}
            elif cause_data == ("[from] ability: Aftermath"):
                cause = {"attacker": None, "source": "Aftermath"}
            elif cause_data == ("[from] ability: Innards Out"):
                cause = {"attacker": None, "source": "Innards Out"}
            elif cause_data == ("[from] ability: Liquid Ooze"):
                cause = {"attacker": None, "source": "Liquid Ooze"}
            elif cause_data == ("[from] Spiky Shield"):
                cause = {"attacker": None, "source": "Spkiy Shield"}
            elif cause_data in ["[from] highjumpkick", "[from] jumpkick"]:
                cause = {"attacker": None, "source": "Crash Damage"}
            else:
                if self.raise_exception(InvalidReplayError(f"Unknown cause of damage: {cause_data}", self.turn)):
                    return
            if cause["source"] in ["Rocky Helmet", "Rough Skin", "Iron Barbs", "Slow Digestion", "Aftermath", "Innards Out", "Liquid Ooze", "Spiky Shield", "Jaboca Berry"]:
                source_index, source_nickname = self.split_player_number_and_pokemon(line_data[3].removeprefix("[of] ").strip())
                damage_credit = [self.teams[source_index].get_teammate_from_nickname(source_nickname)]
        except IndexError:
            cause = {"attacker": self.last_move_used["user"], "source": self.last_move_used["move"]}
            damage_credit, damage_type = [self.last_move_used["user"]], "direct"
        # overly long if statement translation:
        # if the source of the damage is rocky helmet or direct attack, and the attacker exists, and the attacker's team has an illusioned pokemon active
        if cause["source"] in ["Rocky Helmet", self.last_move_used["move"]] and cause["attacker"] is not None and self.illusion_damage_credit[cause["attacker"].team.team_index] is not None:
            damage_credit = self.illusion_damage_credit[cause["source"]["attacker"].team.team_index]
        cause["target"] = target
        health = self.get_health(line_data[1])
        fatal = False
        if health == 0:
            fatal = True
            if cause in ["Stealth Rock", "Spikes"]:
                self.active_post_switchin[target.team.team_index] = False
        damage = target.health - health
        self.do_damage(damage_credit, target, damage, cause["source"], damage_type, fatal)

    def line_faint(self):
        line_data = self.current_line.removeprefix('|faint|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        mon = self.teams[pindex].get_teammate_from_nickname(nickname)
        if mon == self.self_destructing_move_user:
            source = f"User's {self.self_destructing_move}"
            self.do_damage([], mon, mon.health, source, "indirect", True)

    def line_heal(self):
        line_data = self.current_line.removeprefix('|-heal|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        mon = self.teams[pindex].get_teammate_from_nickname(nickname)
        cause = None
        # this gets the health and the cause of the healing, if they exist
        health = None
        for l in line_data:
            if re.match(self.health_regex, l):
                health = self.get_health(l)
            elif l.startswith("[from]"):
                cause = l.removeprefix("[from]").strip()
        if health is None:
            if self.raise_exception(InvalidReplayError(f"Health could not be found", self.turn)):
                return
        amount_healed = health - mon.health
        if amount_healed < 0:
            if self.raise_exception(InvalidReplayError(f"Healed negative amount", self.turn)):
                return
        healer = None
        if cause is not None:
            cause = cause.strip()
        # leech seed
        if cause is None and len(self.expect_leech_seed_heal_from_healer):
            cause = "Leech Seed"
            for potential_healer in self.expect_leech_seed_heal_from_healer:
                if potential_healer.team == mon.team:
                    healer = potential_healer
        # self healing moves
        elif cause is None and self.self_healing_move_user == mon:
            cause = self.last_move_used["move"]
            healer = self.self_healing_move_user
        # target healing moves
        elif cause is None and self.target_healing_move_user.team == mon.team:
            cause = self.last_move_used["move"]
            healer = self.target_healing_move_user
        # grassy terrain
        elif cause == "Grassy Terrain":
            if self.grassy_terrain_setter.team == mon.team:
                healer = self.grassy_terrain_setter
        # healing wish
        elif cause.removeprefix("move: ") in HEALING_WISH_Z_MOVES + HEALING_WISH_MOVES and self.healing_wish[pindex] is not None:
            healer = self.healing_wish[pindex]
        # wish
        elif cause == "move: Wish":
            cause = "Wish"
            wisher = line_data[3].removeprefix("[wisher]").strip()
            healer = mon.team.get_teammate_from_nickname(wisher)
        # ingrain, aqua ring, z-heal bell, etc
        elif cause in SELF_HEALING_EFFECTS:
            healer = mon
        # abilities
        elif cause.removeprefix("ability: ") in SELF_HEALING_ABILITIES:
            cause = cause.removeprefix("ability: ")
            healer = mon
        # items
        elif cause.removeprefix("item: ") in SELF_HEALING_ITEMS:
            cause = cause.removeprefix("item: ")
            healer = mon
        # berries
        elif cause.startswith("item: ") and cause.endswith("Berry"):
            cause = cause.removeprefix("item: ")
            healer = mon
        else:
            if self.raise_exception(InvalidReplayError(f"Unknown source of healing: {cause}", self.turn)):
                return
        self.do_heal(healer, mon, amount_healed, cause)

    def line_sethp(self):
        line_data = self.current_line.removeprefix('|-sethp|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        mon = self.teams[pindex].get_teammate_from_nickname(nickname)
        health = self.get_health(line_data[0])
        cause = None
        try:
            if line_data[2].startswith("[from]"):
                cause = line_data[2].removeprefix("[from]").strip()
        except IndexError:
            cause = None
        # until I find every cause of -sethp, I want to raise an exception whenever I stumble across a new one.
        # may be off by one due to rounding. I don't think it can be avoided, and in the grand scheme of things it doesn't really matter
        if cause == "move: Pain Split":
            # healed
            if health > mon.health:
                if self.last_move_used["user"] == mon:
                    healing = health - mon.health
                    self.do_heal(mon, mon, healing, "Pain Split")
            # damaged
            elif health < mon.heath:
                if self.last_move_used["user"] != mon:
                    damage = mon.health - health
                    damage = self.target.health - health
                    mon.health = health
                    self.do_damage([self.last_move_used["user"]], mon, self.active_pokemon, damage, "Pain Split", "indirect", False)
                mon.damage_received += mon.health - health
            mon.health = health
        else:
            if self.raise_exception(InvalidReplayError(f"Unknown cause of sethp: {cause}", self.turn)):
                return

    def line_start(self):
        line_data = self.current_line.removeprefix('|-start|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        effect = line_data[1].strip()
        if effect == "Mimic":
            mimicked_move = line_data[2]
            target.mimicked_moves[mimicked_move] = effect
        elif effect == "perish3":
            credit = []
            if self.last_move_used["user"].team != target.team:
                credit = self.last_move_used["user"]
            target.volatile_status["Perish"] = credit
        elif effect == "perish0":
            credit = []
            try:
                credit = target.volatile_status["Perish"]
            except KeyError:
                if self.raise_exception(InvalidReplayError(f"Untracked perish song usage", self.turn)):
                    return
            self.do_damage(credit, target, self.active_pokemon, target.health, "Perish Song", "indirect", True)
            cause = {"user": "", "source": "Perish Song", "target": target}
            self.fainted_this_turn.append(cause)
            target.health = 0
        elif effect == "confusion":
            self_inflicted_confusion = False
            if self.expect_silly_soda == True:
                self_inflicted_confusion = True
            try:
                if line_data[2].strip() == "[fatigue]":
                    self_inflicted_confusion = True
            except IndexError:
                pass
            if self_inflicted_confusion == False:
                target.volatile_status["Confusion"] = [self.last_move_used["user"]]
            else:
                target.volatile_status["Confusion"] = []
        elif effect == "Curse":
            expect_retribution = 0
            try:
                line_data[2] 
                source_index, source_nickname = self.split_player_number_and_pokemon(line_data[2].removeprefix("[of] ").strip())                
            except IndexError:
                expect_retribution = 2
            if expect_retribution == 0:
                target.volatile_status["Curse"] = [self.teams[source_index].get_teammate_from_nickname(source_nickname)]
            else:
                target.volatile_status["Curse"] = []
        elif effect == "Nightmare":
            if self.expect_nightmare > 0:
                target.volatile_status["Nightmare"] = self.nightmare_credit
            else:
                if self.raise_exception(InvalidReplayError(f"Unknown cause of nightmare", self.turn)):
                    return
        elif effect == "move: Leech Seed":
            if self.expect_leech_seed_start["target"] == target:
                target.volatile_status["Leech Seed"] = [self.expect_leech_seed_start["user"]]
            else:
                if self.raise_exception(InvalidReplayError(f"Unknown cause of leech seed", self.turn)):
                    return

    def line_end(self):
        line_data = self.current_line.removeprefix('|-end|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        effect = line_data[1]
        if effect == "Retribution":
            if self.expect_retribution > 0:
                self.mon_to_retribute.volatile_status["Curse"] = target

    def line_activate(self):
        line_data = self.current_line.removeprefix('|-activate|')
        line_data = line_data.split("|")
        try:
            pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        except ValueError as e:
            if line_data[1].strip() == "Cloud Guard":
                return
            else:
                raise e
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        effect = line_data[1]
        if effect.removeprefix("move: ") in PARTIAL_TRAPPING_MOVES:
            user_index, user_nickname = self.split_player_number_and_pokemon(line_data[2].removeprefix("[of] ").strip())
            user = self.teams[user_index].get_teammate_from_nickname(user_nickname)
            target.volatile_status[effect.removeprefix("move: ")] = [user]
        elif effect.strip() == "ability: Synchronize":
            self.expect_synchronize = 2
            self.synchronizer = target
        elif effect.strip() == "move: Protect":
            if target in self.baneful_bunker_active:
                self.expect_baneful_bunker = 2
                self.expect_baneful_bunker_user = target
        elif effect.strip() == "healreplacement":
            self.healing_wish[pindex] = target

    def line_status(self):
        line_data = self.current_line.removeprefix('|-status|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        status = line_data[1].strip()
        cause = []
        if self.expect_synchronize > 0:
            cause = [self.synchronizer]
        elif self.expect_baneful_bunker_user is not None and status == "psn":
            cause = [self.expect_baneful_bunker_user]
        elif self.expect_toxic_spikes_damage >= 1 and status in ["psn", "tox"]:
            cause = target.team.hazards["Toxic Spikes"]
        elif self.expect_poison is not None and status in ["psn", "tox"]:
            cause = [self.expect_poison]
        elif self.expect_freeze is not None and status == "frz":
            cause = [self.expect_freeze]
        elif self.expect_burn is not None and status == "brn":
            cause = [self.expect_burn]
        else:
            pass
        if status == "tox":
            target.status = {'status': "Toxic", 'cause': cause}
        elif status == "psn":
            target.status = {'status': "Poison", 'cause': cause}
        elif status == "brn":
            target.status = {'status': "Burn", 'cause': cause}
        elif status == "frz":
            target.status = {'status': "Freeze", 'cause': cause}

    def line_curestatus(self):
        line_data = self.current_line.removeprefix('|-curestatus|')
        line_data = line_data.split("|")
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        target = self.teams[pindex].get_teammate_from_nickname(nickname)
        target.status = {'status': None, 'cause': []}

    def line_fieldstart(self):
        line_data = self.current_line.removeprefix('|-fieldstart|')
        line_data = line_data.split("|")
        if line_data[0].strip() == "move: Grassy Terrain":
            try:
                pindex, nickname = self.split_player_number_and_pokemon(line_data[2].removeprefix("[of] ").strip())
                self.grassy_terrain_setter = self.teams[pindex].get_teammate_from_nickname(nickname)
            except IndexError:
                self.grassy_terrain_setter = self.last_move_used["user"]

    def line_sidestart(self):
        line_data = self.current_line.removeprefix("|-sidestart|")
        line_data = line_data.split("|")
        if line_data[1].strip() in HAZARD_MOVES:
            hazard = line_data[1].strip()
            pindex, trainer_name = self.split_player_number_and_pokemon(line_data[0])
            target_team = self.teams[pindex]
            if self.expect_hazard_setup > 0:
                target_team.hazards[hazard].append(self.hazard_credit)
            else:
                if self.raise_exception(InvalidReplayError(f"Unexpected hazards", self.turn)):
                    return
            
    def line_sideend(self):
        line_data = self.current_line.removeprefix("|-sideend|")
        line_data = line_data.split("|")
        if line_data[1].strip() in HAZARD_MOVES:
            hazard = line_data[1].strip()
            pindex, trainer_name = self.split_player_number_and_pokemon(line_data[0])
            target_team = self.teams[pindex]
            target_team.hazards[hazard] = []

    def line_weather(self):
        line_data = self.current_line.removeprefix('|-weather|')
        line_data = line_data.split("|")
        if line_data[-1].strip() != "[upkeep]":
            self.weather = {"weather": None, "setter": None}
            try:
                pindex, nickname = self.split_player_number_and_pokemon(line_data[2].removeprefix("[of] ").strip())
                setter = self.teams[pindex].get_teammate_from_nickname(nickname)
            except IndexError:
                setter = self.last_move_used["user"]
            if line_data[0].strip() in ["Hail", "Sandstorm"]:
                self.weather = {"weather": line_data[0].strip(), "setter": setter}
            else:
                self.weather = {"weather": None, "setter": None}

    def line_switch(self):
        # deal with regen and silly soda
        if self.current_line.startswith('|switch|'):
            line_data = self.current_line.removeprefix('|switch|')
        elif self.current_line.startswith('|drag|'):
            line_data = self.current_line.removeprefix('|drag|')
        line_data = line_data.split("|")
        illusioned_as = None
        if self.illusion_flag_data != "":
            fake_index, fake_nickname = self.split_player_number_and_pokemon(line_data[0])
            real_index, real_nickname = self.split_player_number_and_pokemon(self.illusion_flag_data)
            self.teams[real_index].active_illusion = real_nickname
            self.illusion_flag_data = ""
            illusioned_as = fake_nickname
        else:
            pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
            self.teams[pindex].active_illusion = None
        pindex, nickname = self.split_player_number_and_pokemon(line_data[0])
        mon = self.teams[pindex].get_teammate_from_nickname(nickname)
        if self.active_pokemon[pindex] is not None:
            self.active_pokemon[pindex].volatile_status = {}
        if mon.species == "Spinda" and mon.item == "Silly Soda":
            self.expect_silly_soda = True
        else:
            self.expect_silly_soda = False
        if line_data[-1].startswith("[from]"):
            health = self.get_health(line_data[-2])
            if self.check_status(line_data[-2]) == False:
                mon.status = {'status': None, 'cause': []}
        else:
            health = self.get_health(line_data[-1])
            if self.check_status(line_data[-1]) == False:
                mon.status = {'status': None, 'cause': []}
        # due to rounding, health may be one off. if it's more than one off, it was changed, possibly by regenerator
        if abs(mon.health - health) > 1:
            if mon.ability in ["Regenerator", "Shadow Rebirth"] and health > mon.health:
                self.do_heal(mon, mon, health - mon.health, mon.ability)
                mon.health = health
            else:
                if self.raise_exception(InvalidReplayError(f"Non-regenerator pokemon changed health while out of battle.", self.turn)):
                    return
        # toxic spikes
        team = mon.team
        if len(team.hazards["Toxic Spikes"]) >= 1:
            number_of_hazards = 1
            if len(team.hazards["Stealth Rock"]) >= 1:
                number_of_hazards += 1
            if len(team.hazards["Spikes"]) >= 1:
                number_of_hazards += 1
            self.expect_toxic_spikes_damage = number_of_hazards + 1
        # active pokemon
        self.active_pokemon[pindex] = mon
        text = f"{mon.team.trainer_name} sent out {mon.species}"
        if illusioned_as is not None:
            text += f" illusioned as {illusioned_as}"
        text += "."
        self.log_append(text)

    def line_turn(self):
        self.turn = int(self.current_line.removeprefix('|turn|'))
        self.log_append(f"### TURN {self.turn} ###", False)
        self.upkeep = False
        self.baneful_bunker_active = [None, None]
        self.healing_wish = [None, None]
        self.expect_leech_seed_heal_from_healer = []

    def analysis_loop(self):
        for line in self.lines:
            if self.halt:
                return
            self.current_line = line.strip()
            #print(self.current_line)
            if self.current_line.startswith('|-zpower|'):
                self.expect_z_move = True
            # MOVE USED
            if self.current_line.startswith('|move|'):
                self.line_move()
            if self.current_line.startswith('|-damage|'):
                self.line_damage()
            # FAINT
            if self.current_line.startswith('|faint|'):
                self.line_faint()
            # HEAL
            if self.current_line.startswith('|-heal|'):
                self.line_heal()
            # SETHP
            if self.current_line.startswith("|-sethp|"):
                self.line_sethp()
            # ON START
            # we'll find important effects here
            if self.current_line.startswith('|-start|') == True:
                self.line_start()
            # ON END
            if self.current_line.startswith('|-end|'):
                self.line_end()
            # ON ACTIVATE
            if self.current_line.startswith('|-activate|') == True:
                self.line_activate()
            # ON STATUS
            if self.current_line.startswith('|-status|') == True:
                self.line_status()
            # ON FIELD START
            if self.current_line.startswith('|-fieldstart|'):
                self.line_fieldstart()
            # ON GRASSY TERRAIN END
            if self.current_line.strip() == ('|-fieldend|move: Grassy Terrain'):
                self.grassy_terrain_setter = None
            # ON SIDE START
            if self.current_line.startswith('|-sidestart|'):
                self.line_sidestart()
            # ON SIDE END
            if self.current_line.startswith("|-sideend|"):
                self.line_sideend()
            # ON WEATHER
            if self.current_line.startswith("|-weather|"):
                self.line_weather()
            # ON SAURBOTFLAG01/ILLUSION SWITCH-IN
            if self.current_line.startswith("|saurbotFlag01|"):
                self.illusion_flag_data = self.current_line.removeprefix("|saurbotFlag01|")
            # ON SWITCH/DRAG
            if self.current_line.startswith('|switch|') or self.current_line.startswith('|drag|'):
                self.line_switch()
            # ON CURE STATUS
            if self.current_line.startswith('|-curestatus|') == True:
                self.line_curestatus()
            # ON UPKEEP, BATTLE START, OR WIN
            if self.current_line.startswith('|upkeep') or self.current_line.startswith('|start') or self.current_line.startswith('|win|'):
                self.upkeep = True
                if self.turn >= 1:
                    for i, mon in enumerate(self.active_pokemon):
                        if mon is not None and self.active_post_switchin[i]:
                            mon.active_turns += 1
                self.active_post_switchin = [True for item in self.active_pokemon]
            # ON START OF TURN
            if self.current_line.startswith('|turn|'):
                self.line_turn()
            # ON TIE
            if self.current_line.startswith('|tie') and self.current_line.startswith("|tier") == False:
                if self.raise_exception(InvalidReplayError("Ties are not supported at this time.", self.turn)):
                    return
            # ON WIN
            if self.current_line.startswith('|win|'):
                if self.turn < 5:
                    if self.raise_exception(InvalidReplayError("A game of this length is not supported.", self.turn)):
                        return
                trainer_name = self.current_line.removeprefix("|win|").strip().removesuffix("</script>")
                self.log_append(trainer_name + " wins", False)
                for team in self.teams:
                    if trainer_name == team.trainer_name:
                        team.on_win()
                self.battle = Battle(self.teams, self.timestamp, self.game_format, self.turn)
                for team in self.teams:
                    team.clean_up()
                self.complete = True
                return
            # this always must be last
            # ON SWITCH (SILLY SODA)
            if self.current_line.startswith('|switch|') == False:
                self.expect_silly_soda = False
            # LINE COUNTERS
            # synchronize
            if self.expect_synchronize > 0:
                self.expect_synchronize -= 1
            else:
                self.synchronizer = None
            # retribution
            if self.expect_retribution > 0:
                self.expect_retribution -= 1
            else:
                self.mon_to_retribute = None
            # nightmare
            if self.expect_nightmare > 0:
                self.expect_nightmare -= 1
            else:
                self.nightmare_credit = None
            # hazard setup
            if self.expect_hazard_setup > 0:
                self.expect_hazard_setup -= 1
            else:
                self.hazard_credit = None
            # toxic spikes
            if self.expect_toxic_spikes_damage > 0:
                self.expect_toxic_spikes_damage -= 1
            # baneful bunker
            if self.expect_baneful_bunker > 0:
                self.expect_baneful_bunker -= 1
            else:
                self.expect_baneful_bunker_user = None

    def get_player_number(self, string):
        string = string.strip()
        string = string.removesuffix(":")
        string = string.removeprefix("p")
        string = string.removesuffix("a")
        # returns player number
        return int(string)

    def split_player_number_and_pokemon(self, string):
        pnum = self.get_player_number(string[:3])
        mon = string.removeprefix(f"p{pnum}").removeprefix("a").removeprefix(":").strip()
        return pnum-1, mon

    def get_health(self, health):
        if health == "0 fnt":
            return 0
        health = health.removesuffix("tox")
        health = health.removesuffix("psn")
        health = health.removesuffix("brn")
        health = health.removesuffix("frz")
        health = health.removesuffix("par")
        health = health.removesuffix("slp")
        health = health.strip()
        health = health.split("/")
        health =  (100 * int(health[0])) / int(health[1])
        if health != 0:
            health = max(1, math.floor(health))
        return health

    def check_status(self, health_line):
        health = health_line.strip()
        if health[-3:] in STATUS_SHORTHANDS:
            return True
        return False

    def do_heal(self, giver, receiver, amount, cause):
        receiver.health += amount
        receiver.healing_received += amount
        if giver is None:
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} healed {amount} from {cause}.")
        else:
            giver.healing_given += amount
            healer_name = "their" if giver == receiver else f"{giver.team.trainer_name}'s {giver.species}'s"
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} healed {amount} from {healer_name} {cause}.")
        if receiver.health == 100:
            receiver.last_damage_credit = None

    def do_damage(self, damage_credit, receiver, amount, cause, damage_type, fatal):   
        active_credit = [mon for mon in self.active_pokemon if self.is_ally(receiver, mon) == False and mon.health > 0]
        receiver.health -= amount
        receiver.damage_taken += amount
        if len(damage_credit) == 0:
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} took {amount} damage from {cause}.")
            credit_dicts = []
        elif len(damage_credit) == 1:
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} took {amount} damage from {damage_credit[0].team.trainer_name}'s {damage_credit[0].species}'s {cause}.")
            credit_dicts = [{"pokemon": damage_credit[0], "damage": amount, "kill": fatal}]
        elif len(damage_credit) >= 2:
            if receiver.species == "Shedinja":
                credit_dicts = [{"pokemon": damage_credit[0], "damage": amount, "kill": fatal}]
            # this may be slightly inaccurate at very low max HP levels (less than 16). not much I can do, and it's a very uncommon situation
            elif cause == "Poison":
                if amount > 13:
                    credit_dicts = [{"pokemon": damage_credit[0], "damage": 13, "kill": False},
                                    {"pokemon": damage_credit[1], "damage": amount-13, "kill": fatal}]
                else:
                    credit_dicts = [{"pokemon": damage_credit[0], "damage": amount, "kill": fatal}]
            elif cause == "Spikes":
                if amount > 17:
                    credit_dicts = [{"pokemon": damage_credit[0], "damage": 13, "kill": False},
                                    {"pokemon": damage_credit[1], "damage": 4, "kill": False},
                                    {"pokemon": damage_credit[2], "damage": amount - 17, "kill": fatal}]
                elif amount > 13:
                    credit_dicts = [{"pokemon": damage_credit[0], "damage": 13, "kill": False},
                                    {"pokemon": damage_credit[1], "damage": amount-13, "kill": fatal}]
                else:
                    credit_dicts = [{"pokemon": damage_credit[0], "damage": amount, "kill": fatal}]
            dealers_text = self.put_list_into_words(list(set([dealer.species for dealer in damage_credit])))
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} took {amount} damage from {damage_credit[0].team.trainer_name}'s {dealers_text}'s {cause}.")
        if len(damage_credit) > 0 and damage_credit[-1].team is not receiver.team:
            receiver.last_damage_credit = damage_credit[-1]
        if fatal:
            self.log_append(f"{receiver.team.trainer_name}'s {receiver.species} fainted!")
            if len(damage_credit) == 0:
                ko_credit = None
            elif len(damage_credit) == 1:
                ko_credit = damage_credit[0]
            else:
                ko_credit = [credit_dict["pokemon"] for credit_dict in credit_dicts if credit_dict["kill"]][0]
            receiver.faint(ko_credit, cause)
        for mon in active_credit:
            mon.active_damage += amount
        for credit_dict in credit_dicts:
            credit_dict["pokemon"].do_damage(amount, damage_type == "direct")

    def put_list_into_words(self, string_list):
        if len(string_list) == 0:
            return ""
        elif len(string_list) == 1:
            return string_list[0]
        elif len(string_list) == 2:
            return string_list[0] + " and " + string_list[1]
        else:
            string_list[-1] = "and " + string_list[-1]
            text = ""
            for word in string_list:
                text += word + ", "
            text = text.removesuffix(", ")
            return text

async def analyze(replay_files):
    battles = []
    for replay_file in replay_files:
        with open(replay_file, "r") as f:
            lines = f.readlines()
            game_format = lines[1].strip().removeprefix("FORMAT: ")
            if game_format == "gen7story":
                continue
            if game_format not in fnf_data.formats:
                fnf_data.formats[game_format] = Tier()
            timestamp = int(lines[2].strip().removeprefix("TIMESTAMP: "))
            player1 = lines[3].strip().removeprefix("PLAYER 1: ")
            player2 = lines[4].strip().removeprefix("PLAYER 2: ")
            team_data = html.unescape(lines[5].strip())
            if team_data.strip() == "TEAM DATA:":
                saurbot_functions.timelog(f"{replay_file} is missing team data.")
                continue
            team_data = team_data.removeprefix("TEAM DATA: |c|~|/raw ").replace("<br />", "\n")
            team_data = team_data.split("</details><details><summary>")
            player1_team = team_data[0].removeprefix(f"<div class=\"infobox\"><details><summary>{''.join(re.sub(r'[^0-9a-z]','',player1.lower()))}'s team:</summary>")
            player2_team = team_data[1].removeprefix(f"{''.join(re.sub(r'[^0-9a-z]','',player2.lower()))}'s team:</summary>").removesuffix("</details></div>")
            # elo is only tracked for fnf showdown (guild id 540605600162250762)
            player1_profile = fnf_data.guild_preferences[540605600162250762].get_user_from_showdown(player1)
            player2_profile = fnf_data.guild_preferences[540605600162250762].get_user_from_showdown(player2)
            player1_elo = 1000
            player2_elo = 1000
            if player1_profile is not None:
                player1_elo = player1_profile.get_elo(game_format)
            if player2_profile is not None:
                player2_elo = player2_profile.get_elo(game_format)
            player_dict = {player1: {"team": player1_team, "elo": player1_elo},
                           player2: {"team": player2_team, "elo": player2_elo}}
            replay = Replay(replay_file, player_dict, game_format, timestamp)
            bointa_eligible = False
            if replay.complete:
                if player1_profile is not None and player2_profile is not None:
                    probability1 = 1 / (1 + math.pow(10, ((player2_elo - player1_elo)/400)))
                    probability2 = 1 / (1 + math.pow(10, ((player1_elo - player2_elo)/400)))
                    if replay.teams[0].winner:
                        player1_profile.set_elo(game_format, player1_elo + 30*(1-probability1))
                        player2_profile.set_elo(game_format, player2_elo + 30*(0-probability2))
                    else:
                        player1_profile.set_elo(game_format, player1_elo + 30*(0-probability1))
                        player2_profile.set_elo(game_format, player2_elo + 30*(1-probability2))
                    if len([team for team in replay.battle.teams if team.check_number_of_faints(6, "=")]) == 1 and len(replay.battle.teams[0].team) + len(replay.battle.teams[1].team) == 12:
                        await player1_profile.battle_completed()
                        await player2_profile.battle_completed()
                battles.append(replay.battle)
    battles = sorted(battles, key=lambda x: x.timestamp)
    # timestamps will work like this
    # integer portion: actual timestamp
    # tenths place: player index
    # rest of decimals: unique index for cases where multiple battles end at the same second
    timestamps = {}
    for battle in battles:
        if battle.timestamp not in timestamps:
            timestamps[battle.timestamp] = 0
        timestamps[battle.timestamp] += 1
    repeated_timestamps = [key for key, value in timestamps.items() if value > 1]
    for repeated_timestamp in repeated_timestamps:
        battles_with_repeated_timestamp = [battle for battle in battles if battle.timestamp == repeated_timestamp]
        for i, battle in enumerate(battles_with_repeated_timestamp):
            battle.change_timestamp(repeated_timestamp+i/1000)
    for battle in battles:
        fnf_data.formats[battle.game_format].add_battle(battle)