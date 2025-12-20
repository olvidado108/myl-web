import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

def set_card(card_id, abilities, tags):
    cur.execute(
        "UPDATE cartas SET abilities_json=?, abilities_version='1.0', abilities_processed_at=CURRENT_TIMESTAMP, is_verified=1 WHERE id=?",
        (json.dumps(abilities, ensure_ascii=False), card_id),
    )
    cur.execute("DELETE FROM carta_tags WHERE carta_id=?", (card_id,))
    for slug in tags:
        row = cur.execute("SELECT id FROM tags WHERE slug=?", (slug,)).fetchone()
        if row:
            cur.execute(
                "INSERT OR IGNORE INTO carta_tags (carta_id, tag_id, suggested) VALUES (?,?,0)",
                (card_id, row[0]),
            )

# es1 Dragon Dorado
abilities_es1 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando juegues a Dragón Dorado, destiérralo.",
        },
        {
            "id": "counter_non_oro",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {
                "type": "counter",
                "target": {
                    "type": "filter",
                    "filter": {"type": "cards", "controller": "opponent", "not_type": "oros"},
                },
            },
            "text": "Anula una carta que no sea Oro.",
        },
    ],
}
tags_es1 = ["destierra_objetivo", "anula", "trigger_juega_carta"]
set_card("es1", abilities_es1, tags_es1)

# es10 Corona de Arturo Bob
abilities_es10 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_indestructibles",
            "type": "static",
            "condition": {"controller_allies_at_least": 2},
            "effect": {
                "type": "restriction",
                "restriction": "indestructible",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
            },
            "text": "Mientras controles 2 o más Aliados, los Oros son indestructibles.",
        },
        {
            "id": "exile_from_graveyard_to_draw",
            "type": "activated",
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Si Corona de Arturo está en tu Cementerio, puedes desterrarla para robar 1 carta de tu Mazo Castillo.",
        },
    ],
}
tags_es10 = ["indestructible", "exilia_para_pagar", "roba_cartas", "opcional"]
set_card("es10", abilities_es10, tags_es10)

# es100 Totem de la Ultima Cancion
abilities_es100 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_totem",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu fase de vigilia y una vez por turno, puedes pagar 2 Oro para buscar un Tótem en tu mazo castillo y ponerlo en tu mano.",
        }
    ],
}
tags_es100 = ["busca_mazo", "opcional", "una_vez_por_turno"]
set_card("es100", abilities_es100, tags_es100)

# es101 Excalibur
abilities_es101 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_arthur",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "name": "Rey Arturo Pendragón"}},
            },
            "text": "Sólo puede ser portada por Rey Arturo Pendragón.",
        },
        {
            "id": "base_bonus",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_ally"},
                "modifier": {"type": "add", "value": 3},
            },
            "text": "Gana +3 a la fuerza.",
        },
        {
            "id": "discard_to_boost",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "discard", "amount": 1},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_ally"},
                "modifier": {
                    "type": "add",
                    "value": {"type": "reference", "reference": "discarded_card.cost"},
                },
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu fase de vigilia y una vez por turno, puedes descartar 1 para que gane un bono de fuerza igual al coste en oro de la carta descartada.",
        },
    ],
}
tags_es101 = ["restriccion", "modifica_fuerza", "descarta_para_pagar", "opcional", "una_vez_por_turno"]
set_card("es101", abilities_es101, tags_es101)

# es102 Gitanos
abilities_es102 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_any_card",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}},
                "amount": 1,
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Busca una carta en tu Mazo Castillo y pónla en tu mano.",
        }
    ],
}
tags_es102 = ["busca_mazo", "opcional"]
set_card("es102", abilities_es102, tags_es102)

conn.commit()
conn.close()
print("Updated batch: es1, es10, es100, es101, es102")


