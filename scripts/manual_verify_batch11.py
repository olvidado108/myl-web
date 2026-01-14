import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", "Haste"),
    ("mira_mano_oponente", "Mira mano oponente", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
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


# es19 Espada Larga Legendaria
abilities_es19 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "draw_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "text": "Cuando entra en juego, roba 2 cartas de tu mazo castillo.",
        },
        {
            "id": "boost_equipped",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "El portador gana +1 a la fuerza.",
        },
    ],
}
tags_es19 = ["roba_cartas", "trigger_al_entrar", "modifica_fuerza"]
set_card("es19", abilities_es19, tags_es19)

# es190 Sir Lionel
abilities_es190 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "group_on_end_if_attack_line",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "zone", "value": "support_line", "target": "self"},
            "effect": {"type": "move_zone", "target": "self", "location": "defense_line"},
            "optional": True,
            "text": "Al final de tu turno, si está en línea de ataque, puedes agruparlo.",
        }
    ],
}
tags_es190 = ["mueve_zona", "trigger_fin_turno", "opcional"]
set_card("es190", abilities_es190, tags_es190)

# es191 Sir Hector
abilities_es191 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "opponent_discards_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand"},
            "text": "Cuando entra en juego, tu oponente descarta 1.",
        }
    ],
}
tags_es191 = ["descarta_mano", "trigger_al_entrar"]
set_card("es191", abilities_es191, tags_es191)

# es192 Sir Sagregor
abilities_es192 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_equip_weapons",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_equip_weapon", "target": "self"},
            "text": "No puede portar armas.",
        }
    ],
}
tags_es192 = ["restriccion"]
set_card("es192", abilities_es192, tags_es192)

# es193 Dragon Montaña
abilities_es193 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_if_attacked",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "attacked_this_turn", "target": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "Si atacó, debe ser destruido al final del turno.",
        }
    ],
}
tags_es193 = ["destruye_objetivo", "trigger_fin_turno"]
set_card("es193", abilities_es193, tags_es193)

# es194 Tortuga Dragon
abilities_es194 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        }
    ],
}
tags_es194 = ["apresurado"]
set_card("es194", abilities_es194, tags_es194)

# es195 Dragon Espia
abilities_es195 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_hand_on_deck_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck"},
            "effect": {"type": "reveal", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "hand"}}},
            "optional": True,
            "text": "Si hace daño al mazo castillo oponente, puedes ver su mano.",
        }
    ],
}
tags_es195 = ["mira_mano_oponente", "opcional"]
set_card("es195", abilities_es195, tags_es195)

# es196 Darg
abilities_es196 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_to_boost",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "optional": True,
            "usesPerTurn": 3,
            "text": "En tu fase de vigilia, hasta 3 veces por turno, puedes pagar 1 oro para que gane +1 fuerza hasta el final del turno.",
        }
    ],
}
tags_es196 = ["paga_recursos", "modifica_fuerza", "opcional"]
set_card("es196", abilities_es196, tags_es196)

# es197 Dragon Negro
abilities_es197 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "debuff_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "any"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Todos los Caballeros tienen -1 fuerza mientras esté en juego.",
        }
    ],
}
tags_es197 = ["modifica_fuerza"]
set_card("es197", abilities_es197, tags_es197)

# es198 Dragon de Mercurio
abilities_es198 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_by_dragons_in_grave",
            "type": "static",
            "condition": {"type": "phase", "value": "guerra_talismanes"},
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {
                    "type": "add",
                    "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "zone": "graveyard"}}},
                },
            },
            "text": "En guerra de Talismanes, gana +1 fuerza por cada Dragón en tu cementerio.",
        }
    ],
}
tags_es198 = ["modifica_fuerza"]
set_card("es198", abilities_es198, tags_es198)


conn.commit()
conn.close()
print("Updated batch: es19, es190-es198")






