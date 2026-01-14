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
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
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


# es406 Herrero
abilities_es406 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_weapons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "armas"},
            "optional": True,
            "text": "En tu Fase de Vigilia, puedes pagar 1 oro para generar 2 Oros para jugar Armas.",
        },
        {
            "id": "destroy_if_loses_ability",
            "type": "triggered",
            "trigger": {"type": "lose_ability", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si fuese a perder su habilidad, Herrero es destruido.",
        },
    ],
}
tags_es406 = ["genera_recursos", "paga_recursos", "opcional", "destruye_objetivo"]
set_card("es406", abilities_es406, tags_es406)

# es407 la Velue
abilities_es407 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "La Velue puede atacar cuando entra en juego.",
        },
        {
            "id": "pay_to_boost_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "add", "value": 1}, "duration": "end_turn"},
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, puedes pagar 1 oro: gana +1 a la fuerza hasta la Fase Final.",
        },
    ],
}
tags_es407 = ["apresurado", "paga_recursos", "modifica_fuerza", "opcional", "una_vez_por_turno"]
set_card("es407", abilities_es407, tags_es407)

# es408 Sebile
abilities_es408 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lock_regroup_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "cannot_regroup",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "while_source_in_play",
            },
            "text": "Cuando entra, elige un aliado oponente: no puede ser reagrupado mientras Sebile esté en tu defensa.",
        }
    ],
}
tags_es408 = ["restriccion", "trigger_al_entrar"]
set_card("es408", abilities_es408, tags_es408)

# es409 Reina Guinivere
abilities_es409 = {
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
            "text": "Cuando entra, puedes buscar un Caballero en tu mazo y ponerlo en tu mano.",
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
            "text": "En Vigilia, genera 2 para Armas o 1 para Caballeros.",
        },
    ],
}
tags_es409 = ["busca_mazo", "mueve_zona", "opcional", "genera_recursos", "trigger_al_entrar"]
set_card("es409", abilities_es409, tags_es409)

# es41 Espada Larga
abilities_es41 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "text": "Cuando entra en juego, roba dos cartas.",
        },
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
    ],
}
tags_es41 = ["roba_cartas", "modifica_fuerza", "trigger_al_entrar"]
set_card("es41", abilities_es41, tags_es41)

# es410 Sir Boores
abilities_es410 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Tus Caballeros ganan +2 a la fuerza mientras esté en juego.",
        }
    ],
}
tags_es410 = ["modifica_fuerza"]
set_card("es410", abilities_es410, tags_es410)

# es411 Sir Tristan
abilities_es411 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}},
                "action": "put_in_hand",
            },
            "text": "Cuando entra, busca una carta en tu cementerio y ponla en tu mano.",
        }
    ],
}
tags_es411 = ["busca_mazo", "mueve_zona", "trigger_al_entrar"]
set_card("es411", abilities_es411, tags_es411)

# es412 el Gran Wyrm
abilities_es412 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_other_dragons",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "not": {"id": "self"}}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus otros Dragones ganan +1 a la fuerza.",
        },
        {
            "id": "haste_for_dragons",
            "type": "static",
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "not": {"id": "self"}}},
                "value": {"restriction": "can_attack_on_enter"},
            },
            "text": "Tus otros Dragones pueden atacar cuando entran en juego.",
        },
    ],
}
tags_es412 = ["modifica_fuerza", "apresurado"]
set_card("es412", abilities_es412, tags_es412)

# es413 Gitanos
abilities_es413 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_any_card",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}},
                "amount": 1,
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Busca una carta en tu mazo y ponla en tu mano.",
        }
    ],
}
tags_es413 = ["busca_mazo", "mueve_zona", "opcional"]
set_card("es413", abilities_es413, tags_es413)

# es414 la Llama Fria
abilities_es414 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_and_play_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "text": "Solo en tu Fase de Vigilia: busca un Aliado en tu mazo y juégalo sin pagar su coste.",
        }
    ],
}
tags_es414 = ["busca_mazo", "pone_en_juego", "restriccion"]
set_card("es414", abilities_es414, tags_es414)


conn.commit()
conn.close()
print("Updated batch: es406-es414 y es41")






