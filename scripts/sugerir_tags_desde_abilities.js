/**
 * Genera sugerencias de tags a partir de abilities_json.
 * Uso:
 *   node scripts/sugerir_tags_desde_abilities.js [ruta_db]
 * Por defecto usa server/data/game.db. Solo lee y muestra sugerencias; no modifica la BD.
 */

const path = require('path');
const Database = require('better-sqlite3');

const dbPath = process.argv[2] || path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath, { readonly: true });

const triggerToTag = {
  enters_play: 'trigger_al_entrar',
  leaves_play: 'trigger_al_salir',
  attacks: 'trigger_al_atacar',
  declared_attacker: 'trigger_al_atacar',
  blocks: 'trigger_al_bloquear',
  declared_blocker: 'trigger_al_bloquear',
  turn_start: 'trigger_inicio_turno',
  phase_start: 'trigger_inicio_turno',
  turn_end: 'trigger_fin_turno',
  phase_end: 'trigger_fin_turno',
  receives_damage: 'trigger_recibe_dano',
  takes_damage: 'trigger_recibe_dano',
  damage: 'trigger_recibe_dano',
  destroyed: 'trigger_destruido',
  card_played: 'trigger_juega_carta',
  plays_card: 'trigger_juega_carta',
  discard: 'trigger_descarta',
  discards: 'trigger_descarta',
};

const effectToTag = {
  draw_cards: 'roba_cartas',
  destroy: 'destruye_objetivo',
  exile: 'destierra_objetivo',
  search: 'busca_mazo',
  immunity: 'inmunidad',
  damage: 'hace_dano',
  modify_force: 'modifica_fuerza',
  modify_cost: 'modifica_coste',
  modify_race: 'modifica_raza',
  modify_type: 'modifica_tipo',
  modify_rule: 'modifica_regla',
  generate_resources: 'genera_recursos',
  prevent_damage: 'previene_dano',
  move_zone: 'mueve_zona',
  put_in_play: 'pone_en_juego',
  reorder_deck: 'mira_mazo',
  look_deck: 'mira_mazo',
  reorder: 'mira_mazo',
  shuffle: 'baraja',
  look_hand: 'mira_mano_oponente',
  reveal_hand: 'mira_mano_oponente',
  reveal_top_card: 'revela_superior',
  reveal_top_cards: 'revela_superior',
  counter: 'anula',
  copy_ability: 'copia_habilidad',
  gain_ability: 'gana_habilidad',
  lose_ability: 'pierde_habilidad',
  tap: 'tap',
  skip_phase: 'salta_fase',
  skip_phases: 'salta_fase',
  restriction: 'restriccion',
  redirect: 'redirige_objetivo',
  remove_modifiers: 'limpia_mods',
};

const cards = db.prepare('SELECT id, nombre, abilities_json FROM cartas WHERE abilities_json IS NOT NULL').all();

const frequency = new Map();
const suggestions = [];

const addTag = (set, tag) => {
  if (!tag) return;
  set.add(tag);
  frequency.set(tag, (frequency.get(tag) || 0) + 1);
};

