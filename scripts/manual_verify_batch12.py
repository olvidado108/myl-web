import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("bota_cartas", "Muele mazo oponente", "control", "Descarta desde mazo del oponente"),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("indestructible", "Indestructible", "defensivo", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("trigger_destruido", "Trigger al ser destruido", "triggers", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
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


# es199 Monta Dragones
abilities_es199 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_on_death_by_force",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": {"type": "reference", "reference": "self_force"},
                "location": "deck",
            },
            "text": "Si es destruido, el oponente bota tantas cartas como fuerza tenga.",
        }
    ],
}
tags_es199 = ["bota_cartas", "trigger_destruido"]
set_card("es199", abilities_es199, tags_es199)

# es2 Fe Sin Limite Bob
abilities_es2 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_talisman",
            "type": "activated",
            "effect": {"type": "counter", "target": {"type": "filter", "filter": {"type": "talisman"}}},
            "text": "Anula un Talismán.",
        }
    ],
}
tags_es2 = ["anula"]
set_card("es2", abilities_es2, tags_es2)

# es20 Corona de Arturo Legendaria
abilities_es20 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_indestructibles",
            "type": "static",
            "condition": {"controller_allies_at_least": 2},
            "effect": {
                "type": "restriction",
                "restriction": "indestructible",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
            },
            "text": "Mientras controles 2 o más Aliados, los Oros son indestructibles.",
        },
        {
            "id": "exile_from_grave_draw",
            "type": "activated",
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Si está en tu cementerio, puedes desterrarla para robar 1 carta.",
        },
    ],
}
tags_es20 = ["indestructible", "exilia_para_pagar", "roba_cartas", "opcional"]
set_card("es20", abilities_es20, tags_es20)

# es200 Wyvern
abilities_es200 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_destroyer",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "reference", "reference": "destroying_card"}},
            "text": "La carta que lo destruya debe ser desterrada.",
        }
    ],
}
tags_es200 = ["destierra_objetivo", "trigger_destruido"]
set_card("es200", abilities_es200, tags_es200)

# es201 Draco Esmeralda
abilities_es201 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_faerie",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Faerie en tu mazo castillo y ponerlo en tu mano.",
        }
    ],
}
tags_es201 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es201", abilities_es201, tags_es201)

# es202 Serpentino
abilities_es202 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "debuff_opponent_allies",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En guerra de Talismanes, puedes pagar 1 oro para que un Aliado oponente tenga -1 fuerza hasta fin de turno.",
        }
    ],
}
tags_es202 = ["paga_recursos", "modifica_fuerza", "opcional"]
set_card("es202", abilities_es202, tags_es202)

# es203 Mulvan, El Dragón
abilities_es203 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "double_force_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "multiply", "value": 2},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En guerra de Talismanes, puede duplicar su fuerza.",
        },
        {
            "id": "exile_at_end",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Al final de este turno, destiérralo.",
        },
    ],
}
tags_es203 = ["modifica_fuerza", "destierra_objetivo", "trigger_fin_turno", "opcional"]
set_card("es203", abilities_es203, tags_es203)

# es204 Lord Elfo
abilities_es204 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_faerie",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 a la fuerza por cada Faerie que tengas en juego.",
        }
    ],
}
tags_es204 = ["modifica_fuerza"]
set_card("es204", abilities_es204, tags_es204)

# es205 Lady Shee Dia
abilities_es205 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_sir_galahad",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"name": "Sir Galahad", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar a Sir Galahad en tu mazo castillo y ponerlo en tu mano.",
        }
    ],
}
tags_es205 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es205", abilities_es205, tags_es205)

# es206 Greenknight
abilities_es206 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_gold",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "oros", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 a la fuerza por cada oro que tengas en juego.",
        }
    ],
}
tags_es206 = ["modifica_fuerza"]
set_card("es206", abilities_es206, tags_es206)


conn.commit()
conn.close()
print("Updated batch: es199, es2, es20, es200-es206")






