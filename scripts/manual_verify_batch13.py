import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
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


# es207 Banshee
abilities_es207 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lock_attacks",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "cannot_attack",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "duration": "while_source_in_play",
            },
            "optional": True,
            "text": "Cuando entra, puedes elegir un Aliado oponente para que no pueda atacar mientras Banshee esté en juego.",
        }
    ],
}
tags_es207 = ["restriccion", "trigger_al_entrar", "opcional"]
set_card("es207", abilities_es207, tags_es207)

# es208 Pooka
abilities_es208 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_faeries",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "graveyard"}},
                        "amount": 3,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar hasta 3 Faeries de tu cementerio en tu mazo castillo.",
        }
    ],
}
tags_es208 = ["mueve_zona", "baraja", "opcional", "trigger_al_entrar"]
set_card("es208", abilities_es208, tags_es208)

# es209 Elfo Oscuro
abilities_es209 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_one_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Cuando entra en juego, roba 1 carta.",
        }
    ],
}
tags_es209 = ["roba_cartas", "trigger_al_entrar"]
set_card("es209", abilities_es209, tags_es209)

# es21 Reina Guinivere
abilities_es21 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_knight",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Caballero y ponerlo en tu mano.",
        },
        {
            "id": "generate_for_weapons_or_knights",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "choice",
                "choices": [
                    {"type": "generate_resources", "amount": 2, "restriction": "weapon"},
                    {"type": "generate_resources", "amount": 1, "restriction": "knight"},
                ],
            },
            "text": "En tu fase de vigilia, genera 2 para armas o 1 para Caballeros.",
        },
    ],
}
tags_es21 = ["busca_mazo", "opcional", "trigger_al_entrar", "genera_recursos"]
set_card("es21", abilities_es21, tags_es21)

# es210 Nixx
abilities_es210 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "gain_force_with_weapon",
            "type": "static",
            "condition": {"type": "has_equipment", "equipment_type": "weapon", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Cuando porta un arma, gana +2 a la fuerza.",
        }
    ],
}
tags_es210 = ["modifica_fuerza"]
set_card("es210", abilities_es210, tags_es210)

# es211 Lobos de Avalon
abilities_es211 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_copy",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"name": "Lobos de Avalon", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar otro Lobos de Avalon y ponerlo en tu mano.",
        }
    ],
}
tags_es211 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es211", abilities_es211, tags_es211)

# es212 Kelpie
abilities_es212 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_dragon_and_unblockable",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "modify_force",
                        "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                        "modifier": {"type": "add", "value": 2},
                        "permanent": True,
                    },
                    {
                        "type": "restriction",
                        "restriction": "unblockable",
                        "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "Cuando entra, un Dragón tuyo gana +2 fuerza permanente y es imbloqueable este turno.",
        }
    ],
}
tags_es212 = ["modifica_fuerza", "imbloqueable", "trigger_al_entrar"]
set_card("es212", abilities_es212, tags_es212)

# es213 Bane
abilities_es213 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_gold_with_ability",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent", "zone": "play", "has_ability": True}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "opponent", "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes hacer que un oro con habilidad del oponente se baraje en su mazo castillo.",
        }
    ],
}
tags_es213 = ["mueve_zona", "baraja", "opcional", "trigger_al_entrar"]
set_card("es213", abilities_es213, tags_es213)

# es214 Ettin
abilities_es214 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "fetch_ally_on_attack_declare",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "force": {"operator": "==", "value": 2}}},
                "action": "put_in_play",
                "destination": "defense_line",
            },
            "optional": True,
            "text": "En respuesta a ser declarado atacante, puedes buscar un Aliado de fuerza 2 y ponerlo en la línea de defensa sin pagar su coste.",
        }
    ],
}
tags_es214 = ["busca_mazo", "trigger_al_atacar", "opcional", "pone_en_juego"]
set_card("es214", abilities_es214, tags_es214)

# es215 San Jorge y el Dragon
abilities_es215 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_per_opponent_dragon",
            "type": "activated",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "modifier": {
                    "type": "add",
                    "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "opponent", "zone": "play"}}},
                },
                "duration": "end_turn",
            },
            "text": "Por cada Dragón de tu oponente, un Aliado gana +1 fuerza hasta fin de turno.",
        }
    ],
}
tags_es215 = ["modifica_fuerza"]
set_card("es215", abilities_es215, tags_es215)


conn.commit()
conn.close()
print("Updated batch: es207-es215")






