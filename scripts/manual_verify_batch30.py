import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("restriccion", "Restricción/regla", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
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


# es360 Desleal
abilities_es360 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_opponent_ally",
            "type": "activated",
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}},
            "text": "Destierra un Aliado oponente.",
        }
    ],
}
tags_es360 = ["destierra_objetivo"]
set_card("es360", abilities_es360, tags_es360)

# es361 Herrero
abilities_es361 = {
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
tags_es361 = ["genera_recursos", "paga_recursos", "opcional", "destruye_objetivo", "pierde_habilidad"]
set_card("es361", abilities_es361, tags_es361)

# es362 el Gran Wyrm
abilities_es362 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_other_dragons",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "not": {"id": "self"}}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus otros Dragones ganan +1 a la fuerza.",
        },
        {
            "id": "haste_for_dragons",
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
tags_es362 = ["modifica_fuerza", "apresurado"]
set_card("es362", abilities_es362, tags_es362)

# es363 Draco Conjurador
abilities_es363 = {
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
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Oro en tu mazo y ponerlo en tu mano.",
        }
    ],
}
tags_es363 = ["busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es363", abilities_es363, tags_es363)

# es364 Taliesin
abilities_es364 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Taliesin en juego.",
        },
        {
            "id": "play_faerie_for_free",
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
            "text": "Cuando entra en juego, puedes buscar un Aliado Faerie en tu mazo y jugarlo sin pagar su coste.",
        },
    ],
}
tags_es364 = ["restriccion", "busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es364", abilities_es364, tags_es364)

# es365 Federico Barbarroja
abilities_es365 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "no_weapon_limit",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "no_weapon_limit", "target": "self"},
            "text": "No tiene límite de Armas.",
        },
        {
            "id": "search_same_force_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "self", "force": {"operator": "==", "value": {"type": "reference", "reference": "self_force"}}},
                },
                "action": "put_in_play",
                "zone": "defense",
                "amount": 1,
            },
            "optional": True,
            "text": "Si hace daño al Mazo Castillo oponente, puedes buscar un Aliado de su misma fuerza en tu mazo y ponerlo en tu Línea de Defensa.",
        },
    ],
}
tags_es365 = ["restriccion", "busca_mazo", "pone_en_juego", "opcional"]
set_card("es365", abilities_es365, tags_es365)

# es366 la Llama Fria
abilities_es366 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_and_play_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "text": "Sólo en tu Fase de Vigilia: busca un Aliado en tu mazo y juégalo sin pagar su coste.",
        }
    ],
}
tags_es366 = ["busca_mazo", "pone_en_juego", "restriccion"]
set_card("es366", abilities_es366, tags_es366)

# es367 Sir Gaheris
abilities_es367 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "cost": {"operator": "<=", "value": 2}}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Arma de coste 2 o menos en tu mazo y jugarla sin pagar su coste.",
        }
    ],
}
tags_es367 = ["busca_mazo", "pone_en_juego", "opcional", "trigger_al_entrar"]
set_card("es367", abilities_es367, tags_es367)

# es368 Aneirin
abilities_es368 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}}},
            "optional": True,
            "text": "Cuando entra en juego, puedes desterrar una carta del Cementerio oponente.",
        },
        {
            "id": "exile_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}}},
            "optional": True,
            "text": "Cuando sale del juego, puedes desterrar una carta del Cementerio oponente.",
        },
    ],
}
tags_es368 = ["destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("es368", abilities_es368, tags_es368)

# es369 Espada de Caballero
abilities_es369 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_if_knight",
            "type": "static",
            "condition": {"type": "race_is", "race": "Caballero", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "Si el portador es Caballero, gana +2 a la fuerza.",
        },
        {
            "id": "prevent_shuffle_next_turn",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "restriction", "restriction": "cannot_shuffle", "target": "opponent", "duration": "next_turn"},
            "text": "Si el portador daña el mazo oponente, ese jugador no podrá barajar en su próximo turno.",
        },
    ],
}
tags_es369 = ["modifica_fuerza", "restriccion"]
set_card("es369", abilities_es369, tags_es369)


conn.commit()
conn.close()
print("Updated batch: es360-es369")

