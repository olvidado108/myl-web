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
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("baraja", "Baraja cartas", "control", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
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


# hd104 Boobrie
abilities_hd104 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "flashback_blocker",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}},
            "condition": {"type": "in_zone", "target": "self", "zone": "graveyard"},
            "cost": {"type": "pay_resources", "amount": 2},
            "effect": {
                "type": "put_in_play",
                "target": "self",
                "location": "defense_line",
                "controller": "self",
                "pay_cost": False,
                "as_blocker": True,
            },
            "optional": True,
            "text": "En respuesta a declarar ataque oponente, si está en tu Cementerio, paga 2: ponlo en tu defensa como bloqueador.",
        },
        {
            "id": "destroy_at_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "En la Fase Final, debe ser destruido.",
        },
    ],
}
tags_hd104 = ["paga_recursos", "mueve_zona", "opcional"]
set_card("hd104", abilities_hd104, tags_hd104)

# hd105 Rhiannon
abilities_hd105 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reveal_three_choose",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "reveal_top", "target": {"type": "reference", "reference": "controller.deck"}, "amount": 3},
                    {
                        "type": "choice",
                        "options": [
                            {
                                "type": "move_zone",
                                "target": {"type": "filter", "filter": {"type": "cards", "zone": "revealed", "controller": "self", "type": {"operator": "!=", "value": "allies"}}},
                                "location": "hand",
                                "amount": 1,
                            },
                            {
                                "type": "move_zone",
                                "target": {"type": "filter", "filter": {"type": "allies", "race": "Desafiante", "zone": "revealed", "controller": "self"}},
                                "location": "hand",
                            },
                        ],
                        "optional": True,
                    },
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "cards", "zone": "revealed", "controller": "self"}},
                        "location": "graveyard",
                    },
                ],
            },
            "text": "Al entrar, mira las 3 primeras: toma una que no sea Aliado o todos los Aliados Desafiante y ponlos en tu mano; el resto al Cementerio.",
        }
    ],
}
tags_hd105 = ["mueve_zona", "opcional", "trigger_al_entrar"]
set_card("hd105", abilities_hd105, tags_hd105)

# hd106 Wyrm Abismal
abilities_hd106 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "opponent_sac_on_shadow_death",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self"}}},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "amount": 1,
            },
            "text": "En respuesta a la destrucción de un Sombra propio, el oponente destruye uno de sus Aliados.",
        }
    ],
}
tags_hd106 = ["destruye_objetivo"]
set_card("hd106", abilities_hd106, tags_hd106)

# hd107 Caoranach
abilities_hd107 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_shadow_to_shuffle",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "race": "Sombra", "controller": "self", "exclude": "self"}}, "amount": 1},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, destruye otro Sombra propio para barajar 2 cartas de tu Cementerio.",
        },
        {
            "id": "play_from_grave",
            "type": "activated",
            "condition": {"type": "and", "conditions": [{"type": "phase", "value": "vigilia", "controller": "self"}, {"type": "in_zone", "target": "self", "zone": "graveyard"}]},
            "cost": {"type": "pay_resources", "amount": 4},
            "effect": {"type": "put_in_play", "target": "self", "controller": "self", "pay_cost": False},
            "optional": True,
            "text": "Si está en tu Cementerio, en Vigilia puedes pagar 4 Oros para jugarlo sin pagar su coste.",
        },
    ],
}
tags_hd107 = ["destruye_para_pagar", "baraja", "opcional", "una_vez_por_turno", "paga_recursos", "pone_en_juego"]
set_card("hd107", abilities_hd107, tags_hd107)

# hd108 Fergus
abilities_hd108 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_strongest_each_vigilia",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play", "sort": "force_desc", "limit": 1}}},
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, destruye el Aliado oponente de mayor fuerza.",
        }
    ],
}
tags_hd108 = ["destruye_objetivo", "una_vez_por_turno"]
set_card("hd108", abilities_hd108, tags_hd108)

# hd109 Pryderi
abilities_hd109 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede ser declarado atacante el turno que entra.",
        },
        {
            "id": "mill_three_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 3, "location": "deck"},
            "text": "Cuando entra, tu oponente bota 3 cartas.",
        },
    ],
}
tags_hd109 = ["apresurado", "bota_cartas", "trigger_al_entrar"]
set_card("hd109", abilities_hd109, tags_hd109)

# hd11 la Serpiente Negra
abilities_hd11 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "indestructible",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "indestructible", "target": "self"},
            "text": "Es indestructible.",
        },
        {
            "id": "shuffle_to_exile_two",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "shuffle", "target": {"type": "filter", "filter": {"type": "cards", "zone": "hand", "controller": "self"}}, "amount": 1, "location": "deck"},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "cards", "zone": "deck", "controller": "opponent"}}, "amount": 2},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, baraja 1 carta de tu mano para desterrar 2 cartas del mazo oponente.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_hd11 = ["restriccion", "baraja", "destierra_objetivo", "opcional", "una_vez_por_turno"]
set_card("hd11", abilities_hd11, tags_hd11)

# hd110 Cuchulain
abilities_hd110 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_other_to_prevent_destruction",
            "type": "response",
            "trigger": {"type": "destroyed", "target": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "exclude": "self"}}, "amount": 1},
            "effect": {"type": "prevent_destruction", "target": "self"},
            "optional": True,
            "text": "Si fuese a ser destruido, puedes destruir otro de tus Aliados para prevenirlo.",
        },
        {
            "id": "draw_on_deck_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self"},
            "effect": {"type": "draw_cards", "amount": 2, "target": "controller"},
            "optional": True,
            "text": "Si hace daño al mazo oponente, puedes robar 2 cartas.",
        },
    ],
}
tags_hd110 = ["destruye_para_pagar", "previene_dano", "roba_cartas", "opcional"]
set_card("hd110", abilities_hd110, tags_hd110)

# hd111 Aed Finn
abilities_hd111 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "group_in_final",
            "type": "activated",
            "condition": {"type": "phase", "value": "final", "controller": "self"},
            "effect": {"type": "move_zone", "target": "self", "location": "support_line"},
            "optional": True,
            "text": "En tu Fase Final puedes agrupar a Aed Finn.",
        }
    ],
}
tags_hd111 = ["mueve_zona", "opcional"]
set_card("hd111", abilities_hd111, tags_hd111)

# hd112 Dianan y Bechulle
abilities_hd112 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_per_copy",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "target": {"type": "filter", "filter": {"type": "allies", "name": "Dianan y Bechulle", "zone": "play"}}}},
            },
            "text": "Gana +1 a la fuerza por cada copia en juego.",
        }
    ],
}
tags_hd112 = ["modifica_fuerza"]
set_card("hd112", abilities_hd112, tags_hd112)


conn.commit()
conn.close()
print("Updated batch: hd104-hd112 y hd11")








