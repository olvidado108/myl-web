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
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
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


# es514 Aliento de Luz
abilities_es514 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_dragon_to_exile",
            "type": "activated",
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "operator": ">=", "targetValue": 1},
                    {
                        "type": "all",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "condition": {"type": "race", "value": "Dragón"},
                    },
                ],
            },
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "amount": 1},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                "amount": 1,
            },
            "text": "Solo si solo controlas Aliados Dragón, destruye uno propio para que el oponente destierre una carta en juego que no sea Oro.",
        }
    ],
}
tags_es514 = ["restriccion", "destierra_objetivo", "destruye_para_pagar"]
set_card("es514", abilities_es514, tags_es514)

# es515 Colmillo Negro
abilities_es515 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "set_force_one",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "set", "value": 1}},
            "text": "El portador tiene fuerza 1.",
        },
        {
            "id": "cannot_attack_or_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"cannot_attack_or_block": True}, "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "El portador no puede atacar ni bloquear.",
        },
    ],
}
tags_es515 = ["restriccion", "modifica_fuerza"]
set_card("es515", abilities_es515, tags_es515)

# es516 Monte Kilgharrah
abilities_es516 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_big_dragon",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "cost": {"operator": ">=", "value": 3}}}},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cuando juegues un Aliado Dragón de coste 3 o más, puedes robar 1 carta.",
        },
        {
            "id": "shuffle_when_dragon_leaves",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}}},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando un Dragón propio salga del juego, puedes barajar 1 carta de tu Cementerio en tu Mazo Castillo.",
        },
    ],
}
tags_es516 = ["roba_cartas", "baraja", "opcional"]
set_card("es516", abilities_es516, tags_es516)

# es517 Corte de la Furia
abilities_es517 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_or_exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": ">=", "value": 2}}}},
            "effect": {
                "type": "choice",
                "options": [
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "location": "deck",
                        "amount": 1,
                    },
                    {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}}, "amount": 1},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, cuando juegues un Aliado de coste 2 o más, puedes barajar 1 carta de tu Cementerio o desterrar 1 carta del Cementerio oponente.",
        }
    ],
}
tags_es517 = ["baraja", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("es517", abilities_es517, tags_es517)

# es518 Dragón de Eter
abilities_es518 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "debuff_opponents_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "text": "Si es declarado atacante, los Aliados oponentes pierden 1 a la fuerza hasta la Fase Final.",
        },
    ],
}
tags_es518 = ["apresurado", "modifica_fuerza"]
set_card("es518", abilities_es518, tags_es518)

# es519 Kilgharrah
abilities_es519 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Kilgharrah en juego.",
        },
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "shuffle_two_draw_two",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia, una vez por turno, puedes barajar 2 cartas de tu Cementerio para robar 2 cartas.",
        },
    ],
}
tags_es519 = ["restriccion", "imbloqueable", "apresurado", "baraja", "roba_cartas", "opcional", "una_vez_por_turno"]
set_card("es519", abilities_es519, tags_es519)

# es52 Sir Boores
abilities_es52 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "play"}},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Tus Caballeros ganan +2 a la fuerza mientras esté en juego.",
        }
    ],
}
tags_es52 = ["modifica_fuerza"]
set_card("es52", abilities_es52, tags_es52)

# es520 Wyvern de Sangre
abilities_es520 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar el turno que entra en juego.",
        },
        {
            "id": "return_from_grave",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {"type": "move_zone", "target": "self", "location": "hand"},
            "optional": True,
            "text": "Si está en tu Cementerio, puedes pagar 2 Oros para ponerlo en tu mano.",
        },
    ],
}
tags_es520 = ["apresurado", "mueve_zona", "paga_recursos", "opcional"]
set_card("es520", abilities_es520, tags_es520)

# es521 Draco Esmeralda
abilities_es521 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_faerie_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Faerie en tu mazo y ponerlo en tu mano.",
        }
    ],
}
tags_es521 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es521", abilities_es521, tags_es521)

# es522 Alquimista
abilities_es522 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "fetch_gold_in_vigilia",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self", "subtype": "normal"}},
                "action": "put_in_play",
            },
            "text": "En tu Fase de Vigilia, busca un Oro normal en tu mazo y ponlo en tu reserva.",
        }
    ],
}
tags_es522 = ["busca_mazo", "pone_en_juego"]
set_card("es522", abilities_es522, tags_es522)


conn.commit()
conn.close()
print("Updated batch: es514-es522")

