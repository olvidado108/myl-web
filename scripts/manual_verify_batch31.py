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
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("descarta_mano", "Descarta de mano", "control", None),
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


# es370 Rey Arturo Pendragon
abilities_es370 = {
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
tags_es370 = ["restriccion", "modifica_fuerza", "bota_cartas", "opcional", "descarta_mano"]
set_card("es370", abilities_es370, tags_es370)

# es371 Sir Bedivere
abilities_es371 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_named_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand"}},
                "location": "defense",
                "controller": "self",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia, una vez por turno, puedes nombrar un Aliado; si el oponente lo tiene en mano, lo pones en tu defensa sin pagar su coste.",
        }
    ],
}
tags_es371 = ["mueve_zona", "pone_en_juego", "opcional", "una_vez_por_turno"]
set_card("es371", abilities_es371, tags_es371)

# es372 Guerrero de la Libertad
abilities_es372 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reduce_cost_this_turn",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "text": "Este turno, los Aliados que bajes cuestan 1 Oro menos.",
        }
    ],
}
tags_es372 = ["modifica_coste", "trigger_al_entrar"]
set_card("es372", abilities_es372, tags_es372)

# es373 Sir Lamorak
abilities_es373 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_gold_from_deck",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_play",
            },
            "text": "Cuando entra en juego, juega una carta de Oro desde tu mazo.",
        },
        {
            "id": "draw_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "Cuando salga del juego, puedes robar hasta 2 cartas.",
        },
    ],
}
tags_es373 = ["busca_mazo", "pone_en_juego", "roba_cartas", "opcional", "trigger_al_entrar"]
set_card("es373", abilities_es373, tags_es373)

# es374 Carwennan
abilities_es374 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_silence",
            "type": "activated",
            "condition": {"type": "zone", "value": "oro_reserva", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "not": {"type": "oros"}}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "Si está en tu Reserva de Oro, puedes desterrarlo para que una carta oponente no Oro pierda su habilidad hasta la Fase Final.",
        }
    ],
}
tags_es374 = ["destierra_para_pagar", "pierde_habilidad", "opcional"]
set_card("es374", abilities_es374, tags_es374)

# es375 Milano Rojo
abilities_es375 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_shuffle",
            "type": "activated",
            "condition": {"type": "zone", "value": "oro_reserva", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "optional": True,
            "text": "Si Milano Rojo está en tu Reserva de Oro, puedes desterrarlo para barajar dos cartas de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es375 = ["destierra_para_pagar", "baraja", "opcional"]
set_card("es375", abilities_es375, tags_es375)

# es376 Tom Thumb
abilities_es376 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_top_three",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "look_deck", "target": "controller", "amount": 3, "reveal": True},
                    {
                        "type": "move_zone",
                        "target": {
                            "type": "filter",
                            "filter": {
                                "type": "cards",
                                "controller": "self",
                                "zone": "deck_top",
                                "any": [{"type": "oros"}, {"type": "allies", "race": "Faerie"}],
                            },
                        },
                        "amount": 1,
                        "location": "hand",
                        "optional": True,
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes mostrar las 3 primeras cartas de tu mazo; si alguna es Oro o Aliado Faerie, puedes poner 1 en tu mano. Luego, baraja el resto en tu mazo.",
        }
    ],
}
tags_es376 = ["mira_mazo", "baraja", "busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es376", abilities_es376, tags_es376)

# es377 Yvain de Leon
abilities_es377 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Arma en tu Cementerio y ponerla en tu mano.",
        },
        {
            "id": "cheaper_knight_weapons",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "equip_target_race": "Caballero"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Jugar Armas en tus Caballeros cuesta 1 Oro menos.",
        },
    ],
}
tags_es377 = ["busca_mazo", "mueve_zona", "opcional", "modifica_coste"]
set_card("es377", abilities_es377, tags_es377)

# es378 Dragon Nube
abilities_es378 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choose_draw_or_mill",
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
            "text": "Cuando entra en juego, puedes elegir: robar 2 cartas o que el oponente bote 2.",
        }
    ],
}
tags_es378 = ["roba_cartas", "bota_cartas", "opcional", "trigger_al_entrar"]
set_card("es378", abilities_es378, tags_es378)

# es379 Sir Persival
abilities_es379 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1, "location": "deck"},
            "text": "Cuando Sir Pérsival entra en juego, baraja un aliado oponente.",
        }
    ],
}
tags_es379 = ["baraja", "mueve_zona", "trigger_al_entrar"]
set_card("es379", abilities_es379, tags_es379)


conn.commit()
conn.close()
print("Updated batch: es370-es379")

