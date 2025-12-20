import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
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


# es550 Broceliaden
abilities_es550 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "look_two_keep_one_exile_one",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal", "target": {"type": "reference", "reference": "controller.deck"}, "amount": 2},
                    {"type": "move_zone", "target": {"type": "reference", "reference": "controller.deck_top"}, "amount": 1, "location": "hand"},
                    {"type": "move_zone", "target": {"type": "reference", "reference": "controller.deck_top"}, "amount": 1, "location": "exile"},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, mira las 2 primeras cartas de tu mazo, pon una en tu mano y la otra en tu destierro.",
        }
    ],
}
tags_es550 = ["roba_cartas", "opcional", "una_vez_por_turno"]
set_card("es550", abilities_es550, tags_es550)

# es551 Mago Merlin
abilities_es551 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Mago Merlín en juego.",
        },
        {
            "id": "tutor_talisman_on_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": ">=", "value": 3}}},
                "operator": ">=",
                "targetValue": 2,
            },
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talismans", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En tu Fase Final, si controlas 2 o más Aliados de coste 3 o más, puedes buscar un Talismán y ponerlo en tu mano.",
        },
    ],
}
tags_es551 = ["restriccion", "busca_mazo", "opcional"]
set_card("es551", abilities_es551, tags_es551)

# es552 Nativitas
abilities_es552 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "everyone_draw_three",
            "type": "activated",
            "effect": {"type": "draw_cards", "target": "all", "amount": 3},
            "text": "Cada jugador roba 3 cartas.",
        },
        {
            "id": "search_fiesta",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "cards", "name": "Fiesta", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Luego, puedes buscar una carta Fiesta en tu mazo y ponerla en tu mano.",
        },
    ],
}
tags_es552 = ["roba_cartas", "busca_mazo", "opcional"]
set_card("es552", abilities_es552, tags_es552)

# es553 Dama Encantada
abilities_es553 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_talisman_each_player",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "talismans", "controller": "all"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "text": "Cuando entra en juego, cada jugador elige un Talismán de su Cementerio y lo pone en su mano.",
        }
    ],
}
tags_es553 = ["busca_mazo", "mueve_zona", "trigger_al_entrar"]
set_card("es553", abilities_es553, tags_es553)

# es554 Sir Tyolet
abilities_es554 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "grant_haste_when_ally_enters",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": "self", "location": "attack_line"},
                    {
                        "type": "gain_ability",
                        "target": "triggered_card",
                        "value": {"restriction": "can_attack_on_enter"},
                        "duration": "end_turn",
                    },
                ],
            },
            "optional": True,
            "text": "Cuando un Aliado propio entra, puedes mover a Sir Tyolet a la línea de ataque para que ese Aliado pueda atacar este turno.",
        }
    ],
}
tags_es554 = ["apresurado", "mueve_zona", "opcional"]
set_card("es554", abilities_es554, tags_es554)

# es555 Sir Osanain
abilities_es555 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "exile_from_grave_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "cost": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}}, "amount": 1},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "graveyard"}},
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando sea declarado atacante, puedes desterrar una carta de tu Cementerio para desterrar un Aliado del Cementerio oponente.",
        },
    ],
}
tags_es555 = ["apresurado", "destierra_objetivo", "exilia_para_pagar", "opcional"]
set_card("es555", abilities_es555, tags_es555)

# es556 Fiesta de Mayo
abilities_es556 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando la juegues, destiérrala.",
        },
        {
            "id": "play_fiesta_from_grave",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "cards", "name": "Fiesta", "controller": "self", "not_name": "Fiesta de Mayo"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "text": "Busca una carta Fiesta (que no sea Fiesta de Mayo) en tu Cementerio y juégala sin pagar su coste.",
        },
        {
            "id": "search_fiesta_deck",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "cards", "name": "Fiesta", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Luego, puedes buscar una carta Fiesta en tu mazo y ponerla en tu mano.",
        },
    ],
}
tags_es556 = ["exilia_para_pagar", "busca_mazo", "pone_en_juego", "opcional"]
set_card("es556", abilities_es556, tags_es556)

# es557 Jack O' The Green
abilities_es557 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_small_ally_to_destroy",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "cost": {"operator": "<=", "value": 2}}},
                        "amount": 1,
                        "is_cost": True,
                    },
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes destruir un Aliado propio de coste 2 o menos; si lo haces, destruye un Aliado oponente.",
        }
    ],
}
tags_es557 = ["destruye_para_pagar", "destruye_objetivo", "opcional", "trigger_al_entrar"]
set_card("es557", abilities_es557, tags_es557)

# es558 Rey Arturo Pendragon
abilities_es558 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener en juego a un Rey Arturo Pendragón.",
        },
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "play"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus Caballeros ganan +1 a la fuerza.",
        },
        {
            "id": "mill_each_grouping",
            "type": "triggered",
            "trigger": {"type": "phase_start", "phase": "agrupacion", "target": "all"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "text": "En cada fase de agrupación, tu oponente bota 2 cartas.",
        },
        {
            "id": "save_by_discarding",
            "type": "response",
            "trigger": {"type": "destroyed", "target": "self"},
            "cost": {"type": "discard", "target": "controller", "amount": 2, "location": "hand"},
            "effect": {"type": "prevent_destruction", "target": "self"},
            "optional": True,
            "text": "En respuesta a ser destruido, puedes descartar 2 cartas para salvarlo.",
        },
    ],
}
tags_es558 = ["restriccion", "modifica_fuerza", "bota_cartas", "opcional"]
set_card("es558", abilities_es558, tags_es558)

# es559 Reynard el Zorro
abilities_es559 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "pay_and_sac_to_tutor",
            "type": "activated",
            "cost": {
                "type": "group",
                "costs": [
                    {"type": "pay_resources", "amount": 1},
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
                ],
            },
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Puedes pagar 1 Oro y destruir este u otro Aliado propio para buscar un Aliado en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "destroy_small_opponent_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "cost": {"operator": "<=", "value": 2}}},
                "amount": 1,
            },
            "text": "Cuando salga del juego, destruye un Aliado oponente de coste 2 o menos.",
        },
    ],
}
tags_es559 = ["imbloqueable", "paga_recursos", "destruye_para_pagar", "busca_mazo", "opcional", "destruye_objetivo"]
set_card("es559", abilities_es559, tags_es559)


conn.commit()
conn.close()
print("Updated batch: es550-es559")

