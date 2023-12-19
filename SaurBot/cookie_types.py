import random
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
            "The perfect cookie will be yours."]

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
            self.bitterness += (self.well_done / 2)
        self.bitterness *= self.bitterness_modifier * random.uniform(0.75, 1.25)
        self.bitterness = round(min(self.bitterness, random.uniform(85, 90)), 2)
        self.sweetness = 100 - self.bitterness

    def __str__(self):
        text = "Cookie Analysis\n"
        text += f"Cookie Type: {self.name}\n"
        text += "Primary Ingredients:\n"
        for ingredient in self.ingredients:
            text += f"- {ingredient}\n"
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
        if random.random() < 0.01:
            text += f"There's a fortune inside the cookie: \"{random.choice(fortunes)}\"\n"
        return text

class ChocolateMoonCookie(MoonCookie):
    name = "Chocolate Moon Cookie"
    base_bitterness = 0
    bitterness_modifier = 0.75
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
    bitterness_modifier = 0.5
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
    bitterness_modifier = 0.75
    base_calories = 218
    def __init__(self):
        super().__init__()
        self.ingredients.append("Berry Paste")