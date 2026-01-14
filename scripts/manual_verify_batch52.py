import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
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


# es56 Dragón Demonio
abilities_es56 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "must_attack_on_enter", "target": "self"},
            "text": "Debe atacar cuando entra en juego.",
        },
        {
            "id": "immune_to_talismans",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"cannot_be_targeted_by": {"type": "talismanes", "controller": "opponent"}}, "target": "self"},
            "text": "No puede ser afectado por Talismanes.",
        },
        {
            "id": "exile_at_end",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Al final de este turno, destiérralo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es56 = ["restriccion", "destierra_objetivo"]
set_card("es56", abilities_es56, tags_es56)

# es560 Lady Calvaur
abilities_es560 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "exile_two_non_gold_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                "amount": 2,
            },
            "optional": True,
            "text": "Cuando entra, puedes desterrar hasta dos cartas oponentes que no sean Oro.",
        },
        {
            "id": "destroy_dragon_to_hand",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "in_zone", "value": "graveyard", "target": "self"}]},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}}, "amount": 1},
            "effect": {"type": "move_zone", "target": "self", "location": "hand"},
            "optional": True,
            "text": "En Vigilia desde el Cementerio, destruye un Dragón propio para regresarla a la mano.",
        },
    ],
}
tags_es560 = ["imbloqueable", "destierra_objetivo", "opcional", "destruye_para_pagar", "mueve_zona", "trigger_al_entrar"]
set_card("es560", abilities_es560, tags_es560)

# es561 Isengrim el Lobo
abilities_es561 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_big_faerie",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "cost": {"operator": ">=", "value": 4}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Aliado Faerie de coste 4 o más y ponerlo en tu mano.",
        },
        {
            "id": "shuffle_three_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 3,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando salga del juego, puedes barajar 3 cartas de tu Cementerio en tu Mazo Castillo.",
        },
    ],
}
tags_es561 = ["busca_mazo", "baraja", "opcional", "trigger_al_entrar"]
set_card("es561", abilities_es561, tags_es561)

# es562 Maldición Lunar
abilities_es562 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_and_discard_ally",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "hand"}}, "amount": 2, "random": True},
                    {
                        "type": "choice",
                        "options": [
                            {"type": "discard", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand", "from_revealed": True}}, "amount": 1, "location": "hand"},
                            {"type": "none"},
                        ],
                        "optional": True,
                    },
                ],
            },
            "text": "Mira hasta 2 cartas al azar de la mano oponente; si hay Aliados, puedes descartar uno y devolver el resto.",
        }
    ],
}
tags_es562 = ["descarta_mano", "opcional"]
set_card("es562", abilities_es562, tags_es562)

# es563 Caceria Infernal
abilities_es563 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_on_ally_removed",
            "type": "response",
            "trigger": {"type": "leaves_play", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "causedBy": "opponent"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "self", "cost": {"operator": "<=", "value": {"type": "reference", "reference": "triggered_card.cost"}}},
                },
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En respuesta a que un Aliado propio salga del juego por efecto oponente, busca un Aliado de igual o menor coste y ponlo en tu mano.",
        }
    ],
}
tags_es563 = ["busca_mazo", "opcional"]
set_card("es563", abilities_es563, tags_es563)

# es564 Tótem del Lobo
abilities_es564 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_top_to_buff",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "exile", "target": {"type": "reference", "reference": "controller.deck_top"}},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "zone": "play"}},
                "modifier": {"type": "add", "value": 1},
                "duration": "permanent",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, destierra la primera carta de tu mazo: un Aliado en juego gana +1 fuerza permanente.",
        }
    ],
}
tags_es564 = ["exilia_para_pagar", "modifica_fuerza", "opcional", "una_vez_por_turno"]
set_card("es564", abilities_es564, tags_es564)

# es565 Vínculo del Aullido
abilities_es565 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_two_gold_draw_then_discard",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "pay_resources", "amount": 2},
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes pagar este y otro Oro para robar 2 cartas; luego descarta 1 carta.",
        }
    ],
}
tags_es565 = ["paga_recursos", "roba_cartas", "descarta_mano", "opcional", "trigger_al_entrar"]
set_card("es565", abilities_es565, tags_es565)

# es57 Dragón de Luz
abilities_es57 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_three_and_cannot_attack",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 3,
                        "location": "deck",
                    },
                    {"type": "restriction", "restriction": "cannot_attack", "target": "self", "duration": "end_turn"},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes barajar 3 cartas de tu Cementerio; si lo haces, no puede ser declarado atacante este turno.",
        }
    ],
}
tags_es57 = ["baraja", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es57", abilities_es57, tags_es57)

# es58 Dragón Nube
abilities_es58 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_or_mill_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes elegir: robar 2 cartas o que el oponente bote 2.",
        }
    ],
}
tags_es58 = ["roba_cartas", "bota_cartas", "opcional", "trigger_al_entrar"]
set_card("es58", abilities_es58, tags_es58)

# es59 Desleal
abilities_es59 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_opponent_ally",
            "type": "activated",
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Destierra un Aliado oponente.",
        }
    ],
}
tags_es59 = ["destierra_objetivo"]
set_card("es59", abilities_es59, tags_es59)


conn.commit()
conn.close()
print("Updated batch: es56, es57-es59 y es560-es565")






