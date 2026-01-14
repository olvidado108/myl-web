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
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
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


# es523 Merlin
abilities_es523 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Merlin en juego.",
        },
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "pay_three_play_talisman",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "talismans", "controller": "self", "cost": {"operator": "<=", "value": 3}}},
                        "action": "put_in_play",
                        "pay_cost": False,
                        "amount": 1,
                    },
                    {
                        "type": "delayed_trigger",
                        "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
                        "effect": {"type": "exile", "target": {"type": "reference", "reference": "last_put_in_play"}},
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, paga 3 Oro para jugar un Talismán de coste 3 o menos desde tu mazo sin pagar su coste. Al final del turno, destiérralo.",
        },
    ],
}
tags_es523 = ["restriccion", "imbloqueable", "paga_recursos", "busca_mazo", "pone_en_juego", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("es523", abilities_es523, tags_es523)

# es524 Belial
abilities_es524 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "force_per_other_faerie",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "any", "exclude": "self"}}}},
            },
            "text": "Gana +1 a la fuerza por cada otro Aliado Faerie en juego.",
        },
    ],
}
tags_es524 = ["imbloqueable", "modifica_fuerza"]
set_card("es524", abilities_es524, tags_es524)

# es525 Goblin Maligno
abilities_es525 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "boost_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "target": {"type": "filter", "filter": {"type": "allies", "subtype": "Goblin", "controller": "any", "exclude": "self"}}}},
                "duration": "end_turn",
            },
            "text": "Cuando es declarado atacante, gana +1 a la fuerza hasta la Fase Final por cada otro Goblin en juego.",
        },
    ],
}
tags_es525 = ["apresurado", "modifica_fuerza"]
set_card("es525", abilities_es525, tags_es525)

# es526 Menw
abilities_es526 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_and_unblockable",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "modify_force",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "modifier": {"type": "add", "value": 1},
                        "duration": "end_turn",
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "value": {"restriction": "unblockable"},
                        "duration": "end_turn",
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia, una vez por turno, un Aliado propio gana +1 a la fuerza y es Imbloqueable hasta la Fase Final.",
        }
    ],
}
tags_es526 = ["modifica_fuerza", "imbloqueable", "opcional", "una_vez_por_turno"]
set_card("es526", abilities_es526, tags_es526)

# es527 Fuath
abilities_es527 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_to_weaken",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -2},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "Puedes destruirlo para que un Aliado oponente pierda 2 a la fuerza hasta la Fase Final.",
        }
    ],
}
tags_es527 = ["destruye_para_pagar", "modifica_fuerza", "opcional"]
set_card("es527", abilities_es527, tags_es527)

# es528 Nimue
abilities_es528 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "copy_faerie_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"type": "copy_from_graveyard", "race": "Faerie"}, "duration": "end_turn"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia y una vez por turno, puedes copiar un Aliado Faerie de tu Cementerio hasta la Fase Final.",
        }
    ],
}
tags_es528 = ["opcional", "una_vez_por_turno"]
set_card("es528", abilities_es528, tags_es528)

# es529 Aulladores Grises
abilities_es529 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_same_type_on_leave",
            "type": "response",
            "trigger": {
                "type": "leaves_play",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                "causedBy": "opponent",
            },
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "sameTypeAs": {"type": "reference", "reference": "triggered_card"}}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "text": "En respuesta a que una de tus cartas que no sea Oro salga del juego por efecto oponente, baraja una carta oponente del mismo tipo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es529 = ["baraja", "opcional", "restriccion"]
set_card("es529", abilities_es529, tags_es529)

# es53 Sir Persival
abilities_es53 = {
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
tags_es53 = ["baraja", "trigger_al_entrar"]
set_card("es53", abilities_es53, tags_es53)

# es530 Ataque de Goblins
abilities_es530 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_per_cheap_ally",
            "type": "activated",
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": {"type": "count", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play", "cost": {"operator": "<=", "value": 1}}}},
                "location": "deck",
            },
            "text": "Tu oponente bota 1 carta de su Mazo Castillo por cada Aliado en juego de coste 1 o menos.",
        }
    ],
}
tags_es530 = ["bota_cartas"]
set_card("es530", abilities_es530, tags_es530)

# es531 Crear Fungoides
abilities_es531 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_two_cost_one",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": "==", "value": 1}}},
                        "action": "put_in_play",
                        "amount": 2,
                        "pay_cost": False,
                    },
                    {
                        "type": "delayed_trigger",
                        "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
                        "effect": {"type": "destroy", "target": {"type": "reference", "reference": "last_put_in_play_group"}},
                    },
                ],
            },
            "text": "Busca hasta dos Aliados de coste 1 en tu mazo y juégalos sin pagar su coste. En la Fase Final, destruye esos Aliados.",
        }
    ],
}
tags_es531 = ["busca_mazo", "pone_en_juego", "destruye_objetivo"]
set_card("es531", abilities_es531, tags_es531)


conn.commit()
conn.close()
print("Updated batch: es523-es531")






