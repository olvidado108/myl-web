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
    ("modifica_coste", "Modifica coste", "soporte", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
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


# es415 Codex Arturicus
abilities_es415 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "prevent_all_damage",
            "type": "activated",
            "condition": {"type": "phase", "value": "asignacion_dano", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "prevent_damage", "target": "all", "amount": 0},
            "text": "En asignación de daño, destiérralo para reducir todo el daño a 0.",
        },
        {
            "id": "cannot_be_initial_oro",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_be_initial_oro", "target": "self"},
            "text": "No puede ser usado como oro inicial.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es415 = ["restriccion", "destierra_para_pagar"]
set_card("es415", abilities_es415, tags_es415)

# es416 Mercaderes
abilities_es416 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "move_to_block",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": "self", "from": "reserve", "to": "defense_line"},
                    {"type": "modify_force", "target": "self", "modifier": {"type": "set", "value": 3}, "duration": "end_turn"},
                ],
            },
            "optional": True,
            "text": "En respuesta a un ataque, muévelo a tu defensa; se considera bloqueador de fuerza 3.",
        },
        {
            "id": "destroy_at_end",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "En tu Fase Final, destrúyelo.",
        },
    ],
}
tags_es416 = ["mueve_zona", "modifica_fuerza", "opcional", "destruye_objetivo"]
set_card("es416", abilities_es416, tags_es416)

# es417 Dragones
abilities_es417 = {
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
tags_es417 = ["restriccion", "paga_recursos", "genera_recursos"]
set_card("es417", abilities_es417, tags_es417)

# es418 Draco Conjurador
abilities_es418 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_gold_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Oro en tu mazo y ponerlo en tu mano.",
        }
    ],
}
tags_es418 = ["busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es418", abilities_es418, tags_es418)

# es419 Greenknight
abilities_es419 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_per_gold",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "oros", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 fuerza por cada oro que tengas en juego.",
        }
    ],
}
tags_es419 = ["modifica_fuerza"]
set_card("es419", abilities_es419, tags_es419)

# es42 Yvain del Leon
abilities_es42 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Arma en tu Cementerio y ponerla en tu mano.",
        },
        {
            "id": "cheaper_knight_weapons",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "equip_target_race": "Caballero"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Jugar Armas en tus Caballeros cuesta 1 Oro menos.",
        },
    ],
}
tags_es42 = ["busca_mazo", "mueve_zona", "opcional", "modifica_coste"]
set_card("es42", abilities_es42, tags_es42)

# es420 Pixie
abilities_es420 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_or_shuffle_if_morgana",
            "type": "activated",
            "condition": {"type": "all", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "has_card", "card": "Morgana", "controller": "self", "zone": "play"}]},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "draw_cards", "amount": 3, "target": "controller"},
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "En Vigilia, si controlas a Morgana, elige robar 3 o barajar 2 cartas de tu cementerio en tu mazo.",
        }
    ],
}
tags_es420 = ["roba_cartas", "baraja", "opcional", "restriccion"]
set_card("es420", abilities_es420, tags_es420)

# es421 Levitar Ciudad
abilities_es421 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cast_from_grave_exile",
            "type": "activated",
            "condition": {"type": "zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "any", "zone": "play"}},
                "amount": 1,
                "location": "deck_top",
            },
            "optional": True,
            "text": "Si está en tu cementerio, puedes desterrarlo: elige un Tótem y ponlo en el tope del mazo de su dueño.",
        }
    ],
}
tags_es421 = ["destierra_para_pagar", "baraja", "mueve_zona", "opcional"]
set_card("es421", abilities_es421, tags_es421)

# es422 Sir Owen
abilities_es422 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw3_discard2_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "draw_cards", "amount": 3, "target": "controller"},
                    {"type": "discard", "target": "controller", "amount": 2, "location": "hand"},
                ],
            },
            "text": "Cuando entra, roba 3 cartas y descarta 2.",
        }
    ],
}
tags_es422 = ["roba_cartas", "descarta_mano", "trigger_al_entrar"]
set_card("es422", abilities_es422, tags_es422)

# es423 Llewelyn, voz de plata
abilities_es423 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
                "location": "hand",
            },
            "text": "Cuando entra, elige un aliado oponente y súbelo a su mano.",
        }
    ],
}
tags_es423 = ["mueve_zona", "trigger_al_entrar"]
set_card("es423", abilities_es423, tags_es423)


conn.commit()
conn.close()
print("Updated batch: es415-es423 y es42")

