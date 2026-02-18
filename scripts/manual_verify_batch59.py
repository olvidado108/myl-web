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
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
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


# hd113 Slaine
abilities_hd113 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede ser declarado atacante el turno que entra.",
        },
        {
            "id": "opponent_sac_highest_on_death",
            "type": "triggered",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "sort": "force_desc", "limit": 1}}},
            "text": "Si es destruido, el oponente destruye su Aliado de mayor fuerza.",
        },
    ],
}
tags_hd113 = ["apresurado", "destruye_objetivo"]
set_card("hd113", abilities_hd113, tags_hd113)

# hd114 Conla
abilities_hd114 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_opponent_card_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "play", "cost": {"operator": "<=", "value": {"type": "math", "operation": "card_cost_minus", "value": 3}}}},
                "location": "deck",
                "amount": 1,
            },
            "optional": True,
            "text": "Cuando entra, baraja una carta oponente en juego de coste 3 o menos.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd114 = ["baraja", "opcional", "restriccion", "trigger_al_entrar"]
set_card("hd114", abilities_hd114, tags_hd114)

# hd115 Bran el Bendito
abilities_hd115 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "mill_all_on_combat_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self", "combat": True},
            "effect": {"type": "discard", "target": "all", "amount": 1, "location": "deck"},
            "text": "Si hace daño de combate al mazo oponente, todos los jugadores botan 1 carta.",
        },
    ],
}
tags_hd115 = ["apresurado", "bota_cartas"]
set_card("hd115", abilities_hd115, tags_hd115)

# hd116 Defensores Celtas
abilities_hd116 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "buff_defenders_this_turn_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "grant_ability_until",
                "duration": "end_turn",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Defensor", "controller": "self", "zone": "play"}},
                "value": {"type": "group", "effects": [{"type": "restriction", "restriction": "unblockable"}, {"type": "restriction", "restriction": "can_attack_on_enter"}]},
            },
            "text": "Cuando entra, los Defensores que controles este turno son imbloqueables y pueden atacar al entrar.",
        },
        {
            "id": "buff_defenders_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {
                "type": "grant_ability_until",
                "duration": "end_turn",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Defensor", "controller": "self", "zone": "play"}},
                "value": {"type": "group", "effects": [{"type": "restriction", "restriction": "unblockable"}, {"type": "restriction", "restriction": "can_attack_on_enter"}]},
            },
            "text": "Cuando sale del juego, los Defensores que controles este turno son imbloqueables y pueden atacar al entrar.",
        },
    ],
}
tags_hd116 = ["restriccion"]
set_card("hd116", abilities_hd116, tags_hd116)

# hd117 Goidel Glas
abilities_hd117 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "attack_requires_company",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {
                    "attack_requires": {
                        "type": "count",
                        "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play", "exclude": "self"}},
                        "operator": ">=",
                        "targetValue": 1,
                    }
                },
                "target": "self",
            },
            "text": "Solo puede ser declarado atacante si lo acompaña otro Aliado.",
        },
        {
            "id": "boost_if_two_attackers",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "attack_line"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "effect": {"type": "modify_force", "target": "self", "modifier": {"type": "add", "value": 1}, "duration": "end_turn"},
            "text": "Si ataca junto a 2 o más Aliados, gana +1 a la fuerza hasta la Fase Final.",
        },
    ],
}
tags_hd117 = ["restriccion", "modifica_fuerza"]
set_card("hd117", abilities_hd117, tags_hd117)

# hd118 Brian Boru
abilities_hd118 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar el turno que entra.",
        },
        {
            "id": "move_opponent_defender",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "move_zone", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "defense_line"}}, "location": "attack_line"},
            "optional": True,
            "text": "Al entrar, puedes mover un Aliado oponente de la defensa a la línea de ataque.",
        },
    ],
}
tags_hd118 = ["apresurado", "mueve_zona", "opcional", "trigger_al_entrar"]
set_card("hd118", abilities_hd118, tags_hd118)

# hd119 Piel de Lobo
abilities_hd119 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Piel de Lobo en juego.",
        },
        {
            "id": "draw_then_discard_on_defender_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": {"type": "filter", "filter": {"type": "allies", "race": "Defensor", "controller": "self"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "draw_cards", "amount": 1, "target": "controller"},
                    {"type": "discard", "target": "controller", "amount": 1, "location": "hand"},
                ],
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "Una vez por turno, cuando un Defensor entre bajo tu control, puedes robar 1 carta y luego descartar 1.",
        },
    ],
}
tags_hd119 = ["restriccion", "roba_cartas", "descarta_mano", "opcional", "una_vez_por_turno"]
set_card("hd119", abilities_hd119, tags_hd119)

# hd12 Conla
abilities_hd12 = abilities_hd114
tags_hd12 = tags_hd114
set_card("hd12", abilities_hd12, tags_hd12)

# hd120 Brigit
abilities_hd120 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "challengers_cannot_be_exiled",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "cannot_be_exiled",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self", "exclude": "self"}},
            },
            "text": "Tus otros Desafiantes no pueden ser desterrados.",
        },
        {
            "id": "challengers_indestructible",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "indestructible",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "controller": "self", "exclude": "self"}},
            },
            "text": "Tus otros Desafiantes son indestructibles.",
        },
    ],
}
tags_hd120 = ["restriccion"]
set_card("hd120", abilities_hd120, tags_hd120)

# hd121 Lugh
abilities_hd121 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
        {
            "id": "exile_opponent_graveyard",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "zone": "graveyard"}}},
            "optional": True,
            "text": "Cuando entra, puedes desterrar todas las cartas del Cementerio oponente.",
        },
    ],
}
tags_hd121 = ["restriccion", "destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("hd121", abilities_hd121, tags_hd121)


conn.commit()
conn.close()
print("Updated batch: hd113-hd121 y hd12")








