import asyncio
import threading

import discord
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
    async def lista(self, ctx,
                    timespan: discord.Option(str, "Dzisiaj czy w tym tygodniu?", choices=["today", "weekly"])):
        if timespan == "today":
            with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
                songs_list = pickle.load(f)
        else:
            with open(os.path.join(path, "Spotify_list_weekly.pkl"), "rb") as f:
                songs_list = pickle.load(f)

        if len(songs_list) > 0:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")
            final = ""
            for item in songs_list:
                if len(f"{item[0]} - {item[1]}") > 5:
                    final = f"{final}{item[0]} - {item[1]}\n"

            final = split_str(final, 1900)
            if timespan == "today":
                await odpowiedz.edit_original_response(content="**Dzisiaj zagraliśmy:**")
            else:
                await odpowiedz.edit_original_response(content="**Ostatnio zagraliśmy:**")
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
                          timespan: discord.Option(str, "Przedział czasowy",
                                                   choices=["short_term", "medium_term", "long_term"])):
        await ctx.response.send_message(content=top_100(10, timespan))

    @commands.slash_command(description="Dodaj 3 losowe piosenki z naszej playlisty")
    async def losowe(self, ctx,
                     id: discord.Option(str, "ID lub link playlisty z której chcesz dodać 3 piosenki", required=False,
                                        default=default_playlist)):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            try:
                odpowiedz = await ctx.response.send_message("Dodaję...")

                await odpowiedz.edit_original_response(content=queue_random(id))
            except spotipy.exceptions.SpotifyException:
                await ctx.response.send_message(f"Sorry, nasz Spotify jest wyłączony...")

    @commands.slash_command(description="Wyczyść listę dzisiaj zagranych")
    async def wyczysc(self, ctx,
                    timespan: discord.Option(str, "Dzisiaj czy w tym tygodniu?", choices=["today", "weekly"])):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            await ctx.response.send_message(content="Już czyszczę...", ephemeral=True)
            if timespan == "today":
                with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                    pickle.dump([], f)
            else:
                with open(os.path.join(path, "Spotify_list_weekly.pkl"), "wb") as f:
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

            try:
                await ctx.channel.send("Dzięki, już dodaję...")
                queue_id(id_list[int(int(wanted_index)-1)])
            except spotipy.exceptions.SpotifyException:
                await ctx.channel.send(f"Sorry, nasz Spotify jest wyłączony...")

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

    @commands.slash_command(description="Wyślij nam propozycję piosenki")
    async def propozycja(self, ctx,
                         query: discord.Option(str, "Tytuł (i najlepiej wykonawca) piosenki którą chcesz dodać"),
                         dedykacja: discord.Option(str, "Dla kogo chcesz zadedykować?", required=False, default="")):

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

        track_info = track_info[int(int(wanted_index)-1)].split(". ")[1]
        if explicit_or_not(id_list[int(int(wanted_index)-1)]):
            track_info = f"{track_info} - Explicit"
        output = f"**Propozycja od {ctx.author.mention}:** {track_info} - " \
                 f"https://open.spotify.com/track/{id_list[int(int(wanted_index)-1)]}"

        if not dedykacja == "":
            output = f"{output}\n - Dedykacja dla: **{dedykacja}**"

        await ctx.channel.send("Dzięki, już przesłałem moderacji")
        await self.bot.get_channel(proposition_channel).send(output)

    @commands.slash_command(description="Pomiń piosenkę")
    async def pomin(self, ctx):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")

            await odpowiedz.edit_original_response(content=skip_song())

    @commands.slash_command(description="Zatrzymaj muzykę")
    async def stop(self, ctx):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            odpowiedz = await ctx.response.send_message("Czekaj sekundę...")

            await odpowiedz.edit_original_response(content=stop_music())

    @commands.slash_command(description="Zapusc muzykę na danej przerwie")
    async def przerwa(self, ctx,
                      godzina: discord.Option(int, "Godzina o której mam puszczać muzykę")):
        if admin_role not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(content="Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        else:
            if (datetime.now().hour < godzina <= 23) or (datetime.now().hour == godzina and datetime.now().minute <= 15):
                odpowiedz = await ctx.response.send_message("Czekaj sekundę...")

                breakthread = threading.Thread(target=break_thread, args=(godzina,))
                breakthread.start()

                await odpowiedz.edit_original_response(content=f"Zaplanowana przerwa o godzinie: {godzina}")
            else:
                await ctx.response.send_message("Błędna godzina...", ephemeral=True)
