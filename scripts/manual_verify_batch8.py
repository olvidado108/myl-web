import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("descarta_mano", "Descarta de mano", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("modifica_coste", "Modifica coste", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("indestructible", "Indestructible", "defensivo", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
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


# es162 Duendes Foil
abilities_es162 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "text": "Cuando entra en juego, debes descartar 1 carta.",
        }
    ],
}
tags_es162 = ["descarta_mano", "trigger_al_entrar"]
set_card("es162", abilities_es162, tags_es162)

# es163 Balduino Foil
abilities_es163 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lose_force_after_attack",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "attacked_this_turn", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": -1},
                "permanent": True,
            },
            "text": "Al finalizar cada turno en que atacó, gana -1 fuerza de forma permanente.",
        }
    ],
}
tags_es163 = ["modifica_fuerza", "trigger_fin_turno"]
set_card("es163", abilities_es163, tags_es163)

# es164 Duque Godofredo Foil
abilities_es164 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en juego, tus Caballeros ganan +1 a la fuerza.",
        }
    ],
}
tags_es164 = ["modifica_fuerza"]
set_card("es164", abilities_es164, tags_es164)

# es165 Curandera Foil
abilities_es165 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reduce_cost_all",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Mientras esté en juego, tus cartas reducen en 1 su coste.",
        }
    ],
}
tags_es165 = ["modifica_coste"]
set_card("es165", abilities_es165, tags_es165)

# es166 Ataque A Traicion Foil
abilities_es166 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_all_allies",
            "type": "activated",
            "condition": {"phase": "main"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "changeController": True,
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "value": {"restriction": "can_be_declared_attacker"},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "En Vigilia, todos los aliados oponentes pasan a tu control y pueden ser declarados atacantes este turno.",
        },
        {
            "id": "lose_if_no_win",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "lose_game"},
            "text": "Si no ganas este turno, pierdes el juego.",
        },
    ],
}
tags_es166 = ["mueve_zona", "restriccion", "trigger_fin_turno"]
set_card("es166", abilities_es166, tags_es166)

# es167 Misil Magico Foil
abilities_es167 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choice_draw_or_boost",
            "type": "activated",
            "condition": {"phase": "guerra_talismanes"},
            "effect": {
                "type": "choice",
                "choices": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {
                        "type": "modify_force",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "modifier": {"type": "add", "value": 2},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "En guerra de Talismanes, elige robar 2 cartas o dar +2 fuerza a un aliado hasta fin de turno.",
        }
    ],
}
tags_es167 = ["roba_cartas", "modifica_fuerza", "opcional"]
set_card("es167", abilities_es167, tags_es167)

# es168 Corona de Arturo Foil
abilities_es168 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_indestructibles",
            "type": "static",
            "condition": {"controller_allies_at_least": 2},
            "effect": {
                "type": "restriction",
                "restriction": "indestructible",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
            },
            "text": "Mientras controles 2 o más Aliados, los Oros son indestructibles.",
        },
        {
            "id": "exile_from_grave_draw",
            "type": "activated",
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Si está en el cementerio, puedes desterrarla para robar 1 carta.",
        },
    ],
}
tags_es168 = ["indestructible", "exilia_para_pagar", "roba_cartas", "opcional"]
set_card("es168", abilities_es168, tags_es168)

# es169 Cria de Wyrm
abilities_es169 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_cost3_opponent",
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
tags_es169 = ["destierra_objetivo", "trigger_al_entrar", "opcional"]
set_card("es169", abilities_es169, tags_es169)

# es17 Dragon de Magma Legendaria
abilities_es17 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}},
            "text": "Cuando entra en juego, destruye un Aliado oponente.",
        }
    ],
}
tags_es17 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es17", abilities_es17, tags_es17)

# es170 Lohengrin
abilities_es170 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_weapon_on_knight",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}}},
            "condition": {"phase": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia y una vez por turno, si un Caballero entra en juego, puedes buscar un arma y ponerla en tu mano.",
        }
    ],
}
tags_es170 = ["busca_mazo", "opcional", "una_vez_por_turno", "trigger_al_entrar"]
set_card("es170", abilities_es170, tags_es170)


conn.commit()
conn.close()
print("Updated batch: es162-es170")






