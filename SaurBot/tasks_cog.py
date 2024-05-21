from discord.ext import tasks, commands
import fnf_data
import saurbot_functions
import datetime
import os
import replay_analyzer

class TasksCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.backup.start()
        self.check_showdown_data.start()

    def cog_unload(self):
        self.backup.cancel()
        self.check_showdown_data.cancel()

    @tasks.loop(time=datetime.time(hour=0,minute=0,second=0,tzinfo=datetime.datetime.now().astimezone().tzinfo))
    async def backup(self):
        saurbot_functions.timelog("Creating backup")
        now = datetime.datetime.now()
        now_text = now.strftime("%m-%d-%y")
        guild_file_name = 'guild_preferences_backup - ' + now_text + '.pickle'
        guild_file_path = os.path.join("backups", "guild_preferences", guild_file_name)
        user_file_name = 'user_preferences_backup - ' + now_text + '.pickle'
        user_file_path = os.path.join("backups", "user_preferences", user_file_name)
        battle_file_name = 'battle_data_backup - ' + now_text + '.pickle'
        battle_file_path = os.path.join("backups", "battle_data", battle_file_name)
        self.bot.write_preferences(guild_file_path, user_file_path, battle_file_path)

    @backup.before_loop
    async def before_backup(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=60)
    async def check_showdown_data(self):
        await self.check_showdown_instructions()
        await self.check_new_replays()

    @check_showdown_data.before_loop
    async def before_check_showdown_data(self):
        await self.bot.wait_until_ready()
        
        
    async def check_showdown_instructions(self):
        with open("most_recent_instruction_check.txt", "r") as f:
            most_recent_instruction_check = float(f.read().strip())
        new_instructions = []
        with open(fnf_data.SHOWDOWN_INSTRUCTIONS_FILE, "r") as f:
            now = datetime.datetime.now().timestamp()
            instructions = f.readlines()
            for instruction in reversed(instructions):
                split_instruction = instruction.split("|")
                instruction_timestamp = float(split_instruction[0].strip())
                if instruction_timestamp >= most_recent_instruction_check:
                    new_instructions.insert(0, instruction)
                else:
                    break
        with open("most_recent_instruction_check.txt", "w") as f:
            f.write(str(now))
        for instruction in new_instructions:
            split_instruction = instruction.split("|")
            if split_instruction[1] == "Link":
                discord_id = int(split_instruction[2])
                showdown_name = split_instruction[3].strip()
                for guild in fnf_data.guild_preferences.values():
                    if discord_id in guild.user_profiles:
                        # this is done weirdly to avoid RuntimeError: dictionary changed size during iteration
                        # keep an eye on this, I'm probably doing something wrong
                        for key in list(guild.user_profiles[discord_id].pending_showdown_account_links):
                            if showdown_name.lower() == key.lower() and guild.user_profiles[discord_id].pending_showdown_account_links[key]+500 >= now:
                                guild.user_profiles[discord_id].showdown_accounts.append(key)
                                del guild.user_profiles[discord_id].pending_showdown_account_links[key]
        self.bot.write_preferences()

    async def check_new_replays(self):
        replay_files = [f for f in os.listdir(fnf_data.REPLAY_FOLDER)
                        if os.path.isfile(os.path.join(fnf_data.REPLAY_FOLDER, f))
                        and f not in fnf_data.analyzed_replays]
        replay_files_with_path = [os.path.join(fnf_data.REPLAY_FOLDER, f) for f in replay_files]
        if len(replay_files):
            saurbot_functions.timelog(f"Reading {len(replay_files)} replay(s).")
            fnf_data.analyzed_replays += replay_files
            self.bot.write_preferences()
            await replay_analyzer.analyze(replay_files_with_path)
            


async def setup(bot: commands.Bot):
    await bot.add_cog(TasksCog(bot))
