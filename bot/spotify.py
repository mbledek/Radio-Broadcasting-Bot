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

            elif not devices["devices"][i]['is_active']:
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


def queue_random(id="0jH70qZn1b4pBva0Xj0rk6"):
    tracks = "**Dodałem:**\n"
    playlist = sp.playlist(id)
    length = len(playlist["tracks"]["items"])

    with open(os.path.join(path, "Spotify_list.pkl"), "rb") as f:
        id_list = pickle.load(f)
    if id_list in ["", None, []]:
        id_list = []
    for i in range(3):
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


