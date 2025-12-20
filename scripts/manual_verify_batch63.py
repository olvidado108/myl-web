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
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("previene_dano", "Previene daño", "defensivo", None),
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


# hd15 Mess Buachalla
abilities_hd15 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "boost_allies_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "exclude": "self"}},
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "text": "Si es declarado atacante, tus otros Aliados ganan +1 a la fuerza hasta la Fase Final.",
        },
        {
            "id": "shuffle_self_at_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "effect": {"type": "shuffle", "target": "self", "location": "deck"},
            "text": "En tu Fase Final, barájalo en tu mazo.",
        },
    ],
}
tags_hd15 = ["apresurado", "modifica_fuerza", "baraja"]
set_card("hd15", abilities_hd15, tags_hd15)

# hd150 Glas Gaibhenenn
abilities_hd150 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_and_pay_to_destroy_artifact",
            "type": "activated",
            "condition": {"type": "in_zone", "target": "self", "zone": "reserve"},
            "cost": {"type": "group", "costs": [{"type": "exile", "target": "self"}, {"type": "pay_resources", "amount": 1}]},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "cardType": {"operator": "in", "value": ["armas", "totems"]}}},
                "amount": 1,
            },
            "optional": True,
            "text": "Desde la Reserva: destiérralo y paga 1 Oro para destruir un Arma o Tótem oponente.",
        }
    ],
}
tags_hd150 = ["exilia_para_pagar", "paga_recursos", "destruye_objetivo", "opcional"]
set_card("hd150", abilities_hd150, tags_hd150)

# hd151 Fragarach
abilities_hd151 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_carrier",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
        {
            "id": "tutor_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": "<=", "value": 3}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Aliado de coste 3 o menos y ponerlo en tu mano.",
        },
    ],
}
tags_hd151 = ["modifica_fuerza", "busca_mazo", "opcional", "trigger_al_entrar"]
set_card("hd151", abilities_hd151, tags_hd151)

# hd152 Manzana Sidhe
abilities_hd152 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
        {
            "id": "pay_to_draw_discard",
            "type": "activated",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "cost": {"type": "pay_resources", "amount": {"type": "reference", "reference": "self.cost"}},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "En Vigilia, si controlas 2 o más Aliados, puedes pagarla para robar 1 carta.",
        },
        {
            "id": "discard_after_draw",
            "type": "activated",
            "effect": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "text": "Luego, descarta 1 carta.",
        },
    ],
}
tags_hd152 = ["restriccion", "paga_recursos", "roba_cartas", "descarta_mano", "opcional"]
set_card("hd152", abilities_hd152, tags_hd152)

# hd153 Salmon del Saber
abilities_hd153 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar 1 carta de tu Cementerio en tu mazo.",
        },
        {
            "id": "exile_from_reserve_prevent_deck_damage",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "reserve", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "prevent_damage",
                "target": {"type": "reference", "reference": "controller.deck"},
                "duration": "turn",
                "source": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "optional": True,
            "text": "Desde la Reserva, puedes desterrarlo: el daño de Aliados oponentes a tu mazo es 0 este turno.",
        },
    ],
}
tags_hd153 = ["baraja", "exilia_para_pagar", "previene_dano", "opcional"]
set_card("hd153", abilities_hd153, tags_hd153)

# hd154 Horda Fomore
abilities_hd154 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_shadow_to_hand",
            "type": "activated",
            "condition": {"type": "in_zone", "value": "graveyard", "target": "self"},
            "cost": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "zone": "graveyard", "controller": "self"}}, "amount": 1},
            "effect": {"type": "move_zone", "target": "self", "location": "hand"},
            "optional": True,
            "oncePerTurn": True,
            "text": "Si está en tu Cementerio, destierra un Sombra para ponerlo en tu mano (1 vez por turno).",
        }
    ],
}
tags_hd154 = ["exilia_para_pagar", "mueve_zona", "opcional", "una_vez_por_turno"]
set_card("hd154", abilities_hd154, tags_hd154)

# hd155 Carmix
abilities_hd155 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_not_exiled",
            "type": "static",
            "condition": {"type": "in_zone", "target": "self", "zone": "reserve"},
            "effect": {"type": "restriction", "restriction": "cannot_be_exiled", "target": {"type": "filter", "filter": {"type": "oros", "controller": "any", "zone": "play"}}},
            "text": "Mientras esté en la Reserva, los Oros en juego no pueden ser desterrados.",
        }
    ],
}
tags_hd155 = ["restriccion"]
set_card("hd155", abilities_hd155, tags_hd155)

# hd156 Ogham
abilities_hd156 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_totems",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "totems"},
            "optional": True,
            "text": "Págalo para generar 2 Oros para jugar Tótems.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd156 = ["paga_recursos", "genera_recursos", "opcional", "restriccion"]
set_card("hd156", abilities_hd156, tags_hd156)

# hd157 Gaitas
abilities_hd157 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "group_in_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "effect": {"type": "move_zone", "target": "self", "location": "support_line"},
            "optional": True,
            "text": "En tu Fase Final, puedes agrupar este Oro.",
        }
    ],
}
tags_hd157 = ["mueve_zona", "opcional"]
set_card("hd157", abilities_hd157, tags_hd157)

# hd158 Linaje Celta
abilities_hd158 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "next_challenger_uncounterable",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "grant_ability_until",
                "duration": "end_turn",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self", "zone": "hand"}},
                "value": {"restriction": "cannot_be_countered"},
            },
            "text": "El turno que entra, el próximo Desafiante que juegues no puede ser anulado.",
        },
        {
            "id": "destroy_to_tutor_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "En Vigilia, puedes destruirlo desde la Reserva para buscar un Desafiante en tu Cementerio y ponerlo en tu mano.",
        },
    ],
}
tags_hd158 = ["restriccion", "busca_mazo", "opcional"]
set_card("hd158", abilities_hd158, tags_hd158)


conn.commit()
conn.close()
print("Updated batch: hd15 y hd150-hd158")

