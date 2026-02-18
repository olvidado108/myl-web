import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("pierde_habilidad", "Pierde habilidad", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("baraja", "Baraja cartas", "control", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
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


# es144 Mezquita de Damasco
abilities_es144 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lose_abilities_in_war",
            "type": "static",
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}},
                "condition": {"phase": "guerra_talismanes"},
            },
            "text": "En Guerra de Talismanes, todos los aliados en juego pierden sus habilidades.",
        }
    ],
}
tags_es144 = ["pierde_habilidad", "restriccion"]
set_card("es144", abilities_es144, tags_es144)

# es145 Fantasmas del Desierto
abilities_es145 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_one_no_bonus",
            "type": "activated",
            "condition": {"phase": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "modify_force",
                        "target": {"type": "filter", "filter": {"type": "allies", "zone": "play"}},
                        "modifier": {"type": "set", "value": 1},
                        "duration": "end_turn",
                    },
                    {
                        "type": "restriction",
                        "restriction": "cannot_receive_force_bonus",
                        "target": {"type": "filter", "filter": {"type": "allies", "zone": "play"}},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "En Guerra de Talismanes, todos los aliados en juego tienen fuerza 1 y no pueden recibir bonos de fuerza hasta el final del turno.",
        }
    ],
}
tags_es145 = ["modifica_fuerza", "restriccion", "opcional"]
set_card("es145", abilities_es145, tags_es145)

# es146 Pedro el Ermitaño
abilities_es146 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_immunity_talismans",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "discard", "amount": 1},
            "effect": {
                "type": "immunity",
                "target": "self",
                "source": {"type": "filter", "filter": {"type": "talismanes"}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En tu Fase de Vigilia, puedes descartar 1 carta para que Pedro el Ermitaño no pueda ser afectado por Talismanes hasta el final del turno.",
        }
    ],
}
tags_es146 = ["inmunidad", "descarta_para_pagar", "opcional"]
set_card("es146", abilities_es146, tags_es146)

# es147 la Llama Fria
abilities_es147 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_ally_to_defense",
            "type": "activated",
            "condition": {"phase": "main"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "action": "put_in_play",
                "zone": "defense_line",
            },
            "text": "En tu Fase de Vigilia, busca un aliado en tu Mazo Castillo y ponlo en tu Línea de Defensa.",
        }
    ],
}
tags_es147 = ["busca_mazo", "pone_en_juego", "mueve_zona"]
set_card("es147", abilities_es147, tags_es147)

# es148 Bernardo de Clairvaux
abilities_es148 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_draw_two",
            "type": "activated",
            "condition": {"phase": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "En Guerra de Talismanes puedes desterrar a Bernardo de Clairvaux para robar 2 cartas.",
        }
    ],
}
tags_es148 = ["destierra_para_pagar", "roba_cartas", "opcional"]
set_card("es148", abilities_es148, tags_es148)

# es149 Org, El Hechizero
abilities_es149 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reduce_force_enemy",
            "type": "activated",
            "condition": {"phase": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "set", "value": 0},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En guerra de Talismanes, puedes pagar 2 de oro para que un Aliado oponente tenga fuerza 0 hasta el final del turno.",
        }
    ],
}
tags_es149 = ["paga_recursos", "modifica_fuerza", "restriccion", "opcional"]
set_card("es149", abilities_es149, tags_es149)

# es15 Capa de Invisibilidad Legendaria
abilities_es15 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_card",
            "type": "response",
            "trigger": {
                "type": "card_played",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "not_type": "oros"}},
            },
            "effect": {"type": "shuffle", "target": {"type": "reference", "reference": "trigger.card"}, "location": "deck"},
            "optional": True,
            "text": "Cuando entra en juego una carta oponente que no sea Oro, puedes jugar Capa de Invisibilidad para barajar esa carta en el Mazo Castillo de su dueño.",
        }
    ],
}
tags_es15 = ["baraja", "trigger_juega_carta", "opcional", "mueve_zona"]
set_card("es15", abilities_es15, tags_es15)

# es150 Sir Owen
abilities_es150 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw3_discard2",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "draw_cards", "amount": 3, "target": "controller"},
                    {"type": "discard", "target": "controller", "amount": 2, "location": "hand"},
                ],
            },
            "text": "Cuando Sir Owen entra en juego, roba 3 cartas y descarta 2.",
        }
    ],
}
tags_es150 = ["roba_cartas", "descarta_mano", "trigger_al_entrar"]
set_card("es150", abilities_es150, tags_es150)

# es151 Dragon Nival
abilities_es151 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_force_le_2",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "force": {"operator": "<=", "value": 2}}},
            },
            "text": "Cuando Dragón Nival entra en juego, destruye todos los Aliados de fuerza 2 o menos.",
        }
    ],
}
tags_es151 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es151", abilities_es151, tags_es151)

# es152 Bruja Anis Foil
abilities_es152 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_if_all_faeries",
            "type": "response",
            "trigger": {"type": "turn_end", "target": "self"},
            "condition": {
                "type": "all",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "condition": {"type": "race", "value": "Faerie"},
            },
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "En respuesta a finalizar tu turno, y si todos tus aliados son Faeries, roba 1 carta extra.",
        }
    ],
}
tags_es152 = ["roba_cartas", "trigger_fin_turno", "response"]
set_card("es152", abilities_es152, tags_es152)


conn.commit()
conn.close()
print("Updated batch: es144-es152")









