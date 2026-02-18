import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("baraja", "Baraja cartas", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("mira_mazo", "Mira/Reordena mazo", "control", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("bloquea_multiple", "Puede bloquear múltiples", "soporte", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("copia_habilidad", "Copia habilidad/efecto", "soporte", None),
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


# es324 Argusthat
abilities_es324 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay2_shuffle_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, paga 2 oro para barajar un Aliado de tu cementerio en tu mazo.",
        }
    ],
}
tags_es324 = ["paga_recursos", "baraja", "mueve_zona", "opcional", "una_vez_por_turno"]
set_card("es324", abilities_es324, tags_es324)

# es325 Totem del Alba
abilities_es325 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_when_totem_played",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "totem", "controller": "self"}}},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "deck"},
            "text": "Cada vez que bajas un Tótem, el oponente bota 1 carta.",
        }
    ],
}
tags_es325 = ["bota_cartas"]
set_card("es325", abilities_es325, tags_es325)

# es326 Caballo de Batalla
abilities_es326 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_be_knight",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"equip_target_race": "Caballero"}, "target": "self"},
            "text": "Su portador debe ser un Caballero.",
        },
        {
            "id": "scry_four_if_not_attack",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "did_not_attack_this_turn", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "look_deck",
                "target": "controller",
                "amount": 4,
                "reorder": True,
            },
            "optional": True,
            "text": "Si no fue declarado atacante, mira y ordena las 4 superiores de tu mazo.",
        },
    ],
}
tags_es326 = ["restriccion", "mira_mazo", "opcional"]
set_card("es326", abilities_es326, tags_es326)

# es327 Caballo Ligero
abilities_es327 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable_bearer",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "Su portador es imbloqueable.",
        }
    ],
}
tags_es327 = ["imbloqueable"]
set_card("es327", abilities_es327, tags_es327)

# es328 Dardos Envenenados
abilities_es328 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "self_nerf",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": -1},
                "permanent": True,
            },
            "text": "En Vigilia, su portador gana -1 a la fuerza permanente.",
        }
    ],
}
tags_es328 = ["modifica_fuerza"]
set_card("es328", abilities_es328, tags_es328)

# es329 Catapulta
abilities_es329 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_blocker_on_block",
            "type": "triggered",
            "trigger": {"type": "declared_blocker", "target": "opponent"},
            "condition": {"type": "was_blocked_this_turn", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand"},
            "text": "Si su portador es bloqueado, el oponente descarta 1 carta.",
        }
    ],
}
tags_es329 = ["descarta_mano"]
set_card("es329", abilities_es329, tags_es329)

# es33 Nimue
abilities_es33 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "copy_faerie_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "gain_ability",
                "target": "self",
                "value": {"type": "copy_from_graveyard", "race": "Faerie"},
                "duration": "end_turn",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puede convertirse en copia de un Faerie de tu cementerio hasta la Fase Final.",
        }
    ],
}
tags_es33 = ["copia_habilidad", "opcional", "una_vez_por_turno"]
set_card("es33", abilities_es33, tags_es33)

# es330 Espada Corta
abilities_es330 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_and_extra_weapon",
            "type": "static",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
                    {"type": "restriction", "restriction": "equip_extra_weapon", "target": {"type": "reference", "reference": "equipped_to"}},
                ],
            },
            "text": "Portador gana +1 fuerza y puede portar otra arma.",
        }
    ],
}
tags_es330 = ["modifica_fuerza", "equipa_armas_extra"]
set_card("es330", abilities_es330, tags_es330)

# es331 Alabarda
abilities_es331 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_buff_permanent",
            "type": "activated",
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
                "permanent": True,
            },
            "optional": True,
            "text": "Destierra Alabarda: el portador gana +2 fuerza permanente.",
        }
    ],
}
tags_es331 = ["destierra_para_pagar", "modifica_fuerza", "opcional"]
set_card("es331", abilities_es331, tags_es331)

# es332 Conrado Iii
abilities_es332 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_attack",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_attack", "target": "self"},
            "text": "No puede atacar.",
        },
        {
            "id": "block_two_double_force",
            "type": "triggered",
            "trigger": {"type": "declared_blocker", "target": "self"},
            "condition": {"type": "count_blocking", "target": "self", "operator": ">=", "value": 2},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "multiply", "value": 2},
                "duration": "end_turn",
            },
            "text": "Puede bloquear 2; si lo hace, duplica su fuerza hasta fin de turno.",
        },
    ],
}
tags_es332 = ["restriccion", "bloquea_multiple", "modifica_fuerza"]
set_card("es332", abilities_es332, tags_es332)

# es333 (placeholder for next card after Alabarda?)

conn.commit()
conn.close()
print("Updated batch: es324-es332 y es33")








