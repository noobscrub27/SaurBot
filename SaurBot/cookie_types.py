import random
import discord
# have you ever taken a joke too far?

fortunes = ["You will come across great riches.",
            "You will find true love.",
            "You should stay indoors today.",
            "You will not survive the apocalypse.",
            "You will have an amazing day.",
            "Sleep with one eye open.",
            "Cherish your loved ones.",
            "Be careful tomorrow.",
            "A life-changing opportunity is ahead of you.",
            "Today will be alright I guess.",
            "The perfect cookie will be yours.",
            "You will lose a game to a crit.",
            "Be kind to those around you and good things will happen.",
            "Never give up hope.",
            "Nothing is impossible unless you believe it to be so.",
            "The two ingredients for financial success are dedication and gambling.",
            "A genie will grant you three wishes on your next birthday. However, one of them will have an ironic twist.",
            "Why are you reading this? You know fortunes aren't real right?",
            "Trust your instincts.",
            "Your instincts are awful. Don't trust them.",
            "Wow I just saw your fortune and, well, uh... You probably don't want to know. Good luck though.",
            "Your favorite pokemon won't be in the next game.",
            "You're going to stub your toe and it'll really hurt but you'll get over it.",
            "You're going to have a bad day. Like, truly awful. The next day will be good though.",
            "A life-changing opportunity is ahead of you. Don't take it. You have no idea how good you have it.",
            "Follow your dreams.",
            "The secret to happiness is having a ton of money.",
            "Get out of coal mines free! The next time you ruin a cookie, redeem this fortune to be immune to ridicule!",
            "Coupon for Hexagon Lemonade: Buy one drink of any size, get five free!",
            "rot"]

class MoonCookie:
    name = "Plain Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 1
    base_calories = 162
    def __init__(self):
        self.ingredients = ["Flour", "Sugar", "Kansui", "Oil", "Egg", "Vanilla Extract"]
        self.allergens = ["Gluten", "Egg"]
        self.calories = round(self.base_calories * random.uniform(0.75, 1.25), 2)
        self.get_burntness()
        self.get_sweetness()

    def get_burntness(self):
        burnt = False
        bad_recipe = False
        if random.random() < 0.1:
            burnt = True
        if random.random() < 0.05:
            bad_recipe = True
        if bad_recipe == False:
            self.recipe_accuracy = max(random.uniform(75.00, 100.00), random.uniform(75.00, 100.00))
        else:
            self.recipe_accuracy = min(random.uniform(0.00, 100.00), random.uniform(0.00, 100.00))
        self.recipe_accuracy = round(self.recipe_accuracy, 2)
        if burnt == False:
            self.well_done = min(random.uniform(0.00, 25.00), random.uniform(0.00, 25.00))
        else:
            self.well_done = max(random.uniform(0.00, 100.00), random.uniform(0.00, 100.00))
        self.well_done = round(self.well_done, 2)
        if random.random() > 0.5:
            self.well_done *= -1

    def get_sweetness(self):
        self.bitterness = self.base_bitterness + ((100 - self.recipe_accuracy) / 2)
        if self.well_done > 0:
            self.bitterness += (3 * self.well_done / 4)
        self.bitterness *= self.bitterness_modifier * random.uniform(0.75, 1.25)
        self.bitterness = round(min(self.bitterness, random.uniform(85, 90)), 2)
        self.bitterness = min(self.bitterness, 100)
        self.sweetness = 100 - self.bitterness

    def __str__(self):
        text = "Cookie Analysis\n"
        text += f"Cookie Type: {self.name}\n"
        text += "Primary Ingredients:\n"
        for ingredient in self.ingredients:
            text += f"{ingredient}, "
        text = text.removesuffix(", ")
        text += "\n"
        text += f"Calories: {self.calories}\n"
        text += f"This cookie's ingredient proportions are {self.recipe_accuracy}% accurate to the recipe.\n"
        if self.well_done >= 0:
            text += f"This cookie is {self.well_done}% overcooked.\n"
        else:
            text += f"This cookie is {abs(self.well_done)}% undercooked.\n"
        text += f"This cookie is {self.sweetness}% sweet and {self.bitterness}% bitter.\n"
        for ingredient in self.allergens:
            text += f"**ALLERGEN WARNING**: Contains {ingredient}.\n"
        if random.random() < 0.01:
            text += f"**TOXIN WARNING**: Contains lethal levels of cyanide.\n"
        if random.random() < 0.05:
            text += f"There's a fortune inside the cookie: \"{random.choice(fortunes)}\"\n"
        if random.randint(1, 4096) == 1:
            text += f"This cookie is shiny!\n"
        return text

