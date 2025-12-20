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
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
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


# hd122 Tutatis
abilities_hd122 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_requires_two_allies",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {
                    "play_requires": {
                        "type": "count",
                        "value": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "operator": ">=",
                        "targetValue": 2,
                    }
                },
                "target": "self",
            },
            "text": "Solo puedes jugarlo si controlas dos o más Aliados.",
        },
        {
            "id": "all_allies_attack_with_tutatis",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "must_attack",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "exclude": "self"}},
                "duration": "combat",
            },
            "text": "Si es declarado atacante, todos tus otros Aliados que puedan deben ser atacantes.",
        },
    ],
}
tags_hd122 = ["restriccion"]
set_card("hd122", abilities_hd122, tags_hd122)

# hd123 Boobrie
abilities_hd123 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "flashback_blocker",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}},
            "condition": {"type": "in_zone", "target": "self", "zone": "graveyard"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "put_in_play",
                "target": "self",
                "location": "defense_line",
                "controller": "self",
                "pay_cost": False,
                "as_blocker": True,
            },
            "optional": True,
            "text": "En respuesta a declarar ataque oponente, si está en tu Cementerio, paga 2: ponlo en tu defensa como bloqueador.",
        },
        {
            "id": "destroy_at_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "En la Fase Final, debe ser destruido.",
        },
    ],
}
tags_hd123 = ["paga_recursos", "mueve_zona", "opcional"]
set_card("hd123", abilities_hd123, tags_hd123)

# hd124 Macha
abilities_hd124 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "remove_modifiers_set_base",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}},
                "modifier": {"type": "set_base"},
            },
            "text": "Todos los Aliados pierden modificadores de fuerza (se consideran su fuerza base).",
        },
        {
            "id": "allies_indestructible",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "indestructible", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}}},
            "text": "Todos los Aliados son Indestructibles.",
        },
    ],
}
tags_hd124 = ["restriccion", "modifica_fuerza"]
set_card("hd124", abilities_hd124, tags_hd124)

# hd125 Rhiannon
abilities_hd125 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_three_choose",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal_top", "target": {"type": "reference", "reference": "controller.deck"}, "amount": 3},
                    {
                        "type": "choice",
                        "options": [
                            {
                                "type": "move_zone",
                                "target": {"type": "filter", "filter": {"type": "cards", "zone": "revealed", "controller": "self", "type": {"operator": "!=", "value": "allies"}}},
                                "location": "hand",
                                "amount": 1,
                            },
                            {
                                "type": "move_zone",
                                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "zone": "revealed", "controller": "self"}},
                                "location": "hand",
                            },
                        ],
                        "optional": True,
                    },
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "cards", "zone": "revealed", "controller": "self"}},
                        "location": "graveyard",
                    },
                ],
            },
            "text": "Al entrar, mira las 3 primeras: toma una que no sea Aliado o todos los Desafiante y ponlos en tu mano; el resto al Cementerio.",
        }
    ],
}
tags_hd125 = ["mueve_zona", "opcional", "trigger_al_entrar"]
set_card("hd125", abilities_hd125, tags_hd125)

# hd126 Aine
abilities_hd126 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_challenger_to_exile",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "condition": {"type": "has_card_in_hand", "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self", "zone": "hand"}}},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}},
            "optional": True,
            "text": "Cuando entra, puedes mostrar un Desafiante en tu mano para desterrar un Aliado oponente.",
        }
    ],
}
tags_hd126 = ["destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("hd126", abilities_hd126, tags_hd126)

# hd127 Aife
abilities_hd127 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_force_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": {"type": "reference", "reference": "self.force"},
                "location": "deck",
            },
            "optional": True,
            "text": "Al entrar, puedes barajar tantas cartas de tu Cementerio como fuerza tenga.",
        }
    ],
}
tags_hd127 = ["baraja", "opcional", "trigger_al_entrar"]
set_card("hd127", abilities_hd127, tags_hd127)

# hd128 Artio
abilities_hd128 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_to_draw_if_only_challengers",
            "type": "activated",
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "phase", "value": "vigilia", "controller": "self"},
                    {"type": "all", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "condition": {"type": "race", "value": "Desafiante"}},
                ],
            },
            "cost": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, si solo controlas Desafiante, descarta 1 para robar 1 (una vez por turno).",
        }
    ],
}
tags_hd128 = ["descarta_mano", "roba_cartas", "opcional", "una_vez_por_turno", "restriccion"]
set_card("hd128", abilities_hd128, tags_hd128)

# hd129 Linaje Celta
abilities_hd129 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "next_challenger_uncounterable",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "grant_ability_until",
                "duration": "end_turn",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self", "zone": "hand"}},
                "value": {"restriction": "cannot_be_countered"},
            },
            "text": "El turno que entra, el próximo Desafiante que juegues no puede ser anulado.",
        },
        {
            "id": "destroy_to_tutor_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En Vigilia, puedes destruirlo desde la Reserva para buscar un Desafiante en tu Cementerio y ponerlo en tu mano.",
        },
    ],
}
tags_hd129 = ["restriccion", "busca_mazo", "opcional"]
set_card("hd129", abilities_hd129, tags_hd129)

# hd13 Morir de Pie
abilities_hd13 = {
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
            "id": "counter_non_gold_non_ally",
            "type": "activated",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "effect": {
                "type": "counter",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "type": {"operator": "not_in", "value": ["oros", "allies"]}}}},
            "text": "Solo si controlas dos o más Aliados de una misma raza: anula una carta oponente que no sea Oro ni Aliado.",
        },
    ],
}
tags_hd13 = ["destierra_objetivo", "anula", "restriccion"]
set_card("hd13", abilities_hd13, tags_hd13)

# hd130 Caturix
abilities_hd130 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_four_challenger_or_gold",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "cards",
                        "controller": "self",
                        "zone": "graveyard",
                        "cardType": {"operator": "in", "value": ["oros", "allies"]},
                        "condition": {"type": "or", "conditions": [{"type": "card_type", "value": "oros"}, {"type": "race", "value": "Desafiante"}]},
                    },
                },
                "amount": 4,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando entra, baraja hasta cuatro Oros y/o Aliados Desafiante de tu Cementerio en tu mazo.",
        }
    ],
}
tags_hd130 = ["baraja", "opcional", "trigger_al_entrar"]
set_card("hd130", abilities_hd130, tags_hd130)


conn.commit()
conn.close()
print("Updated batch: hd122-hd130 y hd13")

