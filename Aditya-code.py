import requests
import sqlite3
import json
import random
from requests.auth import HTTPBasicAuth

CLIENT_ID = "517c3756591244359ba33301aae3b33e"
CLIENT_SECRET = "5ea0dfd004c546ddbf14bb09c0dc6acb"
auth_url = "https://accounts.spotify.com/api/token"
credentials = { 'grant_type' : 'client_credentials', 'client_id' : CLIENT_ID, 'client_secret': CLIENT_SECRET,}
auth_response = requests.post(auth_url, data=credentials)
access_token = auth_response.json().get('access_token')

def search_track(track_name):
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": track_name,
        "type": "track",
        "limit": 1 
    }
    response = requests.get(url, headers=credentials, params=params)
    tracks = response.json().get("tracks", {}).get("items", [])
    return tracks[0]

def get_track_details(track_name):
    track_data = search_track(track_name)
    track_info = {
        "title": track_data["name"],
        "artists": [artist["name"] for artist in track_data["artists"]],
        "duration_ms": track_data["duration_ms"],
        "popularity": track_data["popularity"],
        "track_id": track_data["id"]
    }
    if track_data["artists"]:
        artist_id = track_data["artists"][0]["id"]
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = requests.get(artist_url, headers=credentials)
        artist_data = artist_response.json()
        track_info["genres"] = artist_data.get("genres", [])
    return track_info

def get_artist_genres(artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer{access_token}"})
    artist_data = response.json()
    return artist_data.get("genres", [])
