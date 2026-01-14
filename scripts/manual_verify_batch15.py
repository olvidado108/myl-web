import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("baraja", "Baraja cartas", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
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


# es225 Knockers
abilities_es225 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_equipped_ally",
            "type": "activated",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "has_equipment": True}},
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "Un Aliado con arma gana +2 a la fuerza hasta el final del turno.",
        }
    ],
}
tags_es225 = ["modifica_fuerza"]
set_card("es225", abilities_es225, tags_es225)

# es226 Brownie
abilities_es226 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_two_then_opponent_draws",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "discard", "target": "opponent", "amount": 2, "location": "hand", "random": True},
                    {"type": "draw_cards", "amount": 1, "target": "opponent"},
                ],
            },
            "text": "Descarta 2 al azar de tu oponente. Luego, tu oponente roba 1 carta.",
        }
    ],
}
tags_es226 = ["descarta_mano"]
set_card("es226", abilities_es226, tags_es226)

# es227 Legado del Bosque
abilities_es227 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "each_shuffle_two_then_draw",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                    {"type": "shuffle", "target": "opponent", "location": "deck"},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                    {"type": "draw_cards", "amount": 1, "target": "opponent"},
                ],
            },
            "text": "Cada jugador baraja 2 de su cementerio en su mazo y luego roba 1 carta.",
        }
    ],
}
tags_es227 = ["baraja", "roba_cartas", "mueve_zona"]
set_card("es227", abilities_es227, tags_es227)

# es228 Producir Terremoto
abilities_es228 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "each_player_mill_three_uncounterable",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "discard", "target": "controller", "amount": 3, "location": "deck"},
                    {"type": "discard", "target": "opponent", "amount": 3, "location": "deck"},
                ],
            },
            "uncounterable": True,
            "text": "Cada jugador bota 3 cartas. No puede ser anulado.",
        }
    ],
}
tags_es228 = ["bota_cartas", "anula"]
set_card("es228", abilities_es228, tags_es228)

# es229 Totem del Errante
abilities_es229 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_top_card_opponent",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "deck", "position": "top"}}, "amount": 1},
            "optional": True,
            "text": "En tu Vigilia, paga 2 oro para desterrar la carta superior del mazo oponente.",
        }
    ],
}
tags_es229 = ["destierra_objetivo", "paga_recursos", "opcional"]
set_card("es229", abilities_es229, tags_es229)

# es23 Sir Persival
abilities_es23 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_ally",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Cuando entra en juego, baraja un aliado oponente.",
        }
    ],
}
tags_es23 = ["baraja", "mueve_zona", "trigger_al_entrar"]
set_card("es23", abilities_es23, tags_es23)

# es230 Totem Goblin
abilities_es230 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_three_opponent",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {"type": "discard", "target": "opponent", "amount": 3, "location": "deck"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia y una vez por turno, paga 3 oro para que tu oponente bote 3 cartas.",
        }
    ],
}
tags_es230 = ["bota_cartas", "paga_recursos", "opcional", "una_vez_por_turno"]
set_card("es230", abilities_es230, tags_es230)

# es231 Totem de Cristal
abilities_es231 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_talisman_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "talisman", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia y una vez por turno, paga 3 oro para barajar un Talismán de tu cementerio en tu mazo.",
        }
    ],
}
tags_es231 = ["baraja", "mueve_zona", "paga_recursos", "opcional", "una_vez_por_turno"]
set_card("es231", abilities_es231, tags_es231)

# es232 Totem Alquimico
abilities_es232 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_to_generate_equal_force",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "generate_resources", "amount": {"type": "reference", "reference": "sacrificed_force"}},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes destruir un Aliado propio para generar oro igual a su fuerza.",
        }
    ],
}
tags_es232 = ["genera_recursos", "destruye_objetivo", "opcional", "una_vez_por_turno"]
set_card("es232", abilities_es232, tags_es232)

# es233 Oldhage
abilities_es233 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_totem",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {
                "type": "group",
                "costs": [
                    {"type": "pay_resources", "amount": 2},
                    {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
                ],
            },
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "totem", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En Vigilia, paga 2 oro y descarta 1 carta para buscar un Tótem y ponerlo en tu mano.",
        }
    ],
}
tags_es233 = ["paga_recursos", "descarta_mano", "busca_mazo", "opcional"]
set_card("es233", abilities_es233, tags_es233)


conn.commit()
conn.close()
print("Updated batch: es225-es233")






