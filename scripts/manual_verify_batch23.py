import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("baraja", "Baraja cartas", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
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


# es298 Brag
abilities_es298 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_hand_card_draw",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": {"type": "filter", "filter": {"controller": "self", "zone": "hand"}}, "amount": 1, "location": "deck"},
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar 1 carta de tu mano en tu mazo y luego robar 1.",
        }
    ],
}
tags_es298 = ["baraja", "roba_cartas", "opcional", "trigger_al_entrar", "mueve_zona"]
set_card("es298", abilities_es298, tags_es298)

# es299 Asesinos En la Corte
abilities_es299 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_ally_force_le_2",
            "type": "activated",
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "<=", "value": 2}}},
            },
            "text": "Destruye un Aliado oponente de fuerza 2 o menor.",
        }
    ],
}
tags_es299 = ["destruye_objetivo"]
set_card("es299", abilities_es299, tags_es299)

# es3 Capa de Invisibilidad Bob
abilities_es3 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_on_non_gold_enter",
            "type": "response",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"controller": "opponent", "type": {"operator": "!=", "value": "oros"}}}},
            "effect": {
                "type": "move_zone",
                "target": "triggered_card",
                "location": "deck",
            },
            "text": "En respuesta a que entre una carta oponente que no sea Oro, barájala en el mazo de su dueño.",
        }
    ],
}
tags_es3 = ["baraja", "mueve_zona"]
set_card("es3", abilities_es3, tags_es3)

# es30 Draig Ifanc
abilities_es30 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cuando entra, puedes robar 1 carta.",
        },
        {
            "id": "search_gold_if_destroyed_with_only_dragons",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "condition": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}}, "operator": "==", "targetValue": 0, "invert": True},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_play",
                "amount": 1,
            },
            "text": "Si es destruido o barajado y solo controlabas Aliados Dragón, busca un Oro y ponlo en juego.",
        },
    ],
}
tags_es30 = ["roba_cartas", "busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es30", abilities_es30, tags_es30)

# es300 Camino A Avalon
abilities_es300 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_shuffle_grave_card",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1, "store": "sacrificed_force"},
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "text": "Destruye 1 de tus Aliados para barajar 1 carta de tu cementerio en tu mazo.",
        }
    ],
}
tags_es300 = ["destruye_objetivo", "baraja", "mueve_zona"]
set_card("es300", abilities_es300, tags_es300)

# es301 Cantrip
abilities_es301 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_one",
            "type": "activated",
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Roba 1 carta.",
        }
    ],
}
tags_es301 = ["roba_cartas"]
set_card("es301", abilities_es301, tags_es301)

# es302 Nombrado Escudero
abilities_es302 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "prevent_block_knights",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "restriction",
                "restriction": {"cannot_block_race": "Caballero"},
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "duration": "end_turn",
            },
            "text": "En Vigilia, elige un Aliado oponente: no puede bloquear Caballeros este turno.",
        }
    ],
}
tags_es302 = ["restriccion"]
set_card("es302", abilities_es302, tags_es302)

# es303 Grig
abilities_es303 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "En guerra de Talismanes, un aliado tuyo gana +2 fuerza hasta fin de turno.",
        }
    ],
}
tags_es303 = ["modifica_fuerza"]
set_card("es303", abilities_es303, tags_es303)

# es304 Talisman Celta
abilities_es304 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "opponent_sac_one",
            "type": "activated",
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "play"}},
                "amount": 1,
                "chooser": "opponent",
            },
            "text": "Tu oponente debe destruir un Aliado a su elección.",
        }
    ],
}
tags_es304 = ["destruye_objetivo"]
set_card("es304", abilities_es304, tags_es304)

# es305 Juglares
abilities_es305 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_one",
            "type": "activated",
            "effect": {"type": "generate_resources", "amount": 1, "duration": "end_turn"},
            "text": "Genera 1 oro hasta el final del turno.",
        }
    ],
}
tags_es305 = ["genera_recursos"]
set_card("es305", abilities_es305, tags_es305)


conn.commit()
conn.close()
print("Updated batch: es298-es305, es3, es30")






