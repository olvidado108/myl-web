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
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
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


# es460 Sir Persival
abilities_es460 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1, "location": "deck"},
            "text": "Cuando entra en juego, baraja un aliado oponente.",
        }
    ],
}
tags_es460 = ["baraja", "mueve_zona", "trigger_al_entrar"]
set_card("es460", abilities_es460, tags_es460)

# es461 Sir Robin de Locksley
abilities_es461 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_opponent_ally_until_end",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "gain_control",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "end_turn",
            },
            "text": "Cuando entra, gana el control de un Aliado oponente hasta la Fase Final.",
        }
    ],
}
tags_es461 = ["mueve_zona", "trigger_al_entrar"]
set_card("es461", abilities_es461, tags_es461)

# es462 Sir Galahad
abilities_es462 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "discard_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand", "random": True},
            "text": "Si hace daño al mazo oponente, descarta 1 carta al azar de su mano.",
        },
    ],
}
tags_es462 = ["apresurado", "descarta_mano", "trigger_al_entrar"]
set_card("es462", abilities_es462, tags_es462)

# es463 Curandera
abilities_es463 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reduce_cost_all",
            "type": "static",
            "effect": {"type": "modify_cost", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}}, "modifier": {"type": "add", "value": -1}},
            "text": "Tus cartas reducen en 1 su coste.",
        }
    ],
}
tags_es463 = ["modifica_coste"]
set_card("es463", abilities_es463, tags_es463)

# es464 Yvain del Leon
abilities_es464 = {
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
            "text": "Cuando entra, puedes buscar un Arma en tu Cementerio y ponerla en tu mano.",
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
tags_es464 = ["busca_mazo", "mueve_zona", "opcional", "modifica_coste"]
set_card("es464", abilities_es464, tags_es464)

# es465 Caballeros (Oro)
abilities_es465 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Caballeros en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Sólo puede ser jugado desde tu mano.",
        },
        {
            "id": "shuffle_knight_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "En Vigilia, puedes pagarlo para barajar un Caballero de tu cementerio en tu mazo.",
        },
    ],
}
tags_es465 = ["restriccion", "baraja", "mueve_zona", "paga_recursos"]
set_card("es465", abilities_es465, tags_es465)

# es466 Hugues de Payens
abilities_es466 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar el turno que entra en juego.",
        },
        {
            "id": "search_weapon_or_ally_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "cost": {"operator": "<=", "value": 2}, "any": [{"type": "armas"}, {"type": "allies"}]}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Si daña el mazo oponente, puedes buscar un Arma o Aliado de coste 2 o menos y ponerlo en tu mano.",
        },
    ],
}
tags_es466 = ["apresurado", "busca_mazo", "mueve_zona", "opcional"]
set_card("es466", abilities_es466, tags_es466)

# es467 Melisende
abilities_es467 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_be_blocked_by_3_plus",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"unblockable_by_force_at_least": 3}, "target": "self"},
            "text": "No puede ser bloqueado por Aliados de fuerza 3 o más.",
        },
        {
            "id": "tutor_knight_top",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "action": "put_on_top",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Caballero y ponerlo en el tope de tu mazo.",
        },
    ],
}
tags_es467 = ["restriccion", "busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es467", abilities_es467, tags_es467)

# es468 Boveda Templaria
abilities_es468 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_reserve_to_get_knight",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "requires": {
                "type": "and",
                "conditions": [
                    {"type": "zone", "value": "reserve", "target": "self"},
                    {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "play"}}, "operator": ">=", "targetValue": 2},
                ],
            },
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": "<=", "value": 2}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Si está en tu Reserva y controlas 2+ Caballeros, destiérrala: busca un Aliado de coste 2 o menos en tu cementerio y ponlo en tu mano.",
        }
    ],
}
tags_es468 = ["restriccion", "destierra_para_pagar", "busca_mazo", "mueve_zona", "opcional"]
set_card("es468", abilities_es468, tags_es468)

# es469 Dragón de Luz
abilities_es469 = {
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
            "text": "En Vigilia, una vez por turno, baraja 3 cartas de tu cementerio en tu mazo; si lo haces, no puede ser declarado atacante este turno.",
        }
    ],
}
tags_es469 = ["baraja", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es469", abilities_es469, tags_es469)


conn.commit()
conn.close()
print("Updated batch: es460-es469")








