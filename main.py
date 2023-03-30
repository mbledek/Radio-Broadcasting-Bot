import asyncio
from abc import ABC
import threading
import discord
import spotipy
from discord.ext import commands
from logzero import logfile, logger
from datetime import datetime, date

from bot.radiowezel import Radio
from bot.config import TOKEN, default_playlist
from bot.spotify import spotify_list, queue_random, skip_song, volume_lowerer


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
        spotify_list_thread = threading.Thread(target=spotify_list)
        spotify_list_thread.start()

        await self.change_presence(activity=discord.Game(name="https://github.com/mbledek"))

        # Start music at round hours
        played = False
        while True:
            if 0 <= date.today().weekday() <= 4:
                if 10 <= datetime.now().hour <= 12 and datetime.now().minute == 1 and not played:
                    try:
                        queue_random(default_playlist, count=5)
                        await asyncio.sleep(5)
                        skip_song()
                        played = True
                    except spotipy.exceptions.SpotifyException:
                        logger.error("Aplikacja Spotify jest wyłączona")
                elif 10 <= datetime.now().hour <= 12 and datetime.now().minute == 2 and played:
                    played = False

                elif 10 <= datetime.now().hour <= 12 and datetime.now().minute == 15:
                    volume_lowerer()

            await asyncio.sleep(45)


Radiowezel()
