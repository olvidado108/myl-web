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
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
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


# es505 Sir Jason de Sangre
abilities_es505 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "draw_when_destroyed",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Si es destruido, puedes robar una carta de tu Mazo Castillo.",
        },
    ],
}
tags_es505 = ["apresurado", "roba_cartas", "opcional"]
set_card("es505", abilities_es505, tags_es505)

# es506 Lanza Divina
abilities_es506 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_carrier",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador gana +2 a la fuerza.",
        },
        {
            "id": "mill_opponent_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "controller"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "oncePerTurn": True,
            "text": "Una vez por turno, tu oponente bota 2 cartas de su Mazo Castillo.",
        },
    ],
}
tags_es506 = ["modifica_fuerza", "bota_cartas", "una_vez_por_turno"]
set_card("es506", abilities_es506, tags_es506)

# es507 Excalibur
abilities_es507 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_king_arthur",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "name": "Rey Arturo Pendragón"}},
            },
            "text": "Solo puede ser portada por Rey Arturo Pendragón.",
        },
        {
            "id": "base_boost",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 3}},
            "text": "El portador gana +3 a la fuerza.",
        },
        {
            "id": "discard_to_boost",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": {"type": "reference", "reference": "discarded_card.cost"}},
                "duration": "end_turn",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Vigilia y una vez por turno, puedes descartar 1 carta para que el portador gane fuerza igual a su coste en Oro hasta la Fase Final.",
        },
    ],
}
tags_es507 = ["restriccion", "modifica_fuerza", "opcional", "una_vez_por_turno", "descarta_mano"]
set_card("es507", abilities_es507, tags_es507)

# es508 Dragón Demonio
abilities_es508 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "must_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "must_attack_on_enter", "target": "self"},
            "text": "Debe atacar cuando entra en juego.",
        },
        {
            "id": "immune_to_talismans",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"cannot_be_targeted_by": {"type": "talismanes", "controller": "opponent"}}, "target": "self"},
            "text": "No puede ser afectado por Talismanes.",
        },
        {
            "id": "exile_at_end",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Al final de este turno, destiérralo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es508 = ["restriccion", "destierra_objetivo"]
set_card("es508", abilities_es508, tags_es508)

# es509 Org, Maestro de Dragones
abilities_es509 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reduce_opponent_force",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "set", "value": 0},
                "duration": "end_turn",
                "amount": 1,
            },
            "text": "Cuando entra, un Aliado oponente tiene fuerza 0 hasta la Fase Final.",
        },
        {
            "id": "boost_other_dragons",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "zone": "play", "exclude": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras esté en juego, tus otros Dragones ganan +1 a la fuerza.",
        },
    ],
}
tags_es509 = ["modifica_fuerza", "trigger_al_entrar"]
set_card("es509", abilities_es509, tags_es509)

# es51 Morgana
abilities_es51 = {
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
tags_es51 = ["restriccion", "destierra_objetivo", "opcional", "una_vez_por_turno", "destruye_objetivo"]
set_card("es51", abilities_es51, tags_es51)

# es510 Orium
abilities_es510 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "destroy_if_attacked",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {"type": "was_attacker", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si fue declarado atacante, destrúyelo en la Fase Final.",
        },
    ],
}
tags_es510 = ["apresurado", "destruye_objetivo"]
set_card("es510", abilities_es510, tags_es510)

# es511 Vouivre
abilities_es511 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_self_to_shuffle_opponents",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "amount": 1,
                        "location": "deck",
                    },
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "amount": 2,
                        "location": "deck",
                    },
                ],
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar un Aliado propio para barajar 2 Aliados oponentes.",
        },
        {
            "id": "tutor_dragon_once_per_turn",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes buscar un Aliado Dragón en tu mazo y ponerlo en tu mano.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es511 = ["baraja", "mueve_zona", "opcional", "busca_mazo", "una_vez_por_turno", "restriccion", "trigger_al_entrar"]
set_card("es511", abilities_es511, tags_es511)

# es512 Tormenta de Dragón
abilities_es512 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando juegues este Talismán, destiérralo.",
        },
        {
            "id": "exile_to_tutor_dragon_plus_one",
            "type": "activated",
            "cost": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "amount": 1},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "allies",
                        "race": "Dragón",
                        "controller": "self",
                        "cost": {"operator": "==", "value": {"type": "reference", "reference": "exiled_card.cost_plus_one"}},
                    },
                },
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Destierra un Aliado propio para buscar un Dragón que cueste 1 Oro más y jugarlo sin pagar su coste.",
        },
    ],
}
tags_es512 = ["exilia_para_pagar", "busca_mazo", "pone_en_juego", "opcional", "destierra_objetivo"]
set_card("es512", abilities_es512, tags_es512)

# es513 Cuna de Wurms
abilities_es513 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_dragon_draw_two",
            "type": "activated",
            "cost": {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "zone": "play"}}, "amount": 1, "location": "deck"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "Baraja un Aliado Dragón que controles para robar 2 cartas.",
        }
    ],
}
tags_es513 = ["baraja", "roba_cartas", "opcional", "mueve_zona"]
set_card("es513", abilities_es513, tags_es513)


conn.commit()
conn.close()
print("Updated batch: es505-es513 y es51")






