import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("restriccion", "Restricción/regla", "control", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
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


# es398 Sir Robin de Lockesley
abilities_es398 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_defender_until_end",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense"}},
                "location": "defense",
                "controller": "self",
                "duration": "end_turn",
            },
            "text": "Al entrar, un aliado de la defensa oponente pasa a tu defensa hasta el final del turno.",
        }
    ],
}
tags_es398 = ["mueve_zona", "trigger_al_entrar"]
set_card("es398", abilities_es398, tags_es398)

# es399 Dragon Nube
abilities_es399 = {
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
tags_es399 = ["roba_cartas", "bota_cartas", "opcional", "trigger_al_entrar"]
set_card("es399", abilities_es399, tags_es399)

# es4 Bola de Fuego Bob
abilities_es4 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_non_gold",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "not": {"type": "oros"}}}},
            "text": "Destruye una carta en juego, que no sea un oro.",
        }
    ],
}
tags_es4 = ["destruye_objetivo"]
set_card("es4", abilities_es4, tags_es4)

# es40 Cruz Templaria
abilities_es40 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_tutor_play",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "action": "put_in_play",
                    },
                    {
                        "type": "delayed_trigger",
                        "trigger": {"type": "phase_start", "phase": "final", "target": "controller"},
                        "effect": {"type": "exile", "target": {"type": "reference", "reference": "last_put_in_play"}},
                    },
                ],
            },
            "optional": True,
            "text": "En tu Vigilia, destiérrala: busca un Aliado y juégalo pagando su coste. En la Fase Final, ese Aliado debe ser desterrado.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es40 = ["destierra_para_pagar", "busca_mazo", "pone_en_juego", "opcional", "restriccion", "destierra_objetivo"]
set_card("es40", abilities_es40, tags_es40)

# es400 Dragon de Magma
abilities_es400 = {
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
tags_es400 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es400", abilities_es400, tags_es400)

# es401 Dragon de Luz
abilities_es401 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_three_cannot_attack",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}}, "amount": 3, "location": "deck"},
                    {"type": "restriction", "restriction": "cannot_attack", "target": "self", "duration": "end_turn"},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes barajar 3 de tu Cementerio en tu mazo. Si lo haces, no puede ser declarado atacante este turno.",
        }
    ],
}
tags_es401 = ["baraja", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es401", abilities_es401, tags_es401)

# es402 Draig Ifanc
abilities_es402 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cuando entra en juego, puedes robar una carta.",
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
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_play",
            },
            "optional": True,
            "text": "Si es destruido o barajado y solo controlabas Dragones, busca un Oro y ponlo en juego.",
        },
    ],
}
tags_es402 = ["roba_cartas", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es402", abilities_es402, tags_es402)

# es403 Cathach
abilities_es403 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}}, "amount": 2, "location": "deck"},
            "optional": True,
            "text": "Cuando entra, puedes barajar 2 cartas de tu Cementerio en tu mazo.",
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
tags_es403 = ["baraja", "modifica_fuerza", "opcional", "restriccion"]
set_card("es403", abilities_es403, tags_es403)

# es404 Santo Grial
abilities_es404 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "save_destroyed_card",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"controller": "self", "zone": "play"}}},
            "effect": {"type": "move_zone", "target": "triggered_card", "location": "hand"},
            "text": "En respuesta a que una de tus cartas sea destruida, súbela a la mano.",
        }
    ],
}
tags_es404 = ["mueve_zona"]
set_card("es404", abilities_es404, tags_es404)

# es405 Toque de Persival
abilities_es405 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_recent_attacker_or_blocker",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "attacked_or_blocked_this_turn": True}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Baraja un Aliado oponente que haya sido declarado atacante o bloqueador este turno.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es405 = ["baraja", "restriccion"]
set_card("es405", abilities_es405, tags_es405)


conn.commit()
conn.close()
print("Updated batch: es398-es405 y es4/es40")

