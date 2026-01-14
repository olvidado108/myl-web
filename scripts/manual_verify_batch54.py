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
    ("busca_mazo", "Busca en mazo", "tutor", None),
    ("pone_en_juego", "Pone en juego", "soporte", None),
    ("opcional", "Efecto opcional", "triggers", "Texto incluye “puedes”"),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("roba_cartas", "Roba cartas", "recursos", None),
    ("descarta_mano", "Descarta desde mano", "control", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("apresurado", "Puede atacar al entrar", "ofensivo", None),
    ("mueve_zona", "Mueve zona", "soporte", None),
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


# es69 Mercaderes
abilities_es69 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "jump_in_front",
            "type": "response",
            "trigger": {"type": "attack_declared", "target": "opponent"},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": "self", "location": "defense_line"},
                    {"type": "modify_force", "target": "self", "modifier": {"type": "set", "value": 3}, "duration": "end_turn"},
                ],
            },
            "optional": True,
            "text": "En respuesta a la declaración de ataque oponente, puedes moverlo a tu defensa; se considera bloqueador de fuerza 3.",
        },
        {
            "id": "destroy_at_final",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "effect": {"type": "destroy", "target": "self"},
            "text": "En tu Fase Final, destrúyelo.",
        },
        {
            "id": "return_to_gold_if_alive",
            "type": "triggered",
            "trigger": {"type": "phase_end", "phase": "final", "controller": "self"},
            "condition": {"type": "is_in_play", "target": "self"},
            "effect": {"type": "move_zone", "target": "self", "location": "reserve"},
            "text": "Si no es destruido, vuelve a la zona de Oro desde donde fue movido.",
        },
    ],
}
tags_es69 = ["mueve_zona", "opcional"]
set_card("es69", abilities_es69, tags_es69)

# es7 Cathach
abilities_es7 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "shuffle_two_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "shuffle",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "self", "zone": "graveyard"}},
                "amount": 2,
                "location": "deck",
            },
            "optional": True,
            "text": "Cuando entra, puedes barajar 2 cartas de tu Cementerio en tu mazo.",
        },
        {
            "id": "debuff_if_only_dragons",
            "type": "static",
            "condition": {
                "type": "all",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                "condition": {"type": "race", "value": "Dragón"},
            },
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent", "zone": "play"}},
                "modifier": {"type": "add", "value": -1},
            },
            "text": "Los Aliados oponentes pierden 1 a la fuerza mientras solo controles Dragones.",
        },
    ],
}
tags_es7 = ["baraja", "modifica_fuerza", "opcional", "restriccion", "trigger_al_entrar"]
set_card("es7", abilities_es7, tags_es7)

# es70 Cruz Templaria
abilities_es70 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_tutor_ally",
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
                        "trigger": {"type": "phase_end", "phase": "final", "target": "controller"},
                        "effect": {"type": "exile", "target": {"type": "reference", "reference": "last_put_in_play"}},
                    },
                ],
            },
            "optional": True,
            "text": "En Vigilia, puedes desterrarla para buscar un Aliado y jugarlo pagando su coste. En la Fase Final, destierra ese Aliado.",
        },
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
    ],
}
tags_es70 = ["exilia_para_pagar", "busca_mazo", "pone_en_juego", "destierra_objetivo", "opcional", "restriccion"]
set_card("es70", abilities_es70, tags_es70)

# es71 Dragones
abilities_es71 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Solo puedes tener un Dragones en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Solo puede ser jugado desde tu mano.",
        },
        {
            "id": "generate_for_big_dragons",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {"type": "generate_resources", "amount": 2, "restriction": {"type": "filter", "filter": {"type": "allies", "race": "Dragón", "cost": {"operator": ">=", "value": 4}}}},
            "optional": True,
            "text": "En Vigilia, puedes pagarlo para generar 2 Oros para Aliados Dragón de coste 4 o más.",
        },
    ],
}
tags_es71 = ["restriccion", "paga_recursos", "genera_recursos", "opcional"]
set_card("es71", abilities_es71, tags_es71)

