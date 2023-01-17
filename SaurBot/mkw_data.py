MKW_CHARACTERS = {"Light": ["Baby Mario", "Baby Luigi", "Baby Peach", "Baby Daisy", "Toad", "Toadette", "Koopa", "Dry Bones"],
                  "Medium": ["Mario", "Luigi", "Peach", "Daisy", "Yoshi", "Birdo", "Diddy Kong", "Bowser Jr."],
                  "Heavy": ["Wario", "Waluigi", "DK", "Bowser", "King Boo", "Rosalina", "Funky Kong", "Dry Bowser"]}
MKW_KARTS = {"Light": ["Standard Kart S", "Booster Seat", "Mini Beast", "Cheep Charger", "Tiny Titan", "Blue Falcon"],
             "Medium": ["Standard Kart M", "Classic Dragster", "Wild Wing", "Super Blooper", "Daytripper", "Sprinter"],
             "Heavy": ["Standard Kart L", "Offroader", "Flame Flyer", "Piranha Prowler", "Jetsetter", "Honeycoupe"]}
MKW_BIKES = {"Light": ["Standard Bike S", "Bullet Bike", "Bit Bike", "Quacker", "Magikruiser", "Jet Bubble"],
             "Medium": ["Standard Bike M", "Mach Bike", "Sugarscoot", "Zip Zip", "Sneakster", "Dolphin Dasher"],
             "Heavy": ["Standard Bike L", "Flame Runner", "Wario Bike", "Shooting Star", "Spear", "Phantom"]}

MKW_EVIL_PLAYERS = ["Diana"]
MKW_EASTER_EGG = ["<evilplayer> is displeased.",
                  "<evilplayer> is watching.",
                  "<evilplayer> wants blood.",
                  "<evilplayer> is contemplating something...",
                  "<evilplayer> is pleased... for now.",
                  "Everyone target Noel for this race.",
                  "<evilplayer> forgot to prepare a menacing message.",
                  "You wouldn't have liked what you got so I'm giving you another chance."]

def add_tracks(filename):
    tracks = []
    with open(filename, "r") as f:
        for line in f.readlines():
            tracks.append(line.strip())
    return tracks


CTGP_CUSTOM = add_tracks("MKW CTGP tracks.txt")
CTGP_RETRO = add_tracks("MKW CTGP retro tracks.txt")
VANILLA_WII = add_tracks("MKW wii tracks.txt")
VANILLA_RETRO = add_tracks("MKW retro tracks.txt")