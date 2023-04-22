import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import pickle
from datetime import datetime
from .config import *

scopes = "app-remote-control user-modify-playback-state user-read-playback-state streaming user-top-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri="https://example.com/callback",
                                               scope=scopes,
                                               open_browser=False,
                                               cache_path=os.path.join(path, ".cache")))

with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
    pickle.dump([], f)
if not os.path.isfile(os.path.join(path, "Spotify_list_weekly.pkl")):
    with open(os.path.join(path, "Spotify_list_weekly.pkl"), "wb") as f:
        pickle.dump([], f)


def get_current_id():
    devices = sp.devices()

    if len(devices["devices"]) != 0:
        for i in range(len(devices["devices"])):
            if devices["devices"][i]['is_active']:
                return devices["devices"][i]['id']

        for i in range(len(devices["devices"])):
            if not devices["devices"][i]['is_active']:
                return devices["devices"][i]['id']

    return


def current_playing():
    track = sp.current_user_playing_track()
    try:
        artist = track["item"]["artists"]
        for i in range(len(artist)):
            artist[i] = artist[i]["name"]

        track_name = track["item"]["name"]

        artist = ", ".join(artist) + ": "
        return str(artist + track_name)
    except TypeError:
        return ""


def queue_random(playlist_id, count=7):
    tracks = "**Dodałem:**\n"
    total_songs = []
    i = 0
    while True:
        playlist = sp.playlist_items(playlist_id, offset=i)
        songs = playlist["items"]
        if not songs:
            break
        else:
            total_songs.extend(songs)
            i = i + 100

    device = get_current_id()
    if device is not None:
        try:
            sp.volume(default_volume, device)
        except spotipy.exceptions.SpotifyException:
            print("Aplikacja Spotify jest wyłączona")

    with open(os.path.join(path, "Spotify_list_weekly.pkl"), "rb") as f:
        played_list = pickle.load(f)
    id_list = []
    for i in range(len(played_list)):
        id_list.append(played_list[i][1])
    if id_list in ["", None, []]:
        id_list = []
    for i in range(count):
        random.shuffle(total_songs)
        number = random.randint(0, len(total_songs) - 1)
        now_id = total_songs[number]["track"]["name"]
        now = time.perf_counter()

        while now_id in id_list:
            number = random.randint(0, len(total_songs) - 1)
            now_id = total_songs[number]["track"]["name"]
            if time.perf_counter() - now > 10:
                break

        artist = total_songs[number]["track"]["album"]["artists"]
        for j in range(len(artist)):
            artist[j] = artist[j]["name"]
        artist = ", ".join(artist) + ": "

        tracks = f'{tracks}{artist} - {now_id}\n'
        try:
            sp.add_to_queue(total_songs[number]["track"]["id"], device)
            played_list.append([datetime.now().strftime("%H:%M"), f"{artist} - {now_id}"])
            id_list.append(f"{artist} - {now_id}")
        except spotipy.exceptions.SpotifyException:
            print("Aplikacja Spotify jest wyłączona")
    with open(os.path.join(path, "Spotify_list_weekly.pkl"), "wb") as f:
        pickle.dump(played_list, f)

    return tracks


def top_100(count=100, timespan="short_term"):
    output = {"short_term": "**Short term:**\n",
              "medium_term": "**Medium term:**\n",
              "long_term": "**Long term:**\n"}[timespan]
    artist = sp.current_user_top_artists(count, time_range=timespan)

    for item in artist["items"]:
        output = output + f'{item["name"]} - {item["popularity"]}\n'

    output = output + "\n"
    track = sp.current_user_top_tracks(count, time_range=timespan)

    for item in track["items"]:
        output = output + f'{item["album"]["artists"][0]["name"]} - {item["name"]}, {item["popularity"]}\n'

    return output


def queue_id(track_id):
    device = get_current_id()
    if device is not None:
        try:
            sp.volume(default_volume, device)
            sp.add_to_queue(track_id)
        except spotipy.exceptions.SpotifyException:
            print("Aplikacja Spotify jest wyłączona")
    track = sp.track(track_id)
    artist = track["album"]["artists"][0]["name"]
    track_name = track["name"]

    return f"{artist} - {track_name}"


