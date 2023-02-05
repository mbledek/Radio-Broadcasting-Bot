# Radio-Broadcasting-Bot
A simple Discord bot used to handle school's broadcasting system

# Usage:
Here's a list of all of its commands:
 - `/grane` - shows what's currently playing
 - `/lista` - shows what what played since launch of the bot
 - `/dodaj <id>` - adds a song to queue (given that you're an admin)
 - `/zestawienie <timespan>` - shows top 10 tracks in a given timespan
 - `/losowe` - adds 3 random songs from a playlist
 - `/clear` - clears the list of today's played tracks
 
 # Configuration
 Remember to edit the config.py file:
 - TOKEN is your Discord bot token
 - SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are your client id and client secret from Spotify's API
 - admin_role is the ID of an admin role from your server
 - spotify_random_playlist is the link to a spotify playlist from which the bot will add random songs (/losowe)