# es72 Sir Balin
abilities_es72 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "no_weapon_limit",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "no_weapon_limit", "target": "self"},
            "text": "No tiene límite de Armas.",
        },
        {
            "id": "attack_only_with_weapon",
            "type": "static",
            "effect": {"type": "restriction", "restriction": {"attack_requires": {"type": "filter", "filter": {"type": "armas", "controller": "self", "zone": "play"}, "operator": ">=", "value": 1}}, "target": "self"},
            "text": "Solo puede atacar si controlas una o más Armas.",
        },
        {
            "id": "draw_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self"},
            "effect": {"type": "draw_cards", "amount": 1, "target": "controller"},
            "text": "Si hace daño al mazo castillo oponente, roba una carta.",
        },
    ],
}
tags_es72 = ["restriccion", "roba_cartas"]
set_card("es72", abilities_es72, tags_es72)

# es73 Criatura Familiar
abilities_es73 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "play_from_grave_if_only_faeries",
            "type": "activated",
            "condition": {
                "type": "and",
                "conditions": [
                    {"type": "phase", "value": "vigilia", "controller": "self"},
                    {
                        "type": "all",
                        "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "zone": "play"}},
                        "condition": {"type": "race", "value": "Faerie"},
                    },
                ],
            },
            "cost": {"type": "group", "costs": [{"type": "discard", "target": "controller", "amount": 1, "location": "hand"}, {"type": "pay_resources", "amount": 2}]},
            "effect": {"type": "move_zone", "target": "self", "location": "play", "controller": "self"},
            "optional": True,
            "text": "En Vigilia, si solo controlas Aliados Faerie, descarta 1 y paga 2 Oros para jugarla desde tu Cementerio.",
        }
    ],
}
tags_es73 = ["paga_recursos", "descarta_mano", "pone_en_juego", "opcional", "restriccion"]
set_card("es73", abilities_es73, tags_es73)

# es74 Juramento Ferrico
abilities_es74 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "search_and_play_weapon",
            "type": "activated",
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "search",
                        "location": "deck",
                        "target": {"type": "filter", "filter": {"type": "armas", "controller": "self"}},
                        "action": "put_in_play",
                        "pay_cost": False,
                        "equip_to": {"type": "filter", "filter": {"type": "allies", "controller": "self"}},
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "reference", "reference": "equipped_to"},
                        "value": {"restriction": "can_attack_on_enter"},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "Busca un Arma en tu mazo o Cementerio y juégala en un Aliado reduciendo su coste en 1 Oro. El portador puede atacar este turno.",
        }
    ],
}
tags_es74 = ["busca_mazo", "pone_en_juego", "apresurado"]
set_card("es74", abilities_es74, tags_es74)

# es75 Sir Tristan
abilities_es75 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_card_from_grave",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard"}},
                "location": "hand",
                "amount": 1,
            },
            "text": "Cuando entra en juego, busca una carta en tu Cementerio y ponla en tu mano.",
        }
    ],
}
tags_es75 = ["busca_mazo", "mueve_zona", "trigger_al_entrar"]
set_card("es75", abilities_es75, tags_es75)

# es76 Sir Galahad
abilities_es76 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "can_attack_on_enter",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "can_attack_on_enter", "target": "self"},
            "text": "Puede atacar cuando entra en juego.",
        },
        {
            "id": "discard_random_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 1, "location": "hand", "random": True},
            "optional": True,
            "text": "Si hace daño al mazo oponente, puedes descartarle 1 al azar.",
        },
    ],
}
tags_es76 = ["apresurado", "descarta_mano", "opcional"]
set_card("es76", abilities_es76, tags_es76)

# es77 Federico Barbarroja
abilities_es77 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "no_weapon_limit",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "no_weapon_limit", "target": "self"},
            "text": "No tiene límite de Armas.",
        },
        {
            "id": "tutor_on_deck_damage",
            "type": "triggered",
            "trigger": {"type": "damage_to_deck", "target": "opponent", "source": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "allies", "controller": "self", "force": {"operator": "==", "value": {"type": "reference", "reference": "self.force"}}}},
                "action": "put_in_play",
                "controller": "self",
                "destination": "defense_line",
            },
            "optional": True,
            "text": "Si hace daño al mazo oponente, puedes buscar un Aliado de igual fuerza en tu mazo y ponerlo en tu defensa.",
        },
    ],
}
tags_es77 = ["restriccion", "busca_mazo", "pone_en_juego", "opcional"]
set_card("es77", abilities_es77, tags_es77)


conn.commit()
conn.close()
print("Updated batch: es69-es77")






