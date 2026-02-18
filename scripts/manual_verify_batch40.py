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
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("muestra_mano", "Muestra mano", "control", None),
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


# es451 Cultistas del Dragon
abilities_es451 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_to_shuffle_opponent_ally",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "look_hand", "target": "opponent"},
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand"}},
                        "amount": 1,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "Destrúyelo: mira la mano oponente y baraja en su mazo un Aliado de su mano.",
        }
    ],
}
tags_es451 = ["destruye_para_pagar", "baraja", "mueve_zona", "muestra_mano", "opcional"]
set_card("es451", abilities_es451, tags_es451)

# es452 Duendes
abilities_es452 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "text": "Cuando entra en juego, descarta 1 carta de tu mano.",
        }
    ],
}
tags_es452 = ["descarta_mano", "trigger_al_entrar"]
set_card("es452", abilities_es452, tags_es452)

# es453 Lailoken
abilities_es453 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_to_search_talisman",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "cost": {"type": "discard", "amount": 1, "target": "controller", "location": "hand"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talismans", "controller": "self", "cost": {"operator": ">=", "value": 3}}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra, puedes descartar 1 para buscar un Talismán de coste 3+ y ponerlo en tu mano.",
        }
    ],
}
tags_es453 = ["descarta_mano", "busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es453", abilities_es453, tags_es453)

# es454 Duphon
abilities_es454 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_grave_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes barajar 1 carta de tu cementerio en tu mazo.",
        }
    ],
}
tags_es454 = ["baraja", "opcional", "una_vez_por_turno"]
set_card("es454", abilities_es454, tags_es454)

# es455 Rhongomiant
abilities_es455 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_bearer",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
        {
            "id": "shuffle_on_combat_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "choice",
                "options": [
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "totems", "controller": "opponent", "zone": "play"}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 1,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "Si su portador daña el mazo oponente, puedes barajar un Tótem oponente o una carta de tu cementerio en tu mazo.",
        },
    ],
}
tags_es455 = ["modifica_fuerza", "baraja", "mueve_zona", "opcional"]
set_card("es455", abilities_es455, tags_es455)

# es456 Caballeros (Oro)
abilities_es456 = {
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
tags_es456 = ["restriccion", "baraja", "mueve_zona", "paga_recursos"]
set_card("es456", abilities_es456, tags_es456)

# es457 Duque Godofredo
abilities_es457 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}}, "modifier": {"type": "add", "value": 1}},
            "text": "Tus Caballeros ganan +1 a la fuerza.",
        }
    ],
}
tags_es457 = ["modifica_fuerza"]
set_card("es457", abilities_es457, tags_es457)

# es458 Guardia Real
abilities_es458 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "destroy_if_not_attacked",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
            "condition": {"type": "did_not_attack_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si en tu turno no ataca, se destruye en la Fase Final.",
        },
    ],
}
tags_es458 = ["apresurado", "destruye_objetivo"]
set_card("es458", abilities_es458, tags_es458)

# es459 Balduino
abilities_es459 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lose_force_if_attacked",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
            "condition": {"type": "attacked_this_turn", "target": "self"},
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "add", "value": -1}, "permanent": True},
            "text": "Si fue declarado atacante, en tu Fase Final pierde 1 fuerza permanente.",
        }
    ],
}
tags_es459 = ["modifica_fuerza"]
set_card("es459", abilities_es459, tags_es459)

# es46 Cathach
abilities_es46 = {
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
            "text": "Los Aliados oponentes pierden 1 a la fuerza mientras sólo controles Dragones.",
        },
    ],
}
tags_es46 = ["baraja", "modifica_fuerza", "opcional", "restriccion"]
set_card("es46", abilities_es46, tags_es46)


conn.commit()
conn.close()
print("Updated batch: es451-es459 y es46")








