import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("descarta_para_pagar", "Descarta para pagar", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("indestructible", "Indestructible", "defensivo", None),
    ("inmunidad", "Inmunidad", "defensivo", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("equipa_armas_extra", "Puede equipar armas extra", "soporte", None),
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


# es261 Lailoken
abilities_es261 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_search_talisman",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "cost": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talisman", "controller": "self", "cost": {"operator": ">=", "value": 3}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes descartar 1 para buscar un Talismán de coste 3+ y ponerlo en tu mano.",
        }
    ],
}
tags_es261 = ["busca_mazo", "descarta_para_pagar", "opcional", "trigger_al_entrar"]
set_card("es261", abilities_es261, tags_es261)

# es262 Bandidos Pictos
abilities_es262 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_shuffle_equal_force",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "==", "value": {"type": "reference", "reference": "self_force"}}},
                },
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Puedes destruirlo para barajar un aliado oponente de igual fuerza en su mazo.",
        }
    ],
}
tags_es262 = ["destruye_para_pagar", "baraja", "mueve_zona", "opcional"]
set_card("es262", abilities_es262, tags_es262)

# es263 Duphon
abilities_es263 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "once_shuffle_from_grave",
            "type": "activated",
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, puedes barajar una carta de tu cementerio en tu mazo.",
        }
    ],
}
tags_es263 = ["baraja", "mueve_zona", "opcional", "una_vez_por_turno"]
set_card("es263", abilities_es263, tags_es263)

# es264 Rhongomiant
abilities_es264 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_equipped",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
        {
            "id": "choice_on_combat_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "choice",
                "choices": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "totem", "controller": "opponent", "zone": "play"}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": 1,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "Si el portador hace daño al mazo oponente, puedes barajar un Tótem oponente o una carta de tu cementerio en tu mazo.",
        },
    ],
}
tags_es264 = ["modifica_fuerza", "baraja", "mueve_zona", "opcional"]
set_card("es264", abilities_es264, tags_es264)

# es265 Kay
abilities_es265 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_have_arturo_to_attack",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"requires_card_in_play": "Rey Arturo Pendragón", "action": "attack"},
                "target": "self",
            },
            "text": "Sólo puede atacar si Rey Arturo Pendragón está en juego.",
        }
    ],
}
tags_es265 = ["restriccion"]
set_card("es265", abilities_es265, tags_es265)

# es266 Piqueros
abilities_es266 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_from_grave_to_play",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "zone", "value": "graveyard", "target": "self"}]},
            "cost": {"type": "pay_resources", "amount": {"type": "reference", "reference": "self_cost"}},
            "effect": {"type": "move_zone", "target": "self", "location": "play"},
            "optional": True,
            "text": "En Vigilia, si está en tu cementerio, puedes pagar su coste para ponerlo en juego.",
        }
    ],
}
tags_es266 = ["paga_recursos", "pone_en_juego", "opcional"]
set_card("es266", abilities_es266, tags_es266)

# es267 Caballeria Ligera
abilities_es267 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "block_two",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"can_block_multiple": 2}, "target": "self"},
            "text": "Puede bloquear a dos Aliados atacantes.",
        }
    ],
}
tags_es267 = ["bloquea_multiple"]
set_card("es267", abilities_es267, tags_es267)

# es268 Comisario
abilities_es268 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_prevent_draw",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "restriction", "restriction": "prevent_draw", "target": "opponent", "duration": "end_turn"},
            "optional": True,
            "text": "En Vigilia, destiérralo para que tu oponente no pueda robar en su turno.",
        }
    ],
}
tags_es268 = ["destierra_para_pagar", "restriccion", "opcional"]
set_card("es268", abilities_es268, tags_es268)

# es269 Campesino
abilities_es269 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_generate_one",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "generate_resources", "amount": 1, "duration": "end_turn"},
            "optional": True,
            "text": "En Vigilia, destrúyelo para generar 1 oro por este turno.",
        }
    ],
}
tags_es269 = ["destruye_para_pagar", "genera_recursos", "opcional"]
set_card("es269", abilities_es269, tags_es269)

# es27 Dragon Demonio
abilities_es27 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_attack_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "restriction", "restriction": "must_attack_this_turn", "target": "self"},
            "text": "Debe atacar cuando entra en juego.",
        },
        {
            "id": "immune_talismans",
            "type": "static",
            "effect": {"type": "immunity", "target": "self", "value": "talismans"},
            "text": "No puede ser afectado por Talismanes.",
        },
        {
            "id": "exile_end_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Al final de este turno, destiérralo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es27 = ["restriccion", "destierra_objetivo", "inmunidad", "trigger_fin_turno", "trigger_al_entrar"]
set_card("es27", abilities_es27, tags_es27)


conn.commit()
conn.close()
print("Updated batch: es261-es269 y es27")