class ChocolateMoonCookie(MoonCookie):
    name = "Chocolate Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 0.8
    base_calories = 195
    def __init__(self):
        super().__init__()
        self.ingredients.append("Sweet Heart Chocolate")
        self.allergens.append("Dairy")

class HerbalMoonCookie(MoonCookie):
    name = "Herbal Moon Cookie"
    base_bitterness = 10
    bitterness_modifier = 1.5
    base_calories = 162
    def __init__(self):
        super().__init__()
        self.ingredients.append("Apricorn Powder")

class RoyalMoonCookie(MoonCookie):
    name = "Royal Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 0.7
    base_calories = 200
    def __init__(self):
        super().__init__()
        self.ingredients.append("Honey")

class DenseMoonCookie(MoonCookie):
    name = "Dense Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 1
    base_calories = 194
    def __init__(self):
        super().__init__()
        self.ingredients.append("Crushed Poke Bean")

class BerryliciousMoonCookie(MoonCookie):
    name = "Berrylicious Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 0.9
    base_calories = 218
    def __init__(self):
        super().__init__()
        self.ingredients.append("Berry Paste")

class DigitalCookieView(discord.ui.View):
    async def send(self, interaction):
        self.timeout = 43200
        learn_more_button = discord.ui.Button(label="Manage cookies", style=discord.ButtonStyle.url, url="https://noobscrub27.github.io/SaurbotCookiePreferences/", row=0)
        self.add_item(learn_more_button)
        text = "**This bot uses cookies.**\n"
        text += "Some of them are essential while others are used to serve you a customized Saurbot experience.\n"
        await interaction.response.send_message(text, view=self, ephemeral=False)

# Artifacts

