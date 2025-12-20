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
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
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


# es333 Luis Ix el Santo
abilities_es333 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Luis IX El Santo puede atacar cuando entra en juego.",
        }
    ],
}
tags_es333 = ["apresurado", "trigger_al_entrar"]
set_card("es333", abilities_es333, tags_es333)

# es334 Leonor de Aquitania
abilities_es334 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Cuando Leonor de Aquitania entra en juego, roba 1 carta.",
        }
    ],
}
tags_es334 = ["roba_cartas", "trigger_al_entrar"]
set_card("es334", abilities_es334, tags_es334)

# es335 Caballeria Pesada
abilities_es335 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_three_mill_six",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "requires": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "name": "Caballería Pesada", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 3,
            },
            "cost": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "name": "Caballería Pesada", "controller": "self", "zone": "play"}},
                "amount": 3,
            },
            "effect": {"type": "discard", "target": "opponent", "amount": 6, "location": "deck"},
            "optional": True,
            "text": "En tu Vigilia, si controlas 3 Caballería Pesada, puedes destruirlas para que tu oponente bote 6 cartas.",
        }
    ],
}
tags_es335 = ["bota_cartas", "destruye_para_pagar", "opcional"]
set_card("es335", abilities_es335, tags_es335)

# es336 Infante
abilities_es336 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_three_infantry",
            "type": "triggered",
            "trigger": {"type": "phase_start", "phase": "vigilia", "target": "controller"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "name": "Infante", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 3,
            },
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "name": "Infante", "controller": "self", "zone": "play"}},
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "Si en tu Fase de Vigilia tienes 3 Infante en juego, ganan +2 a la fuerza hasta el final del turno.",
        }
    ],
}
tags_es336 = ["modifica_fuerza"]
set_card("es336", abilities_es336, tags_es336)

# es337 Tancredo
abilities_es337 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "double_force_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": "self"},
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "multiply", "value": 2}, "duration": "end_turn"},
            "text": "Si Tancredo es declarado atacante, duplica su fuerza.",
        }
    ],
}
tags_es337 = ["modifica_fuerza", "trigger_al_atacar"]
set_card("es337", abilities_es337, tags_es337)

# es338 Alejo
abilities_es338 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable_self",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Alejo se considera imbloqueable.",
        }
    ],
}
tags_es338 = ["imbloqueable", "restriccion"]
set_card("es338", abilities_es338, tags_es338)

# es339 Cimitarra Dorada
abilities_es339 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "El portador de Cimitarra gana +2 a la fuerza cuando ataca.",
        }
    ],
}
tags_es339 = ["modifica_fuerza", "trigger_al_atacar"]
set_card("es339", abilities_es339, tags_es339)

# es34 Capa de Invisibilidad
abilities_es34 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_card",
            "type": "response",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"controller": "opponent", "type": {"operator": "!=", "value": "oros"}}}},
            "effect": {"type": "move_zone", "target": "triggered_card", "location": "deck"},
            "optional": True,
            "text": "Cuando entra en juego una carta oponente que no sea Oro, puedes barajar esa carta en el Mazo Castillo de su dueño.",
        }
    ],
}
tags_es34 = ["baraja", "mueve_zona", "opcional"]
set_card("es34", abilities_es34, tags_es34)

# es340 Aceite Hirviendo
abilities_es340 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_opponent_bearer",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"equip_target_controller": "opponent", "equip_target_type": "allies"}, "target": "self"},
            "text": "Solo la puede portar un aliado oponente.",
        },
        {
            "id": "lose_force_each_turn",
            "type": "triggered",
            "trigger": {"type": "turn_start", "target": "all"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": -2},
                "permanent": True,
            },
            "text": "Cada turno, su portador gana -2 a la fuerza permanentemente.",
        },
    ],
}
tags_es340 = ["restriccion", "modifica_fuerza"]
set_card("es340", abilities_es340, tags_es340)

# es341 Antioquia
abilities_es341 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "limit_allies_per_turn",
            "type": "static",
            "effect": {"type": "modify_rule", "rule": "max_allies_per_turn", "value": 2, "target": "all"},
            "text": "Mientras Antioquia está en juego, los jugadores podrán jugar un máximo de 2 aliados por turno.",
        }
    ],
}
tags_es341 = ["restriccion"]
set_card("es341", abilities_es341, tags_es341)


conn.commit()
conn.close()
print("Updated batch: es333-es341")

