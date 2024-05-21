import fnf_data
import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import io
import enum

class Quest04Paths(enum.Enum):
    iris_cavern = 0
    faisca_hollow = 1
QUEST04_NUMBER_OF_BOXES = 15
QUEST04_MINIMUM_SELECTABLE_BOXES = 5

QUEST04_CHALLENGE_TEXTS = {"single": {"start": "<@CHALLENGER> challenged <@CHALLENGEE> to a battle at ",
                                        "accepted": ["<@CHALLENGEE> accepted the challenge!",
                                                       "<@CHALLENGER> and <@CHALLENGEE> agreed to battle. Winner takes all!",
                                                       "Knowing that the only thing worse than losing is being a coward, <@CHALLENGEE> accepted the challenge.",
                                                       "<@CHALLENGEE> is the only thing standing between <@CHALLENGER> and riches. Battle start!",
                                                       "Humanity is cursed to endlessly quarrel over worldly possessions. Not one to break the cycle, <@CHALLENGEE> accepted the challenge!",
                                                       "There's more than enough treasure for all of you, but sure, fight over it.",
                                                       "<@CHALLENGER> VS <@CHALLENGEE>! My bet's on <@CHALLENGER>.",
                                                       "<@CHALLENGER> VS <@CHALLENGEE>! My bet's on <@CHALLENGEE>.",
                                                       "<@CHALLENGER> and <@CHALLENGEE> agreed to battle for the treasure! Whoever wins, share some with me!",
                                                       "<@CHALLENGER> and <@CHALLENGEE> fight for riches and glory!"],
                                          "declined": ["<@CHALLENGEE> declined the challenge.",
                                                       "Sorry <@CHALLENGER>, <@CHALLENGEE> has plans with someone else.",
                                                       "In a show of mercy towards <@CHALLENGER>, <@CHALLENGEE> declined the challenge.",
                                                       "<@CHALLENGEE> put their cowardice on full display and declined the challenge.",
                                                       "<@CHALLENGEE> decided that the real treasure is the friends they made along the way.",
                                                       "<@CHALLENGEE> knows the truth: they don't need treasure when the cookie command is right there.",
                                                       "Feeling charitable, <@CHALLENGEE> let <@CHALLENGER> have the treasure.",
                                                       "<@CHALLENGEE> would have loved to battle <@CHALLENGER>, but they really had to use the restroom.",
                                                       "<@CHALLENGEE> needed to restock on potions.",
                                                       "<@CHALLENGEE> thinks about their family. They miss <@CHALLENGEE>. <@CHALLENGEE> works late every day and for what? They're no richer than before. <@CHALLENGEE> thinks about their kids, growing up without them. Who needs treasure? Family is what's important."]},
                               "multi": {"start": "<@CHALLENGER> and <@CHALLENGER2> challenged <@CHALLENGEE> and <@CHALLENGEE2> to a battle at ",
                                         "accepted": ["<@CHALLENGEE> and <@CHALLENGEE2> accepted the challenge!",
                                                      "<@CHALLENGER>, <@CHALLENGER2>, <@CHALLENGEE>, and <@CHALLENGEE2> agreed to battle. Winners take all!",
                                                      "Knowing that the only thing worse than losing is being a coward, <@CHALLENGEE> and <@CHALLENGEE2> accepted the challenge.",
                                                      "<@CHALLENGER>, <@CHALLENGER2>, <@CHALLENGEE>, and <@CHALLENGEE2> agreed to fight for fortune!",
                                                      "Humanity is cursed to endlessly quarrel over worldly possessions. Not ones to break the cycle, <@CHALLENGEE> and <@CHALLENGEE2> accepted the challenge!",
                                                      "There's more than enough treasure for all of you, but sure, fight over it.",
                                                      "<@CHALLENGER> and <@CHALLENGER2> VS <@CHALLENGEE> and <@CHALLENGEE2>! My bet's on <@CHALLENGER> and <@CHALLENGER2>.",
                                                      "<@CHALLENGER> and <@CHALLENGER2> VS <@CHALLENGEE> and <@CHALLENGEE2>! My bet's on <@CHALLENGEE> and <@CHALLENGEE2>.",
                                                      "<@CHALLENGER>, <@CHALLENGER2>, <@CHALLENGEE>, and <@CHALLENGEE2> agreed to battle for the treasure! Whoever wins, share some with me!",
                                                      "<@CHALLENGER>, <@CHALLENGER2>, <@CHALLENGEE>, and <@CHALLENGEE2> fight for riches and glory!"],
                                         "declined": ["<@CHALLENGEE> and <@CHALLENGEE2> declined the challenge.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> were too busy chatting to hear <@CHALLENGER> and <@CHALLENGER2> challenge them.",
                                                      "In a show of mercy towards <@CHALLENGER> and <@CHALLENGER2>, <@CHALLENGEE> and <@CHALLENGEE2> declined the challenge.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> put their cowardice on full display and declined the challenge.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> decided that the real treasure is the friends they made along the way.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> have no time for battling. The cookie command is more important.",
                                                      "Feeling charitable, <@CHALLENGEE> and <@CHALLENGEE2> let <@CHALLENGER> and <@CHALLENGEE2> have the treasure.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> are frantically looking for an outlet to charge their PokeNavs. No time for battle.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> needed to restock on potions.",
                                                      "<@CHALLENGEE> and <@CHALLENGEE2> are arguing over their shares of the treasure. <@CHALLENGER> and <@CHALLENGER2> decided that it's not a good time to interrupt."],
                                         "ally declined": ["<@CHALLENGER2> declined the challenge.",
                                                           "Sorry <@CHALLENGER>, <@CHALLENGER2> has plans with someone else.",
                                                           "In a show of mercy towards <@CHALLENGEE> and <@CHALLENGEE2>, <@CHALLENGER2> declined the challenge.",
                                                           "<@CHALLENGER2> put their cowardice on full display and declined the challenge.",
                                                           "<@CHALLENGER2> decided that the real treasure is the friends they made along the way.",
                                                           "<@CHALLENGER2> knows the truth: they don't need treasure when the cookie command is right there.",
                                                           "<@CHALLENGER2> would have loved to battle <@CHALLENGEE> and <@CHALLENGEE2>, but they really had to use the restroom.",
                                                           "<@CHALLENGER2> needed to restock on potions.",
                                                           "<@CHALLENGER2> thinks about their family. They miss <@CHALLENGER2>. <@CHALLENGER2> works late every day and for what? They're no richer than before. <@CHALLENGER2> thinks about their kids, growing up without them. Who needs treasure? Family is what's important."]}}

class ChallengeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    async def send(self, interaction, challengee, challenger2, challengee2, path, bot):
        self.interaction = interaction
        self.challenger = interaction.user
        self.challengee = challengee
        self.challenger2 = challenger2
        self.challengee2 = challengee2
        self.bot = bot
        self.battle_type = "single" if (self.challenger2 is None or self.challengee2 is None) else "multi"
        self.bot.create_guild_user_profile(interaction.guild, self.challengee.id)
        self.waiting_on_response = {self.challengee.id}
        if self.battle_type == "multi":
            self.bot.create_guild_user_profile(interaction.guild, self.challenger2.id)
            self.bot.create_guild_user_profile(interaction.guild, self.challengee2.id)
            self.waiting_on_response.add(self.challenger2.id)
            self.waiting_on_response.add(self.challengee2.id)
        self.responded = set()
        self.path = path
        self.attachments = []
        self.show_accepted_amount = True
        self.text = QUEST04_CHALLENGE_TEXTS[self.battle_type]["start"]
        self.text += "Iris Cavern!" if self.path.value == 0 else "Faisca Hollow!"

        await interaction.response.defer()
        self.message = await interaction.followup.send(content=self.replace_text(), view=self)
        # this is the only way to make the ping visually appear. the actual notification is impossible however.
        await self.update_message()

    def replace_text(self):
        text = self.text.replace("<@CHALLENGER>", f"<@{self.challenger.id}>").replace("<@CHALLENGEE>", f"<@{self.challengee.id}>")
        if self.battle_type == "multi":
             text = text.replace("<@CHALLENGER2>", f"<@{self.challenger2.id}>").replace("<@CHALLENGEE2>", f"<@{self.challengee2.id}>")
        return text

    async def update_message(self):
        text = self.replace_text()
        if self.show_accepted_amount and self.battle_type == "multi":
            text += f"\n({len(self.responded)}/3 accepted)"
        await self.message.edit(content=text, view=self)

    async def decline_challenge(self, ally_declined):
        if ally_declined:
            self.text += "\n" + random.choice(QUEST04_CHALLENGE_TEXTS["multi"]["ally declined"])
        else:
            self.text += "\n" + random.choice(QUEST04_CHALLENGE_TEXTS[self.battle_type]["declined"])
        self.show_accepted_amount = False
        await self.update_message()
        await self.destroy()

    async def accept_challenge(self):
        self.text += "\n" + random.choice(QUEST04_CHALLENGE_TEXTS[self.battle_type]["accepted"])
        self.text += "\nHere is your safari box:"
        safari_box = self.get_safari_box()
        if self.path.value == 0:
            url = f"https://raw.githubusercontent.com/noelcerulean/pokemonshowdownimages/master/safaris/treasure%20hunting/Iris%20Cavern/{safari_box}.PNG"
        else:
            url = f"https://raw.githubusercontent.com/noelcerulean/pokemonshowdownimages/master/safaris/treasure%20hunting/Faisca%20Hollow/{safari_box}.PNG"
        # source https://stackoverflow.com/questions/73475687/how-to-make-discord-py-send-an-image-from-a-url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as f:
                    await self.message.edit(content=self.replace_text(), attachments=[discord.File(f, "safari_image.png")], view=self)
        self.show_accepted_amount = False
        await self.update_message()
        self.add_to_seen_safaris(safari_box)
        await self.destroy()
    
    def get_safari_box(self):
        selectable_boxes = set(range(1,QUEST04_NUMBER_OF_BOXES+1))
        challenger_box = fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[self.challenger.id].quest_data[4]["boxes seen"][self.path.value]
        challengee_box = fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[self.challengee.id].quest_data[4]["boxes seen"][self.path.value]
        box_lists = [challenger_box, challengee_box]
        if self.battle_type == "single":
            loop_iterations = max(len(challenger_box), len(challengee_box))
        else:
            challenger2_box = fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[self.challenger2.id].quest_data[4]["boxes seen"][self.path.value]
            challengee2_box = fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[self.challengee2.id].quest_data[4]["boxes seen"][self.path.value]
            loop_iterations = max(len(challenger_box), len(challengee_box), len(challenger2_box), len(challengee2_box))
            box_lists.append(challenger2_box)
            box_lists.append(challengee2_box)
        stop_flag = False
        for i in range(loop_iterations):
            for box_list in box_lists:
                try:
                    selectable_boxes.discard(box_list[i])
                except IndexError:
                    pass
                if len(selectable_boxes) == QUEST04_MINIMUM_SELECTABLE_BOXES:
                    stop_flag = True
                    break
            if stop_flag:
                break
        return random.choice(list(selectable_boxes))
    
    def add_to_seen_safaris(self, box):
        player_ids = [self.challenger.id, self.challengee.id]
        if self.battle_type == "multi":
            player_ids.append(self.challenger2.id)
            player_ids.append(self.challengee2.id)
        for player in player_ids:
            try:
                fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[player].quest_data[4]["boxes seen"][self.path.value].remove(box)
            except ValueError:
                pass
            fnf_data.guild_preferences[self.interaction.guild_id].user_profiles[player].quest_data[4]["boxes seen"][self.path.value].insert(0, box)
        self.bot.write_preferences()

    async def destroy(self):
        for item in self.children:
            item.disabled = True
        await self.update_message()
        self.stop()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="ChallengeView:accept_challenge_button")
    async def accept_challenge_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_message()
        if len(self.waiting_on_response) == 0:
            await self.accept_challenge()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="ChallengeView:decline_challenge_button")
    async def decline_challenge_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        ally_declined = True if self.battle_type == "multi" and interaction.user.id == self.challenger2.id else False
        await self.decline_challenge(ally_declined)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] in ["ChallengeView:accept_challenge_button", "ChallengeView:decline_challenge_button"]:
            if interaction.user.id in self.waiting_on_response:
                self.waiting_on_response.remove(interaction.user.id)
                self.responded.add(interaction.user.id)
                return True
            elif interaction.user.id in self.responded and len(self.waiting_on_response):
                await interaction.response.send_message(f"At least one other player has not accepted yet.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Only the players invited can choose to accept or decline this challenge.", ephemeral=True)
        return False


