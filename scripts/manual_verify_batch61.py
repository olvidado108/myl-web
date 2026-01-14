import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("baraja", "Baraja cartas", "control", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
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


# hd131 Árbol de Sangre
abilities_hd131 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "all_discard_two",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "all", "amount": 2, "location": "deck"},
            "text": "Cuando entra, todos los jugadores botan 2 cartas de su mazo.",
        },
        {
            "id": "shuffle_one_after",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Luego, baraja 1 carta de tu Cementerio en tu mazo.",
        },
    ],
}
tags_hd131 = ["bota_cartas", "baraja", "trigger_al_entrar"]
set_card("hd131", abilities_hd131, tags_hd131)

# hd132 Kobold
abilities_hd132 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "additional_cost_mill_three",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"play_additional_cost": {"type": "discard", "amount": 3, "target": "controller", "location": "deck"}},
                "target": "self",
            },
            "text": "Para jugarlo debes botar 3 cartas de tu mazo.",
        }
    ],
}
tags_hd132 = ["bota_cartas", "restriccion"]
set_card("hd132", abilities_hd132, tags_hd132)

# hd133 Gruagash
abilities_hd133 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "strip_and_shuffle_all_others",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "lose_ability", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play", "exclude": "self"}}},
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play", "exclude": "self"}},
                        "location": "deck",
                    },
                ],
            },
            "text": "Cuando entra, los demás Aliados pierden su habilidad y son barajados.",
        }
    ],
}
tags_hd133 = ["baraja", "restriccion", "trigger_al_entrar"]
set_card("hd133", abilities_hd133, tags_hd133)

# hd134 Oengus
abilities_hd134 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_to_mill_two_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "optional": True,
            "text": "En Guerra de Talismanes, puedes destruirlo para que el oponente bote 2 cartas.",
        },
        {
            "id": "play_from_graveyard",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "in_zone", "target": "self", "zone": "graveyard"}]},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {"type": "put_in_play", "target": "self", "pay_cost": False},
            "optional": True,
            "text": "En Vigilia, si está en tu Cementerio, paga 2 Oros para jugarlo sin pagar su coste.",
        },
    ],
}
tags_hd134 = ["destruye_para_pagar", "bota_cartas", "paga_recursos", "pone_en_juego", "opcional"]
set_card("hd134", abilities_hd134, tags_hd134)

# hd135 la Serpiente Negra
abilities_hd135 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "indestructible",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "indestructible", "target": "self"},
            "text": "Es indestructible.",
        },
        {
            "id": "shuffle_to_exile_two",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "zone": "hand", "controller": "self"}}, "amount": 1, "location": "deck"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "zone": "deck", "controller": "opponent"}}, "amount": 2},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, baraja 1 carta de tu mano para desterrar 2 cartas del mazo oponente.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd135 = ["restriccion", "baraja", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("hd135", abilities_hd135, tags_hd135)

# hd136 Wyrm Abismal
abilities_hd136 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "opponent_sac_on_shadow_death",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self"}}},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
            },
            "text": "En respuesta a destruirse un Sombra propio, el oponente destruye uno de sus Aliados.",
        }
    ],
}
tags_hd136 = ["destruye_objetivo"]
set_card("hd136", abilities_hd136, tags_hd136)

# hd137 Conand
abilities_hd137 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_totem_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "self", "cost": {"operator": "<=", "value": 2}}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Al entrar, puedes buscar un Tótem de coste 2 o menos y jugarlo sin pagar su coste.",
        }
    ],
}
tags_hd137 = ["busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("hd137", abilities_hd137, tags_hd137)

# hd138 Horda Fomore
abilities_hd138 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_shadow_to_hand",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "zone": "graveyard", "controller": "self"}}, "amount": 1},
            "effect": {"type": "move_zone", "target": "self", "location": "hand"},
            "optional": True,
            "oncePerTurn": True,
            "text": "Si está en tu Cementerio, destierra un Aliado Sombra de tu Cementerio para ponerlo en tu mano (1 vez por turno).",
        }
    ],
}
tags_hd138 = ["exilia_para_pagar", "mueve_zona", "opcional", "una_vez_por_turno"]
set_card("hd138", abilities_hd138, tags_hd138)

# hd139 Caoranach
abilities_hd139 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_shadow_to_shuffle",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self", "exclude": "self"}}, "amount": 1},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, destruye otro Sombra propio para barajar 2 cartas de tu Cementerio.",
        },
        {
            "id": "play_from_grave",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "in_zone", "target": "self", "zone": "graveyard"}]},
            "cost": {"type": "pay_resources", "amount": 4},
            "effect": {"type": "put_in_play", "target": "self", "controller": "self", "pay_cost": False},
            "optional": True,
            "text": "Si está en tu Cementerio, en Vigilia puedes pagar 4 Oros para jugarlo sin pagar su coste.",
        },
    ],
}
tags_hd139 = ["destruye_para_pagar", "baraja", "opcional", "una_vez_por_turno", "paga_recursos", "pone_en_juego"]
set_card("hd139", abilities_hd139, tags_hd139)

# hd14 Aplastar Fomor
abilities_hd14 = {
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
            "id": "destroy_ally_and_copies",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}}, "destroyCopies": True},
            "text": "Destruye un Aliado y todas sus copias en juego.",
        },
    ],
}
tags_hd14 = ["destierra_objetivo", "destruye_objetivo"]
set_card("hd14", abilities_hd14, tags_hd14)


conn.commit()
conn.close()
print("Updated batch: hd131-hd139 y hd14")