QUEST04_ARTIFACTS = {"Faisca Hollow": {"Common": [["Chipped Saucer", "I've never seen anything like this! Maybe it's a no surely it couldn't be. Could Beheeyem have visited here long ago? - Xiomara"],
                                                  ["Faded Band", "Oh, these bands are quite special, aren't they? I heard that people in the past used to use these to help Kurstraw overcome their curse, before Cleanse Tags were used. -Xiomara"],
                                                  ["Gem Cluster", "Elder Sableye are known to have many gems growing out of their body, sometimes they even fuse together! Looks like this is an example of that phenomenon. -Xiomara"],
                                                  ["Jade Mask", "Millenia ago, Lansol's people would disguise themselves as Pokemon in order to hunt large prey. They're usually made out of wood, so this one is a good find! -Xiomara"],
                                                  ["Sandy Scale", "These scales have such an interesting texture. It's said that they shed off of ancient Arbok that used to slither through these sands. -Xiomara"],
                                                  ["Spark Fossil", "Huojara are very serious and stoic Pokemon. Its scales are like charcoal and easily are caught ablazee. Consequently, many trainers avoid interacting with it. It seems to be drawn to dancing and will often practice doing so when it can. Since Huojara spark up so easily, we don't like to keep them around important equipment. -Mallorie and Ryan"]],
                                       "Uncommon": [["Charred Mega Stone", "Looks like a Mega Stone for a Pokemon that lives nearby. It's pretty charred though, so I don't know for which one it's for. -Xiomara"],
                                                    ["Spherical Boulder", "How did you even carry this here!? Ahem, the way this stone is built shows that it was once owned by an Ancient Bombseal! They used to be much larger and aggressive and couldn't yet produce fire, so instead they used large rocks like this one. -Xiomara"],
                                                    ["Spiked Ball", "You may think this is some kind of weapon but you would be wrong! Ancient Anchorage used to have tails mimicking Qwilfish, they used them to lure in Numpuff, their favorite meal. -Xiomara"],
                                                    ["Torn Up Kite", "People used to make these in homage of Ancient Magikarp, a feared Pokemon. Magikarp in the past used to be way stronger and vicious... I wonder what happened to them. -Xiomara"],
                                                    ["Armor Fossil", "Shieldon are very docile and tend to mind to themselves. They polish their faces whenever they can, which lets them take hits better. Scientists have investigated Shieldon's cell structure to try and find out what makes them so sturdy. If replicated, we could potentially build indestructible buildings. Unfortunately, it seems like the Delta scientists chose to explore that in a cruel way... -Mallorie and Ryan"],
                                                    ["Dome Fossil", "Kabuto tend to prefer aquatic areas. They molt every few days, leading their shell to grow harder over time. Apparently Kabuto were really common based on the frequency of fossils found. Can you imagine walking out onto a beach and seeing whole hordes of them? -Mallorie and Ryan"],
                                                    ["Old Amber", "Aerodactyl's sharp teeth and claws make it a dangerous pokemon to encounter. The ones revived from fossils are kept under close supervision. Whew, I remember the first time I revived an Aerodactyl... It attacked right away and things got tense until Petra calmed it down. Luckily, she's great at handling tough pokemon like that. -Mallorie and Ryan"],
                                                    ["Skull Fossil", "Cranidos love to ram into all kinds of objects with a fierce headbutt. This action hardens their head further and prepares them for evolution. The sheer force behind Cranidos's headbutts can't be put into words. There was once an incident where one rammed into a scientist- he ended up breaking several bones. Luckily, Dirigo's hospital rehabilitated him successfully. -Mallorie and Ryan"],
                                                    ["Plume Fossil", "It's said that all birds come from Archen's genetics! It's early wings leave it unable to fly, but it loves to run and jump. These little guys are so fun! I love to see Archen running around playing, as they're so energetic. They do get startled easily, though. They're the opposite of what you'd consider a \"Brave Bird!\" -Mallorie and Ryan"]],
                                       "Rare": [["Scarlet Spearhead", "This ornate spearhead is said to give protection to the beasts of the desert. It seems to be related to the one we dubbed Buzz Stinger. -Xiomara"],
                                                ["Sun Statue", "A very well maintained example of a Sun Statue! Some millennia ago they made figures of stone representing Volcarona, nowadays the richest in Areia Village make them out of gemstones. -Xiomara"]]},
                     "Iris Cavern": {"Common": [["Glass Shard", "These pieces of glass really stood the test of time. It's said that ancient Mr. Mime used the power of the sun to superheat sand to construct glass barriers before they achieved psychic abilities. -Xiomara"],
                                                ["Lansol Code", "The Lansol code is an ancient code that many people had copies of to remind them of proper conduct. It had such rules as \"thou shall not forfeit\" and \"thou shall not early gg.\" I wonder what that means... There's a bit to it that's kinda faded out, too. To be honest, I'm not the best at reading this ancient language, but maybe Mallorie at Fossil Aquisition could help with that other part. -Xiomara"],
                                                ["Mud Statuette", "This is no statue! You've picked up a sleeping Blockodile! -Xiomara"],
                                                ["Pocket Sundial", "Back in the day before the invention of clocks, it's said that people used to use small sundials fashioned by Hypno. When held at the right spot, you could estimate the time based on how the sun's shadow was cast on it. -Xiomara"],
                                                ["Rug Piece", "This may look old and ragged, but I believe this to be a piece of ancient decorative rug. The people who lived here in the past created rugs to give their Delcatty and Royalynx a relaxing place to lounge. -Xiomara"],
                                                ["Brush Fossil", "Rudoodle are shy Pokemon, even though they lived alongside humans they were seldom seen. It's very intelligent and it communicates by spreading the ink its tail secretes. You know, all those paintings down there in the caverns...? I think they're done by Rudoodle. Smeargle in the present day are attracted to them, but carbon dating shows them lasting before the first instance of Smeargle has been recorded! I wonder if Rudoodle could show me how to paint... Apparently its paintings have mystical properties! -Mallorie and Ryan"]],
                                     "Uncommon": [["Chipped Bell", "Once restored, this bell will make a beautiful sound. It was how the people of Lansol's past would honor Bronzong and pray for rain. -Xiomara"],
                                                  ["Clay Figure", "A fond memory of the past! Children used to construct doll-like figures such as this one out of clay. It bears a striking resemblance to Claydol, don't you think? -Xiomara"],
                                                  ["Fur Coat", "These coats were fashioned to handle the cold nights here, especially when Lansol's people were more nomadic. Sadly you'll almost never find these made today as Mamoswine went extinct in the area. -Xiomara"],
                                                  ["Tattered Rope", "This sturdy rope is made of Tangrowth vines woven together, since there is not much natural plant growth here that would lend well to making rope. Even though these are high quality the practice is more or less gone as Tangrowth populations dwindled. -Xiomara"],
                                                  ["Claw Fossil", "Anorith's wing-like appendages allow it to swim at surprisingly fast speeds. It tends to hide among rocks to ambush prey with sharp claws. Ironically, Anorith would ambush Omanyte the most, despite how slow they move in the water. I wonder if they liked to conserve energy, or if they have a cruel side to them like Lileep... -Mallorie and Ryan"],
                                                  ["Helix Fossil", "Omanyte calmly drifts through the water with its tentacles. If threatened, it will withdraw into its shell until the attacker leaves. Omanyte is such a cutie! You wouldn't guess it, but it loves to be pet and to cuddle. One of our scientists floated the idea of opening an Omanyte Cafe, and from the sounds of it, I think it's gonna go through! -Mallorie and Ryan"],
                                                  ["Root Fossil", "Lileep is quite deceptive- it disguises itself as plantlife while anchored to the seafloor. Unsuspecting prey looking for plantlife will then be grabbed by its appendages. You know that saying \"it's always the quiet ones?\" Lileep kinda falls into that. Because it's unassuming, you wouldn't expect Lileep to be so... scary. But uh... I've seen some things... -Mallorie and Ryan"],
                                                  ["Sail Fossil", "Due to the time it lived in, Amaura are docile and kind as they faced no predation. They prefer cold environments. Amaura is often chosen as the first fossil for a scientist to resurrect! The reason for this is because it doesn't attack or run right away. It's friendly disposition often means it will approach with a curious smile.  -Mallorie and Ryan"],
                                                  ["Cover Fossil", "Tirtouga's body can withstand immense pressure, and thus it has dived to depths that are currently inaccessible to humans. I wonder what Tirtouga see when they dive into the deep ocean... Considering how fierce Huntail and Gorebyss are, maybe it's better we don't know, hmm?  -Mallorie and Ryan"]],
                                     "Rare": [["Pretty Jar", "Now this is a rare find! It's said that, long ago, ancient Maractus used to be able to pour neverending streams of water from its arms. Scholars believe that these Maractus inspired the first jars to be made! -Xiomara"],
                                              ["Miniature Hourglass", "Oh how interesting, seems like Lansol's people have been fashioning hourglasses since long ago! Every household nowadays has one in reverence to Samsarula. -Xiomara"]]},
                     "Both": {"Common": [],
                              "Uncommon": [],
                              "Rare": [["Jaw Fossil", "Tyrunt are extremely difficult to care for, as they can get violent quickly and crush anything in their jaws. This little guy is Petra's favorite. They're both headstrong and extremely powerful, so I see why. Tyrunt raised by strong trainers with good discipline can actually grow into well behaved Tyrantrum- Petra is a great example of this phenomenon. -Mallorie and Ryan"]]}}

def random_artifact(location):
    rarity = random.random()
    if rarity < 0.60:
        rarity = "Common"
    elif rarity < 0.95:
        rarity = "Uncommon"
    else:
        rarity = "Rare"
    if random.randint(1, len(QUEST04_ARTIFACTS[location][rarity])+len(QUEST04_ARTIFACTS["Both"][rarity])) > len(QUEST04_ARTIFACTS[location][rarity]):
        location = "Both"
    index = random.randrange(len(QUEST04_ARTIFACTS[location][rarity]))
    return location, rarity, index, QUEST04_ARTIFACTS[location][rarity][index]