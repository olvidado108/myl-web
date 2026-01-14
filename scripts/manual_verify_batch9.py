import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("restriccion", "Restricción/regla", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("baraja", "Baraja cartas", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("inmunidad", "Inmunidad", "defensivo", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
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


# es171 Rey Pescador
abilities_es171 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_for_weapons",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "draw_cards",
                "amount": {
                    "type": "count",
                    "value": {"type": "filter", "filter": {"type": "armas", "controller": "self", "zone": "play"}},
                },
                "target": "controller",
            },
            "text": "Cuando entra en juego, roba tantas cartas como Armas controles.",
        }
    ],
}
tags_es171 = ["roba_cartas", "trigger_al_entrar"]
set_card("es171", abilities_es171, tags_es171)

# es172 Draco Conjurador
abilities_es172 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_gold_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Oro normal en tu mazo castillo y ponerlo en tu mano.",
        }
    ],
}
tags_es172 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es172", abilities_es172, tags_es172)

# es173 Faeries
abilities_es173 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Faeries en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Sólo puede ser jugado desde tu mano.",
        },
        {
            "id": "buff_faeries_from_reserve",
            "type": "static",
            "condition": {"zone": "oros", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "allies",
                        "race": "Faerie",
                        "controller": "self",
                        "zone": "defense",
                        "cost": {"operator": "<=", "value": 3},
                    },
                },
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en tu Reserva de Oro, tus Aliados Faerie de coste 3 o menos en Línea de Defensa ganan +1 a la fuerza.",
        },
    ],
}
tags_es173 = ["restriccion", "modifica_fuerza"]
set_card("es173", abilities_es173, tags_es173)

# es174 Llewelyn, voz de plata
abilities_es174 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_opponent_ally",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
                "location": "hand",
            },
            "text": "Cuando entra en juego, elige un Aliado oponente y súbelo a su mano.",
        }
    ],
}
tags_es174 = ["mueve_zona", "trigger_al_entrar"]
set_card("es174", abilities_es174, tags_es174)

# es175 Flecha Acida
abilities_es175 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_and_draw",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "destroy",
                        "target": {
                            "type": "filter",
                            "filter": {"type": "allies", "controller": "opponent", "zone": "play", "force": {"operator": "<=", "value": 2}},
                        },
                        "amount": 1,
                    },
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "text": "Destruye un Aliado oponente de fuerza 2 o menor. Luego roba 1 carta.",
        }
    ],
}
tags_es175 = ["destruye_objetivo", "roba_cartas"]
set_card("es175", abilities_es175, tags_es175)

# es176 Pixie
abilities_es176 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choice_draw_or_recover",
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
                "choices": [
                    {"type": "draw_cards", "amount": 3, "target": "controller"},
                    {
                        "type": "group",
                        "effects": [
                            {
                                "type": "move_zone",
                                "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                                "amount": 2,
                                "location": "deck",
                            },
                            {"type": "shuffle", "target": "controller", "location": "deck"},
                        ],
                    },
                ],
            },
            "optional": True,
            "text": "En tu fase de vigilia, si tienes a Morgana, puedes robar 3 cartas o barajar 2 de tu cementerio en tu mazo castillo.",
        }
    ],
}
tags_es176 = ["roba_cartas", "mueve_zona", "baraja", "opcional"]
set_card("es176", abilities_es176, tags_es176)

# es177 Simon de Montfort
abilities_es177 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_totem",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "totem"},
            "text": "En tu fase de vigilia, genera 2 oros para pagar el coste de un Tótem.",
        }
    ],
}
tags_es177 = ["genera_recursos"]
set_card("es177", abilities_es177, tags_es177)

# es178 Maza de Guerra
abilities_es178 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_equipped",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Su portador gana +2 a la fuerza.",
        },
        {
            "id": "immune_to_talismans",
            "type": "static",
            "effect": {"type": "immunity", "target": {"type": "reference", "reference": "equipped_to"}, "value": "talismans"},
            "text": "Su portador no puede ser afectado por Talismanes.",
        },
    ],
}
tags_es178 = ["modifica_fuerza", "inmunidad"]
set_card("es178", abilities_es178, tags_es178)

# es179 Templo del Desierto
abilities_es179 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "limit_attackers",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"max_attackers_per_turn": 1}, "target": {"type": "global"}},
            "text": "Mientras está en juego, sólo se puede declarar un Aliado atacante por turno.",
        }
    ],
}
tags_es179 = ["restriccion"]
set_card("es179", abilities_es179, tags_es179)

# es18 Morgana
abilities_es18 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener una Morgana en juego.",
        },
        {
            "id": "destroy_to_exile",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "amount": 1},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu fase de vigilia y una vez por turno, puedes destruir uno de tus Aliados para desterrar un Aliado oponente.",
        },
    ],
}
tags_es18 = ["restriccion", "destruye_para_pagar", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("es18", abilities_es18, tags_es18)


conn.commit()
conn.close()
print("Updated batch: es171-es179 y es18")