const mapEffect = (ability, set) => {
  const eff = ability.effect;
  if (!eff || typeof eff !== 'object') return;
  const base = effectToTag[eff.type];
  addTag(set, base);

  if (eff.type === 'discard') {
    // Heurística: si descarta desde mazo, bota_cartas; si es mano, descarta_mano.
    const from = eff.location || eff.from || eff.zone;
    const target = eff.target || {};
    const targetZone = target.zone || target.location;
    const zones = [from, targetZone].filter(Boolean).join(',').toLowerCase();
    if (zones.includes('deck') || zones.includes('mazo')) {
      addTag(set, 'bota_cartas');
    } else {
      addTag(set, 'descarta_mano');
    }
  }

  if (eff.type === 'move_zone') addTag(set, 'mueve_zona');
  if (eff.type === 'reveal_top_card' || eff.type === 'reveal_top_cards') addTag(set, 'revela_superior');
  if (eff.type === 'put_in_play') addTag(set, 'pone_en_juego');

  // Casos de restricciones específicas dentro de gain_ability
  if (eff.type === 'gain_ability' && eff.value && typeof eff.value === 'object') {
    if (eff.value.restriction === 'cannot_be_grouped') {
      addTag(set, 'no_agrupable');
      addTag(set, 'restriccion');
    }
    const r = eff.value.restriction;
    const map = {
      cannot_be_regrouped: ['no_reagrupable', 'restriccion'],
      cannot_be_shuffled: ['no_barajable', 'restriccion'],
      cannot_be_tapped: ['no_tap', 'restriccion'],
      cannot_attack: ['no_puede_atacar', 'restriccion'],
      cannot_block: ['no_puede_bloquear', 'restriccion'],
      must_attack: ['debe_atacar', 'restriccion'],
      must_block: ['debe_bloquear', 'restriccion'],
      must_attack_or_return_to_hand: ['debe_atacar', 'restriccion'],
      cannot_be_countered: ['no_anulable'],
      cannot_lose_abilities: ['no_pierde_habilidad'],
      cannot_receive_force_bonuses: ['sin_bonus_fuerza', 'restriccion'],
      cannot_leave_play: ['no_sale_juego'],
      cannot_be_declared_attacker: ['no_puede_ser_declarado_atacante', 'restriccion'],
      cannot_be_declared_blocker: ['no_puede_ser_declarado_bloqueador', 'restriccion'],
      can_attack_on_enter: ['apresurado'],
      can_attack_on_enter_turn: ['apresurado'],
      can_attack_this_turn: ['apresurado'],
      can_be_declared_attacker: ['puede_ser_declarado_atacante'],
      can_be_declared_blocker: ['puede_ser_declarado_bloqueador'],
      can_block: ['puede_bloquear'],
      can_block_multiple: ['bloquea_multiple'],
      can_block_up_to: ['bloquea_multiple'],
      can_block_unblockable: ['bloquea_imbloqueables'],
      can_equip_extra_weapon: ['equipa_armas_extra'],
      no_weapon_limit: ['equipa_armas_extra'],
      indestructible: ['indestructible'],
      cannot_be_exiled: ['indesterrable'],
      unblockable: ['imbloqueable'],
    };
    if (r && map[r]) {
      map[r].forEach(tag => addTag(set, tag));
    }
  }
};

const mapTrigger = (ability, set) => {
  const trig = ability.trigger;
  if (!trig || typeof trig !== 'object') return;
  addTag(set, triggerToTag[trig.type]);
};

for (const card of cards) {
  let parsed;
  try {
    parsed = JSON.parse(card.abilities_json);
  } catch {
    continue;
  }
  const abilities = parsed.abilities || [];
  const tagSet = new Set();

  for (const ability of abilities) {
    mapTrigger(ability, tagSet);
    mapEffect(ability, tagSet);
    if (ability.optional) addTag(tagSet, 'opcional');
    if (ability.oncePerTurn) addTag(tagSet, 'una_vez_por_turno');
    // Costs
    const cost = ability.cost;
    if (cost && typeof cost === 'object') {
      const ct = cost.type;
      if (ct === 'destroy') addTag(tagSet, 'sacrifica');
      if (ct === 'discard') addTag(tagSet, 'descarta_para_pagar');
      if (ct === 'exile') addTag(tagSet, 'exilia_para_pagar');
      if (ct === 'reveal') addTag(tagSet, 'revela_para_pagar');
      if (ct === 'choose') addTag(tagSet, 'elige_coste');
    }
  }

  if (tagSet.size > 0) {
    suggestions.push({
      id: card.id,
      nombre: card.nombre,
      tags: Array.from(tagSet).sort(),
    });
  }
}

// Salida principal: TSV de carta_id, nombre, tags sugeridos.
for (const s of suggestions) {
  console.log(`${s.id}\t${s.nombre}\t${s.tags.join(',')}`);
}

// Resumen de frecuencias al final.
console.log('\n--- Frecuencia de tags (sugeridos) ---');
Array.from(frequency.entries())
  .sort((a, b) => b[1] - a[1])
  .forEach(([tag, count]) => console.log(`${tag}\t${count}`));

console.error(`Cartas analizadas: ${cards.length}, con sugerencias: ${suggestions.length}`);







