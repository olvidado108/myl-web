import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("baraja", "Baraja cartas", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("previene_dano", "Previene daño", "defensivo", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
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


# es6 Sir Persival Bob
abilities_es6 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Cuando entra en juego, baraja un Aliado oponente.",
        }
    ],
}
tags_es6 = ["baraja", "trigger_al_entrar"]
set_card("es6", abilities_es6, tags_es6)

# es60 Bola de Fuego
abilities_es60 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_non_gold",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "type": {"operator": "!=", "value": "oros"}}}, "amount": 1},
            "text": "Destruye una carta en juego que no sea Oro.",
        }
    ],
}
tags_es60 = ["destruye_objetivo"]
set_card("es60", abilities_es60, tags_es60)

# es61 Fe Sin Limite
abilities_es61 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_talisman",
            "type": "response",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "talismans"}}},
            "effect": {"type": "counter", "target": "triggered_card"},
            "optional": True,
            "text": "Anula un Talismán.",
        }
    ],
}
tags_es61 = ["anula", "opcional"]
set_card("es61", abilities_es61, tags_es61)

# es62 Dragon Dorado
abilities_es62 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando lo juegues, destiérralo.",
        },
        {
            "id": "counter_non_gold",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "counter", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "type": {"operator": "!=", "value": "oros"}}}},
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
tags_es62 = ["destierra_objetivo", "anula", "restriccion"]
set_card("es62", abilities_es62, tags_es62)

# es63 Capa de Invisibilidad
abilities_es63 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_card",
            "type": "response",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"controller": "opponent", "type": {"operator": "!=", "value": "oros"}}}},
            "effect": {"type": "shuffle", "target": "triggered_card", "location": "deck"},
            "optional": True,
            "text": "Cuando entra una carta oponente que no sea Oro, puedes barajarla en el mazo de su dueño.",
        }
    ],
}
tags_es63 = ["baraja", "opcional"]
set_card("es63", abilities_es63, tags_es63)

# es64 Codex Arturicus
abilities_es64 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "prevent_all_damage",
            "type": "activated",
            "condition": {"type": "phase", "value": "asignacion_dano", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "prevent_damage", "target": {"type": "global"}, "amount": 0},
            "text": "En asignación de daño, destiérralo para reducir todo el daño a 0.",
        },
        {
            "id": "cannot_be_initial_oro",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_be_initial_oro", "target": "self"},
            "text": "No puede ser usado como Oro inicial.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es64 = ["exilia_para_pagar", "previene_dano", "restriccion"]
set_card("es64", abilities_es64, tags_es64)

# es65 Herrero
abilities_es65 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_weapons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "armas"},
            "optional": True,
            "text": "En Vigilia, puedes pagarlo para generar 2 Oros para jugar Armas.",
        },
        {
            "id": "destroy_if_loses_ability",
            "type": "triggered",
            "trigger": {"type": "lose_ability", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si fuese a perder su habilidad, es destruido.",
        },
    ],
}
tags_es65 = ["paga_recursos", "genera_recursos", "opcional", "destruye_objetivo"]
set_card("es65", abilities_es65, tags_es65)

# es66 Sir Robin de Lockesley
abilities_es66 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_defender_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "gain_control",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense_line"}},
                "controller": "self",
                "duration": "end_turn",
            },
            "text": "Cuando entra, un Aliado en la defensa oponente pasa a tu defensa hasta el final del turno.",
        }
    ],
}
tags_es66 = ["mueve_zona", "trigger_al_entrar"]
set_card("es66", abilities_es66, tags_es66)

# es67 Felipe Ii
abilities_es67 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_oro_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Cuando entra, destruye una carta Oro oponente.",
        },
        {
            "id": "destroy_oro_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Cuando sale del juego, destruye una carta Oro oponente.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es67 = ["destruye_objetivo", "restriccion"]
set_card("es67", abilities_es67, tags_es67)

# es68 Saladino
abilities_es68 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
        {
            "id": "generate_two_in_vigilia",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "generate_resources", "amount": 2},
            "text": "En tu Vigilia, genera 2 oros.",
        },
    ],
}
tags_es68 = ["restriccion", "genera_recursos"]
set_card("es68", abilities_es68, tags_es68)


conn.commit()
conn.close()
print("Updated batch: es6 y es60-es68")








