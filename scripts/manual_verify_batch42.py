import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
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


# es47 Nimue
abilities_es47 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "copy_faerie_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"type": "copy_from_graveyard", "race": "Faerie"}, "duration": "end_turn"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puede copiar un Faerie de tu cementerio hasta la Fase Final.",
        }
    ],
}
tags_es47 = ["opcional", "una_vez_por_turno"]
set_card("es47", abilities_es47, tags_es47)

# es470 Dragón Nube
abilities_es470 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choose_draw_or_mill",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes elegir: robar 2 cartas o que el oponente bote 2.",
        }
    ],
}
tags_es470 = ["roba_cartas", "bota_cartas", "opcional", "trigger_al_entrar"]
set_card("es470", abilities_es470, tags_es470)

# es471 Aghast, el Dragón
abilities_es471 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un arma en tu mazo y ponerla en tu mano.",
        }
    ],
}
tags_es471 = ["busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"] if False else ["busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]  # keep tags consistent
set_card("es471", abilities_es471, tags_es471)

# es472 Dragón Nival
abilities_es472 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_force_two_or_less",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "force": {"operator": "<=", "value": 2}}}},
            "text": "Cuando entra, destruye todos los Aliados de fuerza 2 o menos.",
        }
    ],
}
tags_es472 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es472", abilities_es472, tags_es472)

# es473 Cria de Wyrm
abilities_es473 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_cost_three_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "cost": {"operator": "==", "value": 3}}}},
            "optional": True,
            "text": "Cuando entra, puedes desterrar un Aliado oponente de coste 3.",
        }
    ],
}
tags_es473 = ["destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("es473", abilities_es473, tags_es473)

# es474 Draig Ifanc
abilities_es474 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cuando entra, puedes robar una carta.",
        },
        {
            "id": "search_oro_on_leave_if_dragons",
            "type": "response",
            "trigger": {"type": "leaves_play", "target": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "race": {"operator": "!=", "value": "Dragón"}}},
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {"type": "search", "location": "deck", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}, "action": "put_in_play"},
            "optional": True,
            "text": "Si es destruido o barajado y solo controlabas Dragones, busca un Oro y ponlo en juego.",
        },
    ],
}
tags_es474 = ["roba_cartas", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es474", abilities_es474, tags_es474)

# es475 Cathach
abilities_es475 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}}, "amount": 2, "location": "deck"},
            "optional": True,
            "text": "Cuando entra, puedes barajar 2 cartas de tu cementerio en tu mazo.",
        },
        {
            "id": "debuff_opponents_if_only_dragons",
            "type": "static",
            "condition": {"type": "all", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "condition": {"type": "race", "value": "Dragón"}},
            "effect": {"type": "modify_force", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "modifier": {"type": "add", "value": -1}},
            "text": "Los Aliados oponentes pierden 1 a la fuerza mientras solo controles Dragones.",
        },
    ],
}
tags_es475 = ["baraja", "modifica_fuerza", "opcional", "restriccion"]
set_card("es475", abilities_es475, tags_es475)

# es476 Dragones
abilities_es476 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Dragones en juego.",
        },
        {
            "id": "only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Sólo puede ser jugado desde tu mano.",
        },
        {
            "id": "generate_for_big_dragons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "cost": {"operator": ">=", "value": 4}}}},
            "optional": True,
            "text": "En Vigilia, puedes pagarlo para generar 2 oros para Aliados Dragón de coste 4 o más.",
        },
    ],
}
tags_es476 = ["restriccion", "paga_recursos", "genera_recursos"]
set_card("es476", abilities_es476, tags_es476)

# es477 Zaratán
abilities_es477 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_to_exile_if_only_dragons",
            "type": "activated",
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "phase", "value": "vigilia", "controller": "self"},
                    {
                        "type": "count",
                        "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "race": {"operator": "!=", "value": "Dragón"}}},
                        "operator": "==",
                        "targetValue": 0,
                    },
                ],
            },
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}}, "amount": 1},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, si solo controlas Dragones, paga 1 oro: destierra 1 carta del cementerio oponente (1 vez por turno).",
        }
    ],
}
tags_es477 = ["paga_recursos", "destierra_objetivo", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es477", abilities_es477, tags_es477)

# es478 Dragón de Magma
abilities_es478 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}},
            "text": "Cuando entra en juego, destruye un Aliado oponente.",
        }
    ],
}
tags_es478 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es478", abilities_es478, tags_es478)


conn.commit()
conn.close()
print("Updated batch: es47, es470-es478")








