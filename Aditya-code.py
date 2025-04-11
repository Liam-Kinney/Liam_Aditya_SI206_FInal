import requests
import sqlite3

GENIUS_API_TOKEN = "hKlKBCGgU-bxN-yq3rUi9-4CxuiTeB_VSQ7rSjSO3YvptIZjz21cUh2QomTL4Ulo"

def create_db():
    conn = sqlite3.connect("genius_songs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            genius_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def search_genius_song(query):
    base_url = "https://api.genius.com/search"
    headers = {
        "Authorization": f"Bearer {GENIUS_API_TOKEN}"
    }
    params = {
        "q": query
    }

    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json()["response"]["hits"]
        for hit in results:
            title = hit["result"]["full_title"]
            url = hit["result"]["url"]
            print(f"{title} - {url}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Example usage
search_genius_song("Power Kanye West")
create_db()