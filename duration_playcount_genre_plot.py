import sqlite3
import matplotlib.pyplot as plt
import random
import numpy as np

conn = sqlite3.connect("tracks.db")
cur = conn.cursor()


cur.execute('''
    SELECT genre, length_minutes, playcount FROM combined_tracks
    WHERE genre != 'unknown'

''')

data = cur.fetchall()
conn.close()

usable_data = {}
for genre, length, playcount in data:
    if genre not in usable_data:
        usable_data[genre] = {"lengths": [], "playcounts": []}
    usable_data[genre]["lengths"].append(length)
    usable_data[genre]["playcounts"].append(playcount)


filtered_data = {
    genre: values
    for genre, values in usable_data.items() if len(values["lengths"]) > 4
}

colors = {

    genre: (random.random(), random.random(), random.random()) for genre in filtered_data
   
}

plt.figure(figsize=(10,16))

for genre in filtered_data:
    colors[genre] = (random.random(), random.random(), random.random())

for genre, values in filtered_data.items():
    x = values["lengths"]
    y = values["playcounts"]

    plt.scatter(x,y, label = genre, color = colors[genre])

    #if len(x) >= 2:
       # m, b = np.polyfit(x,y,1)
      #  x_line = np.linspace(min(x), max(x), 100)
       # y_line = m*x_line + b
      #  plt.plot(x_line, y_line, color = colors[genre], linewidth = 2)


plt.xlabel("Song Length (minutes)")
plt.ylabel("Playcount")
plt.title("Song Length vs Play Count by Genre")
plt.legend(title = "Genre", fontsize = 9)
plt.grid(True, linestyle = '--', alpha = 0.5)
plt.show()

