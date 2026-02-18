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
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("descarta_mano", "Descarta de mano", "control", None),
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


# es38 Herrero
abilities_es38 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_weapons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "armas"},
            "optional": True,
            "text": "En tu Fase de Vigilia, puedes pagar 1 oro para generar 2 Oros para jugar Armas.",
        },
        {
            "id": "destroy_if_loses_ability",
            "type": "triggered",
            "trigger": {"type": "lose_ability", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si fuese a perder su habilidad, Herrero es destruido.",
        },
    ],
}
tags_es38 = ["genera_recursos", "paga_recursos", "opcional", "destruye_objetivo", "pierde_habilidad"]
set_card("es38", abilities_es38, tags_es38)

# es380 Vouivre
abilities_es380 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_self_and_opponents",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "amount": 1,
                        "location": "deck",
                        "optional": True,
                    },
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "amount": 2,
                        "location": "deck",
                    },
                ],
            },
            "text": "Cuando entra, puedes barajar un Aliado propio para barajar 2 Aliados oponentes.",
        },
        {
            "id": "tutor_dragon_once_per_turn",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes buscar un Aliado Dragón en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es380 = ["baraja", "mueve_zona", "opcional", "busca_mazo", "una_vez_por_turno", "restriccion"]
set_card("es380", abilities_es380, tags_es380)

# es381 Bola de Fuego
abilities_es381 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_non_gold",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "not": {"type": "oros"}}}},
            "text": "Destruye una carta en juego, que no sea un oro.",
        }
    ],
}
tags_es381 = ["destruye_objetivo"]
set_card("es381", abilities_es381, tags_es381)

# es382 Capa de Invisibilidad
abilities_es382 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_card",
            "type": "response",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"controller": "opponent", "type": {"operator": "!=", "value": "oros"}}}},
            "effect": {"type": "move_zone", "target": "triggered_card", "location": "deck"},
            "optional": True,
            "text": "Cuando entra en juego una carta oponente que no sea Oro, puedes barajar esa carta en el mazo de su dueño.",
        }
    ],
}
tags_es382 = ["baraja", "mueve_zona", "opcional"]
set_card("es382", abilities_es382, tags_es382)

# es383 Dragon Dorado
abilities_es383 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando juegues a Dragón Dorado, destiérralo.",
        },
        {
            "id": "counter_non_gold",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "counter", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "not": {"type": "oros"}}}},
            "text": "Anula una carta que no sea Oro.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es383 = ["anula", "restriccion"]
set_card("es383", abilities_es383, tags_es383)

# es384 Fe Sin Limite
abilities_es384 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_talisman",
            "type": "activated",
            "effect": {"type": "counter", "target": {"type": "filter", "filter": {"type": "talisman"}}},
            "optional": True,
            "text": "Anula un Talismán.",
        }
    ],
}
tags_es384 = ["anula"]
set_card("es384", abilities_es384, tags_es384)

# es385 Espada Larga
abilities_es385 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "text": "Cuando Espada Larga entra en juego, roba dos cartas.",
        },
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador de Espada Larga gana +1 a la fuerza.",
        },
    ],
}
tags_es385 = ["roba_cartas", "modifica_fuerza", "trigger_al_entrar"]
set_card("es385", abilities_es385, tags_es385)

# es386 Guardia Gozosa
abilities_es386 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "silence_and_destroy_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "lose_ability",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "amount": 1,
                    },
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "amount": 1,
                    },
                ],
            },
            "text": "Cuando entra en juego, un Aliado oponente pierde su habilidad y es destruido.",
        },
        {
            "id": "destroy_to_shuffle",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Puedes destruir a Guardia Gozosa para barajar una carta de tu Cementerio en tu mazo.",
        },
    ],
}
tags_es386 = ["pierde_habilidad", "destruye_objetivo", "baraja", "destruye_para_pagar", "opcional"]
set_card("es386", abilities_es386, tags_es386)

# es387 Sir Agravain
abilities_es387 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_then_discard_if_knight",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "play", "not": {"id": "self"}}},
                "operator": ">=",
                "targetValue": 1,
            },
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "draw_cards", "amount": 2, "target": "controller"},
                    {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
                ],
            },
            "text": "Si controlas otro Caballero, al entrar roba 2 cartas y luego descarta 1.",
        }
    ],
}
tags_es387 = ["roba_cartas", "descarta_mano", "trigger_al_entrar"]
set_card("es387", abilities_es387, tags_es387)

# es388 Purificar el Reino
abilities_es388 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "weaken_two_allies",
            "type": "activated",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -1},
                "amount": 2,
                "permanent": True,
            },
            "text": "Elige hasta dos Aliados oponentes para que pierdan 1 a la fuerza permanentemente.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es388 = ["modifica_fuerza", "restriccion"]
set_card("es388", abilities_es388, tags_es388)


conn.commit()
conn.close()
print("Updated batch: es38 y es380-es388")








