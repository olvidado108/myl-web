import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags usados
needed_tags = [
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("imbloqueable", "Imbloqueable", "defensivo", None),
    ("baraja", "Baraja cartas", "control", None),
    ("restriccion", "Restricción/regla", "control", None),
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


# es126 Ellyllon
abilities_es126 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "text": "Cuando Ellyllon entra en juego, tu oponente bota 2 cartas.",
        },
        {
            "id": "mill_on_leave",
            "type": "triggered",
            "trigger": {"type": "leaves_play", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 2, "location": "deck"},
            "text": "Cuando Ellyllon sale del juego, tu oponente bota 2 cartas.",
        },
    ],
}
tags_es126 = ["bota_cartas", "trigger_al_entrar", "trigger_al_salir"]
set_card("es126", abilities_es126, tags_es126)

# es127 la Traicion de Lancelot
abilities_es127 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sacrifice_to_mill",
            "type": "activated",
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": {"type": "reference", "reference": "destroyed_card.force"},
                "location": "deck",
            },
            "optional": True,
            "text": "Destruye uno de tus Aliados para que tu oponente bote tantas cartas como fuerza tenga el Aliado.",
        }
    ],
}
tags_es127 = ["destruye_para_pagar", "bota_cartas", "opcional"]
set_card("es127", abilities_es127, tags_es127)

# es128 la Mirada de Mordred
abilities_es128 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "retreat_and_block",
            "type": "response",
            "trigger": {"type": "declared_blocker", "target": "controller"},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "move_zone",
                        "target": {"type": "filter", "filter": {"type": "allies", "zone": "attack_line", "controller": "self"}},
                        "location": "defense_line",
                    },
                    {
                        "type": "gain_ability",
                        "target": {"type": "filter", "filter": {"type": "allies", "zone": "defense_line", "controller": "self"}},
                        "value": {"restriction": "can_be_declared_blocker"},
                        "duration": "end_turn",
                    },
                ],
            },
            "text": "En respuesta a declarar tu bloqueo, tus Aliados en línea de ataque vuelven a defensa y pueden ser declarados bloqueadores.",
        }
    ],
}
tags_es128 = ["mueve_zona", "restriccion", "response"]
set_card("es128", abilities_es128, tags_es128)

# es129 Claymore
abilities_es129 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_on_damage",
            "type": "triggered",
            "trigger": {"type": "damage", "causedBy": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "move_zone",
                "target": {
                    "type": "filter",
                    "filter": {"type": "cards", "controller": "opponent", "zone": "play", "not": {"type": "oros"}},
                },
                "location": "hand",
                "amount": 2,
            },
            "optional": True,
            "text": "Si su portador hace daño, puedes subir dos cartas en juego de tu oponente a su mano. No afecta a oros.",
        }
    ],
}
tags_es129 = ["mueve_zona", "opcional", "trigger_recibe_dano"]
set_card("es129", abilities_es129, tags_es129)

# es13 Dragon Dorado (variante)
abilities_es13 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique_self",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Carta única.",
        },
        {
            "id": "exile_on_play",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {"type": "exile", "target": "self"},
            "text": "Cuando juegues a Dragón Dorado, destiérralo.",
        },
        {
            "id": "counter_non_oro",
            "type": "triggered",
            "trigger": {"type": "card_played", "target": "self"},
            "effect": {
                "type": "counter",
                "target": {
                    "type": "filter",
                    "filter": {"type": "cards", "controller": "opponent", "not_type": "oros"},
                },
            },
            "text": "Anula una carta que no sea Oro.",
        },
    ],
}
tags_es13 = ["restriccion", "destierra_objetivo", "anula", "trigger_juega_carta"]
set_card("es13", abilities_es13, tags_es13)

# es130 Torre de Campa
abilities_es130 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "carrier_unblockable",
            "type": "static",
            "effect": {"type": "gain_ability", "target": {"type": "reference", "reference": "equipped_to"}, "value": {"restriction": "unblockable"}},
            "text": "El portador se considera imbloqueable.",
        },
        {
            "id": "shuffle_and_destroy_after_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "shuffle",
                        "target": {"type": "reference", "reference": "equipped_to"},
                        "location": "deck",
                        "amount": 1,
                    },
                    {"type": "destroy", "target": "self"},
                ],
            },
            "text": "Después de atacar, el aliado es barajado en el Mazo Castillo y el arma se destruye.",
        },
    ],
}
tags_es130 = ["imbloqueable", "baraja", "destruye_objetivo", "trigger_al_atacar", "mueve_zona"]
set_card("es130", abilities_es130, tags_es130)

# es131 Ataque Sorpresa
abilities_es131 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reflect_from_opponent_ally",
            "type": "response",
            "trigger": {
                "type": "damage_resolved",
                "target": {"type": "reference", "reference": "controller.deck"},
                "causedBy": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}},
            },
            "effect": {"type": "damage", "target": "opponent", "amount": {"type": "reference", "reference": "damage_amount"}},
            "text": "En respuesta a resolver el daño, el oponente recibe el mismo daño hecho a tu mazo castillo por uno de sus Aliados.",
        }
    ],
}
tags_es131 = ["hace_dano", "trigger_recibe_dano", "response"]
set_card("es131", abilities_es131, tags_es131)

# es132 Woodhage
abilities_es132 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "totem_cost_increase",
            "type": "static",
            "effect": {
                "type": "modify_cost",
                "target": {"type": "filter", "filter": {"type": "totems", "controller": "any"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras está en juego, bajar Tótem cuesta +1 oro.",
        }
    ],
}
tags_es132 = ["modifica_coste", "restriccion"]
set_card("es132", abilities_es132, tags_es132)

# es133 el Circulo Eterno
abilities_es133 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "all_unique_non_oro",
            "type": "static",
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "cards", "controller": "any", "zone": "play", "not": {"type": "oros"}}},
                "value": {"type": "unique"},
            },
            "text": "Mientras está en juego, todas las cartas se consideran Carta única (excepto oros).",
        },
        {
            "id": "clean_duplicates_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "cards",
                        "controller": "any",
                        "zone": "play",
                        "not": {"type": "oros"},
                        "duplicate_name": True,
                    },
                },
            },
            "text": "Al entrar, si algún jugador tiene 2 o más copias de una carta, deja solo una y destruye las demás (no afecta oros).",
        },
    ],
}
tags_es133 = ["restriccion", "destruye_objetivo", "trigger_al_entrar"]
set_card("es133", abilities_es133, tags_es133)

# es134 Espada de Cristal
abilities_es134 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "only_faerie_carrier",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": "equip_only_to",
                "target": "self",
                "value": {"type": "filter", "filter": {"type": "allies", "race": "Faerie"}},
            },
            "text": "Su portador sólo puede ser un Faerie.",
        },
        {
            "id": "destroy_to_counter_talisman",
            "type": "response",
            "trigger": {"type": "card_played", "target": {"type": "filter", "filter": {"type": "talismanes", "controller": "opponent"}}},
            "cost": {"type": "destroy", "target": "self"},
            "effect": {"type": "counter", "target": {"type": "reference", "reference": "trigger.card"}},
            "optional": True,
            "text": "Si el oponente juega un Talismán, puedes destruir Espada de Cristal para anularlo.",
        },
    ],
}
tags_es134 = ["restriccion", "anula", "destruye_para_pagar", "trigger_juega_carta", "opcional"]
set_card("es134", abilities_es134, tags_es134)

conn.commit()
conn.close()
print("Updated batch: es126-es134")


