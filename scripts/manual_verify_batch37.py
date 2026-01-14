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
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
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


# es424 Capitan Imperial
abilities_es424 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "move_opponent_defense_to_attack",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense_line"}},
                "location": "support_line",
            },
            "text": "Al entrar, todos los aliados en la defensa oponente pasan a su línea de ataque.",
        }
    ],
}
tags_es424 = ["mueve_zona", "trigger_al_entrar"]
set_card("es424", abilities_es424, tags_es424)

# es425 Sir Gabriel
abilities_es425 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_exile",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "exile"}}}},
            },
            "text": "Gana +1 fuerza por cada carta en tu zona de destierro.",
        }
    ],
}
tags_es425 = ["modifica_fuerza"]
set_card("es425", abilities_es425, tags_es425)

# es426 Org, El Hechizero
abilities_es426 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "war_reduce_force_zero",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "set", "value": 0},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En guerra de Talismanes, paga 2 oro: un aliado oponente queda con fuerza 0 hasta el final del turno.",
        }
    ],
}
tags_es426 = ["paga_recursos", "modifica_fuerza", "opcional", "restriccion"]
set_card("es426", abilities_es426, tags_es426)

# es427 Dragon Nival
abilities_es427 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_force_two_or_less",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "force": {"operator": "<=", "value": 2}}}},
            "text": "Cuando entra, destruye todos los Aliados de fuerza 2 o menos.",
        }
    ],
}
tags_es427 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es427", abilities_es427, tags_es427)

# es428 Cria de Wyrm
abilities_es428 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_cost_three_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "cost": {"operator": "==", "value": 3}}},
            },
            "optional": True,
            "text": "Cuando entra, puedes desterrar un Aliado oponente de coste 3.",
        }
    ],
}
tags_es428 = ["destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("es428", abilities_es428, tags_es428)

# es429 Mulvan, El Dragón
abilities_es429 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "double_force_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "multiply", "value": 2}, "duration": "end_turn"},
            "optional": True,
            "text": "En guerra de Talismanes, puede duplicar su fuerza hasta fin de turno.",
        },
        {
            "id": "exile_at_end_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Al final del turno, destiérralo.",
        },
    ],
}
tags_es429 = ["modifica_fuerza", "opcional", "destierra_objetivo"]
set_card("es429", abilities_es429, tags_es429)

# es43 Vouivre
abilities_es43 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_self_and_opponents",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "amount": 1,
                        "location": "deck",
                        "optional": True,
                    },
                    {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 2, "location": "deck"},
                ],
            },
            "text": "Cuando entra, puedes barajar un aliado propio para barajar 2 aliados oponentes.",
        },
        {
            "id": "tutor_dragon_once_per_turn",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes buscar un Aliado Dragón y ponerlo en tu mano.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es43 = ["baraja", "mueve_zona", "opcional", "busca_mazo", "una_vez_por_turno", "restriccion"]
set_card("es43", abilities_es43, tags_es43)

# es430 Bruja Anis
abilities_es430 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_if_all_faeries",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {"type": "all", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "condition": {"type": "race", "value": "Faerie"}},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Al final de tu turno, si todos tus Aliados son Faerie, puedes robar 1 carta.",
        }
    ],
}
tags_es430 = ["roba_cartas", "opcional", "restriccion"]
set_card("es430", abilities_es430, tags_es430)

# es431 Elfo Oscuro
abilities_es431 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Cuando entra en juego, roba 1 carta.",
        }
    ],
}
tags_es431 = ["roba_cartas", "trigger_al_entrar"]
set_card("es431", abilities_es431, tags_es431)

# es432 Misil Magico
abilities_es432 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choose_draw_or_boost",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "modify_force", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "modifier": {"type": "add", "value": 2}, "duration": "end_turn"},
                ],
            },
            "text": "En guerra de Talismanes, elige: robar 2 cartas o dar +2 fuerza a un aliado hasta fin de turno.",
        }
    ],
}
tags_es432 = ["roba_cartas", "modifica_fuerza", "opcional", "restriccion"]
set_card("es432", abilities_es432, tags_es432)


conn.commit()
conn.close()
print("Updated batch: es424-es432 y es43")






