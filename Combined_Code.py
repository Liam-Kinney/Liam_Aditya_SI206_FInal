import requests
import sqlite3
import random
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError
from requests.auth import HTTPBasicAuth
from spotipy.oauth2 import SpotifyClientCredentials
import re

API_KEY_LastFM = "08d3b443588c0efe5d7803f6c8b91630"
BASE_URL_LastFM = "http://ws.audioscrobbler.com/2.0/"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id="517c3756591244359ba33301aae3b33e", client_secret="eb9adf060d27438482d2f403715127cf"))

top_genres = ["pop", "rock", "hip-hop", "jazz", "classical", "country", "electronic", "alternative", "blues", "metal", "anime", "indie", "folk", "reggae", "r&b", "rap", "house", "soul", "funk", "k-pop", "emo", "grunge", "techno"]
genre_re_pattern = re.compile(r'\b(?:' + '|'.join(top_genres) + r')\b', re.IGNORECASE)

def search_track_uri(track_name, artist_name=None, limit=1):
    """Search for a track and return its URI"""
    if artist_name:
        query = f"track:{track_name} artist:{artist_name}"
    else:
        query = track_name
    
    results = spotify.search(q=query, type='track', limit=limit)
    
    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    else:
        return None
    
def return_song_length(track_uri):
    test1 = search_track_uri(track_uri)
    result = spotify.track(test1, None)
    return(result["duration_ms"]/60000)

def get_tracks_from_page(page):  #gets tracks from a specific page in the api
    params = {
        "method": "chart.gettoptracks",
        "api_key": API_KEY_LastFM,
        "format": "json",
        "limit": 100,
        "page": page
    }
    response = requests.get(BASE_URL_LastFM, params = params)
    data = response.json()

    track_list = []
    for track in data["tracks"]["track"]:
        artist_name = track["artist"]["name"]
        track_name = track["name"]
        track_list.append((artist_name, track_name))

    return track_list

def get_top_1050_tracks(): ##calls the function above to read several pages until getting to 1050 tracks
    top_1050_tracks = []
    for page in range(1, 13):
        tracks = get_tracks_from_page(page)
        top_1050_tracks.extend(tracks)
    return top_1050_tracks

def get_genre(tags):
    for tag in tags:
        match = genre_re_pattern.search(tag)
        if match:
            return match.group(0).lower()
    return "unknown"

def get_track_info(artist, track): ##returns info from Last.FM api
    params = {
        "method": "track.getInfo",
        "api_key": API_KEY_LastFM,
        "artist": artist,
        "track": track,
        "format": "json"
    }
    response = requests.get(BASE_URL_LastFM, params=params)
    data = response.json()

    if "track" not in data:
        print("Track not found.")
        return None

    track_data = data["track"]
    name = track_data.get("name")
    playcount = track_data.get("playcount")
    tags = [tag["name"] for tag in track_data.get("toptags", {}).get("tag", [])]
    genre = get_genre(tags)
    return (name, artist, playcount, genre)

track_list = get_top_1050_tracks()  ##calling function to get a list of 1050 tracks

random.shuffle(track_list)


def search_25_track_lengths(track_list):
    count = 0
    track_length_tuple_list = []
    while count < 25:
        track_uri = search_track_uri(track_list[count])

        if track_uri is None:
            print("Track not found")
            count += 1
        else:
            track_length_tuple_list.append((track_list[count][0], track_list[count][1], return_song_length(track_uri)))
            count += 1
    return track_length_tuple_list    

print(search_25_track_lengths(track_list))
conn = sqlite3.connect("tracks.db")
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS tracks(
        title TEXT,
        artist TEXT,
        playcount INTEGER,
        genre TEXT,
        PRIMARY KEY (title, artist)
        )
''')

num_inserted = 0

for artist, track in track_list: ##Looping to add tracks to the database
    if num_inserted >= 25: ##limits the data base additions to 25 elements
        break
    info = get_track_info(artist, track)
    if info:
        cur.execute("INSERT OR IGNORE INTO tracks (title, artist, playcount, genre) VALUES (?, ?, ?, ?)", info)
        if cur.rowcount > 0:
            num_inserted += 1

conn.commit()
conn.close()

conn = sqlite3.connect("tracks.db")
cur = conn.cursor()




