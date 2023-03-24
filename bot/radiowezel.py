import asyncio

import discord
from logzero import logger
from discord.ext import commands
from .spotify import *
from .converters import *
from .config import *


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Sprawdź co teraz gramy")
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

    @commands.slash_command(description="Sprawdź co dzisiaj graliśmy")
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

    @commands.slash_command(description="Dodaj piosenkę do kolejki (musisz podać ID lub link)")
    async def dodaj(self, ctx,
                    id: discord.Option(str, "ID lub link piosenki którą chcesz dodać")):
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

    @commands.slash_command(description="Sprawdź jakich piosenek słuchamy najczęściej")
    async def zestawienie(self, ctx,
                          timespan: discord.Option(str, choices=["short_term", "medium_term", "long_term"])):
        await ctx.response.send_message(content=top_100(10, timespan))

    @commands.slash_command(description="Dodaj 3 losowe piosenki z naszej playlisty")
    async def losowe(self, ctx,
                     id: discord.Option(str, "ID lub link playlisty z której chcesz dodać 3 piosenki", required=False,
                                        default="2Jlz3GhvPnf3z9v86EYWLR")):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            try:
                odpowiedz = await ctx.response.send_message("Dodaję...")

                await odpowiedz.edit_original_response(content=queue_random(id))
            except spotipy.exceptions.SpotifyException:
                await ctx.response.send_message(f"Sorry, nasz Spotify jest wyłączony...")

    @commands.slash_command(description="Wyczyść listę dzisiaj zagranych")
    async def clear(self, ctx):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            await ctx.response.send_message(content="Już czyszczę...", ephemeral=True)

            with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                pickle.dump([], f)

    @commands.slash_command(description="Dodaj piosenkę do kolejki, wyszukując ją po jej nazwie")
    async def szukaj(self, ctx,
                     query: discord.Option(str, "Tytuł (i najlepiej wykonawca) piosenki którą chcesz dodać")):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")

            track_info, id_list = search_tracks(query)

            await odpowiedz.edit_original_response(content=f"O którą z tych piosenek Ci chodziło?: ")
            await ctx.channel.send("\n".join(track_info))

            def check(m):
                return m.author.id == ctx.author.id and 1 <= int(m.content) <= 5

            try:
                wanted_index = await self.bot.wait_for("message", check=check, timeout=30.0)
                wanted_index = wanted_index.content
            except asyncio.TimeoutError:
                await ctx.channel.send("Timed out... Please start the process again")
                return

            await ctx.channel.send("Dzięki, już dodaję...")
            queue_id(id_list[int(int(wanted_index)-1)])

    @commands.slash_command(description="Stwórz playlistę z danych gatunków")
    async def playlista(self, ctx,
                        gatunki: discord.Option(str, "Gatunki (po angielsku) z których chcesz stworzyć playlistę"),
                        explicit: discord.Option(bool, "Czy chcesz zawrzeć w niej piosenki z bluźnierstwami?")):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")

            link = new_recommended_playlist(gatunki, explicit)

            await odpowiedz.edit_original_response(content=link)
