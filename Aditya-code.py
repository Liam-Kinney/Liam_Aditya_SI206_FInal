import os
import sys
import spotipy
import spotipy.util as util
import webbrowser
import requests
import sqlite3
import json
from json.decoder import JSONDecodeError
from requests.auth import HTTPBasicAuth
from spotipy.oauth2 import SpotifyClientCredentials

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id="517c3756591244359ba33301aae3b33e", client_secret="eb9adf060d27438482d2f403715127cf"))
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
    test1 = search_track_uri("Everything I Am", "Kanye West")
    result = spotify.track(test1, None)
    return(result["duration_ms"]/60000)
