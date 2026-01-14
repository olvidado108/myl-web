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
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
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


# es442 Corona de Arturo
abilities_es442 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_indestructibles",
            "type": "static",
            "condition": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "operator": ">=", "targetValue": 2},
            "effect": {"type": "restriction", "restriction": "indestructible", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}},
            "text": "Mientras controles 2 o más Aliados, tus Oros son indestructibles.",
        },
        {
            "id": "exile_from_grave_draw",
            "type": "activated",
            "condition": {"type": "zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Desde tu cementerio, puedes desterrarla para robar 1 carta.",
        },
    ],
}
tags_es442 = ["restriccion", "destierra_para_pagar", "roba_cartas"]
set_card("es442", abilities_es442, tags_es442)

# es443 Faeries
abilities_es443 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Faeries en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Sólo puede ser jugado desde tu mano.",
        },
        {
            "id": "boost_faeries_in_reserve",
            "type": "static",
            "condition": {"type": "zone", "value": "reserve", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "defense_line", "cost": {"operator": "<=", "value": 3}}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en tu Reserva de Oro, tus Faerie de coste 3 o menos en defensa ganan +1 fuerza.",
        },
    ],
}
tags_es443 = ["restriccion", "modifica_fuerza"]
set_card("es443", abilities_es443, tags_es443)

# es444 Sir Palamades
abilities_es444 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "gain_force_on_exile",
            "type": "triggered",
            "trigger": {"type": "card_moved", "to": "exile"},
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "add", "value": 1}, "permanent": True},
            "oncePerTurn": True,
            "text": "Una vez por turno, cuando una carta va al destierro, gana +1 fuerza permanente.",
        },
        {
            "id": "exile_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "graveyard"}}, "amount": 1},
            "text": "Cuando es declarado atacante, destierra una carta de un cementerio.",
        },
    ],
}
tags_es444 = ["modifica_fuerza", "destierra_objetivo", "una_vez_por_turno"]
set_card("es444", abilities_es444, tags_es444)

# es445 Guardia Real
abilities_es445 = {
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
tags_es445 = ["apresurado", "destruye_objetivo"]
set_card("es445", abilities_es445, tags_es445)

# es446 Halconero Real
abilities_es446 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "opponent_discard_or_you_draw",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "discard", "target": "opponent", "amount": 1, "location": "hand"},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "text": "Cuando entra, roba 1 a menos que el oponente descarte 1 (elige entre descartar 1 o que robes 1).",
        }
    ],
}
tags_es446 = ["descarta_mano", "roba_cartas", "trigger_al_entrar"]
set_card("es446", abilities_es446, tags_es446)

# es447 Balduino
abilities_es447 = {
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
tags_es447 = ["modifica_fuerza"]
set_card("es447", abilities_es447, tags_es447)

# es448 Duque Godofredo
abilities_es448 = {
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
tags_es448 = ["modifica_fuerza"]
set_card("es448", abilities_es448, tags_es448)

# es449 Curandera
abilities_es449 = {
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
tags_es449 = ["modifica_coste"]
set_card("es449", abilities_es449, tags_es449)

# es45 Draig Ifanc
abilities_es45 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cuando entra, puedes robar 1 carta.",
        },
        {
            "id": "search_gold_on_leave_if_only_dragons",
            "type": "response",
            "trigger": {"type": "leaves_play", "target": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "race": {"operator": "!=", "value": "Dragón"}}},
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {"type": "search", "location": "deck", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}, "action": "put_in_play"},
            "optional": True,
            "text": "Si es destruido o barajado y solo controlabas Dragones, busca un Oro y ponlo en juego.",
        },
    ],
}
tags_es45 = ["roba_cartas", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es45", abilities_es45, tags_es45)

# es450 Aghast
abilities_es450 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "search", "location": "deck", "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}}, "action": "put_in_hand"},
            "optional": True,
            "text": "Cuando entra, puedes buscar un arma en tu mazo y ponerla en tu mano.",
        }
    ],
}
tags_es450 = ["busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es450", abilities_es450, tags_es450)


conn.commit()
conn.close()
print("Updated batch: es442-es450 y es45")






