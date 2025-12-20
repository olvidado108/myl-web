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
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("modifica_coste", "Modifica coste", "soporte", None),
    ("previene_dano", "Previene daño", "defensivo", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
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


# es488 Nimue
abilities_es488 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "copy_faerie_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"type": "copy_from_graveyard", "race": "Faerie"}, "duration": "end_turn"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia y una vez por turno, puedes elegir un Aliado Faerie de tu Cementerio para que Nimue se convierta en una copia exacta hasta la Fase Final.",
        }
    ],
}
tags_es488 = ["opcional", "una_vez_por_turno"]
set_card("es488", abilities_es488, tags_es488)

# es489 Faeries
abilities_es489 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Faeries en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Solo puede ser jugado desde tu mano.",
        },
        {
            "id": "boost_faerie_defenders",
            "type": "static",
            "condition": {"type": "in_zone", "value": "gold_reserve", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "defense_line", "cost": {"operator": "<=", "value": 3}},
                },
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en tu Reserva de Oro, tus Aliados Faerie de coste 3 o menos en Línea de Defensa ganan +1 a la fuerza.",
        },
    ],
}
tags_es489 = ["restriccion", "modifica_fuerza"]
set_card("es489", abilities_es489, tags_es489)

# es49 Rey Arturo Pendragon
abilities_es49 = {
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
            "text": "En respuesta a que sea destruido, puedes descartar 2 cartas para salvarlo.",
        },
    ],
}
tags_es49 = ["restriccion", "modifica_fuerza", "bota_cartas", "opcional", "descarta_mano"]
set_card("es49", abilities_es49, tags_es49)

# es490 Reina Merrow
abilities_es490 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "draw_if_damage_and_faeries",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "did_damage_to_deck", "target": "opponent"},
                    {
                        "type": "count",
                        "value": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "play"}},
                        "operator": ">=",
                        "targetValue": 3,
                    },
                ],
            },
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "En tu Fase Final, si dañó el Mazo Castillo oponente y controlas 3 o más Aliados Faerie, puedes robar una carta.",
        },
    ],
}
tags_es490 = ["imbloqueable", "roba_cartas", "opcional", "restriccion"]
set_card("es490", abilities_es490, tags_es490)

# es491 Gente del Musgo
abilities_es491 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "attack_only_with_faeries",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {
                    "attack_requires": {
                        "type": "count",
                        "value": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "play", "exclude": "self"}},
                        "operator": ">=",
                        "targetValue": 2,
                    }
                },
                "target": "self",
            },
            "text": "Solo puede atacar si controlas otros 2 o más Aliados de raza Faerie.",
        }
    ],
}
tags_es491 = ["restriccion"]
set_card("es491", abilities_es491, tags_es491)

# es492 Diadema Feerica
abilities_es492 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_graveyard",
            "type": "activated",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Solo puedes activarla una vez por turno. Si controlas 2 o más Aliados de una misma raza, puedes pagarla para barajar una carta de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es492 = ["baraja", "opcional", "una_vez_por_turno", "paga_recursos"]
set_card("es492", abilities_es492, tags_es492)

# es493 Sir Lancelot del Lago
abilities_es493 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "protection_from_opponent_talismans",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"cannot_be_targeted_by": {"type": "talismanes", "controller": "opponent"}},
                "target": "self",
            },
            "text": "No puede ser afectado por Talismanes oponentes.",
        },
        {
            "id": "cheaper_weapons_here",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "equip_target_name": "Sir Lancelot del Lago"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Jugar Armas en este Aliado cuesta 1 Oro menos.",
        },
    ],
}
tags_es493 = ["apresurado", "restriccion", "modifica_coste"]
set_card("es493", abilities_es493, tags_es493)

# es494 Reina Guinivere
abilities_es494 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_knight_on_enter",
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
            "text": "Cuando entra en juego, puedes buscar un Caballero en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "generate_for_weapons_or_knights",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "generate_resources", "amount": 2, "restriction": "armas"},
                    {"type": "generate_resources", "amount": 1, "restriction": "caballeros"},
                ],
            },
            "text": "En tu fase de vigilia, genera 2 para bajar Armas o 1 para bajar Caballeros.",
        },
    ],
}
tags_es494 = ["busca_mazo", "opcional", "genera_recursos", "trigger_al_entrar"]
set_card("es494", abilities_es494, tags_es494)

# es495 Sir Galehaut
abilities_es495 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "force_blocker_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "must_block",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "Si es declarado atacante, puedes elegir un Aliado oponente para que lo bloquee.",
        },
    ],
}
tags_es495 = ["apresurado", "opcional", "restriccion"]
set_card("es495", abilities_es495, tags_es495)

# es496 Sir Dagonet
abilities_es496 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Sir Dagonet en juego.",
        },
        {
            "id": "exile_to_prevent_damage",
            "type": "response",
            "trigger": {"type": "phase_start", "phase": "asignacion_dano", "target": "all"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "prevent_damage", "target": {"type": "global"}, "duration": "phase"},
            "optional": True,
            "text": "En la Fase de Asignación de Daño, puedes desterrarlo para reducir todo el daño a 0.",
        },
    ],
}
tags_es496 = ["restriccion", "opcional", "previene_dano", "exilia_para_pagar"]
set_card("es496", abilities_es496, tags_es496)


conn.commit()
conn.close()
print("Updated batch: es488-es496 y es49")

