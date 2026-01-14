import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("paga_recursos", "Paga recursos", "coste", None),
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


# es117 Principe Valiant
abilities_es117 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable_knights",
            "type": "activated",
            "condition": {"phase": "guerra_de_talismanes"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "value": {"restriction": "unblockable"},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En guerra de Talismanes, puedes destruir Príncipe Valiant para que tus Caballeros sean imbloqueables hasta el final del turno.",
        }
    ],
}
tags_es117 = ["destruye_para_pagar", "imbloqueable", "opcional"]
set_card("es117", abilities_es117, tags_es117)

# es118 Josofones
abilities_es118 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_sir_boores",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "name": "Sir Boores", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando Josofones entra en juego, puedes buscar en tu mazo castillo a Sir Boores y ponerlo en tu mano.",
        },
        {
            "id": "no_draw_end_turn",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "restriction", "restriction": "skip_draw"},
            "text": "Al final del turno, no puedes robar.",
        },
    ],
}
tags_es118 = ["busca_mazo", "opcional", "trigger_fin_turno", "restriccion"]
set_card("es118", abilities_es118, tags_es118)

# es119 el Gran Wyrm
abilities_es119 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_dragons",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "not": {"id": "self"}}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus otros Dragones ganan +1 a la fuerza.",
        },
        {
            "id": "dragons_haste",
            "type": "static",
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "not": {"id": "self"}}},
                "value": {"restriction": "can_attack_on_enter"},
            },
            "text": "Tus otros Dragones pueden atacar cuando entran en juego.",
        },
    ],
}
tags_es119 = ["modifica_fuerza", "apresurado"]
set_card("es119", abilities_es119, tags_es119)

# es12 Bruja Anis Bob
abilities_es12 = {
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
            "text": "En respuesta a finalizar tu turno, si todos tus aliados son Faeries, roba 1 carta extra.",
        }
    ],
}
tags_es12 = ["roba_cartas", "trigger_fin_turno", "response"]
set_card("es12", abilities_es12, tags_es12)

# es120 Basoon
abilities_es120 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_on_dragon_play",
            "type": "triggered",
            "trigger": {
                "type": "card_played",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
            },
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "deck"},
            "text": "Cada vez que juegues un Dragón, tu oponente bota 1 carta.",
        }
    ],
}
tags_es120 = ["bota_cartas", "trigger_juega_carta"]
set_card("es120", abilities_es120, tags_es120)

# es121 Oberon
abilities_es121 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Oberon en juego.",
        },
        {
            "id": "pay_opponent_ally_cost_destroy",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "pay_resources", "amount": {"type": "reference", "reference": "target.cost"}},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu fase de vigilia y una vez por turno, puedes pagar el coste de un Aliado oponente y destruirlo.",
        },
    ],
}
tags_es121 = ["restriccion", "paga_recursos", "destruye_objetivo", "opcional", "una_vez_por_turno"]
set_card("es121", abilities_es121, tags_es121)

# es122 Mago Merlin
abilities_es122 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Mago Merlín en juego.",
        },
        {
            "id": "search_talisman_end",
            "type": "triggered",
            "trigger": {"type": "phase_end", "target": "self"},
            "condition": {
                "type": "count",
                "value": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "self", "cost": {"operator": ">=", "value": 3}},
                },
                "operator": ">=",
                "targetValue": 2,
            },
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talismanes", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En tu Fase Final, si controlas 2 o más Aliados de coste 3 o más, puedes buscar un Talismán y ponerlo en tu Mano.",
        },
    ],
}
tags_es122 = ["restriccion", "busca_mazo", "opcional", "trigger_fin_turno"]
set_card("es122", abilities_es122, tags_es122)

# es123 Mordred
abilities_es123 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_be_blocked",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "must_be_blocked",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "text": "Si Mordred es declarado atacante, debe ser bloqueado por un Aliado oponente a tu elección.",
        }
    ],
}
tags_es123 = ["debe_bloquear", "trigger_al_atacar", "restriccion"]
set_card("es123", abilities_es123, tags_es123)

# es124 Las Tres Hermanas
abilities_es124 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_ally_to_hand",
            "type": "activated",
            "condition": {"phase": "guerra_de_talismanes"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "zone": "play", "controller": "any"}},
                "location": "hand",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En guerra de Talismanes y una vez por turno, puedes pagar 2 de oro para que un aliado en juego vuelva a la mano.",
        }
    ],
}
tags_es124 = ["paga_recursos", "mueve_zona", "opcional", "una_vez_por_turno"]
set_card("es124", abilities_es124, tags_es124)

# es125 Each Usige
abilities_es125 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_grave",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "pay_resources", "amount": {"type": "reference", "reference": "target.cost"}},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes pagar el Coste de Oro de una carta en tu Cementerio para barajarla en tu Mazo Castillo.",
        }
    ],
}
tags_es125 = ["paga_recursos", "baraja", "opcional", "una_vez_por_turno"]
set_card("es125", abilities_es125, tags_es125)

conn.commit()
conn.close()
print("Updated batch: es117-es125")







