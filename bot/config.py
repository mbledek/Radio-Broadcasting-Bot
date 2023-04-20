from logzero import logfile, logger
import pathlib
import os

path = pathlib.Path(__file__).parent.absolute()
logfile(os.path.join(path, "radiowezel.log"), encoding='UTF-8')

TOKEN = ''

SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''

admin_role = 0
proposition_channel - 0

default_playlist = '0jH70qZn1b4pBva0Xj0rk6'
default_volume = 50
