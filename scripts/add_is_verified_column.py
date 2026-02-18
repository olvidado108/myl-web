import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")

conn = sqlite3.connect(db)
cur = conn.cursor()

cols = cur.execute("PRAGMA table_info(cartas)").fetchall()
names = {c[1] for c in cols}
if "is_verified" not in names:
    cur.execute("ALTER TABLE cartas ADD COLUMN is_verified INTEGER DEFAULT 0")
    conn.commit()
    print("Column is_verified added")
else:
    print("Column is_verified already exists")

conn.close()









