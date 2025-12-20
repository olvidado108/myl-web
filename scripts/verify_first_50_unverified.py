import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")

conn = sqlite3.connect(db)
cur = conn.cursor()

# Obtener primeras 50 sin verificar
ids = [
    row[0]
    for row in cur.execute(
        "SELECT id FROM cartas WHERE COALESCE(is_verified,0)=0 ORDER BY id LIMIT 50"
    ).fetchall()
]

if not ids:
    print("No hay cartas pendientes de verificación.")
    conn.close()
    raise SystemExit

# Confirmar tags (suggested -> 0) y marcar is_verified=1
cur.executemany(
    "UPDATE carta_tags SET suggested=0 WHERE carta_id=?",
    [(cid,) for cid in ids],
)
cur.executemany(
    "UPDATE cartas SET is_verified=1 WHERE id=?",
    [(cid,) for cid in ids],
)

conn.commit()
print(f"Verificadas {len(ids)} cartas:", ", ".join(ids))
conn.close()


