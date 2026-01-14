import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("inmunidad", "Inmunidad", "defensivo", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
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


# es234 Totem del Conjurador
abilities_es234 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener uno en tu línea de apoyo.",
        },
        {
            "id": "mill_on_ally_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": {"type": "reference", "reference": "played_card_force"},
                "location": "deck",
            },
            "text": "Cada vez que bajes un Aliado, tu oponente bota tantas cartas como fuerza tenga el Aliado.",
        },
    ],
}
tags_es234 = ["restriccion", "bota_cartas"]
set_card("es234", abilities_es234, tags_es234)

# es235 Armadura Completa
abilities_es235 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "immune_opponent_allies",
            "type": "static",
            "effect": {"type": "immunity", "target": {"type": "reference", "reference": "equipped_to"}, "value": "allies_opponent"},
            "text": "El portador no puede ser afectado por habilidades de Aliados oponentes.",
        }
    ],
}
tags_es235 = ["inmunidad"]
set_card("es235", abilities_es235, tags_es235)

# es236 Hacha de Batalla
abilities_es236 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_equipped",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "El portador gana +2 a la fuerza.",
        },
        {
            "id": "extra_draw_end_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Puedes robar 1 carta extra al final del turno.",
        },
    ],
}
tags_es236 = ["modifica_fuerza", "roba_cartas", "trigger_fin_turno"]
set_card("es236", abilities_es236, tags_es236)

# es237 Botas Elficas
abilities_es237 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_be_declared_attacker",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_be_declared_attacker", "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "El portador puede ser declarado como atacante.",
        }
    ],
}
tags_es237 = ["restriccion"]
set_card("es237", abilities_es237, tags_es237)

# es238 Espada Dentada
abilities_es238 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_if_dragon",
            "type": "static",
            "condition": {"type": "race_is", "race": "Dragón", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "Si el portador es Dragón, gana +2 fuerza.",
        },
        {
            "id": "boost_if_not_dragon",
            "type": "static",
            "condition": {"type": "race_is_not", "race": "Dragón", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "Si no es Dragón, gana +1 fuerza.",
        },
    ],
}
tags_es238 = ["modifica_fuerza"]
set_card("es238", abilities_es238, tags_es238)

# es239 Mandoble
abilities_es239 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "double_force",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "multiply", "value": 2},
            },
            "text": "El portador duplica su fuerza.",
        },
        {
            "id": "must_pay_to_attack",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"attack_cost": {"type": "pay_resources", "amount": 2}}, "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "Para atacar debe pagar 2 de oro.",
        },
    ],
}
tags_es239 = ["modifica_fuerza", "paga_recursos"]
set_card("es239", abilities_es239, tags_es239)

# es24 Duque Godofredo
abilities_es24 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en juego, tus Caballeros ganan +1 a la fuerza.",
        }
    ],
}
tags_es24 = ["modifica_fuerza"]
set_card("es24", abilities_es24, tags_es24)

# es240 Scotish
abilities_es240 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_if_faerie",
            "type": "static",
            "condition": {"type": "race_is", "race": "Faerie", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "Si el portador es Faerie, gana +2 fuerza.",
        },
        {
            "id": "boost_if_not_faerie",
            "type": "static",
            "condition": {"type": "race_is_not", "race": "Faerie", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "Si no es Faerie, gana +1 fuerza.",
        },
    ],
}
tags_es240 = ["modifica_fuerza"]
set_card("es240", abilities_es240, tags_es240)

# es241 Morning Star
abilities_es241 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador gana +2 a la fuerza.",
        },
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "Se considera imbloqueable.",
        },
    ],
}
tags_es241 = ["modifica_fuerza", "imbloqueable"]
set_card("es241", abilities_es241, tags_es241)

# es242 Ivanhoe
abilities_es242 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_blocker_end_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "was_blocked_this_turn", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {"type": "reference", "reference": "blocker"},
            },
            "text": "El Aliado que bloquee a Ivanhoe es destruido al final del turno.",
        }
    ],
}
tags_es242 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es242", abilities_es242, tags_es242)


conn.commit()
conn.close()
print("Updated batch: es234-es242")






