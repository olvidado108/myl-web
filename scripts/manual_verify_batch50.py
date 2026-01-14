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
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("exilia_para_pagar", "Exilia para pagar", "coste", None),
    ("previene_dano", "Previene daño", "defensivo", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
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


# es541 Toque de Persival
abilities_es541 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_recent_attacker_or_blocker",
            "type": "activated",
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "attacked_or_blocked_this_turn": True}},
                "amount": 1,
                "location": "deck",
            },
            "text": "Baraja un Aliado oponente que haya sido declarado atacante o bloqueador este turno.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es541 = ["baraja", "restriccion"]
set_card("es541", abilities_es541, tags_es541)

# es542 Espada Larga
abilities_es542 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "text": "Cuando entra en juego, roba dos cartas.",
        },
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 1}},
            "text": "El portador gana +1 a la fuerza.",
        },
    ],
}
tags_es542 = ["roba_cartas", "modifica_fuerza", "trigger_al_entrar"]
set_card("es542", abilities_es542, tags_es542)

# es543 Bola de Fuego Toolkit
abilities_es543 = {
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
tags_es543 = ["destruye_objetivo"]
set_card("es543", abilities_es543, tags_es543)

# es544 Aliado Feerico
abilities_es544 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "prevent_deck_damage",
            "type": "response",
            "trigger": {"type": "damage_assigned", "target": {"type": "reference", "reference": "controller.deck"}},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "prevent_damage", "target": {"type": "reference", "reference": "controller.deck"}, "duration": "turn", "amount": "all"},
            "optional": True,
            "text": "En respuesta a daño a tu Mazo Castillo, destruye un Aliado propio para reducirlo a 0 este turno.",
        }
    ],
}
tags_es544 = ["previene_dano", "destruye_objetivo", "opcional"]
set_card("es544", abilities_es544, tags_es544)

# es545 Producir Terremoto
abilities_es545 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_each_player_four",
            "type": "activated",
            "effect": {"type": "discard", "target": "all", "amount": 4, "location": "deck"},
            "text": "Cada jugador bota 4 cartas de su Mazo Castillo. No puede ser anulado.",
        }
    ],
}
tags_es545 = ["bota_cartas"]
set_card("es545", abilities_es545, tags_es545)

# es546 Carnwennan
abilities_es546 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_from_reserve_to_remove_ability",
            "type": "activated",
            "condition": {"type": "in_zone", "target": "self", "zone": "reserve"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "type": {"operator": "!=", "value": "oros"}}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "Si está en tu Reserva de Oros, puedes desterrarla: una carta oponente que no sea Oro pierde su habilidad hasta la Fase Final.",
        }
    ],
}
tags_es546 = ["exilia_para_pagar", "opcional"]
set_card("es546", abilities_es546, tags_es546)

# es547 Fantasmas del Desierto
abilities_es547 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "set_force_one",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "zone": "play"}},
                "modifier": {"type": "set", "value": 1},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En Guerra de Talismanes, todos los Aliados tienen fuerza 1 hasta el final del turno.",
        },
        {
            "id": "no_force_bonuses",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "cannot_receive_force_bonuses",
                "target": {"type": "filter", "filter": {"type": "allies", "zone": "play"}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En Guerra de Talismanes, los Aliados no pueden recibir bonos de fuerza este turno.",
        },
    ],
}
tags_es547 = ["modifica_fuerza", "opcional", "restriccion"]
set_card("es547", abilities_es547, tags_es547)

# es548 Ofrendas Al Dragon
abilities_es548 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_and_choose",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "exile",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}},
                        "amount": {"type": "per_type", "max": 1},
                    },
                    {
                        "type": "choice",
                        "options": [
                            {
                                "type": "shuffle",
                                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                                "amount": 1,
                                "location": "deck",
                            },
                            {"type": "draw_cards", "amount": 1, "target": "controller"},
                        ],
                        "optional": True,
                    },
                ],
            },
            "text": "Destierra hasta una carta de cada tipo del Cementerio oponente. Luego, puedes barajar una carta de tu Cementerio o robar una carta.",
        }
    ],
}
tags_es548 = ["destierra_objetivo", "baraja", "roba_cartas", "opcional"]
set_card("es548", abilities_es548, tags_es548)

# es549 Dumbarton
abilities_es549 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_totem_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "self", "cost": {"operator": "<=", "value": 3}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar un Tótem de coste 3 o menos y ponerlo en tu mano.",
        },
        {
            "id": "destroy_to_generate_or_draw",
            "type": "activated",
            "cost": {"type": "destroy", "target": "self"},
            "effect": {
                "type": "choice",
                "options": [
                    {"type": "generate_resources", "amount": 1, "restriction": "totems"},
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                ],
            },
            "optional": True,
            "text": "Puedes destruirlo para generar 1 Oro para Tótem o robar una carta.",
        },
    ],
}
tags_es549 = ["busca_mazo", "opcional", "genera_recursos", "destruye_objetivo", "roba_cartas", "trigger_al_entrar"]
set_card("es549", abilities_es549, tags_es549)

# es55 Dragón de Magma
abilities_es55 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "text": "Cuando entra en juego, destruye un Aliado oponente.",
        }
    ],
}
tags_es55 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es55", abilities_es55, tags_es55)


conn.commit()
conn.close()
print("Updated batch: es541-es549 y es55")






