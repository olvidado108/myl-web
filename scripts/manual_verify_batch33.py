import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("restriccion", "Restricción/regla", "control", None),
    ("destierra_objetivo", "Destierra objetivo", "removal", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("baraja", "Baraja cartas", "control", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("una_vez_por_turno", "Limitado por turno", "triggers", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("descarta_mano", "Descarta de mano", "control", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("copia_habilidad", "Copia habilidad/efecto", "soporte", None),
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


# es389 Morgana
abilities_es389 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener una Morgana en juego.",
        },
        {
            "id": "sac_to_exile_once",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}}, "amount": 1},
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}, "amount": 1},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puedes destruir un aliado propio para desterrar un aliado oponente.",
        },
    ],
}
tags_es389 = ["restriccion", "destierra_objetivo", "destruye_para_pagar", "opcional", "una_vez_por_turno"]
set_card("es389", abilities_es389, tags_es389)

# es39 Mercaderes
abilities_es39 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "move_to_block",
            "type": "response",
            "trigger": {"type": "declared_attacker", "target": "opponent"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": "self", "from": "reserve", "to": "defense_line"},
                    {"type": "modify_force", "target": "self", "modifier": {"type": "set", "value": 3}, "duration": "end_turn"},
                ],
            },
            "optional": True,
            "text": "En respuesta a un ataque, puedes moverlo a tu defensa; se considera aliado bloqueador de fuerza 3.",
        },
        {
            "id": "destroy_at_end",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "En tu Fase Final, destrúyelo (si no, vuelve a su zona de Oro).",
        },
    ],
}
tags_es39 = ["mueve_zona", "modifica_fuerza", "opcional", "destruye_objetivo"]
set_card("es39", abilities_es39, tags_es39)

# es390 Nimue
abilities_es390 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "copy_faerie_from_grave",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"type": "copy_from_graveyard", "race": "Faerie"}, "duration": "end_turn"},
            "optional": True,
            "oncePerTurn": True,
            "text": "En Vigilia, una vez por turno, puede convertirse en copia de un Faerie de tu cementerio hasta la Fase Final.",
        }
    ],
}
tags_es390 = ["copia_habilidad", "opcional", "una_vez_por_turno"]
set_card("es390", abilities_es390, tags_es390)

# es391 Taliesin
abilities_es391 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener un Taliesin en juego.",
        },
        {
            "id": "play_faerie_for_free",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self"}},
                "action": "put_in_play",
                "pay_cost": False,
            },
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Aliado Faerie en tu mazo y jugarlo sin pagar su coste.",
        },
    ],
}
tags_es391 = ["restriccion", "busca_mazo", "mueve_zona", "opcional", "pone_en_juego", "trigger_al_entrar"]
set_card("es391", abilities_es391, tags_es391)

# es392 Yvain de Leon
abilities_es392 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "recover_weapon_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "search", "location": "graveyard", "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}}, "action": "put_in_hand"},
            "optional": True,
            "text": "Cuando entra en juego, puedes buscar un Arma en tu Cementerio y ponerla en tu mano.",
        },
        {
            "id": "cheaper_knight_weapons",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "armas", "controller": "self", "equip_target_race": "Caballero"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Jugar Armas en tus Caballeros cuesta 1 Oro menos.",
        },
    ],
}
tags_es392 = ["busca_mazo", "mueve_zona", "opcional", "modifica_coste"]
set_card("es392", abilities_es392, tags_es392)

# es393 Desleal
abilities_es393 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_opponent_ally",
            "type": "activated",
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}}},
            "text": "Destierra un Aliado oponente.",
        }
    ],
}
tags_es393 = ["destierra_objetivo"]
set_card("es393", abilities_es393, tags_es393)

# es394 Cruz Templaria
abilities_es394 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_tutor_play",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                        "action": "put_in_play",
                    },
                    {
                        "type": "delayed_trigger",
                        "trigger": {"type": "phase_start", "phase": "final", "target": "controller"},
                        "effect": {"type": "exile", "target": {"type": "reference", "reference": "last_put_in_play"}},
                    },
                ],
            },
            "optional": True,
            "text": "En tu Vigilia, destiérrala: busca un Aliado y juégalo pagando su coste. En la Fase Final, ese Aliado debe ser desterrado.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es394 = ["destierra_para_pagar", "busca_mazo", "pone_en_juego", "opcional", "destierra_objetivo", "restriccion"]
set_card("es394", abilities_es394, tags_es394)

# es395 y Ddraig Aur
abilities_es395 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "force_for_each_dragon",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "add", "value": {"type": "count", "value": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "controller": "self", "zone": "play"}}}},
            },
            "text": "Gana +1 fuerza por cada Dragón que controles.",
        }
    ],
}
tags_es395 = ["modifica_fuerza"]
set_card("es395", abilities_es395, tags_es395)

# es396 Aibell
abilities_es396 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_small_faeries_on_attack",
            "type": "triggered",
            "trigger": {"type": "declared_attacker", "target": "self"},
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "cost": {"operator": "<=", "value": 1}, "controller": "self"}},
                "modifier": {"type": "add", "value": 1},
                "duration": "end_turn",
            },
            "text": "Cuando es declarada atacante, tus Faerie de coste 1 o menos ganan +1 fuerza hasta la Fase Final.",
        }
    ],
}
tags_es396 = ["modifica_fuerza"]
set_card("es396", abilities_es396, tags_es396)

# es397 Sir Galahad
abilities_es397 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Sir Galahad puede atacar cuando entra en juego.",
        },
        {
            "id": "discard_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "target": "opponent", "location": "deck", "source": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand", "random": True},
            "text": "Si hace daño al mazo oponente, descarta 1 carta al azar de su mano.",
        },
    ],
}
tags_es397 = ["apresurado", "descarta_mano", "trigger_al_entrar"]
set_card("es397", abilities_es397, tags_es397)


conn.commit()
conn.close()
print("Updated batch: es389-es397 y es39")






