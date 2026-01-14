import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("indestructible", "Indestructible", "defensivo", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("modifica_coste", "Modifica coste", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bloquea_multiple", "Puede bloquear múltiples", "soporte", None),
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


# es243 Caballero Hospitalario
abilities_es243 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_destroy_totem",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "totem", "controller": "opponent"}}, "amount": 1},
            "optional": True,
            "text": "Puedes destruirlo para destruir un Tótem oponente.",
        }
    ],
}
tags_es243 = ["destruye_para_pagar", "destruye_objetivo", "opcional"]
set_card("es243", abilities_es243, tags_es243)

# es244 Caballero Teuton
abilities_es244 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "indestructible_self",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "indestructible", "target": "self"},
            "text": "No puede ser destruido.",
        }
    ],
}
tags_es244 = ["indestructible"]
set_card("es244", abilities_es244, tags_es244)

# es245 Caballero Templario
abilities_es245 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_three_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {
                            "type": "filter",
                            "filter": {"name": "Caballero Templario", "controller": "self", "zone": "graveyard"},
                        },
                        "amount": 3,
                        "location": "defense_line",
                    }
                ],
            },
            "optional": True,
            "text": "En Vigilia, si tienes 3 en cementerio, puedes ponerlos en tu línea de defensa sin pagar su coste.",
        }
    ],
}
tags_es245 = ["pone_en_juego", "opcional"]
set_card("es245", abilities_es245, tags_es245)

# es246 Duque Enrico Dandolo
abilities_es246 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_counter_talisman",
            "type": "response",
            "trigger": {"type": "talisman_cast", "target": "opponent"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "counter", "target": "triggered_spell"},
            "optional": True,
            "text": "En respuesta a que el oponente juegue un Talismán, puedes desterrarlo para anularlo.",
        }
    ],
}
tags_es246 = ["destierra_para_pagar", "anula", "opcional"]
set_card("es246", abilities_es246, tags_es246)

# es247 Basilio Ii Bulgaroktonos
abilities_es247 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_after_attack",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "attacked_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Después de atacar es destruido al final del turno.",
        }
    ],
}
tags_es247 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es247", abilities_es247, tags_es247)

# es248 Sir Beufort
abilities_es248 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "no_gold_if_first_turn",
            "type": "static",
            "condition": {"type": "played_on_first_turn", "target": "self"},
            "effect": {"type": "restriction", "restriction": {"no_gold_generation": True}, "target": {"type": "global"}},
            "text": "Si lo juegas en tu primer turno, no se podrán generar Oros hasta el final del juego.",
        }
    ],
}
tags_es248 = ["restriccion"]
set_card("es248", abilities_es248, tags_es248)

# es249 Sir Vergenio
abilities_es249 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_opponent_deck_to_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "opponent", "location": "deck", "force": {"operator": "<=", "value": 3}},
                },
                "amount": 1,
                "location": "graveyard",
            },
            "text": "Cuando entra, busca en el mazo oponente un aliado de fuerza 3 o menos y mándalo al cementerio.",
        }
    ],
}
tags_es249 = ["mueve_zona", "trigger_al_entrar"]
set_card("es249", abilities_es249, tags_es249)

# es25 Yvain del Leon
abilities_es25 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_weapon_in_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Arma en tu Cementerio y ponerla en tu Mano.",
        },
        {
            "id": "reduce_cost_knight_weapons",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "equip_target_race": "Caballero"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Jugar Armas en tus Caballeros cuesta 1 oro menos.",
        },
    ],
}
tags_es25 = ["busca_mazo", "opcional", "modifica_coste"]
set_card("es25", abilities_es25, tags_es25)

# es250 Hermano Lazarus
abilities_es250 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_draw_two",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "Puedes destruirlo para robar 2 cartas.",
        }
    ],
}
tags_es250 = ["destruye_para_pagar", "roba_cartas", "opcional"]
set_card("es250", abilities_es250, tags_es250)

# es251 Escudo Templario
abilities_es251 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "block_multiple_up_to_force",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"can_block_multiple": {"type": "reference", "reference": "equipped_to_force"}}, "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "El portador puede bloquear a más de un aliado oponente hasta agotar su fuerza.",
        }
    ],
}
tags_es251 = ["bloquea_multiple"]
set_card("es251", abilities_es251, tags_es251)


conn.commit()
conn.close()
print("Updated batch: es243-es251")






