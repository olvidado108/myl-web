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
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
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


# es87 Titania
abilities_es87 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_other_faeries",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "exclude": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus otras Faeries ganan +1 a la fuerza.",
        },
        {
            "id": "faeries_can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "exclude": "self"}}, "value": {"restriction": "can_attack_on_enter"}},
            "text": "Tus otras Faeries pueden atacar cuando entran en juego.",
        },
    ],
}
tags_es87 = ["modifica_fuerza", "apresurado"]
set_card("es87", abilities_es87, tags_es87)

# es88 Belial el Bestial
abilities_es88 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_per_faerie",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 a la fuerza por cada Faerie que controles.",
        }
    ],
}
tags_es88 = ["modifica_fuerza"]
set_card("es88", abilities_es88, tags_es88)

# es89 la Dama del Lago
abilities_es89 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck_or_graveyard",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Arma en tu mazo o Cementerio y ponerla en juego sin pagar su coste.",
        }
    ],
}
tags_es89 = ["busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es89", abilities_es89, tags_es89)

# es9 Taliesin Bob
abilities_es9 = {
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
            "text": "Cuando entra, puedes buscar un Aliado Faerie y jugarlo sin pagar su coste.",
        },
    ],
}
tags_es9 = ["restriccion", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es9", abilities_es9, tags_es9)

# es90 Alto Druida
abilities_es90 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_only_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_only_block", "target": "self"},
            "text": "Solo puede bloquear.",
        }
    ],
}
tags_es90 = ["restriccion"]
set_card("es90", abilities_es90, tags_es90)

# es91 Puck
abilities_es91 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "lock_opponent_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "restriction",
                "restriction": {"cannot_attack": True, "cannot_block": True},
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "duration": "end_turn",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Guerra de Talismanes, una vez por turno, paga 1 Oro: un Aliado oponente no puede atacar ni bloquear este turno.",
        }
    ],
}
tags_es91 = ["paga_recursos", "restriccion", "opcional", "una_vez_por_turno"]
set_card("es91", abilities_es91, tags_es91)

# es92 Plaga
abilities_es92 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_two_opponents",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 2},
            "text": "Destruye dos Aliados oponentes.",
        }
    ],
}
tags_es92 = ["destruye_objetivo"]
set_card("es92", abilities_es92, tags_es92)

# es93 Transmutacion
abilities_es93 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "totems_become_allies",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "gain_ability",
                        "target": {"type": "filter", "filter": {"type": "totems", "controller": "self", "zone": "play"}},
                        "value": {"type": "ally", "force_from_cost": True},
                        "duration": "end_turn",
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "filter", "filter": {"type": "totems", "controller": "self", "zone": "play"}},
                        "value": {"restriction": "can_attack"},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "Hasta fin de turno, tus Tótem pierden su habilidad, son Aliados con fuerza igual a su coste y pueden ser declarados atacantes.",
        }
    ],
}
tags_es93 = ["restriccion"]
set_card("es93", abilities_es93, tags_es93)

# es94 Cuna de Dragones
abilities_es94 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_then_draw",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "location": "deck",
                        "amount": 2,
                    },
                    {"type": "draw_cards", "amount": 1, "target": "controller", "optional": True},
                ],
            },
            "text": "Baraja 2 cartas de tu Cementerio en tu mazo. Luego, puedes robar 1 carta.",
        }
    ],
}
tags_es94 = ["baraja", "roba_cartas", "opcional"]
set_card("es94", abilities_es94, tags_es94)

# es95 Santo Grial
abilities_es95 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "save_destroyed_card",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"controller": "self", "zone": "play"}}},
            "effect": {"type": "move_zone", "target": "triggered_card", "location": "hand"},
            "optional": True,
            "text": "En respuesta a que una de tus cartas sea destruida, súbela a la mano.",
        }
    ],
}
tags_es95 = ["mueve_zona", "opcional"]
set_card("es95", abilities_es95, tags_es95)


conn.commit()
conn.close()
print("Updated batch: es87-es95")








