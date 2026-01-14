import json
import sqlite3
from pathlib import Path

db = Path(r"c:\Users\OLVIDADO\Documents\myl\server\data\game.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

# Asegurar tags necesarios
needed_tags = [
    ("mueve_zona", "Mueve zona", "soporte", None),
    ("trigger_fin_turno", "Trigger fin de turno", "triggers", None),
    ("destierra_para_pagar", "Destierra para pagar", "coste", None),
    ("bota_cartas", "Muele mazo oponente", "control", None),
    ("equipa_armas_extra", "Puede equipar armas extra", "soporte", None),
    ("modifica_fuerza", "Modifica fuerza", "soporte", None),
    ("restriccion", "Restricción/regla", "control", None),
    ("paga_recursos", "Paga recursos", "coste", None),
    ("destruye_para_pagar", "Destruye para pagar", "coste", None),
    ("genera_recursos", "Genera recursos", "recursos", None),
    ("anula", "Anula efectos/talismanes", "control", None),
    ("pierde_habilidad", "Quita habilidad", "control", None),
    ("destruye_objetivo", "Destruye objetivo", "removal", None),
    ("trigger_destruido", "Trigger al ser destruido", "triggers", None),
    ("trigger_al_entrar", "Trigger al entrar en juego", "triggers", None),
    ("baraja", "Baraja cartas", "control", None),
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


# es252 Lanza de Justa
abilities_es252 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "bounce_blocker_if_survived",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "blocked_this_turn_and_blocker_survived", "target": {"type": "reference", "reference": "equipped_to"}},
            "effect": {"type": "move_zone", "target": {"type": "reference", "reference": "blocker"}, "location": "hand"},
            "text": "Al final del turno, si el aliado que lo bloqueó no fue destruido, vuelve a la mano de su controlador.",
        }
    ],
}
tags_es252 = ["mueve_zona", "trigger_fin_turno"]
set_card("es252", abilities_es252, tags_es252)

# es253 Espada Templaria
abilities_es253 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "extra_weapon",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "equip_extra_weapon", "target": {"type": "reference", "reference": "equipped_to"}},
            "text": "El portador puede portar un arma extra.",
        },
        {
            "id": "exile_to_mill_in_war",
            "type": "activated",
            "condition": {"type": "phase", "value": "guerra_talismanes", "controller": "self"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "discard",
                "target": "opponent",
                "amount": {"type": "reference", "reference": "equipped_to_force"},
                "location": "deck",
            },
            "optional": True,
            "text": "En guerra de Talismanes, puedes desterrarla para que el oponente bote cartas iguales a la fuerza del portador.",
        },
    ],
}
tags_es253 = ["equipa_armas_extra", "destierra_para_pagar", "bota_cartas", "opcional"]
set_card("es253", abilities_es253, tags_es253)

# es254 Ballesta Franca
abilities_es254 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "boost_force",
            "type": "static",
            "effect": {"type": "modify_force", "target": {"type": "reference", "reference": "equipped_to"}, "modifier": {"type": "add", "value": 2}},
            "text": "El portador gana +2 a la fuerza.",
        },
        {
            "id": "cannot_be_blocked_by_weaker",
            "type": "static",
            "effect": {
                "type": "restriction",
                "restriction": {"cannot_be_blocked_by_weaker": True},
                "target": {"type": "reference", "reference": "equipped_to"},
            },
            "text": "No puede ser bloqueado por aliados con menor fuerza.",
        },
    ],
}
tags_es254 = ["modifica_fuerza", "restriccion"]
set_card("es254", abilities_es254, tags_es254)

# es255 San Juan de Acre
abilities_es255 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "pay_transform_to_ally",
            "type": "response",
            "trigger": {"type": "declared_blocker", "target": "self"},
            "cost": {"type": "pay_resources", "amount": 1},
            "effect": {
                "type": "group",
                "effects": [
                    {
                        "type": "gain_ability",
                        "target": "self",
                        "value": {"type": "ally", "race": "Caballero", "force": 4},
                        "duration": "end_turn",
                    }
                ],
            },
            "text": "En respuesta a bloquear, paga 1 oro: se convierte en aliado Caballero de fuerza 4 hasta fin de turno.",
        },
        {
            "id": "revert_if_survives",
            "type": "triggered",
            "trigger": {"type": "turn_end", "target": "controller"},
            "condition": {"type": "is_in_play", "target": "self"},
            "effect": {"type": "gain_ability", "target": "self", "value": {"type": "totem"}, "duration": "permanent"},
            "text": "Al final del turno, si no fue destruido, vuelve a ser Tótem.",
        },
    ],
}
tags_es255 = ["paga_recursos", "modifica_fuerza"]
set_card("es255", abilities_es255, tags_es255)

