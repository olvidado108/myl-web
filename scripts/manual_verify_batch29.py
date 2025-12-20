import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("anula", "Anula hechizos/efectos", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("mira_mazo", "Mira/Reordena mazo", "control", None),
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


# es351 Bendicion Siniestra
abilities_es351 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_self_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando juegues este Talismán, destiérralo.",
        },
        {
            "id": "shuffle_faerie_to_exile_and_choose",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "cost": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self", "zone": "play"}},
                "amount": 1,
                "location": "deck",
            },
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}},
                    {
                        "type": "choice",
                        "options": [
                            {"type": "draw_cards", "amount": 1, "target": "controller"},
                            {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self", "zone": "graveyard"}}, "amount": 1, "location": "hand"},
                        ],
                        "optional": True,
                    },
                ],
            },
            "text": "Baraja un Faerie que controles para desterrar un Aliado oponente. Luego, puedes robar una carta o poner un Oro de tu Cementerio en tu mano.",
        },
    ],
}
tags_es351 = ["baraja", "destierra_objetivo", "roba_cartas", "opcional"]
set_card("es351", abilities_es351, tags_es351)

# es352 la Espada Rota
abilities_es352 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_armed_ally",
            "type": "activated",
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play", "has_equipment_type": "arma"}},
                "amount": 1,
            },
            "text": "Destruye un Aliado en juego que porte una o más Armas.",
        }
    ],
}
tags_es352 = ["destruye_objetivo"]
set_card("es352", abilities_es352, tags_es352)

# es353 Merlin Atrapado
abilities_es353 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cancel_attack_and_bottom",
            "type": "response",
            "trigger": {"type": "attack_declared", "target": "opponent"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "counter", "target": "current_attack"},
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                        "amount": 1,
                        "location": "deck_bottom",
                    },
                ],
            },
            "text": "Cancela el ataque oponente. Luego, el oponente elige uno de sus Aliados y lo pone en el fondo de su mazo.",
        }
    ],
}
tags_es353 = ["anula", "mueve_zona", "baraja"]
set_card("es353", abilities_es353, tags_es353)

# es354 Bec de Corbin
abilities_es354 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador de Bec de Corbin gana 2 a la fuerza.",
        },
        {
            "id": "search_weapon",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": {"type": "or", "values": ["deck", "graveyard"]},
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Arma en tu Mazo Castillo o Cementerio y ponerla en tu mano.",
        },
    ],
}
tags_es354 = ["modifica_fuerza", "busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es354", abilities_es354, tags_es354)

# es355 Arco Montadragon
abilities_es355 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador de Arco Montadragón gana 2 a la fuerza.",
        },
        {
            "id": "search_dragon",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": {"type": "or", "values": ["deck", "graveyard"]},
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "cost": {"operator": ">=", "value": 4}}},
                "action": "put_in_hand",
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Aliado Dragón de coste 4 o más en tu Mazo Castillo o Cementerio y ponerlo en tu mano.",
        },
    ],
}
tags_es355 = ["modifica_fuerza", "busca_mazo", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("es355", abilities_es355, tags_es355)

# es356 Dinas Emrys
abilities_es356 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "generate_for_totems",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": "totem"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes generar 2 oros para jugar o activar habilidades de Tótem.",
        },
        {
            "id": "draw_on_totem_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "totems", "controller": "self"}}},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "optional": True,
            "text": "Cada vez que juegues un Tótem puedes robar una carta de tu Mazo Castillo.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es356 = ["genera_recursos", "roba_cartas", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es356", abilities_es356, tags_es356)

# es357 Milano Rojo
abilities_es357 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_shuffle",
            "type": "activated",
            "condition": {"type": "zone", "value": "oro_reserva", "target": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "optional": True,
            "text": "Si Milano Rojo está en tu Reserva de Oro, puedes desterrarlo para barajar dos cartas de tu Cementerio en tu Mazo Castillo.",
        }
    ],
}
tags_es357 = ["destierra_para_pagar", "baraja", "opcional"]
set_card("es357", abilities_es357, tags_es357)

# es358 Dragon de Luz
abilities_es358 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_three_cannot_attack",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "shuffle",
                        "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                        "amount": 3,
                        "location": "deck",
                    },
                    {"type": "restriction", "restriction": "cannot_attack", "target": "self", "duration": "end_turn"},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En tu Fase de Vigilia, una vez por turno, puedes barajar 3 cartas de tu Cementerio en tu Mazo Castillo. Si lo haces, Dragón de Luz no puede ser declarado atacante este turno.",
        }
    ],
}
tags_es358 = ["baraja", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es358", abilities_es358, tags_es358)

# es359 Sir Persival
abilities_es359 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1, "location": "deck"},
            "text": "Cuando Sir Pérsival entra en juego, baraja un aliado oponente.",
        }
    ],
}
tags_es359 = ["baraja", "mueve_zona", "trigger_al_entrar"]
set_card("es359", abilities_es359, tags_es359)

# es36 Bola de Fuego
abilities_es36 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_non_gold",
            "type": "activated",
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "not": {"type": "oros"}}},
            },
            "text": "Destruye una carta en juego, que no sea un oro.",
        }
    ],
}
tags_es36 = ["destruye_objetivo"]
set_card("es36", abilities_es36, tags_es36)


conn.commit()
conn.close()
print("Updated batch: es351-es359 y es36")

