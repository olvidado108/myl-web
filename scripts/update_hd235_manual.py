import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
card_id = "hd235"

abilities = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_play_from_grave",
            "type": "static",
            "condition": {"phase": "main"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "allies",
                        "controller": "self",
                        "cost": {"operator": "<=", "value": 4},
                    },
                },
                "action": "put_in_play",
                "pay_cost": False,
                "store_as": "last_returned_ally",
            },
            "text": "Solo en Fase de Vigilia: busca un Aliado de coste 4 o menos en tu Cementerio y juégalo sin pagar su coste.",
        },
        {
            "id": "end_phase_exile_and_strip",
            "type": "triggered",
            "trigger": {"type": "phase_end", "target": {"type": "reference", "reference": "phase.final"}},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "lose_ability", "target": {"type": "reference", "reference": "last_returned_ally"}},
                    {"type": "exile", "target": {"type": "reference", "reference": "last_returned_ally"}},
                ],
            },
            "text": "En la Fase Final, ese Aliado pierde su habilidad y es desterrado.",
        },
    ],
}

slugs = [
    "busca_mazo",
    "pone_en_juego",
    "destierra_objetivo",
    "pierde_habilidad",
    "trigger_fin_turno",
    "sin_pagar_coste",
    "mueve_zona",
]

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute(
    "INSERT OR IGNORE INTO tags (slug, nombre, categoria, descripcion) VALUES (?,?,?,?)",
    ("sin_pagar_coste", "Sin pagar coste", "soporte", "Juega sin pagar coste"),
)

cur.execute(
    "UPDATE cartas SET abilities_json=?, abilities_version='1.0', abilities_processed_at=CURRENT_TIMESTAMP WHERE id=?",
    (json.dumps(abilities, ensure_ascii=False), card_id),
)

cur.execute("DELETE FROM carta_tags WHERE carta_id=?", (card_id,))

for slug in slugs:
    tag = cur.execute("SELECT id FROM tags WHERE slug=?", (slug,)).fetchone()
    if tag:
        cur.execute(
            "INSERT OR IGNORE INTO carta_tags (carta_id, tag_id, suggested) VALUES (?,?,0)",
            (card_id, tag[0]),
        )

conn.commit()
conn.close()
print("updated", card_id)









