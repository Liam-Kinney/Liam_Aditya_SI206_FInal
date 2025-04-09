import requests
import sqlite3
import json
import random
import matplotlib.pyplot as plt
import re

API_KEY = "08d3b443588c0efe5d7803f6c8b91630"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

top_genres = ["pop", "rock", "hip-hop", "jazz", "classical", "country", "electronic", "alternative", "blues", "metal", "anime", "indie", "folk", "reggae", "r&b", "rap", "house", "soul", "funk", "k-pop", "emo", "grunge", "techno"]
genre_re_pattern = re.compile(r'\b(?:' + '|'.join(top_genres) + r')\b', re.IGNORECASE)


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

num_inserted = 0

for artist, track in track_list:
    if num_inserted >= 25:
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

cur.execute('''
    SELECT genre, AVG(playcount) FROM tracks WHERE genre != 'unknown'
    GROUP BY genre HAVING COUNT(*) >= 5 ORDER BY AVG(playcount) DESC
''')

results = cur.fetchall()
conn.close()

genres = [row[0].title() for row in results]
avg_playcounts = [row[1] for row in results]

plt.figure(figsize=(10, 6))
plt.scatter(avg_playcounts, genres, s = 100)
plt.ylabel("Genre")
plt.xlabel("Average Playcount (in millions)")
plt.title("Average Playcounts by Genre")
plt.grid(axis = 'x', linestyle = '--', alpha = 0.7)
plt.show()
