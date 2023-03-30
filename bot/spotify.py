import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import pickle
from datetime import datetime
import pathlib

from .config import *

path = pathlib.Path(__file__).parent.absolute()

scopes = "app-remote-control user-modify-playback-state user-read-playback-state streaming user-top-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri="https://example.com/callback",
                                               scope=scopes,
                                               open_browser=False,
                                               cache_path=os.path.join(path, ".cache")))

with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
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


def queue_random(id, count=3):
    tracks = "**Dodałem:**\n"
    playlist = sp.playlist(id)
    length = len(playlist["tracks"]["items"])
    device = get_current_id()
    if device is not None:
        sp.volume(default_volume, device)

    with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
        id_list = pickle.load(f)
    if id_list in ["", None, []]:
        id_list = []
    for i in range(count):
        number = random.randint(0, length - 1)
        now_id = playlist["tracks"]["items"][number]["track"]["id"]
        now = time.perf_counter()

        while now_id in id_list:
            number = random.randint(0, length - 1)
            now_id = playlist["tracks"]["items"][number]["track"]["id"]
            if time.perf_counter() - now > 3:
                break
        tracks = f'{tracks}{playlist["tracks"]["items"][number]["track"]["album"]["artists"][0]["name"]} -' \
                 f' {playlist["tracks"]["items"][number]["track"]["name"]}\n'
        id_list.append(now_id)
        sp.add_to_queue(now_id)
    with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
        pickle.dump(id_list, f)

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


def queue_id(id):
    device = get_current_id()
    if device is not None:
        sp.volume(default_volume, device)
    sp.add_to_queue(id)
    track = sp.track(id)
    artist = track["album"]["artists"][0]["name"]
    track_name = track["name"]

    return f"{artist} - {track_name}"


def spotify_list():
    with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
        pickle.dump([], f)
    while True:
        song = current_playing()
        if song != "":
            with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
                songs_list = pickle.load(f)
            if len(songs_list) > 0:
                if songs_list[-1][1] != song:
                    print(song)
                    songs_list.append([datetime.now().strftime("%H:%M"), song])
                    with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                        pickle.dump(songs_list, f)
            else:
                print(song)
                songs_list.append([datetime.now().strftime("%H:%M"), song])
                with open(os.path.join(path, "Spotify_list.pkl"), "wb") as f:
                    pickle.dump(songs_list, f)
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


def divide_chunks(list, length):
    # looping till length l
    for i in range(0, len(list), length):
        yield list[i:i + length]


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
    playlist_description = "A long playlist of appropriate tracks for schoolwide radio broadcasting"
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
        if devices["devices"][0]["is_active"] is True:
            return devices["devices"][0]["volume_percent"]

    return None


def volume_lowerer():
    volume = 100
    while volume > 1:
        volume = get_current_volume()
        # print(volume)
        if volume is not None:
            if volume > 50:
                volume = volume - 2
                device = get_current_id()
                if device is not None:
                    sp.volume(volume, device)
            elif 50 >= volume:
                volume = volume - 1
                device = get_current_id()
                if device is not None:
                    sp.volume(volume, device)

        time.sleep(2.5)

