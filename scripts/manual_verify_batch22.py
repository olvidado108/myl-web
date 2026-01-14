import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("baraja", "Baraja cartas", "control", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
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


# es289 Arquero Elfo
abilities_es289 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_if_blocks",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "declared_as_blocker_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si fue bloqueador, destrúyelo al final del turno.",
        }
    ],
}
tags_es289 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es289", abilities_es289, tags_es289)

# es29 Dragon Nube
abilities_es29 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choice_draw_or_mill",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "choice",
                "choices": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra, elige: robas 2 o el oponente bota 2.",
        }
    ],
}
tags_es29 = ["roba_cartas", "bota_cartas", "opcional", "trigger_al_entrar"]
set_card("es29", abilities_es29, tags_es29)

# es290 Ciervo Sagrado
abilities_es290 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_unblockables_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "restriction": "unblockable"}},
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "text": "Al atacar, tus Aliados imbloqueables ganan +1 fuerza hasta fin de turno.",
        }
    ],
}
tags_es290 = ["modifica_fuerza", "trigger_al_atacar"]
set_card("es290", abilities_es290, tags_es290)

# es291 Goblin Conjurador
abilities_es291 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_talisman_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talisman", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, paga 3 oro para buscar un Talismán y ponerlo en tu mano.",
        }
    ],
}
tags_es291 = ["busca_mazo", "paga_recursos", "opcional", "una_vez_por_turno"]
set_card("es291", abilities_es291, tags_es291)

# es292 Armada Elfica
abilities_es292 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_per_copy",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {
                    "type": "add",
                    "value": {"type": "count", "value": {"type": "filter", "filter": {"name": "Armada Elfica", "controller": "self", "zone": "play"}}},
                },
            },
            "text": "Gana +1 fuerza por cada Armada Élfica que controlas.",
        }
    ],
}
tags_es292 = ["modifica_fuerza"]
set_card("es292", abilities_es292, tags_es292)

# es293 Talsoi
abilities_es293 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_and_must_attack_if_armed",
            "type": "static",
            "condition": {"type": "has_equipment", "equipment_type": "weapon", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "modify_force", "target": "self", "modifier": {"type": "add", "value": 1}},
                    {"type": "restriction", "restriction": "must_attack_each_turn", "target": "self"},
                ],
            },
            "text": "Si porta un arma, gana +1 fuerza y debe atacar cada turno.",
        }
    ],
}
tags_es293 = ["modifica_fuerza", "restriccion"]
set_card("es293", abilities_es293, tags_es293)

# es294 Hijas del Caldero
abilities_es294 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_three_for_extra_turn",
            "type": "response",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"name": "Hijas del Caldero", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 3,
            },
            "cost": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"name": "Hijas del Caldero", "controller": "self", "zone": "play"}},
                "amount": 3,
            },
            "effect": {"type": "extra_turn"},
            "optional": True,
            "text": "Si controlas 3, puedes desterrarlas al final de tu turno para ganar un turno extra.",
        }
    ],
}
tags_es294 = ["destierra_para_pagar", "opcional", "trigger_fin_turno"]
set_card("es294", abilities_es294, tags_es294)

# es295 Galeb Duhr
abilities_es295 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_to_save_gold",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": "self",
                        "location": "deck",
                    },
                    {
                        "type": "prevent_damage",
                        "target": "triggered_card",
                    },
                ],
            },
            "optional": True,
            "text": "En respuesta a que destruyan uno de tus oros, puedes barajar a Galeb Duhr en tu mazo para salvarlo.",
        }
    ],
}
tags_es295 = ["baraja", "mueve_zona", "opcional"]
set_card("es295", abilities_es295, tags_es295)

# es296 Otyugh
abilities_es296 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_ally",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 fuerza por cada aliado que controlas.",
        }
    ],
}
tags_es296 = ["modifica_fuerza"]
set_card("es296", abilities_es296, tags_es296)

# es297 Boggart
abilities_es297 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choice_on_death",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {
                "type": "choice",
                "chooser": "opponent",
                "choices": [
                    {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
                    {"type": "discard", "target": "opponent", "amount": 1, "location": "hand"},
                ],
            },
            "text": "Si es destruido, el oponente elige: bota 2 de su mazo o descarta 1 de su mano.",
        }
    ],
}
tags_es297 = ["bota_cartas", "descarta_mano", "trigger_destruido"]
set_card("es297", abilities_es297, tags_es297)


conn.commit()
conn.close()
print("Updated batch: es289-es297 y es29")






