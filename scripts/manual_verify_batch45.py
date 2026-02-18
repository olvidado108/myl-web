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
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
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


# es497 Falsa Guinivere
abilities_es497 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "action": "put_in_graveyard",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Aliado en el mazo oponente y enviarlo a su Cementerio.",
        },
        {
            "id": "weaken_opponent_once_per_turn",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -1},
                "duration": "end_turn",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, elige un Aliado oponente para que pierda 1 a la fuerza hasta la Fase Final.",
        },
    ],
}
tags_es497 = ["mueve_zona", "opcional", "modifica_fuerza", "una_vez_por_turno", "trigger_al_entrar"]
set_card("es497", abilities_es497, tags_es497)

# es498 Montaraz
abilities_es498 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_totem_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "self", "cost": {"operator": "<=", "value": 3}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "text": "Cuando entra en juego, pon un Tótem de coste 3 o menos de tu Cementerio en tu mano.",
        },
        {
            "id": "exile_opponent_card_on_death",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {
                "type": "exile",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}},
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando sea destruido, puedes desterrar una carta del Cementerio oponente.",
        },
    ],
}
tags_es498 = ["mueve_zona", "destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("es498", abilities_es498, tags_es498)

# es499 Crear Caballero Negro
abilities_es499 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_opponent_ally_as_knight",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "graveyard",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "cost": {"operator": "<=", "value": 2}}},
                        "action": "put_in_play",
                        "controller": "self",
                        "pay_cost": False,
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "reference", "reference": "last_put_in_play"},
                        "value": {"type": "race_change", "race": "Caballero"},
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "reference", "reference": "last_put_in_play"},
                        "value": {"restriction": "can_attack_on_enter"},
                    },
                    {
                        "type": "delayed_trigger",
                        "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
                        "effect": {"type": "exile", "target": {"type": "reference", "reference": "last_put_in_play"}},
                    },
                ],
            },
            "text": "Juega un Aliado de coste 2 o menos del Cementerio oponente sin pagar su coste. Ese Aliado se considera Caballero y puede atacar este turno. Al final del turno, destiérralo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es499 = ["pone_en_juego", "apresurado", "destierra_objetivo", "restriccion", "mueve_zona"]
set_card("es499", abilities_es499, tags_es499)

# es5 Dragón de Magma Bob
abilities_es5 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Cuando Dragón de Magma entra en juego, destruye un Aliado oponente.",
        }
    ],
}
tags_es5 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es5", abilities_es5, tags_es5)

# es50 Reina Guinivere
abilities_es50 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_knight_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Caballero en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "generate_for_weapons_or_knights",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "generate_resources", "amount": 2, "restriction": "armas"},
                    {"type": "generate_resources", "amount": 1, "restriction": "caballeros"},
                ],
            },
            "text": "En tu Fase de Vigilia, genera 2 para bajar Armas o 1 para bajar Caballeros.",
        },
    ],
}
tags_es50 = ["busca_mazo", "opcional", "genera_recursos", "trigger_al_entrar"]
set_card("es50", abilities_es50, tags_es50)

# es500 Flecha Ácida
abilities_es500 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_and_draw",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "<=", "value": 2}}}, "amount": 1},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "text": "Destruye un Aliado oponente de fuerza 2 o menos. Luego, roba 1 carta.",
        }
    ],
}
tags_es500 = ["destruye_objetivo", "roba_cartas"]
set_card("es500", abilities_es500, tags_es500)

# es501 Funeral de Galehaut
abilities_es501 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_one_each_type",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "location": "deck",
                "amount": {"type": "per_type", "max": 1},
            },
            "text": "Baraja hasta una carta de cada tipo de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es501 = ["baraja"]
set_card("es501", abilities_es501, tags_es501)

# es502 Escudo del Lago
abilities_es502 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_equipped_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
        {
            "id": "generate_for_weapons_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "generate_resources", "amount": 1, "restriction": {"type": "filter", "filter": {"type": "armas"}}},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes generar 1 Oro para jugar Armas.",
        },
    ],
}
tags_es502 = ["modifica_fuerza", "genera_recursos", "opcional", "una_vez_por_turno"]
set_card("es502", abilities_es502, tags_es502)

# es503 Guardia Gozosa
abilities_es503 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "strip_and_destroy_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "lose_ability", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
                    {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
                ],
            },
            "text": "Cuando entra en juego, un Aliado oponente pierde su habilidad y es destruido.",
        },
        {
            "id": "destroy_self_to_shuffle",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Puedes destruir a Guardia Gozosa para barajar una carta de tu Cementerio en tu Mazo Castillo.",
        },
    ],
}
tags_es503 = ["destruye_objetivo", "baraja", "opcional", "destruye_para_pagar", "trigger_al_entrar"]
set_card("es503", abilities_es503, tags_es503)

# es504 Sir Robin de Locksley
abilities_es504 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "gain_control_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "gain_control",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "end_turn",
            },
            "text": "Cuando entra en juego, gana el control de un Aliado oponente hasta la Fase Final.",
        }
    ],
}
tags_es504 = ["mueve_zona", "trigger_al_entrar"]
set_card("es504", abilities_es504, tags_es504)


conn.commit()
conn.close()
print("Updated batch: es497-es504 y es5/es50")








