import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("baraja", "Baraja cartas", "control", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", "Haste"),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("descarta_mano", "Descarta de mano", "control", None),
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


# es28 Dragon de Luz
abilities_es28 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_three_once_per_turn",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                        "amount": 3,
                        "location": "deck",
                    },
                    {"type": "shuffle", "target": "controller", "location": "deck"},
                    {
                        "type": "restriction",
                        "restriction": {"cannot_be_declared_attacker": True},
                        "target": "self",
                        "duration": "end_turn",
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes barajar 3 cartas de tu cementerio en tu mazo; si lo haces, no puede ser declarado atacante este turno.",
        }
    ],
}
tags_es28 = ["baraja", "opcional", "una_vez_por_turno", "restriccion"]
set_card("es28", abilities_es28, tags_es28)

# es280 Barbaros Enfurecidos
abilities_es280 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_if_no_other_dragon",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "count", "value": {"type": "filter", "filter": {"race": "Dragón", "controller": "self", "zone": "play"}}, "operator": "<=", "targetValue": 1},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si no controlas otro Dragón, se destruye al final del turno.",
        }
    ],
}
tags_es280 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es280", abilities_es280, tags_es280)

# es281 Dragon Nodriza
abilities_es281 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_copy",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"name": "Dragón Nodriza", "controller": "self"}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, puedes buscar otra copia en tu mazo y ponerla en tu mano.",
        }
    ],
}
tags_es281 = ["busca_mazo", "opcional", "trigger_al_entrar"]
set_card("es281", abilities_es281, tags_es281)

# es282 Dragonel
abilities_es282 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_only_block", "target": "self"},
            "text": "Sólo puede bloquear.",
        }
    ],
}
tags_es282 = ["restriccion"]
set_card("es282", abilities_es282, tags_es282)

# es283 Draco Aguila
abilities_es283 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Se considera imbloqueable.",
        }
    ],
}
tags_es283 = ["imbloqueable"]
set_card("es283", abilities_es283, tags_es283)

# es284 Caballeros Pictos
abilities_es284 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_if_opponent_knight",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"requires_opponent_card_in_play": {"race": "Caballero"}, "action": "attack"},
                "target": "self",
            },
            "text": "Sólo puede atacar si el oponente tiene un Caballero en juego.",
        }
    ],
}
tags_es284 = ["restriccion"]
set_card("es284", abilities_es284, tags_es284)

# es285 Dregon
abilities_es285 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_after_attack",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "attacked_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si es declarado atacante, debe ser destruido al final del turno.",
        }
    ],
}
tags_es285 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es285", abilities_es285, tags_es285)

# es286 Ravido
abilities_es286 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "attack_on_enter_destroy_eot",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "restriction", "restriction": "must_attack_this_turn", "target": "self"},
                    {"type": "destroy", "target": "self", "duration": "end_turn"},
                ],
            },
            "text": "Al entrar debe ser declarado atacante y se destruye al final del turno.",
        }
    ],
}
tags_es286 = ["apresurado", "destruye_objetivo", "trigger_al_entrar", "trigger_fin_turno"]
set_card("es286", abilities_es286, tags_es286)

# es287 Goblin
abilities_es287 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable_if_three",
            "type": "static",
            "condition": {"type": "count", "value": {"type": "filter", "filter": {"name": "Goblin", "controller": "self", "zone": "play"}}, "operator": ">=", "targetValue": 3},
            "effect": {"type": "restriction", "restriction": "unblockable", "target": {"type": "filter", "filter": {"name": "Goblin", "controller": "self"}}},
            "text": "Si controlas 3 Goblin, son imbloqueables.",
        }
    ],
}
tags_es287 = ["imbloqueable"]
set_card("es287", abilities_es287, tags_es287)

# es288 Hobglobin
abilities_es288 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "discard_one_each_end_step",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "effect": {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
            "text": "Al final de tu turno, debes descartar 1 carta.",
        }
    ],
}
tags_es288 = ["descarta_mano", "trigger_fin_turno"]
set_card("es288", abilities_es288, tags_es288)


conn.commit()
conn.close()
print("Updated batch: es28, es280-es288")