# es256 Bizancio
abilities_es256 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "exile_to_recover_top",
            "type": "response",
            "trigger": {"type": "deck_empty", "target": "controller"},
            "cost": {"type": "exile", "target": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"controller": "self", "zone": "graveyard", "position": "top"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "Si tu mazo queda sin cartas, puedes desterrarlo para regresar la primera carta del cementerio al mazo.",
        }
    ],
}
tags_es256 = ["destierra_para_pagar", "mueve_zona", "opcional"]
set_card("es256", abilities_es256, tags_es256)

# es257 Traficantes de Esclavos
abilities_es257 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "sac_to_pay_all_opponent_gold",
            "type": "response",
            "trigger": {"type": "gold_grouped", "target": "opponent"},
            "cost": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}, "amount": 1},
            "effect": {"type": "restriction", "restriction": {"opponent_gold_considered_paid": True}, "target": {"type": "global"}, "duration": "end_turn"},
            "optional": True,
            "text": "En respuesta a la agrupación de oros oponente, destruye un aliado propio: toda su reserva se considera oro pagado hasta fin de turno.",
        }
    ],
}
tags_es257 = ["destruye_para_pagar", "genera_recursos", "restriccion", "opcional"]
set_card("es257", abilities_es257, tags_es257)

# es258 Falso Tesoro
abilities_es258 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "counter_gold_talisman",
            "type": "response",
            "trigger": {"type": "talisman_cast", "target": {"type": "filter", "filter": {"creates_gold": True, "controller": "opponent"}}},
            "effect": {"type": "counter", "target": "triggered_spell"},
            "text": "Anula un Talismán oponente que genere oros.",
        }
    ],
}
tags_es258 = ["anula"]
set_card("es258", abilities_es258, tags_es258)

# es259 Edessa
abilities_es259 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "return_allies_to_hand_on_destroy",
            "type": "response",
            "trigger": {"type": "destroyed", "target": {"type": "filter", "filter": {"type": "allies", "controller": "self"}}},
            "effect": {
                "type": "group",
                "effects": [
                    {"type": "move_zone", "target": "triggered_card", "location": "hand"},
                    {
                        "type": "restriction",
                        "restriction": "lose_abilities_on_next_entry",
                        "target": "triggered_card",
                        "duration": "until_next_enter",
                    },
                ],
            },
            "optional": True,
            "text": "En respuesta a que tus aliados sean destruidos, vuelven a la mano; al reentrar lo hacen sin habilidad.",
        }
    ],
}
tags_es259 = ["mueve_zona", "pierde_habilidad", "trigger_destruido", "opcional"]
set_card("es259", abilities_es259, tags_es259)

# es26 Dragon de Magma
abilities_es26 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "destroy_opponent_ally_on_enter",
            "type": "triggered",
            "trigger": {"type": "enters_play", "target": "self"},
            "effect": {"type": "destroy", "target": {"type": "filter", "filter": {"type": "allies", "controller": "opponent"}}},
            "text": "Cuando entra en juego, destruye un Aliado oponente.",
        }
    ],
}
tags_es26 = ["destruye_objetivo", "trigger_al_entrar"]
set_card("es26", abilities_es26, tags_es26)

# es260 Caballeros
abilities_es260 = {
    "version": "1.0",
    "abilities": [
        {
            "id": "unique_play_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "unique", "target": "self"},
            "text": "Sólo puedes tener uno en juego.",
        },
        {
            "id": "play_only_from_hand",
            "type": "static",
            "effect": {"type": "restriction", "restriction": "play_only_from_hand", "target": "self"},
            "text": "Sólo puede ser jugado desde tu mano.",
        },
        {
            "id": "pay_to_shuffle_knight",
            "type": "activated",
            "condition": {"type": "phase", "value": "vigilia", "controller": "self"},
            "cost": {"type": "pay_resources", "amount": 1, "source": "self"},
            "effect": {
                "type": "move_zone",
                "target": {"type": "filter", "filter": {"type": "allies", "race": "Caballero", "controller": "self", "zone": "graveyard"}},
                "amount": 1,
                "location": "deck",
            },
            "optional": True,
            "text": "En Vigilia, puedes pagar este Oro para barajar un Caballero de tu cementerio en tu mazo.",
        },
    ],
}
tags_es260 = ["restriccion", "paga_recursos", "baraja", "mueve_zona", "opcional"]
set_card("es260", abilities_es260, tags_es260)


conn.commit()
conn.close()
print("Updated batch: es252-es260 y es26")