class QuestCog(commands.GroupCog, group_name="quest"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="challenge", description="Challenge another player to battle for the treasure.")
    async def command_challenge(self, interaction: discord.Interaction,
                                      path: Quest04Paths,
                                      opponent: discord.Member,
                                      partner: discord.Member=None,
                                      opponent2: discord.Member=None):
        """Placeholder description.

        Parameters
        -----------
        path: Quest04Paths
            Placeholder description.
        opponent: discord.Member
            Placeholder description.
        partner: discord.Member
            Placeholder description.
        opponent2: discord.Member
            Placeholder description.
        """
        multi_battle_players = set([player for player in [partner, opponent2] if player is not None])
        all_other_players = set([player for player in [opponent, partner, opponent2] if player is not None])
        if len(multi_battle_players) == 1:
            await interaction.response.send_message("There must be two players on each side for multi-battles.", ephemeral=True)
        elif interaction.user.id in [item.id for item in all_other_players]:
            await interaction.response.send_message("You can't challenge yourself.", ephemeral=True)
        elif len(multi_battle_players) == 2 and len(all_other_players) < 3:
            await interaction.response.send_message("There must be 4 different players for multi-battles.", ephemeral=True)
        else:
            challenge_view = ChallengeView()
            await challenge_view.send(interaction, opponent, partner, opponent2, path, self.bot)
    '''
    @command_challenge.error
    async def command_challenge_error(self, interaction: discord.Interaction, error):
        await fnf_data.ephemeral_error_message(interaction, error)
    '''
    
async def setup(bot: commands.Bot):
    await bot.add_cog(QuestCog(bot))