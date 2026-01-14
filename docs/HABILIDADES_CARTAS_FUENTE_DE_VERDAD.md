# 📌 Fuente de Verdad: Habilidades de Cartas

Este documento consolida **toda la información vigente** sobre las habilidades de cartas. Reemplaza y absorbe los documentos previos de habilidades.

## Dónde viven los datos
- Base de datos: `server/data/game.db`
- Tabla: `cartas`
- Campos relevantes: `abilities_json` (JSON estructurado), `abilities_version`, `abilities_processed_at`, `textoHabilidad` (texto original).
- Estado actual (2025-12-17): `abilities_json` está poblado en 2631 cartas.

## Formato de `abilities_json` (versión 1.0)
```json
{
  "version": "1.0",
  "abilities": [
    {
      "id": "string_unico",
      "type": "triggered|static|activated|response",
      "trigger": { "type": "<trigger_type>", ... },   // solo triggered/response
      "condition": { ... },                           // opcional
      "effect": { "type": "<effect_type>", ... },     // obligatorio
      "cost": { "type": "<cost_type>", ... },         // solo activated o si aplica
      "optional": true|false,
      "oncePerTurn": true|false,
      "text": "<texto original completo>",
      "cost2": { ... }                                // campo adicional visto en algunos costos compuestos
    }
  ]
}
```
- Algunos costos usan conectores `and|or|choose` y campos extra como `cost2`.
- Mantén siempre el `text` original y un `id` claro por habilidad.

## Catálogo actual de tipos (observado en la BD)
- `type`: `activated`, `response`, `static`, `triggered`
- `trigger.type`: `ability_activated`, `attacks`, `blocks`, `card_played`, `countered`, `damage`, `damage_assignment_phase`, `damage_resolved`, `damages_deck`, `deck_empty`, `declared_attacker`, `declared_blocker`, `destroyed`, `discard`, `discards`, `draw_cards`, `enters_play`, `exile`, `exiled`, `leaves_play`, `or`, `phase_end`, `phase_start`, `plays_card`, `receives_damage`, `search`, `takes_damage`, `targeted`, `turn_end`, `turn_start`
- `effect.type`: `activate`, `activate_ability`, `additional_cost`, `become_type`, `choice`, `choose`, `copy_ability`, `cost`, `counter`, `damage`, `destroy`, `discard`, `draw_cards`, `exile`, `gain_ability`, `generate_resources`, `group`, `immunity`, `look_deck`, `look_hand`, `lose_ability`, `modify_cost`, `modify_force`, `modify_race`, `modify_rule`, `modify_type`, `modify_zone`, `move_zone`, `prevent_damage`, `put_in_play`, `redirect`, `regroup`, `remove_modifiers`, `reorder`, `reorder_deck`, `restriction`, `reveal`, `reveal_hand`, `reveal_top_card`, `reveal_top_cards`, `revert_transform`, `search`, `shuffle`, `skip_phase`, `skip_phases`, `swap_force`, `tap`, `transform`
- `cost.type`: `and`, `choose`, `destroy`, `discard`, `exile`, `move_zone`, `or`, `pay_resources`, `reveal`, `shuffle`

## Ejemplo real (desde la BD)
```json
{
  "version": "1.0",
  "abilities": [
    {
      "id": "unblockable",
      "type": "static",
      "effect": { "type": "gain_ability", "target": "self" },
      "text": "Imbloqueable."
    },
    {
      "id": "pay_and_destroy_to_search",
      "type": "activated",
      "cost": { "type": "pay_resources", "amount": 1 },
      "cost2": {
        "type": "destroy",
        "target": { "type": "filter", "filter": { "type": "allies", "controller": "self" } },
        "amount": 1
      },
      "effect": {
        "type": "search",
        "location": "deck",
        "target": { "type": "filter", "filter": { "type": "allies", "controller": "self" } },
        "action": "put_in_hand",
        "amount": 1
      },
      "optional": true,
      "text": "Puedes pagar 1 Oro y destruir este u otro Aliado que controles para buscar un Aliado en tu Mazo Castillo y ponerlo en tu Mano."
    }
  ]
}
```

## Flujo recomendado para agregar/editar habilidades
1) Obtener cartas pendientes o revisar existentes:
```sql
SELECT id, nombre, tipo, textoHabilidad, abilities_json
FROM cartas
WHERE textoHabilidad IS NOT NULL
  AND textoHabilidad != ''
  AND textoHabilidad NOT IN ('Sin habilidades especiales','NaN','null');
```
2) Interpretar manualmente el `textoHabilidad` y mapear a JSON siguiendo el esquema anterior.
3) Validar contra `game-engine/schemas/ability-schema.json` (usar `AbilityValidator`).
4) Guardar cambios:
```sql
UPDATE cartas
SET abilities_json = '<JSON_ESCAPADO>',
    abilities_version = '1.0',
    abilities_processed_at = CURRENT_TIMESTAMP
WHERE id = '<CARD_ID>';
```
5) Evitar parsing automático; prioriza precisión y consistencia.

## Referencias útiles
- Schema: `game-engine/schemas/ability-schema.json`
- Ejemplos: `game-engine/examples/card-abilities.json`
- Validador: `game-engine/abilities/AbilityValidator.js`







