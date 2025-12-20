import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("restriccion", "Restricción/regla", "control", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("inmunidad", "Inmunidad/anti-objetivo", "defensivo", None),
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


# es433 Flecha Acida
abilities_es433 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_small_and_draw",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "force": {"operator": "<=", "value": 2}}}, "amount": 1},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "text": "Destruye un Aliado oponente de fuerza 2 o menor. Luego roba 1 carta.",
        }
    ],
}
tags_es433 = ["destruye_objetivo", "roba_cartas"]
set_card("es433", abilities_es433, tags_es433)

# es434 Incinerar
abilities_es434 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_two_destroy_non_gold",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "amount": 2},
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "not": {"type": "oros"}}}, "amount": 1},
                ],
            },
            "text": "Destruye 2 de tus Aliados y una carta oponente que no sea Oro.",
        }
    ],
}
tags_es434 = ["destruye_objetivo", "destruye_para_pagar"]
set_card("es434", abilities_es434, tags_es434)

# es435 Favor de la Corte
abilities_es435 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_non_gold",
            "type": "activated",
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "not": {"type": "oros"}}},
                "amount": 1,
                "location": "hand",
            },
            "text": "Elige una carta oponente no Oro y devuélvela a su mano.",
        }
    ],
}
tags_es435 = ["mueve_zona"]
set_card("es435", abilities_es435, tags_es435)

# es436 Urisk
abilities_es436 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "both_draw_two",
            "type": "activated",
            "effect": {"type": "draw_cards", "amount": 2, "target": {"type": "players", "players": "all"}},
            "text": "Cada jugador roba 2 cartas.",
        }
    ],
}
tags_es436 = ["roba_cartas"]
set_card("es436", abilities_es436, tags_es436)

# es437 Traficante de Esclavos
abilities_es437 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_move_opponent_gold",
            "type": "triggered",
            "trigger": {"type": "phase_start", "phase": "agrupacion", "target": "opponent"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "amount": 1},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent", "zone": "reserve"}},
                "location": "paid",
            },
            "text": "Al inicio de la Agrupación oponente, destruye un aliado propio para mover sus oros de reserva a oro pagado.",
        }
    ],
}
tags_es437 = ["destruye_para_pagar", "mueve_zona"]
set_card("es437", abilities_es437, tags_es437)

# es438 Morning Star
abilities_es438 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_and_unblockable",
            "type": "static",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
                    {"type": "restriction", "restriction": "unblockable", "target": {"type": "reference", "reference": "equipped_to"}},
                ],
            },
            "text": "El portador gana +2 fuerza y es imbloqueable.",
        }
    ],
}
tags_es438 = ["modifica_fuerza", "imbloqueable"]
set_card("es438", abilities_es438, tags_es438)

# es439 Hacha de Batalla
abilities_es439 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_bearer",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador gana +2 a la fuerza.",
        },
        {
            "id": "draw_at_turn_end",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": {"type": "reference", "reference": "equipped_to.controller"}},
            "effect": {"type": "draw_cards", "amount": 1, "target": {"type": "reference", "reference": "equipped_to.controller"}},
            "text": "Al final del turno de su controlador, roba 1 carta.",
        },
    ],
}
tags_es439 = ["modifica_fuerza", "roba_cartas"]
set_card("es439", abilities_es439, tags_es439)

# es44 Guardia Gososa
abilities_es44 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "silence_and_destroy_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "lose_ability", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
                ],
            },
            "text": "Cuando entra, un aliado oponente pierde su habilidad y es destruido.",
        },
        {
            "id": "destroy_to_shuffle",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}}, "amount": 1, "location": "deck"},
            "optional": True,
            "text": "Puedes destruirla para barajar 1 carta de tu Cementerio en tu mazo.",
        },
    ],
}
tags_es44 = ["pierde_habilidad", "destruye_objetivo", "baraja", "destruye_para_pagar", "opcional"]
set_card("es44", abilities_es44, tags_es44)

# es440 Maza de Guerra
abilities_es440 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_and_immune_talisman",
            "type": "static",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
                    {"type": "immunity", "target": {"type": "reference", "reference": "equipped_to"}, "value": "talismans"},
                ],
            },
            "text": "El portador gana +2 fuerza y no puede ser afectado por Talismanes.",
        }
    ],
}
tags_es440 = ["modifica_fuerza", "inmunidad"]
set_card("es440", abilities_es440, tags_es440)

# es441 Templo del Desierto
abilities_es441 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "limit_one_attacker",
            "type": "static",
            "effect": {"type": "modify_rule", "rule": "max_attackers_per_turn", "value": 1, "target": "all"},
            "text": "Mientras esté en juego, solo se puede declarar un aliado atacante por turno.",
        }
    ],
}
tags_es441 = ["restriccion"]
set_card("es441", abilities_es441, tags_es441)


conn.commit()
conn.close()
print("Updated batch: es433-es441 y es44")

