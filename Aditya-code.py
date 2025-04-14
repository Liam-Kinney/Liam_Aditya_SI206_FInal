import requests
import sqlite3
import json
import random
from requests.auth import HTTPBasicAuth

CLIENT_ID = "517c3756591244359ba33301aae3b33e"
CLIENT_SECRET = "5ea0dfd004c546ddbf14bb09c0dc6acb"
auth_url = "https://api.spotify.com/v1"
params = { 'grant_type' : 'client_credentials', 'client_id' : CLIENT_ID, 'client_secret': CLIENT_SECRET,}
response = requests.post(auth_url, data=params)
access_token = response.json().get('access_token')

def get_tracks_from_page(page):
    params = {
        "method": "chart.gettoptracks",
        "api_key": API_KEY,
        "format": "json",
        "limit": 100,
        "page": page
    }
    response = requests.get(BASE_URL, params = params)
    data = response.json()

    track_list = []
    for track in data["tracks"]["track"]:
        artist_name = track["artist"]["name"]
        track_name = track["name"]
        track_list.append((artist_name, track_name))

    return track_list

def get_top_1050_tracks():
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

def get_track_info(artist, track):
    params = {
        "method": "track.getInfo",
        "api_key": API_KEY,
        "artist": artist,
        "track": track,
        "format": "json"
    }
    response = requests.get(BASE_URL, params=params)
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

track_list = get_top_1050_tracks()

random.shuffle(track_list)

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