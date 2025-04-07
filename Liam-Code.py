import requests

API_KEY = "08d3b443588c0efe5d7803f6c8b91630"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

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

    return {
        "title": name,
        "artist": artist,
        "playcount": playcount,
        "tags": tags
    }

# Try it out!
info = get_track_info("Kendrick Lamar", "Alright")
print(info)
