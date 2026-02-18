import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_al_atacar", "Trigger al atacar", "triggers", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("modifica_raza", "Modifica raza", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
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


# es216 Cuatro Fuertes Vientos
abilities_es216 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_strongest_attacker",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": {"type": "filter", "filter": {"controller": "opponent"}}},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}, "highest_force": True},
            },
            "text": "En respuesta a un ataque, destruye el Aliado oponente de mayor fuerza.",
        }
    ],
}
tags_es216 = ["destruye_objetivo", "trigger_al_atacar"]
set_card("es216", abilities_es216, tags_es216)

# es217 Congelar
abilities_es217 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "silence_attacker",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": {"type": "filter", "filter": {"controller": "opponent"}}},
            "effect": {
                "type": "lose_ability",
                "target": "triggered_card",
                "duration": "end_turn",
            },
            "text": "En respuesta a un ataque, un Aliado oponente pierde su habilidad hasta fin de turno.",
        }
    ],
}
tags_es217 = ["pierde_habilidad", "trigger_al_atacar"]
set_card("es217", abilities_es217, tags_es217)

# es218 Nombrado Caballero
abilities_es218 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "knight_all_allies",
            "type": "activated",
            "effect": {
                "type": "modify_race",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "value": "Caballero",
                "duration": "end_turn",
            },
            "text": "Tus Aliados son Caballeros hasta el final del turno.",
        }
    ],
}
tags_es218 = ["modifica_raza"]
set_card("es218", abilities_es218, tags_es218)

# es219 Estampida
abilities_es219 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_attack_next_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {
                "type": "restriction",
                "restriction": {"must_attack_next_turn": True, "destroy_if_not": True},
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "text": "Un Aliado oponente debe atacar el próximo turno; si no ataca, es destruido.",
        }
    ],
}
tags_es219 = ["restriccion", "destruye_objetivo", "trigger_fin_turno"]
set_card("es219", abilities_es219, tags_es219)

# es22 Sir Bedivere
abilities_es22 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_named_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "hand",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "action": "put_in_play",
                "controller": "self",
                "destination": "defense_line",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu fase de vigilia, una vez por turno, nombra un Aliado; si tu oponente lo tiene en mano, lo bajas a tu línea de defensa bajo tu control sin pagar su coste.",
        }
    ],
}
tags_es22 = ["pone_en_juego", "opcional", "una_vez_por_turno"]
set_card("es22", abilities_es22, tags_es22)

# es220 Cuna de Gusanos
abilities_es220 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_grave_on_death",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": {"type": "reference", "reference": "triggered_card_force"},
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                ],
            },
            "text": "Baraja de tu cementerio a tu mazo tantas cartas como fuerza tenía ese aliado destruido.",
        }
    ],
}
tags_es220 = ["baraja", "mueve_zona"]
set_card("es220", abilities_es220, tags_es220)

# es221 Pergamino Magico
abilities_es221 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_talisman_unless_opponent_mills",
            "type": "activated",
            "effect": {
                "type": "choice",
                "chooser": "opponent",
                "choices": [
                    {"type": "discard", "target": "opponent", "amount": 3, "location": "deck", "result": "counter_this"},
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "talisman", "controller": "self"}},
                        "action": "put_in_hand",
                        "amount": 1,
                    },
                ],
            },
            "text": "Busca un Talismán en tu mazo y ponlo en tu mano, a menos que el oponente bote 3 cartas para anularlo.",
        }
    ],
}
tags_es221 = ["busca_mazo", "bota_cartas"]
set_card("es221", abilities_es221, tags_es221)

# es222 la Piedra de Los Sue
abilities_es222 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_two_weapons",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 2,
            },
            "text": "Busca dos armas en tu mazo castillo y ponlas en tu mano.",
        }
    ],
}
tags_es222 = ["busca_mazo"]
set_card("es222", abilities_es222, tags_es222)

# es223 Justa
abilities_es223 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "trade_equal_force",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "amount": 1,
                        "store": "destroyed_force",
                    },
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "==", "value": {"type": "reference", "reference": "destroyed_force"}}}},
                        "amount": 1,
                    },
                ],
            },
            "text": "Destruye uno de tus Aliados y un oponente de igual fuerza.",
        }
    ],
}
tags_es223 = ["destruye_objetivo"]
set_card("es223", abilities_es223, tags_es223)

# es224 el Juicio de Dios
abilities_es224 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "each_player_sac_two",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                        "amount": 2,
                        "chooser": "controller",
                    },
                    {
                        "type": "destroy",
                        "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                        "amount": 2,
                        "chooser": "opponent",
                    },
                ],
            },
            "text": "Cada jugador destruye 2 de sus cartas en juego a elección. No afecta oros.",
        }
    ],
}
tags_es224 = ["destruye_objetivo"]
set_card("es224", abilities_es224, tags_es224)


conn.commit()
conn.close()
print("Updated batch: es216-es224")








