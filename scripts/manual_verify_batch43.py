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
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
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


# es479 Lambton Worm
abilities_es479 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "bottom_if_only_dragons",
            "type": "triggered",
            "trigger": {"type": "deals_combat_damage", "target": "self"},
            "condition": {
                "type": "count",
                "value": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "self", "zone": "play", "race": {"operator": "!=", "value": "Dragón"}},
                },
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
                "position": "bottom",
            },
            "optional": True,
            "text": "Si hace daño de combate y solo controlas Aliados Dragón, puedes poner una carta de tu Cementerio en el fondo de tu Mazo Castillo.",
        },
    ],
}
tags_es479 = ["imbloqueable", "restriccion", "baraja", "mueve_zona", "opcional"]
set_card("es479", abilities_es479, tags_es479)

# es48 Toque de Persival
abilities_es48 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_recent_attacker_or_blocker",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "opponent", "zone": "play", "attacked_or_blocked_this_turn": True},
                },
                "amount": 1,
                "location": "deck",
            },
            "text": "Baraja un Aliado oponente que haya sido declarado atacante o bloqueador este turno.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es48 = ["baraja", "restriccion"]
set_card("es48", abilities_es48, tags_es48)

# es480 Tesoro de Mowa
abilities_es480 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable_target_if_same_race",
            "type": "activated",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "value": {"type": "restriction", "restriction": "unblockable"},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "Si controlas 2 o más Aliados de una misma raza, puedes pagarla para que un Aliado sea imbloqueable hasta la Fase Final.",
        }
    ],
}
tags_es480 = ["imbloqueable", "opcional", "paga_recursos", "restriccion"]
set_card("es480", abilities_es480, tags_es480)

# es481 Morgana
abilities_es481 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener una Morgana en juego.",
        },
        {
            "id": "sacrifice_to_exile",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "amount": 1},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes destruir uno de tus Aliados para desterrar un Aliado oponente.",
        },
    ],
}
tags_es481 = ["restriccion", "destierra_objetivo", "opcional", "una_vez_por_turno", "destruye_para_pagar"]
set_card("es481", abilities_es481, tags_es481)

# es482 Pixie
abilities_es482 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_or_shuffle_if_morgana",
            "type": "activated",
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "phase", "value": "vigilia", "controller": "self"},
                    {"type": "has_card", "card": "Morgana", "controller": "self", "zone": "play"},
                ],
            },
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "draw_cards", "amount": 3, "target": "controller"},
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 2,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "En tu Vigilia, si tienes a Morgana en juego, puedes elegir entre robar 3 cartas o barajar 2 cartas de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es482 = ["roba_cartas", "baraja", "opcional", "restriccion"]
set_card("es482", abilities_es482, tags_es482)

# es483 Bruja Anis
abilities_es483 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_if_all_faeries",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {
                "type": "all",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "condition": {"type": "race", "value": "faerie"},
            },
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "En tu Fase Final, si todos tus Aliados son de raza Faerie, puedes robar 1 carta.",
        }
    ],
}
tags_es483 = ["roba_cartas", "opcional", "restriccion"]
set_card("es483", abilities_es483, tags_es483)

# es484 Greenknight
abilities_es484 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_gold",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 a la fuerza por cada oro que tengas en juego.",
        }
    ],
}
tags_es484 = ["modifica_fuerza"]
set_card("es484", abilities_es484, tags_es484)

# es485 Duphon
abilities_es485 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_graveyard",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, puedes barajar una carta de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es485 = ["baraja", "opcional", "una_vez_por_turno"]
set_card("es485", abilities_es485, tags_es485)

# es486 Alto Druida
abilities_es486 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_only_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_only_block", "target": "self"},
            "text": "Alto Druida solo puede bloquear.",
        }
    ],
}
tags_es486 = ["restriccion"]
set_card("es486", abilities_es486, tags_es486)

# es487 Taliesin
abilities_es487 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Taliesin en juego.",
        },
        {
            "id": "tutor_faerie_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Aliado Faerie en tu Mazo Castillo y jugarlo sin pagar su coste.",
        },
    ],
}
tags_es487 = ["restriccion", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es487", abilities_es487, tags_es487)


conn.commit()
conn.close()
print("Updated batch: es479-es487 y es48")

