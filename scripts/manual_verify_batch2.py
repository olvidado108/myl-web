import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

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

# es103 Jerusalén
abilities_es103 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "skip_grouping_phase",
            "type": "static",
            "effect": {"type": "skip_phase", "phase": "grouping"},
            "text": "Mientras Jerusalén está en juego, los jugadores se saltan la Fase de Agrupación.",
        }
    ],
}
tags_es103 = ["salta_fase", "restriccion"]
set_card("es103", abilities_es103, tags_es103)

# es104 Jaques de Molay
abilities_es104 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "haste_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"restriction": "can_attack_on_enter"}},
            "text": "Jaques de Molay puede atacar cuando entra en juego.",
        },
        {
            "id": "mill_talismans_on_attack",
            "type": "triggered",
            "trigger": {"type": "attacks", "target": "self"},
            "effect": {
                "type": "search",
                "location": "deck",
                "target": {"type": "filter", "filter": {"type": "talismanes", "controller": "opponent"}},
                "amount": 2,
                "action": "put_in_graveyard",
            },
            "text": "Si ataca, busca en el Mazo Castillo de tu oponente 2 Talismanes y envíalos al Cementerio.",
        },
    ],
}
tags_es104 = ["apresurado", "busca_mazo", "mueve_zona", "bota_cartas", "trigger_al_atacar"]
set_card("es104", abilities_es104, tags_es104)

# es105 Siroco
abilities_es105 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "steal_small_ally",
            "type": "activated",
            "condition": {"phase": "main"},
            "effect": {
                "type": "move_zone",
                "from": "opponent_graveyard",
                "to": "play",
                "target": {
                    "type": "filter",
                    "filter": {"type": "allies", "controller": "opponent", "force": {"operator": "<=", "value": 3}},
                },
                "as_controller": "self",
                "zone": "defense",
            },
            "text": "En tu Fase de Vigilia, busca en el Cementerio oponente un aliado de fuerza 3 o menos y ponlo en tu Línea de Defensa (bajo tu control).",
        }
    ],
}
tags_es105 = ["mueve_zona", "pone_en_juego"]
set_card("es105", abilities_es105, tags_es105)

# es106 Mesa Redonda
abilities_es106 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_oro",
            "type": "response",
            "trigger": {"type": "destroyed", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {"type": "filter", "filter": {"type": "oros", "controller": "opponent"}},
                "amount": 1,
            },
            "text": "En respuesta a que Mesa Redonda sea destruido, destruye 1 oro oponente.",
        }
    ],
}
tags_es106 = ["destruye_objetivo", "trigger_destruido"]
set_card("es106", abilities_es106, tags_es106)

# es107 el Obispo de Lodinium
abilities_es107 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "mill3_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "discard", "target": "opponent", "amount": 3, "location": "deck"},
            "text": "Cuando El Obispo De Londinium entra en juego, tu oponente bota 3 cartas.",
        }
    ],
}
tags_es107 = ["bota_cartas", "trigger_al_entrar"]
set_card("es107", abilities_es107, tags_es107)

# es108 Arca de la Alianza
abilities_es108 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_destroyed_this_turn",
            "type": "response",
            "trigger": {"type": "turn_end"},
            "effect": {
                "type": "put_in_play",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "cards",
                        "controller": "self",
                        "zone": "graveyard",
                        "destroyedThisTurn": True,
                        "cardType": {"operator": "in", "value": ["allies", "armas", "oros", "totems"]},
                    },
                },
            },
            "text": "En respuesta a finalizar un turno, devuelve al juego todos tus aliados, armas, oros y tótem destruidos este turno.",
        }
    ],
}
tags_es108 = ["pone_en_juego", "mueve_zona", "trigger_fin_turno", "response"]
set_card("es108", abilities_es108, tags_es108)

# es109 Ataque de Aliento
abilities_es109 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "reflect_deck_damage",
            "type": "response",
            "trigger": {"type": "damage_resolved", "target": {"type": "reference", "reference": "controller.deck"}},
            "effect": {"type": "damage", "target": "opponent", "amount": {"type": "reference", "reference": "damage_amount"}},
            "text": "En respuesta a resolver el daño, tu oponente recibe el mismo daño hecho a tu mazo castillo.",
        }
    ],
}
tags_es109 = ["hace_dano", "trigger_recibe_dano", "response"]
set_card("es109", abilities_es109, tags_es109)

# es11 Duque Godofredo Bob
abilities_es11 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_knights",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
                "modifier": {"type": "add", "value": 1},
            },
            "text": "Mientras Duque Godofredo esté en juego, todos tus caballeros ganan +1 a la fuerza.",
        }
    ],
}
tags_es11 = ["modifica_fuerza"]
set_card("es11", abilities_es11, tags_es11)

