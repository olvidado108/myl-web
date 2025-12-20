import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("equipa_armas_extra", "Puede equipar armas extra", "soporte", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("restriccion", "Restricción/regla", "control", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", "Haste"),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("trigger_destruido", "Trigger al ser destruido", "triggers", None),
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


# es270 Sir Gareth
abilities_es270 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "equip_two_weapons",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "equip_extra_weapon", "target": "self"},
            "text": "Puede portar dos armas.",
        }
    ],
}
tags_es270 = ["equipa_armas_extra"]
set_card("es270", abilities_es270, tags_es270)

# es271 Sir Thomas
abilities_es271 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "gain_force_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": 2},
                "duration": "end_turn",
            },
            "text": "Cuando es declarado atacante, gana +2 fuerza hasta fin de turno.",
        }
    ],
}
tags_es271 = ["modifica_fuerza", "trigger_al_atacar"]
set_card("es271", abilities_es271, tags_es271)

# es272 Sir Lucan
abilities_es272 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_copy",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"name": "Sir Lucan", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar otro Sir Lucan y ponerlo en tu mano.",
        }
    ],
}
tags_es272 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es272", abilities_es272, tags_es272)

# es273 Sir Mador del Portal
abilities_es273 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_only_block", "target": "self"},
            "text": "Sólo puede bloquear.",
        },
        {
            "id": "cannot_equip_weapons",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_equip_weapon", "target": "self"},
            "text": "No puede portar armas.",
        },
    ],
}
tags_es273 = ["restriccion"]
set_card("es273", abilities_es273, tags_es273)

# es274 Sir Gaerin, El Blanco
abilities_es274 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_silence_knight",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "any"}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En Vigilia, puedes destruirlo para anular la habilidad de un Caballero hasta fin de turno.",
        }
    ],
}
tags_es274 = ["destruye_para_pagar", "pierde_habilidad", "opcional"]
set_card("es274", abilities_es274, tags_es274)

# es275 Sir Jason de la Sangre
abilities_es275 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter_if_dragon",
            "type": "static",
            "condition": {"type": "has_card_in_play", "filter": {"race": "Dragón", "controller": "self"}},
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Si controlas un Dragón, puede atacar cuando entra.",
        }
    ],
}
tags_es275 = ["apresurado", "restriccion"]
set_card("es275", abilities_es275, tags_es275)

# es276 Duque Thurk Bloodline
abilities_es276 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "requires_two_dragons_to_attack",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"requires_other_attackers": {"race": "Dragón", "count": 2}},
                "target": "self",
            },
            "text": "Sólo puede atacar si designas como atacantes a otros 2 Dragones.",
        }
    ],
}
tags_es276 = ["restriccion"]
set_card("es276", abilities_es276, tags_es276)

# es277 Draco Sangre
abilities_es277 = {
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
tags_es277 = ["apresurado"]
set_card("es277", abilities_es277, tags_es277)

# es278 Atha Uk
abilities_es278 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_exile_grave_card",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "graveyard"}}, "amount": 1},
            "optional": True,
            "text": "En Vigilia, puedes destruirlo para desterrar 1 carta del cementerio oponente.",
        }
    ],
}
tags_es278 = ["destruye_para_pagar", "destierra_objetivo", "opcional"]
set_card("es278", abilities_es278, tags_es278)

# es279 Guerreros del Dragon
abilities_es279 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_if_destroyed",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Si es destruido, debe ser desterrado.",
        }
    ],
}
tags_es279 = ["destierra_objetivo", "trigger_destruido"]
set_card("es279", abilities_es279, tags_es279)


conn.commit()
conn.close()
print("Updated batch: es270-es279")

