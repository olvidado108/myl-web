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
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("anula", "Anula hechizos/efectos", "control", None),
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


# hd140 Crom Cruach
abilities_hd140 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "cannot_block",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "cannot_block", "target": "self"},
            "text": "No puede bloquear.",
        },
        {
            "id": "tutor_shadow_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "search",
                "location": "graveyard",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self", "cost": {"operator": "<=", "value": 2}}},
                "action": "put_in_hand",
                "amount": 1,
            },
            "optional": True,
            "text": "Al ser declarado atacante, puedes buscar un Sombra de coste 2 o menos en tu Cementerio y ponerlo en tu mano.",
        },
    ],
}
tags_hd140 = ["restriccion", "busca_mazo", "opcional"]
set_card("hd140", abilities_hd140, tags_hd140)

# hd141 Corff
abilities_hd141 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unblockable",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unblockable", "target": "self"},
            "text": "Imbloqueable.",
        },
        {
            "id": "boost_two_attackers",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "attack_line"}, "limit": 2},
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "text": "Cuando ataca, hasta 2 Aliados que lo acompañen ganan +1 a la fuerza hasta la Fase Final.",
        },
    ],
}
tags_hd141 = ["imbloqueable", "modifica_fuerza"]
set_card("hd141", abilities_hd141, tags_hd141)

# hd142 Cichol Gricenchos
abilities_hd142 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_from_grave",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "in_zone", "target": "self", "zone": "graveyard"}]},
            "cost": {"type": "pay_resources", "amount": 3},
            "effect": {"type": "put_in_play", "target": "self", "pay_cost": False},
            "optional": True,
            "text": "En Vigilia, si está en tu Cementerio, paga 3 Oros para jugarlo sin pagar su coste.",
        },
        {
            "id": "exile_top_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "exile", "target": {"type": "reference", "reference": "opponent.deck.top"}},
            "text": "Cuando entra, destierra la primera carta del mazo oponente.",
        },
    ],
}
tags_hd142 = ["paga_recursos", "pone_en_juego", "destierra_objetivo", "opcional", "trigger_al_entrar"]
set_card("hd142", abilities_hd142, tags_hd142)

# hd143 Caldero de Corff
abilities_hd143 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_top_if_attacked_with_shadows",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "attacked_this_turn", "target": "self"},
                    {
                        "type": "count",
                        "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self", "zone": "attack_line"}},
                        "operator": ">=",
                        "value": 2,
                    },
                ],
            },
            "effect": {"type": "exile", "target": {"type": "reference", "reference": "opponent.deck.top"}},
            "text": "Al final del turno, si atacaste y tienes 2+ Sombras en línea de ataque, destierra la primera carta del mazo oponente.",
        }
    ],
}
tags_hd143 = ["destierra_objetivo", "restriccion"]
set_card("hd143", abilities_hd143, tags_hd143)

# hd144 Morir de Pie
abilities_hd144 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando la juegues, destiérrala.",
        },
        {
            "id": "counter_non_ally_oro",
            "type": "activated",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "operator": ">=",
                "targetValue": 2,
            },
            "effect": {
                "type": "counter",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "opponent", "type": {"operator": "not_in", "value": ["oros", "allies"]}}}},
            "text": "Solo si controlas dos o más Aliados de una misma raza: anula una carta oponente que no sea Oro ni Aliado.",
        },
    ],
}
tags_hd144 = ["destierra_objetivo", "anula", "restriccion"]
set_card("hd144", abilities_hd144, tags_hd144)

# hd145 Martillo Pesado
abilities_hd145 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "type": {"operator": "!=", "value": "oros"}}}, "amount": 1},
            "optional": True,
            "text": "Cuando entra, puedes destruir una carta en juego que no sea Oro.",
        },
        {
            "id": "boost_carrier",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador gana +2 a la fuerza.",
        },
    ],
}
tags_hd145 = ["destruye_objetivo", "opcional", "modifica_fuerza", "trigger_al_entrar"]
set_card("hd145", abilities_hd145, tags_hd145)

# hd146 Aplastar Fomor
abilities_hd146 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando la juegues, destiérrala.",
        },
        {
            "id": "destroy_ally_and_copies",
            "type": "activated",
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}}, "destroyCopies": True},
            "text": "Destruye un Aliado y todas sus copias en juego.",
        },
    ],
}
tags_hd146 = ["destierra_objetivo", "destruye_objetivo"]
set_card("hd146", abilities_hd146, tags_hd146)

# hd147 Manzana Sidhe
abilities_hd147 = {
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
tags_hd147 = ["restriccion", "paga_recursos", "roba_cartas", "descarta_mano", "opcional"]
set_card("hd147", abilities_hd147, tags_hd147)

# hd148 Caravana de Los Muertos
abilities_hd148 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_low_cost_allies_from_grave",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "graveyard",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "cost": {"operator": "<=", "value": 1}}},
                        "action": "put_in_play",
                        "amount": 3,
                        "pay_cost": False,
                    },
                    {"type": "lose_ability", "target": {"type": "reference", "reference": "last_put_in_play_group"}, "duration": "while_in_play"},
                ],
            },
            "text": "Elige hasta tres Aliados de coste 1 o menos de tu Cementerio y juégalos sin pagar su coste; esos Aliados pierden su habilidad mientras estén en juego.",
        }
    ],
}
tags_hd148 = ["pone_en_juego", "mueve_zona", "restriccion"]
set_card("hd148", abilities_hd148, tags_hd148)

# hd149 Ojo Asesino
abilities_hd149 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_ally_vigilia",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}, "amount": 1},
            "text": "Solo en Vigilia: destruye un Aliado oponente.",
        }
    ],
}
tags_hd149 = ["destruye_objetivo", "restriccion"]
set_card("hd149", abilities_hd149, tags_hd149)


conn.commit()
conn.close()
print("Updated batch: hd140-hd149")








