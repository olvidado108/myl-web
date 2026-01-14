import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
]
for slug, nombre, categoria, descripcion in needed_tags:
    cur.execute(
        "INSERT OR IGNORE INTO tags (slug, nombre, categoria, descripcion) VALUES (?,?,?,?)",
        (slug, nombre, categoria, descripcion),
    )


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


# es306 Hechizo de Niebla
abilities_es306 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_block_this_turn",
            "type": "activated",
            "effect": {
                "type": "restriction",
                "restriction": "cannot_block",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "duration": "end_turn",
            },
            "text": "Un Aliado oponente no puede bloquear este turno.",
        }
    ],
}
tags_es306 = ["restriccion"]
set_card("es306", abilities_es306, tags_es306)

# es307 Yermo
abilities_es307 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_weapon_bearer",
            "type": "activated",
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "has_equipment": True}},
                "amount": 1,
                "location": "hand",
            },
            "text": "Sube a la mano un Aliado oponente que porte un arma.",
        }
    ],
}
tags_es307 = ["mueve_zona"]
set_card("es307", abilities_es307, tags_es307)

# es308 Funeral Para Un Amigo
abilities_es308 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_ally_from_grave",
            "type": "activated",
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Baraja del cementerio a tu mazo castillo un Aliado.",
        }
    ],
}
tags_es308 = ["baraja", "mueve_zona"]
set_card("es308", abilities_es308, tags_es308)

# es309 Dioses En la Sombra
abilities_es309 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "debuff_two",
            "type": "activated",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "add", "value": -2},
                "duration": "end_turn",
            },
            "text": "Un Aliado oponente gana -2 a la fuerza hasta el final del turno.",
        }
    ],
}
tags_es309 = ["modifica_fuerza"]
set_card("es309", abilities_es309, tags_es309)

# es31 Cathach
abilities_es31 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar 2 cartas de tu cementerio en tu mazo.",
        },
        {
            "id": "dragons_only_debuff",
            "type": "static",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "race": {"operator": "!=", "value": "Dragón"}}},
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Mientras solo controles Dragones, los Aliados oponentes pierden 1 a la fuerza.",
        },
    ],
}
tags_es31 = ["baraja", "mueve_zona", "opcional", "trigger_al_entrar", "modifica_fuerza", "restriccion"]
set_card("es31", abilities_es31, tags_es31)

# es310 el Juez
abilities_es310 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "remove_opponent_ability",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "lose_ability", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "duration": "end_turn"},
            "text": "En tu fase de vigilia, elige un Aliado oponente para que pierda su habilidad hasta el final del turno.",
        }
    ],
}
tags_es310 = ["pierde_habilidad"]
set_card("es310", abilities_es310, tags_es310)

# es311 Ataque Dragon
abilities_es311 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_dragon_two",
            "type": "activated",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "any", "zone": "play"}},
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "Un Dragón gana +2 a la fuerza hasta el final del turno.",
        }
    ],
}
tags_es311 = ["modifica_fuerza"]
set_card("es311", abilities_es311, tags_es311)

# es312 Relatos En la Mesa Redonda
abilities_es312 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_hand_and_search_if_no_talisman",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "choice",
                "choices": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "talisman", "controller": "self"}},
                        "action": "put_in_hand",
                        "amount": 1,
                    },
                    {"type": "none"},
                ],
            },
            "text": "Muestra tu mano; si no tienes Talismán, busca uno en tu mazo y ponlo en tu mano.",
        }
    ],
}
tags_es312 = ["busca_mazo"]
set_card("es312", abilities_es312, tags_es312)

# es313 Leprechaun
abilities_es313 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "debuff_opponents_on_attack",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": "opponent"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "text": "En respuesta a un ataque, los Aliados oponentes ganan -1 a la fuerza hasta fin de turno.",
        }
    ],
}
tags_es313 = ["modifica_fuerza", "trigger_al_atacar"]
set_card("es313", abilities_es313, tags_es313)

# es314 Bugbear
abilities_es314 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_random_then_mill_cost",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "discard",
                        "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "hand"}},
                        "amount": 1,
                        "location": "hand",
                        "random": True,
                        "store": "discarded_cost",
                    },
                    {
                        "type": "discard",
                        "target": "opponent",
                        "amount": {"type": "reference", "reference": "discarded_cost"},
                        "location": "deck",
                    },
                ],
            },
            "text": "En Vigilia: descarta al azar 1 carta de la mano oponente; luego bota de su mazo tantas cartas como su coste.",
        }
    ],
}
tags_es314 = ["descarta_mano", "bota_cartas"]
set_card("es314", abilities_es314, tags_es314)


conn.commit()
conn.close()
print("Updated batch: es306-es314 y es31")






