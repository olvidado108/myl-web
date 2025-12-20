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
    ("descarta_mano", "Descarta de mano", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("mira_mazo", "Mira/Reordena mazo", "control", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
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


# es342 Gente Escorpion
abilities_es342 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_random_card",
            "type": "activated",
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand", "random": True},
            "text": "Descarta 1 carta de la mano de tu oponente al azar.",
        }
    ],
}
tags_es342 = ["descarta_mano"]
set_card("es342", abilities_es342, tags_es342)

# es343 Espejismo
abilities_es343 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "zero_force_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "set", "value": 0},
                "duration": "end_turn",
            },
            "text": "En guerra de Talismanes, un aliado oponente tiene fuerza 0 hasta el final del turno.",
        }
    ],
}
tags_es343 = ["modifica_fuerza"]
set_card("es343", abilities_es343, tags_es343)

# es344 Grito de Guerra
abilities_es344 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_two",
            "type": "activated",
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "text": "Tu oponente bota 2 cartas de su Mazo Castillo.",
        }
    ],
}
tags_es344 = ["bota_cartas"]
set_card("es344", abilities_es344, tags_es344)

# es345 Cruzada de Los Pobres
abilities_es345 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_small_allies_stop_attack",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "requires": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "force": {"operator": ">", "value": 2}}},
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}},
                    {"type": "restriction", "restriction": {"cannot_attack": True}, "target": "opponent", "duration": "next_turn"},
                ],
            },
            "optional": True,
            "text": "En tu fase de vigilia, si todos tus aliados tienen fuerza 2 o menos, puedes destruirlos; si lo haces, tu oponente no podrá atacar el próximo turno.",
        }
    ],
}
tags_es345 = ["restriccion", "destruye_para_pagar", "opcional"]
set_card("es345", abilities_es345, tags_es345)

# es346 Oro Inicial
abilities_es346 = {"version": "1.0", "abilities": []}
tags_es346 = []
set_card("es346", abilities_es346, tags_es346)

# es347 Fe Sin Limite Secreta
abilities_es347 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_talisman_secret",
            "type": "activated",
            "effect": {"type": "counter", "target": {"type": "filter", "filter": {"type": "talisman"}}},
            "text": "Anula un Talismán.",
        }
    ],
}
tags_es347 = ["anula"]
set_card("es347", abilities_es347, tags_es347)

# es35 Fe Sin Limite
abilities_es35 = {
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
tags_es35 = ["anula"]
set_card("es35", abilities_es35, tags_es35)

# es348 Sir Erec
abilities_es348 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "haste_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Sir Erec puede atacar cuando entra en juego.",
        },
        {
            "id": "shuffle_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "Cuando es declarado atacante, puedes barajar 1 carta o 2 Aliados Caballero de tu Cementerio en tu Mazo Castillo.",
        },
    ],
}
tags_es348 = ["apresurado", "baraja", "mueve_zona", "opcional", "trigger_al_atacar", "trigger_al_entrar"]
set_card("es348", abilities_es348, tags_es348)

# es349 Draigh Goch
abilities_es349 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Draigh Goch en juego.",
        },
        {
            "id": "pay3_destroy_or_silence",
            "type": "activated",
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {
                "type": "choice",
                "options": [
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "not": {"type": "oros"}}},
                    },
                    {
                        "type": "lose_ability",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play"}},
                        "duration": "end_turn",
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, puedes pagar 3 oros para destruir una carta en juego que no sea Oro o para que una carta en juego y sus copias pierdan su habilidad hasta la Fase Final.",
        },
    ],
}
tags_es349 = ["restriccion", "destruye_objetivo", "pierde_habilidad", "paga_recursos", "opcional", "una_vez_por_turno"]
set_card("es349", abilities_es349, tags_es349)

# es350 Tom Thumb
abilities_es350 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_top_three",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "look_deck", "target": "controller", "amount": 3, "reveal": True},
                    {
                        "type": "move_zone",
                        "target": {
                            "type": "filter",
                            "filter": {
                                "type": "cards",
                                "controller": "self",
                                "zone": "deck_top",
                                "any": [{"type": "oros"}, {"type": "allies", "race": "Faerie"}],
                            },
                        },
                        "amount": 1,
                        "location": "hand",
                        "optional": True,
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes mostrar las 3 primeras cartas de tu Mazo Castillo; si alguna es Oro o Aliado Faerie, puedes poner 1 en tu mano. Luego, baraja el resto en tu mazo.",
        }
    ],
}
tags_es350 = ["mira_mazo", "baraja", "busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es350", abilities_es350, tags_es350)


conn.commit()
conn.close()
print("Updated batch: es342-es350 y es35")

