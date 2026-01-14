import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("opcional", "Efecto opcional", "triggers", None),
    ("baraja", "Baraja cartas", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
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


# es153 Favor de la Corte Foil
abilities_es153 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_non_gold",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                "amount": 1,
                "location": "hand",
            },
            "optional": True,
            "text": "Elige una carta oponente y devuélvela a su mano. No afecta oros.",
        }
    ],
}
tags_es153 = ["mueve_zona", "baraja", "opcional"]
set_card("es153", abilities_es153, tags_es153)

# es154 Urisk Foil
abilities_es154 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "both_draw_two",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "draw_cards", "amount": 2, "target": "opponent"},
                ],
            },
            "text": "Cada jugador roba 2 cartas.",
        }
    ],
}
tags_es154 = ["roba_cartas"]
set_card("es154", abilities_es154, tags_es154)

# es155 Totem de Nwyre Foil
abilities_es155 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay1_draw1",
            "type": "activated",
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Paga 1 de oro y roba 1 carta.",
        }
    ],
}
tags_es155 = ["paga_recursos", "roba_cartas"]
set_card("es155", abilities_es155, tags_es155)

# es156 Joyero Foil
abilities_es156 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_oro",
            "type": "activated",
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent", "zone": "play"}},
                "location": "play",
                "controller": "self",
                "duration": "permanent",
            },
            "text": "Un Oro oponente pasa a tu reserva de Oro (hasta el final del juego).",
        }
    ],
}
tags_es156 = ["mueve_zona"]
set_card("es156", abilities_es156, tags_es156)

# es157 Cruzada de Los Niños
abilities_es157 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_two_opponent",
            "type": "activated",
            "condition": {"phase": "main"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "hand", "random": True},
            "text": "En tu Fase de Vigilia, descarta 2 cartas al azar de la mano de tu oponente.",
        }
    ],
}
tags_es157 = ["descarta_mano"]
set_card("es157", abilities_es157, tags_es157)

# es158 Halconero Real Foil
abilities_es158 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_unless_opponent_discards",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "choice",
                "choices": [
                    {"type": "discard", "target": "opponent", "amount": 1, "location": "hand"},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
                "chooser": "opponent",
            },
            "text": "Cuando entra, roba 1 carta, a menos que el oponente descarte 1.",
        }
    ],
}
tags_es158 = ["roba_cartas", "descarta_mano", "trigger_al_entrar"]
set_card("es158", abilities_es158, tags_es158)

# es159 Guardia Real Foil
abilities_es159 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_attack",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "must_attack_each_turn", "target": "self"},
            "text": "Debe atacar en todos tus turnos.",
        },
        {
            "id": "destroy_if_not_attack",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "did_not_attack_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si algún turno no ataca, debe ser destruido.",
        },
    ],
}
tags_es159 = ["restriccion", "destruye_objetivo", "trigger_fin_turno"]
set_card("es159", abilities_es159, tags_es159)

# es16 Rey Arturo Pendragon Legendaria
abilities_es16 = {
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
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus Caballeros ganan +1 a la fuerza.",
        },
        {
            "id": "mill_two_each_grouping",
            "type": "triggered",
            "trigger": {"type": "phase_start", "target": {"type": "reference", "reference": "phase.agrupacion"}},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "text": "Tu oponente bota 2 cartas en cada fase de agrupación.",
        },
        {
            "id": "save_on_destroy",
            "type": "response",
            "trigger": {"type": "destroyed", "target": "self"},
            "cost": {"type": "discard", "amount": 2},
            "effect": {"type": "prevent_damage", "target": "self"},
            "optional": True,
            "text": "En respuesta a ser destruido, puedes descartar 2 para salvarlo.",
        },
    ],
}
tags_es16 = ["restriccion", "modifica_fuerza", "bota_cartas", "opcional", "trigger_fin_turno", "response"]
set_card("es16", abilities_es16, tags_es16)

# es160 Aghast
abilities_es160 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un arma y ponerla en tu mano.",
        }
    ],
}
tags_es160 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es160", abilities_es160, tags_es160)

# es161 Cultistas del Dragon Foil
abilities_es161 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_to_shuffle_opponent_ally",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand"}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "text": "Puedes destruirlo para ver la mano del oponente y barajar un Aliado de su mano en su mazo.",
        }
    ],
}
tags_es161 = ["destruye_para_pagar", "baraja", "opcional", "mueve_zona"]
set_card("es161", abilities_es161, tags_es161)


conn.commit()
conn.close()
print("Updated batch: es153-es161")







