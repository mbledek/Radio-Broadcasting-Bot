from abc import ABC
import threading
import discord
from discord.ext import commands
from logzero import logfile, logger

from bot.radiowezel import Radio
from bot.config import TOKEN
from bot.spotify import spotify_list


class Radiowezel(commands.Bot, ABC):
    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(),
            auto_sync_commands=True,
        )

        self.remove_command('help')
        logfile("radiowezel.log", encoding='UTF-8')
        self.add_cog(Radio(self))
        self.run(TOKEN)

    async def on_ready(self):
        logger.info(f'We have logged in as {self.user}')
        await self.change_presence(activity=discord.Game(name="https://github.com/mbledek"))
        spotify_list_thread = threading.Thread(target=spotify_list)
        spotify_list_thread.start()


Radiowezel()
