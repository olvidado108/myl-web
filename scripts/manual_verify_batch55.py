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
    ("paga_recursos", "Paga recursos", "coste", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
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


# es78 Ricardo Corazon de Leon
abilities_es78 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_hand_card_to_name_restrict",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "hand"}}, "amount": 1},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "hand"}}},
                    {
                        "type": "restriction",
                        "restriction": "cannot_play_named_card_next_turn",
                        "target": {"type": "reference", "reference": "named_card"},
                        "duration": "next_turn",
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, destierra una carta de tu mano: mira la mano oponente y nombra una carta que no podrá ser jugada en su próximo turno.",
        }
    ],
}
tags_es78 = ["exilia_para_pagar", "restriccion", "opcional", "una_vez_por_turno"]
set_card("es78", abilities_es78, tags_es78)

# es79 Dragón de Eter
abilities_es79 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "debuff_opponents_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "text": "Cuando sea declarado atacante, los Aliados oponentes pierden 1 a la fuerza hasta fin de turno.",
        }
    ],
}
tags_es79 = ["modifica_fuerza"]
set_card("es79", abilities_es79, tags_es79)

# es8 Guerrero de la Libertad Bob
abilities_es8 = {
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
            "text": "Los Aliados que bajes este turno cuestan 1 Oro menos.",
        }
    ],
}
tags_es8 = ["modifica_coste", "trigger_al_entrar"]
set_card("es8", abilities_es8, tags_es8)

# es80 Dragón de Aire
abilities_es80 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        }
    ],
}
tags_es80 = ["apresurado"]
set_card("es80", abilities_es80, tags_es80)

# es81 Dragón del Agua
abilities_es81 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "protect_dragons_from_talismans",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": {"cannot_be_targeted_by": {"type": "talismanes", "controller": "opponent"}},
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                "duration": "end_turn",
            },
            "text": "Cuando entra, los Dragones propios no pueden ser afectados por Talismanes hasta fin de turno.",
        }
    ],
}
tags_es81 = ["restriccion", "trigger_al_entrar"]
set_card("es81", abilities_es81, tags_es81)

# es82 Dragón de Plata
abilities_es82 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_one_draw",
            "type": "activated",
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Paga 1 Oro: roba 1 carta.",
        },
        {
            "id": "pay_two_discard_random",
            "type": "activated",
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand", "random": True},
            "optional": True,
            "text": "Paga 2 Oros: descarta 1 carta al azar de la mano oponente.",
        },
        {
            "id": "pay_three_mill_two",
            "type": "activated",
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "optional": True,
            "text": "Paga 3 Oros: tu oponente bota 2 cartas.",
        },
    ],
}
tags_es82 = ["paga_recursos", "roba_cartas", "descarta_mano", "bota_cartas", "opcional"]
set_card("es82", abilities_es82, tags_es82)

# es83 Dragón Cobrizo
abilities_es83 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_dragons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": {"type": "filter", "filter": {"type": "allies", "race": "Dragón"}}},
            "optional": True,
            "text": "En Vigilia, genera 2 oros para bajar Dragones.",
        }
    ],
}
tags_es83 = ["genera_recursos", "opcional"]
set_card("es83", abilities_es83, tags_es83)

# es84 Dragón de Bronce
abilities_es84 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_be_blocked",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "must_block",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "end_turn",
            },
            "text": "Cuando sea declarado atacante, debe ser bloqueado por un Aliado oponente a tu elección.",
        }
    ],
}
tags_es84 = ["restriccion"]
set_card("es84", abilities_es84, tags_es84)

# es85 Kernuac el Cazador
abilities_es85 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_to_exile_two_from_opponent_deck",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "deck"}},
                "amount": 2,
            },
            "optional": True,
            "text": "En Vigilia, puedes destruirlo para buscar 2 cartas del mazo oponente y desterrarlas.",
        }
    ],
}
tags_es85 = ["destruye_para_pagar", "destierra_objetivo", "opcional"]
set_card("es85", abilities_es85, tags_es85)

# es86 el Poeta
abilities_es86 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "name_card_to_lock",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "cannot_play_named_card",
                "target": {"type": "global"},
                "duration": "while_source_in_play",
            },
            "text": "Cuando entra, nombra una carta; no puede ser jugada mientras El Poeta esté en juego.",
        }
    ],
}
tags_es86 = ["restriccion"]
set_card("es86", abilities_es86, tags_es86)


conn.commit()
conn.close()
print("Updated batch: es78-es86")