# es110 la Espada En la Piedra
abilities_es110 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "knights_cannot_attack_without_arthur",
            "type": "static",
            "condition": {
                "type": "count",
                "value": {"type": "filter", "filter": {"type": "allies", "name": "Rey Arturo Pedragón", "controller": "self", "zone": "play"}},
                "operator": "==",
                "targetValue": 0,
            },
            "effect": {
                "type": "restriction",
                "restriction": "cannot_attack",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}},
            },
            "text": "Si el Rey Arturo Pedragón no está en juego, los Caballeros no pueden atacar (se asume mientras persista la condición).",
        }
    ],
}
tags_es110 = ["no_puede_atacar", "restriccion"]
set_card("es110", abilities_es110, tags_es110)

# es111 Barco
abilities_es111 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "faeries_unblockable_if_merlin",
            "type": "activated",
            "condition": {"phase": "vigilia", "controller": "self"},
            "effect": {
                "type": "gain_ability",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Faerie", "controller": "self"}},
                "value": {"restriction": "unblockable"},
                "duration": "end_turn",
                "condition": {"type": "exists", "value": {"type": "filter", "filter": {"type": "allies", "name": "Merlín", "controller": "self"}}},
            },
            "text": "Si tienes a Merlín en juego, tus faeries son imbloqueables hasta el final del turno.",
        }
    ],
}
tags_es111 = ["imbloqueable", "opcional"]
set_card("es111", abilities_es111, tags_es111)

# es112 Ma'arrat An Numan
abilities_es112 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_all_allies",
            "type": "activated",
            "effect": {"type": "exile", "target": {"type": "filter", "filter": {"type": "allies", "controller": "any", "zone": "play"}}},
            "text": "Destierra todos los aliados en juego.",
        }
    ],
}
tags_es112 = ["destierra_objetivo", "mueve_zona"]
set_card("es112", abilities_es112, tags_es112)

# es113 Cornelius de York
abilities_es113 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_self_destroy_knight",
            "type": "activated",
            "condition": {"phase": "guerra_de_talismanes"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "destroy",
                "target": {
                    "type": "filter",
                    "filter": {
                        "type": "allies",
                        "race": "Caballero",
                        "controller": "opponent",
                        "force": {"operator": "<=", "value": {"type": "reference", "reference": "self.force"}},
                    },
                },
            },
            "optional": True,
            "text": "En guerra de Talismanes, puedes desterrar a Cornelius de York para destruir un Caballero oponente de igual o menor fuerza.",
        }
    ],
}
tags_es113 = ["destierra_para_pagar", "destruye_objetivo", "opcional"]
set_card("es113", abilities_es113, tags_es113)

# es114 Sir Lancelot
abilities_es114 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "immunity_talismans",
            "type": "static",
            "effect": {"type": "immunity", "target": "self", "source": {"type": "filter", "filter": {"type": "talismanes"}}},
            "text": "No puede ser afectado por Talismanes.",
        },
        {
            "id": "no_weapon_limit",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "no_weapon_limit", "target": "self"},
            "text": "No tiene límite de armas.",
        },
        {
            "id": "weapon_force_bonus",
            "type": "static",
            "effect": {
                "type": "modify_force",
                "target": "self",
                "modifier": {"type": "per_equipped_weapon", "value": 2},
            },
            "text": "Por cada arma que porte, gana +2 a la fuerza.",
        },
    ],
}
tags_es114 = ["inmunidad", "equipa_armas_extra", "modifica_fuerza"]
set_card("es114", abilities_es114, tags_es114)

# es115 Sir Gawein
abilities_es115 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "silence_talismans",
            "type": "activated",
            "condition": {"phase": "guerra_de_talismanes"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "restriction",
                "restriction": "cannot_play_talismans",
                "target": "all",
                "duration": "end_turn",
            },
            "text": "En guerra de Talismanes, destierra a Sir Gawein para que no se puedan jugar Talismanes hasta el final del turno.",
        }
    ],
}
tags_es115 = ["destierra_para_pagar", "restriccion", "anula"]
set_card("es115", abilities_es115, tags_es115)

# es116 Lady Dawn
abilities_es116 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "save_knight",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self"}}},
            "cost": {"type": "or", "options": [{"type": "pay_resources", "amount": 3}, {"type": "destroy", "target": "self"}]},
            "effect": {"type": "prevent_damage", "target": "triggered_card"},
            "optional": True,
            "text": "En respuesta a que uno de tus Caballeros sea destruido, puedes pagar 3 de oro o destruir a Lady Dawn para salvarlo.",
        }
    ],
}
tags_es116 = ["opcional", "previene_dano", "paga_recursos", "destruye_para_pagar", "response"]
set_card("es116", abilities_es116, tags_es116)

conn.commit()
conn.close()
print("Updated batch: es103-es116")









