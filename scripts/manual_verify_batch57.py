import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("previene_dano", "Previene daño", "defensivo", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
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


# es96 Una
abilities_es96 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "hands_reset_and_no_attack",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "discard", "target": "all", "amount": "all", "location": "hand"},
                    {
                        "type": "draw_cards",
                        "target": "all",
                        "amount": {"type": "reference", "reference": "last_discard_amount"},
                    },
                    {
                        "type": "restriction",
                        "restriction": "cannot_attack",
                        "target": {"type": "global"},
                        "duration": {"type": "turns", "value": 2},
                    },
                ],
            },
            "text": "En Guerra de Talismanes: cada jugador descarta su mano y roba la misma cantidad. Los próximos 2 turnos nadie puede declarar ataque.",
        }
    ],
}
tags_es96 = ["descarta_mano", "roba_cartas", "restriccion"]
set_card("es96", abilities_es96, tags_es96)

# es97 Aulladores Blancos
abilities_es97 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_same_type_on_response",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}}},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "sameTypeAs": {"type": "reference", "reference": "triggered_card"}}},
            },
            "optional": True,
            "text": "En respuesta a que una de tus cartas sea destruida, destruye una carta oponente del mismo tipo.",
        }
    ],
}
tags_es97 = ["destruye_objetivo", "opcional"]
set_card("es97", abilities_es97, tags_es97)

# es98 Atraer la Tormenta
abilities_es98 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_unless_mill_three",
            "type": "activated",
            "effect": {
                "type": "counter",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "type": {"operator": "!=", "value": "oros"}}},
                "unless": {"type": "discard", "target": "opponent", "amount": 3, "location": "deck"},
            },
            "text": "Anula una carta oponente que no sea Oro, a menos que bote 3 cartas.",
        }
    ],
}
tags_es98 = ["anula", "bota_cartas"]
set_card("es98", abilities_es98, tags_es98)

# es99 Caballo Lunar
abilities_es99 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_all_allies_in_hand",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "hand"}}},
                    {"type": "discard", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand"}}, "amount": "all", "location": "hand"},
                ],
            },
            "text": "Mira la mano de tu oponente y descarta todos los Aliados que tenga.",
        }
    ],
}
tags_es99 = ["descarta_mano"]
set_card("es99", abilities_es99, tags_es99)

# hd1 Salmon del Saber
abilities_hd1 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_one_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar 1 carta de tu Cementerio en tu mazo.",
        },
        {
            "id": "exile_from_reserve_prevent_deck_damage",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "reserve", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "prevent_damage",
                "target": {"type": "reference", "reference": "controller.deck"},
                "duration": "turn",
                "source": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "optional": True,
            "text": "Desde la Reserva, puedes desterrarlo: el daño de Aliados oponentes a tu mazo es 0 este turno.",
        },
    ],
}
tags_hd1 = ["baraja", "exilia_para_pagar", "previene_dano", "opcional"]
set_card("hd1", abilities_hd1, tags_hd1)

# hd10 Alas de Druida
abilities_hd10 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_small_ally",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": "<=", "value": {"type": "math", "operation": "card_cost_minus", "value": 2}}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "text": "Busca un Aliado de coste 2 menos en tu Cementerio y ponlo en tu mano.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd10 = ["busca_mazo", "mueve_zona", "restriccion"]
set_card("hd10", abilities_hd10, tags_hd10)

# hd100 Exilio
abilities_hd100 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_opponent_ally",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Cuando entra, destierra un Aliado oponente.",
        },
        {
            "id": "draw_optional",
            "type": "triggered",
            "trigger": {"type": "after_effect", "ability": "exile_opponent_ally"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Luego, puedes robar 1 carta.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd100 = ["destierra_objetivo", "roba_cartas", "opcional", "restriccion", "trigger_al_entrar"]
set_card("hd100", abilities_hd100, tags_hd100)

# hd101 Llama Marina
abilities_hd101 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_from_grave",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "text": "Baraja 2 cartas de tu Cementerio en tu mazo.",
        }
    ],
}
tags_hd101 = ["baraja"]
set_card("hd101", abilities_hd101, tags_hd101)

# hd102 Slaine
abilities_hd102 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede ser declarado atacante el turno que entra.",
        },
        {
            "id": "opponent_sac_highest_force_on_death",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "sort": "force_desc", "limit": 1}},
            },
            "text": "Si es destruido, el oponente destruye su Aliado de mayor fuerza.",
        },
    ],
}
tags_hd102 = ["apresurado", "destruye_objetivo"]
set_card("hd102", abilities_hd102, tags_hd102)

# hd103 Cuchulain
abilities_hd103 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_other_to_prevent_destruction",
            "type": "response",
            "trigger": {"type": "destroyed", "target": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "exclude": "self"}}, "amount": 1},
            "effect": {"type": "prevent_destruction", "target": "self"},
            "optional": True,
            "text": "Si fuese a ser destruido, puedes destruir otro de tus Aliados para prevenirlo.",
        },
        {
            "id": "draw_on_deck_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "Si hace daño al mazo oponente, puedes robar 2 cartas.",
        },
    ],
}
tags_hd103 = ["destruye_para_pagar", "previene_dano", "roba_cartas", "opcional"]
set_card("hd103", abilities_hd103, tags_hd103)


conn.commit()
conn.close()
print("Updated batch: es96-es99 y hd1/hd10/hd100-hd103")








