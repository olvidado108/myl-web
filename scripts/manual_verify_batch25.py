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
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("muestra_mano", "Muestra mano", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
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


# es315 Ser Incorporeo
abilities_es315 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_block_unblockables",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_block_unblockable", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "text": "Un aliado tuyo puede bloquear imbloqueables.",
        }
    ],
}
tags_es315 = ["restriccion", "imbloqueable"]
set_card("es315", abilities_es315, tags_es315)

# es316 Gwyllion
abilities_es316 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_hands_two_turns",
            "type": "activated",
            "effect": {"type": "restriction", "restriction": "reveal_hand", "target": {"type": "players", "players": "opponents"}, "duration": "two_turns"},
            "text": "Por dos turnos, los oponentes juegan mostrando su mano.",
        }
    ],
}
tags_es316 = ["muestra_mano"]
set_card("es316", abilities_es316, tags_es316)

# es317 Vegetacion Animada
abilities_es317 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_gold_to_set_force_zero",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}}, "amount": 1},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
                "modifier": {"type": "set", "value": 0},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En Vigilia, destruye uno de tus oros: un aliado oponente queda en fuerza 0 este turno.",
        }
    ],
}
tags_es317 = ["destruye_para_pagar", "modifica_fuerza", "opcional"]
set_card("es317", abilities_es317, tags_es317)

# es318 Alquimista
abilities_es318 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_gold_to_reserve",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "self"}},
                "action": "put_in_play",
                "destination": "reserve",
                "amount": 1,
            },
            "text": "En Vigilia, busca un oro normal en tu mazo y ponlo en tu reserva.",
        }
    ],
}
tags_es318 = ["busca_mazo", "genera_recursos"]
set_card("es318", abilities_es318, tags_es318)

# es319 Totem Celta
abilities_es319 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_on_named_type",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "opponent"},
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": 2,
                "location": "deck",
            },
            "text": "Nombra un tipo; cuando el oponente juega ese tipo, bota 2 cartas.",
        }
    ],
}
tags_es319 = ["bota_cartas"]
set_card("es319", abilities_es319, tags_es319)

# es32 Morgana
abilities_es32 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener una Morgana en juego.",
        },
        {
            "id": "destroy_to_exile",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "amount": 1},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia y una vez por turno, puedes destruir uno de tus aliados para desterrar un aliado oponente.",
        },
    ],
}
tags_es32 = ["restriccion", "destruye_para_pagar", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("es32", abilities_es32, tags_es32)

# es320 Totem de Bossus
abilities_es320 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_one_each_group",
            "type": "triggered",
            "trigger": {"type": "phase_start", "target": {"type": "reference", "reference": "phase.agrupacion"}},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"controller": "opponent", "zone": "graveyard"}}, "amount": 1},
            "text": "En cada fase de agrupar, tu oponente destierra 1 carta de su cementerio.",
        }
    ],
}
tags_es320 = ["destierra_objetivo"]
set_card("es320", abilities_es320, tags_es320)

# es321 Totem de Hobgoblin
abilities_es321 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "choice_mill_or_draw",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "choice",
                "choices": [
                    {
                        "type": "group",
                        "effects": [
                            {"type": "pay_resources", "amount": 4},
                            {"type": "discard", "target": "opponent", "amount": 4, "location": "deck"},
                        ],
                    },
                    {
                        "type": "group",
                        "effects": [
                            {"type": "destroy", "target": "self"},
                            {"type": "draw_cards", "amount": 2, "target": "controller"},
                        ],
                    },
                ],
            },
            "optional": True,
            "text": "En Vigilia, elige: paga 4 oro y el oponente bota 4; o destruye este tótem y roba 2 cartas.",
        }
    ],
}
tags_es321 = ["bota_cartas", "paga_recursos", "roba_cartas", "destruye_para_pagar", "opcional"]
set_card("es321", abilities_es321, tags_es321)

# es322 Totem de Las Alas Eternas
abilities_es322 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_unblockables",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "restriction": "unblockable"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Tus Aliados imbloqueables ganan +1 a la fuerza.",
        }
    ],
}
tags_es322 = ["modifica_fuerza", "imbloqueable"]
set_card("es322", abilities_es322, tags_es322)

# es323 Totem del Draco
abilities_es323 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_from_grave_on_dragon",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"race": "Dragón", "controller": "self"}}},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Cada vez que bajes un Dragón, puedes barajar una carta de tu cementerio en tu mazo.",
        }
    ],
}
tags_es323 = ["baraja", "mueve_zona", "opcional"]
set_card("es323", abilities_es323, tags_es323)


conn.commit()
conn.close()
print("Updated batch: es315-es323 y es32")






