import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("pierde_habilidad", "Pierde habilidad", "control", None),
    ("indestructible", "Indestructible", "defensivo", None),
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


# es135 Escudo Sidhe
abilities_es135 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "indestructible_when_blocking",
            "type": "triggered",
            "trigger": {"type": "blocks", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "gain_ability",
                "target": {"type": "reference", "reference": "equipped_to"},
                "value": {"restriction": "indestructible"},
                "duration": "end_turn",
            },
            "text": "Cuando el portador bloquea, no puede ser destruido hasta el final del turno.",
        }
    ],
}
tags_es135 = ["indestructible", "trigger_al_bloquear", "restriccion"]
set_card("es135", abilities_es135, tags_es135)

# es136 Malla de Mitril
abilities_es136 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_dragon",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón"}},
            },
            "text": "Sólo puede ser portada por un Dragón.",
        },
        {
            "id": "boost",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Gana +2 a la fuerza.",
        },
        {
            "id": "immune_talismans_destroy",
            "type": "static",
            "effect": {
                "type": "immunity",
                "target": {"type": "reference", "reference": "equipped_to"},
                "source": {"type": "filter", "filter": {"type": "talismanes"}},
            },
            "text": "No puede ser destruido por Talismanes.",
        },
    ],
}
tags_es136 = ["restriccion", "modifica_fuerza", "inmunidad"]
set_card("es136", abilities_es136, tags_es136)

# es137 Lanza de Los Dioses
abilities_es137 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_carrier",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 4},
            },
            "text": "Su portador gana +4 a la fuerza.",
        },
        {
            "id": "group_and_exile",
            "type": "response",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "not_destroyed_this_turn", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "reference", "reference": "equipped_to"},
                        "location": "defense_line",
                    },
                    {"type": "exile", "target": "self"},
                ],
            },
            "text": "Si no fue destruido en batalla, al final del turno agrúpalo a la línea de defensa y destierra la Lanza.",
        },
    ],
}
tags_es137 = ["modifica_fuerza", "mueve_zona", "destierra_objetivo", "trigger_fin_turno", "response"]
set_card("es137", abilities_es137, tags_es137)

# es138 Armadura del Sol
abilities_es138 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_per_talisman",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "talismanes", "controller": "any", "phase": "guerra_talismanes"}}},
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "text": "Por cada Talismán jugado en guerra de Talismanes, el portador gana +1 a la fuerza hasta el final del turno.",
        }
    ],
}
tags_es138 = ["modifica_fuerza", "trigger_juega_carta"]
set_card("es138", abilities_es138, tags_es138)

# es139 Espada de Dragon
abilities_es139 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_dragon",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón"}},
            },
            "text": "Su portador debe ser un Dragón.",
        },
        {
            "id": "boost",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "reference", "reference": "equipped_to"},
                "modifier": {"type": "add", "value": 2},
            },
            "text": "Gana +2 a la fuerza.",
        },
        {
            "id": "exile_to_silence_card",
            "type": "activated",
            "condition": {"phase": "main"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "cards", "zone": "play", "controller": "any"}},
                "duration": "end_turn",
            },
            "optional": True,
            "text": "En tu fase de vigilia, destierra Espada Dragón para anular la habilidad de una carta en juego hasta el final del turno.",
        },
    ],
}
tags_es139 = ["restriccion", "modifica_fuerza", "destierra_para_pagar", "pierde_habilidad", "opcional"]
set_card("es139", abilities_es139, tags_es139)

# es14 Bola de Fuego Legendaria
abilities_es14 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_non_oro",
            "type": "activated",
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "exclude": {"type": "oros"}}},
            },
            "text": "Destruye una carta en juego, que no sea un oro.",
        }
    ],
}
tags_es14 = ["destruye_objetivo"]
set_card("es14", abilities_es14, tags_es14)

# es140 Stonehage
abilities_es140 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "oros_lose_abilities",
            "type": "static",
            "effect": {
                "type": "lose_ability",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "any"}},
            },
            "text": "Mientras está en juego, los oros en juego pierden sus habilidades.",
        }
    ],
}
tags_es140 = ["pierde_habilidad", "restriccion"]
set_card("es140", abilities_es140, tags_es140)

# es141 Totem Maldito
abilities_es141 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_blocker",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": "opponent"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "zone": "defense_line", "controller": "opponent"}},
                        "location": "defense_line",
                        "as_controller": "opponent",
                        "amount": 1,
                    },
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En respuesta a un ataque oponente y una vez por turno, elige un aliado en su línea de defensa para bloquear. Si no es destruido, vuelve a la defensa al final del turno (implícito).",
        }
    ],
}
tags_es141 = ["mueve_zona", "trigger_al_atacar", "opcional", "una_vez_por_turno", "response"]
set_card("es141", abilities_es141, tags_es141)

# es142 Totem de Fe
abilities_es142 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "limit_talismans_war",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "limit_talismans_per_turn",
                "value": 1,
                "context": "guerra_de_talismanes",
            },
            "text": "En guerra de Talismanes, cada jugador sólo puede jugar un Talismán.",
        }
    ],
}
tags_es142 = ["restriccion"]
set_card("es142", abilities_es142, tags_es142)

# es143 Totem de Runas Elficas
abilities_es143 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_blocker_temp",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense_line"}},
                "location": "attack_line",
                "as_controller": "self",
                "duration": "end_turn",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En respuesta a declarar tu ataque y una vez por turno, elige un Aliado oponente y ponlo en tu línea de ataque. Si no es destruido, al final del turno vuelve a la defensa del oponente (implícito).",
        }
    ],
}
tags_es143 = ["mueve_zona", "trigger_al_atacar", "opcional", "una_vez_por_turno", "response"]
set_card("es143", abilities_es143, tags_es143)

conn.commit()
conn.close()
print("Updated batch: es135-es143")









