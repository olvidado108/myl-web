import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("previene_dano", "Previene daño", "defensivo", None),
    ("descarta_para_pagar", "Descarta para pagar", "coste", None),
    ("bloquea_multiple", "Puede bloquear múltiples", "soporte", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("mira_mazo", "Mira/Reordena mazo", "control", None),
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


# es180 Capitan Imperial
abilities_es180 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "push_to_attack_line",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense_line"}},
                "location": "support_line",
            },
            "text": "Cuando entra, todos los aliados en la Línea de Defensa oponente pasan a la Línea de Ataque.",
        }
    ],
}
tags_es180 = ["mueve_zona", "trigger_al_entrar"]
set_card("es180", abilities_es180, tags_es180)

# es181 Incinerar
abilities_es181 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_own_and_opponent",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 2},
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"controller": "opponent", "type": {"operator": "!=", "value": "oros"}}},
                        "amount": 1,
                    },
                ],
            },
            "text": "Destruye 2 de tus Aliados y una carta oponente. No afecta oros.",
        }
    ],
}
tags_es181 = ["destruye_objetivo"]
set_card("es181", abilities_es181, tags_es181)

# es182 Lady Rachel
abilities_es182 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_destroy_dragon",
            "type": "activated",
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "opponent"}}, "amount": 1},
            "optional": True,
            "text": "Puedes desterrarla para destruir un Dragón oponente.",
        }
    ],
}
tags_es182 = ["exilia_para_pagar", "destruye_objetivo", "opcional"]
set_card("es182", abilities_es182, tags_es182)

# es183 Sir Gabriel
abilities_es183 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_exile",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"controller": "self", "zone": "exile"}}}},
            },
            "text": "Gana +1 a la fuerza por cada carta en tu zona de destierro.",
        }
    ],
}
tags_es183 = ["modifica_fuerza"]
set_card("es183", abilities_es183, tags_es183)

# es184 Isolda
abilities_es184 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "save_knight",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}}},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "prevent_damage", "target": "triggered_card"},
            "optional": True,
            "text": "En respuesta a la destrucción de uno de tus Caballeros, puedes desterrar a Isolda para salvarlo.",
        }
    ],
}
tags_es184 = ["exilia_para_pagar", "previene_dano", "opcional"]
set_card("es184", abilities_es184, tags_es184)

# es185 Lord Fergus Macloud
abilities_es185 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_discard_to_attack",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"must_discard_to_attack": 3}, "target": "self"},
            "text": "Sólo puede atacar si descartas 3.",
        }
    ],
}
tags_es185 = ["restriccion", "descarta_para_pagar"]
set_card("es185", abilities_es185, tags_es185)

# es186 Sir Wesley
abilities_es186 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_equip_weapons",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_equip_weapon", "target": "self"},
            "text": "No puede portar armas.",
        }
    ],
}
tags_es186 = ["restriccion"]
set_card("es186", abilities_es186, tags_es186)

# es187 Sir Badallor
abilities_es187 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "blocks_two_if_equipped",
            "type": "static",
            "condition": {"type": "has_equipment", "equipment_type": "weapon", "target": "self"},
            "effect": {"type": "restriction", "restriction": {"can_block_multiple": 2}, "target": "self"},
            "text": "Si porta un arma, puede bloquear 2 Aliados.",
        }
    ],
}
tags_es187 = ["bloquea_multiple"]
set_card("es187", abilities_es187, tags_es187)

# es188 Loth
abilities_es188 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lock_talismans_if_solo_attacker",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "declared_as": "attacker"}},
                "operator": "==",
                "targetValue": 1,
            },
            "effect": {
                "type": "restriction",
                "restriction": "prevent_talismans",
                "target": {"type": "global"},
                "duration": "end_turn",
            },
            "text": "Si es tu único Aliado atacante, no se pueden jugar Talismanes hasta el final del turno.",
        }
    ],
}
tags_es188 = ["restriccion", "trigger_al_atacar"]
set_card("es188", abilities_es188, tags_es188)

# es189 Sir Baldwin
abilities_es189 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reorder_top_three_on_death",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {"type": "reorder_deck", "target": "controller", "amount": 3},
            "optional": True,
            "text": "Si es destruido, puedes ver las 3 cartas superiores de tu mazo castillo y devolverlas en el orden que quieras.",
        }
    ],
}
tags_es189 = ["mira_mazo", "opcional"]
set_card("es189", abilities_es189, tags_es189)


conn.commit()
conn.close()
print("Updated batch: es180-es189")








