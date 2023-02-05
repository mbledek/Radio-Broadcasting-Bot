import discord
from logzero import logger
from discord.ext import commands
from .spotify import *
from .converters import *
from .config import *


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def auto_spot_list(self):
        return ["short_term", "medium_term", "long_term"]

    @commands.slash_command()
    async def grane(self, ctx):
        try:
            track = current_playing()
            if not track == "":
                logger.info(f"Teraz gramy: {track}")
                await ctx.response.send_message(f"**Teraz gramy:** {track}")
            else:
                await ctx.response.send_message("Nie gramy teraz żadnej piosenki...", ephemeral=True)
        except spotipy.exceptions.SpotifyException:
            await ctx.response.send_message(f"Sorry, nasz Spotify jest wyłączony...")

    @commands.slash_command()
    async def lista(self, ctx):
        with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
            songs_list = pickle.load(f)

        if len(songs_list) > 0:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")
            final = ""
            for item in songs_list:
                final = f"{final}{item[0]} - {item[1]}\n"

            final = split_str(final, 1900)
            await odpowiedz.edit_original_response(content="**Dzisiaj zagraliśmy:**")
            for item in final:
                await ctx.channel.send(item)
        else:
            await ctx.response.send_message("Dzisiaj nie zagraliśmy jeszcze żadnej piosenki", ephemeral=True)

    @commands.slash_command()
    async def dodaj(self, ctx, id: str):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            try:
                await ctx.response.send_message("Dodaję...")
                track = queue_id(id)
                logger.info(f"Dodałem: {track}")
                await ctx.channel.send(f"**Dodałem:** {track}")
            except spotipy.exceptions.SpotifyException:
                await ctx.response.send_message(f"Sorry, nasz Spotify jest wyłączony...")

    @commands.slash_command()
    async def zestawienie(self, ctx, timespan: discord.Option(
                        str, "Hasło", name="query", autocomplete=auto_spot_list
                        )):
        await ctx.response.send_message(content=top_100(10, timespan))

    @commands.slash_command()
    async def losowe(self, ctx):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            try:
                odpowiedz = await ctx.response.send_message("Dodaję...")

                await odpowiedz.edit_original_response(content=queue_random())
            except spotipy.exceptions.SpotifyException:
                await ctx.response.send_message(f"Sorry, nasz Spotify jest wyłączony...")

    @commands.slash_command()
    async def clear(self, ctx):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            await ctx.response.send_message(content="Już czyszczę...", ephemeral=True)

            with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                pickle.dump([], f)