def spotify_list():
    while True:
        song = current_playing()
        if song != "":
            with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
                songs_list = pickle.load(f)
            with open(os.path.join(path, "Spotify_list_weekly.pkl"), "rb") as f:
                songs_list_weekly = pickle.load(f)

            if len(songs_list) > 0:
                if songs_list[-1][1] != song:
                    # print(song)
                    songs_list.append([datetime.now().strftime("%H:%M"), song])
                    with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                        pickle.dump(songs_list, f)
            else:
                # print(song)
                songs_list.append([datetime.now().strftime("%H:%M"), song])
                with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                    pickle.dump(songs_list, f)

            if len(songs_list_weekly) > 0:
                if songs_list_weekly[-1][1] != song:
                    print(song)
                    songs_list_weekly.append([datetime.now().strftime("%H:%M"), song])
                    with open(os.path.join(path, "Spotify_list_weekly.pkl"), "wb") as f:
                        pickle.dump(songs_list_weekly, f)
            else:
                print(song)
                songs_list_weekly.append([datetime.now().strftime("%H:%M"), song])
                with open(os.path.join(path, "Spotify_list_weekly.pkl"), "wb") as f:
                    pickle.dump(songs_list_weekly, f)

        time.sleep(30)


def search_tracks(query: str):
    search_result = sp.search(q=query, type="track", limit=5)

    track_info = []
    id_list = []
    for track in search_result['tracks']['items']:
        index = search_result['tracks']['items'].index(track)
        artist_name = track['artists'][0]['name']
        song_name = track['name']
        track_info.append(f"{index+1}. {artist_name} - {song_name}")
        id_list.append(track['id'])

    return track_info, id_list


def divide_chunks(given_list, length):
    # looping till length l
    for i in range(0, len(given_list), length):
        yield given_list[i:i + length]


def new_recommended_playlist(genres: str, explicit: bool):
    playlist_name = f"{datetime.now().strftime('%d.%m')} - {genres}"
    genres = genres.split(", ")
    track_ids = []

    for genre in genres:
        results = sp.search(q=f"genre:{genre}", type="track", limit=50)
        tracks = results["tracks"]["items"]

        # Loop over each track and check if it has explicit content
        for track in tracks:
            track_id = track["id"]
            track_info = sp.track(track_id)
            if not (track_info["explicit"] is True and explicit is False):
                track_ids.append(track_id)

    # Shuffle the track IDs to randomize the order of the playlist
    random.shuffle(track_ids)

    # Create a new playlist on Spotify
    playlist_description = "A long playlist of appropriate tracks for school-wide radio broadcasting"
    user_id = sp.current_user()["id"]
    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
    # print(new_playlist['id'])

    # Add the tracks to the new playlist
    length = len(track_ids)
    track_ids = divide_chunks(track_ids, 50)
    for item in track_ids:
        sp.playlist_add_items(new_playlist["id"], item)
        time.sleep(2)

    # Print the number of tracks in the playlist
    print(f"Generated playlist with {length} tracks")

    # Print the link to the new playlist on Spotify
    playlist_link = f"https://open.spotify.com/playlist/{new_playlist['id']}"
    if length > 0:
        return f"Oto link do playlisty: {playlist_link}"
    else:
        time.sleep(3)
        sp.current_user_unfollow_playlist(new_playlist['id'])
        return "Spróbuj zmienić swoje hasła, Spotify zwrócił mi pustą playlistę"


def skip_song():
    try:
        sp.next_track(get_current_id())
        return "Pominąłem!"
    except spotipy.exceptions.SpotifyException:
        return "Wystąpił błąd..."


def explicit_or_not(track_id):
    return sp.track(track_id)['explicit']


def get_current_volume():
    devices = sp.devices()

    if len(devices["devices"]) > 0:
        for i in range(len(devices["devices"])):
            if devices["devices"][i]["is_active"] is True:
                return devices["devices"][i]["volume_percent"]

    return None


def stop_music():
    try:
        sp.pause_playback(get_current_id())
        return "Zatrzymałem!"
    except spotipy.exceptions.SpotifyException:
        return "Wystąpił błąd..."


def volume_lowerer():
    logger.info("Starting to lower volume")
    volume = 100
    while volume > 25:
        volume = get_current_volume()
        # print(volume)
        if volume is not None:
            if volume > 50:
                volume = volume - 3
                device = get_current_id()
                # print(device)
                if device is not None:
                    sp.volume(volume, device)
                time.sleep(1)
            elif 50 >= volume:
                volume = volume - 2
                device = get_current_id()
                # print(device)
                if device is not None:
                    sp.volume(volume, device)

        time.sleep(1)
    stop_music()
    logger.info("Volume lowered")


def break_thread(hour: int):
    played = False
    while True:
        if datetime.now().hour == hour and datetime.now().minute == 1 and not played:
            logger.info(f"Preparing playback for {hour} hour")
            try:
                queue_random(default_playlist, count=5)
                time.sleep(5)
                skip_song()
                played = True
            except spotipy.exceptions.SpotifyException:
                logger.error("Aplikacja Spotify jest wyłączona")

        elif datetime.now().hour == hour and datetime.now().minute == 15:
            volume_lowerer()
            logger.info(f"Playback for {hour} hour finished")
            return

        time.sleep(15)
