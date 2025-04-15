import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("tracks.db")
cur = conn.cursor()

cur.execute('''
    SELECT genre, AVG(playcount) FROM tracks WHERE genre != 'unknown'
    GROUP BY genre  HAVING COUNT(*) >= 5 ORDER BY AVG(playcount) DESC 
''')

results = cur.fetchall()
conn.close()

genres = [row[0].title() for row in results]
avg_playcounts = [row[1] for row in results]

plt.figure(figsize=(10, 6))
plt.bar(genres, avg_playcounts)
plt.xlabel("Genre")
plt.ylabel("Average Playcount")
plt.title("Average Playcounts by Genre")
plt.xticks(rotation=90, ha = 'right')
plt.show()