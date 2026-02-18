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
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("baraja", "Baraja cartas", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("anula", "Anula hechizos/efectos", "control", None),
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


# es532 Espada Bruja
abilities_es532 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "equip_only_faerie",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "race": "Faerie"}},
            },
            "text": "Solo puede ser portada por Aliados Faerie.",
        },
        {
            "id": "boost_carrier",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
        {
            "id": "recover_gold_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar 1 Oro en tu Cementerio y ponerlo en tu mano.",
        },
    ],
}
tags_es532 = ["restriccion", "modifica_fuerza", "busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es532", abilities_es532, tags_es532)

# es533 Duendes
abilities_es533 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "text": "Cuando entra en juego, descarta 1 carta de tu mano.",
        }
    ],
}
tags_es533 = ["descarta_mano", "trigger_al_entrar"]
set_card("es533", abilities_es533, tags_es533)

# es534 Goblin Stone
abilities_es534 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "tutor_goblin_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "subtype": "Goblin", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Aliado Goblin en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "boost_faerie_low_cost",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "cost": {"operator": "<=", "value": 1}}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus Aliados Faerie de coste 1 o menos ganan +1 a la fuerza.",
        },
    ],
}
tags_es534 = ["busca_mazo", "opcional", "modifica_fuerza", "trigger_al_entrar"]
set_card("es534", abilities_es534, tags_es534)

# es535 Sirocco
abilities_es535 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_ally_from_opponent_grave",
            "type": "activated",
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "<=", "value": 3}}},
                "action": "put_in_play",
                "controller": "self",
                "pay_cost": False,
            },
            "text": "Busca en el Cementerio oponente un Aliado de fuerza 3 o menos y juégalo sin pagar su coste.",
        }
    ],
}
tags_es535 = ["pone_en_juego", "busca_mazo"]
set_card("es535", abilities_es535, tags_es535)

# es536 Hobgoblin
abilities_es536 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_other_goblins",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "subtype": "Goblin", "controller": "self", "exclude": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus otros Goblin ganan +1 a la fuerza.",
        }
    ],
}
tags_es536 = ["modifica_fuerza"]
set_card("es536", abilities_es536, tags_es536)

# es537 Goblin
abilities_es537 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "goblins_unblockable_if_three",
            "type": "static",
            "condition": {
                "type": "count",
                "target": {"type": "filter", "filter": {"type": "allies", "subtype": "Goblin", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "value": 3,
            },
            "effect": {
                "type": "restriction",
                "restriction": "unblockable",
                "target": {"type": "filter", "filter": {"type": "allies", "subtype": "Goblin", "controller": "self", "zone": "play"}},
            },
            "text": "Si controlas 3 Goblin, tus Goblin son Imbloqueables.",
        }
    ],
}
tags_es537 = ["imbloqueable", "restriccion"]
set_card("es537", abilities_es537, tags_es537)

# es538 Corona de Arturo
abilities_es538 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_indestructible_if_two_allies",
            "type": "static",
            "condition": {
                "type": "count",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "value": 2,
            },
            "effect": {"type": "restriction", "restriction": "indestructible", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}},
            "text": "Mientras controles 2 o más Aliados, tus Oros son indestructibles.",
        },
        {
            "id": "exile_from_grave_to_draw",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Desde el Cementerio, puedes desterrarla para robar 1 carta.",
        },
    ],
}
tags_es538 = ["restriccion", "roba_cartas", "opcional", "exilia_para_pagar"]
set_card("es538", abilities_es538, tags_es538)

# es539 Guardia Gozosa
abilities_es539 = {
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
            "text": "Puedes destruirla para barajar una carta de tu Cementerio en tu Mazo Castillo.",
        },
    ],
}
tags_es539 = ["destruye_objetivo", "baraja", "opcional", "destruye_para_pagar", "trigger_al_entrar"]
set_card("es539", abilities_es539, tags_es539)

# es54 Sir Bedivere
abilities_es54 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_named_ally",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "hand"}},
                "location": "defense",
                "controller": "self",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia, una vez por turno, nombra un Aliado; si el oponente lo tiene en mano, lo pones en tu defensa sin pagar su coste.",
        }
    ],
}
tags_es54 = ["mueve_zona", "pone_en_juego", "opcional", "una_vez_por_turno"]
set_card("es54", abilities_es54, tags_es54)

# es540 Fe Sin Limite
abilities_es540 = {
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
tags_es540 = ["anula", "opcional"]
set_card("es540", abilities_es540, tags_es540)


conn.commit()
conn.close()
print("Updated batch: es532-es540")








