import json
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

def search_track_uri(track_name, artist_name, limit=1):
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
    result = spotify.track(track_uri, None)
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


def search_100_track_lengths(track_list):
    count = 0
    track_length_tuple_list = []
    while count < 100:
        track_uri = search_track_uri(track_list[count][1], track_list[count][0])

        if track_uri is None:
            print("Track not found")
            count += 1
        else:
            track_length_tuple_list.append((track_list[count][0], track_list[count][1], return_song_length(track_uri)))
            count += 1
    return track_length_tuple_list    

track_length_tuple_list = search_100_track_lengths(track_list)
conn = sqlite3.connect("tracks.db")
cur = conn.cursor()

'''# Drop and recreate the table to ensure it has the correct structure
cur.execute('DROP TABLE IF EXISTS tracks')'''

cur.execute('''
    CREATE TABLE IF NOT EXISTS tracks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        playcount INTEGER,
        genre TEXT,
        artist_id INTEGER,
        genre_id INTEGER,
        CONSTRAINT unique_track UNIQUE(title, artist)
    )
''')

num_inserted = 0
for artist, track in track_list:
    if num_inserted >= 25:  # Still limit to 25 tracks
        break
    info = get_track_info(artist, track)
    if info:
        cur.execute("INSERT OR IGNORE INTO tracks (title, artist, playcount, genre) VALUES (?, ?, ?, ?)", info)
        if cur.rowcount > 0:
            num_inserted += 1

# Now update artist_ids using a subquery to generate sequential IDs
cur.execute('''
    UPDATE tracks
    SET artist_id = (
        SELECT COUNT(DISTINCT t2.artist) 
        FROM tracks t2 
        WHERE t2.artist <= tracks.artist
    )
    WHERE artist_id IS NULL
''')

# Update genre_ids using a similar subquery
cur.execute('''
    UPDATE tracks
    SET genre_id = (
        SELECT COUNT(DISTINCT t2.genre) 
        FROM tracks t2 
        WHERE t2.genre <= tracks.genre
    )
    WHERE genre_id IS NULL
''')

conn.commit()
conn.close()

conn = sqlite3.connect("tracks.db")
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS track_lengths(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        length_minutes REAL,
        CONSTRAINT unique_track UNIQUE(title, artist)
        )
    '''
)

for artist, track_name, length in track_length_tuple_list:
    cur.execute('''
        INSERT OR IGNORE INTO track_lengths(title, artist, length_minutes) VALUES (?, ?, ?)''', 
        (track_name, artist, length))

conn.commit()
conn.close()

conn = sqlite3.connect("tracks.db")
cur = conn.cursor()

cur.execute('Drop TABLE IF EXISTS combined_tracks')

cur.execute('''
    CREATE TABLE combined_tracks AS
    SELECT t.title, t.artist, t.playcount, t.genre, l.length_minutes, t.artist_id, t.genre_id
    FROM tracks t
    JOIN track_lengths l ON t.title = l.title AND t.artist = l.artist
    ''')

conn.commit()
cur.execute("SELECT * FROM combined_tracks")
rows = cur.fetchall()

tracks_data = []
columns = [desc[0] for desc in cur.description]
for row in rows:
    tracks_data.append(dict(zip(columns, row)))

# Write to JSON file
with open("tracks.json", 'w', encoding='utf-8') as f:
    json.dump(tracks_data, f, indent=4, ensure_ascii=False)

conn.commit()
conn.close()




