/**
 * AbilityValidator - Valida la estructura de habilidades según el JSON Schema
 * 
 * Este módulo valida que las habilidades cumplan con el formato JSON estructurado
 * definido en el schema, asegurando que sean ejecutables correctamente.
 */

class AbilityValidator {
    constructor() {
        this.errors = [];
    }

    /**
     * Valida un objeto de habilidades completo
     * @param {Object} abilitiesData - Objeto con version y abilities
     * @returns {Object} { valid: boolean, errors: Array }
     */
    validate(abilitiesData) {
        this.errors = [];

        // Validar estructura base
        if (!abilitiesData || typeof abilitiesData !== 'object') {
            this.errors.push("El objeto de habilidades debe ser un objeto válido");
            return { valid: false, errors: this.errors };
        }

        if (!abilitiesData.version) {
            this.errors.push("Falta la propiedad 'version'");
        }

        if (!Array.isArray(abilitiesData.abilities)) {
            this.errors.push("La propiedad 'abilities' debe ser un array");
            return { valid: false, errors: this.errors };
        }

        // Validar cada habilidad
        abilitiesData.abilities.forEach((ability, index) => {
            this._validateAbility(ability, index);
        });

        return {
            valid: this.errors.length === 0,
            errors: this.errors
        };
    }

    /**
     * Valida una habilidad individual
     */
    _validateAbility(ability, index) {
        const prefix = `Habilidad ${index + 1}`;

        // Validar tipo
        if (!ability.type) {
            this.errors.push(`${prefix}: Falta la propiedad 'type'`);
            return;
        }

        const validTypes = ['triggered', 'static', 'activated', 'response'];
        if (!validTypes.includes(ability.type)) {
            this.errors.push(`${prefix}: Tipo inválido '${ability.type}'. Debe ser uno de: ${validTypes.join(', ')}`);
        }

        // Validar trigger para triggered/response
        if (ability.type === 'triggered' || ability.type === 'response') {
            if (!ability.trigger) {
                this.errors.push(`${prefix}: Las habilidades '${ability.type}' requieren un 'trigger'`);
            } else {
                this._validateTrigger(ability.trigger, prefix);
            }
        }

        // Validar costo para activated
        if (ability.type === 'activated') {
            if (!ability.cost) {
                this.errors.push(`${prefix}: Las habilidades 'activated' requieren un 'cost'`);
            } else {
                this._validateCost(ability.cost, prefix);
            }
        }

        // Validar efecto (obligatorio para todos)
        if (!ability.effect) {
            this.errors.push(`${prefix}: Todas las habilidades requieren un 'effect'`);
        } else {
            this._validateEffect(ability.effect, prefix);
        }

        // Validar propiedades opcionales
        if (ability.optional !== undefined && typeof ability.optional !== 'boolean') {
            this.errors.push(`${prefix}: 'optional' debe ser un booleano`);
        }

        if (ability.oncePerTurn !== undefined && typeof ability.oncePerTurn !== 'boolean') {
            this.errors.push(`${prefix}: 'oncePerTurn' debe ser un booleano`);
        }
    }

    /**
     * Valida un trigger
     */
    _validateTrigger(trigger, prefix) {
        if (!trigger.type) {
            this.errors.push(`${prefix}: El trigger requiere un 'type'`);
            return;
        }

        const validTriggerTypes = [
            'enters_play', 'leaves_play', 'attacks', 'blocks',
            'declared_attacker', 'declared_blocker', 'takes_damage',
            'receives_damage', 'destroyed', 'phase_start', 'phase_end',
            'turn_start', 'turn_end', 'card_played', 'ability_activated'
        ];

        if (!validTriggerTypes.includes(trigger.type)) {
            this.errors.push(`${prefix}: Tipo de trigger inválido '${trigger.type}'`);
        }
    }

    /**
     * Valida un costo
     */
    _validateCost(cost, prefix) {
        if (!cost.type) {
            this.errors.push(`${prefix}: El costo requiere un 'type'`);
            return;
        }

        const validCostTypes = ['pay_resources', 'discard', 'destroy', 'exile', 'tap', 'sacrifice'];

        if (!validCostTypes.includes(cost.type)) {
            this.errors.push(`${prefix}: Tipo de costo inválido '${cost.type}'`);
        }

        if (cost.type === 'pay_resources' && (!cost.amount || typeof cost.amount !== 'number')) {
            this.errors.push(`${prefix}: El costo 'pay_resources' requiere un 'amount' numérico`);
        }

        if (cost.type === 'discard' && (!cost.amount || typeof cost.amount !== 'number')) {
            this.errors.push(`${prefix}: El costo 'discard' requiere un 'amount' numérico`);
        }
    }

    /**
     * Valida un efecto
     */
    _validateEffect(effect, prefix) {
        if (!effect.type) {
            this.errors.push(`${prefix}: El efecto requiere un 'type'`);
            return;
        }

        const validEffectTypes = [
            'modify_force', 'draw_cards', 'search', 'destroy', 'exile',
            'discard', 'shuffle', 'put_in_hand', 'put_in_play', 'lose_ability',
            'gain_ability', 'counter', 'damage', 'heal', 'tap', 'untap',
            'move_zone', 'modify_cost', 'prevent_damage', 'copy_ability'
        ];

        if (!validEffectTypes.includes(effect.type)) {
            this.errors.push(`${prefix}: Tipo de efecto inválido '${effect.type}'`);
        }

        // Validaciones específicas por tipo de efecto
        switch (effect.type) {
            case 'draw_cards':
                if (!effect.amount || typeof effect.amount !== 'number') {
                    this.errors.push(`${prefix}: El efecto 'draw_cards' requiere un 'amount' numérico`);
                }
                break;

            case 'modify_force':
                if (!effect.modifier) {
                    this.errors.push(`${prefix}: El efecto 'modify_force' requiere un 'modifier'`);
                } else {
                    this._validateModifier(effect.modifier, prefix);
                }
                break;

            case 'search':
                if (!effect.location) {
                    this.errors.push(`${prefix}: El efecto 'search' requiere un 'location'`);
                }
                if (!effect.action) {
                    this.errors.push(`${prefix}: El efecto 'search' requiere un 'action'`);
                }
                break;

            case 'discard':
                if (!effect.amount || typeof effect.amount !== 'number') {
                    this.errors.push(`${prefix}: El efecto 'discard' requiere un 'amount' numérico`);
                }
                break;
        }
    }

    /**
     * Valida un modificador
     */
    _validateModifier(modifier, prefix) {
        if (!modifier.type) {
            this.errors.push(`${prefix}: El modificador requiere un 'type'`);
            return;
        }

        const validModifierTypes = ['add', 'subtract', 'multiply', 'divide', 'set'];
        if (!validModifierTypes.includes(modifier.type)) {
            this.errors.push(`${prefix}: Tipo de modificador inválido '${modifier.type}'`);
        }

        if (modifier.value === undefined) {
            this.errors.push(`${prefix}: El modificador requiere un 'value'`);
        }
    }

    /**
     * Valida rápidamente una habilidad (versión simplificada)
     */
    validateQuick(ability) {
        if (!ability || typeof ability !== 'object') {
            return { valid: false, error: "La habilidad debe ser un objeto" };
        }

        if (!ability.type) {
            return { valid: false, error: "Falta el tipo de habilidad" };
        }

        if ((ability.type === "triggered" || ability.type === "response") && !ability.trigger) {
            return { valid: false, error: "Las habilidades triggered/response requieren un trigger" };
        }

        if (ability.type === "activated" && !ability.cost) {
            return { valid: false, error: "Las habilidades activated requieren un costo" };
        }

        if (!ability.effect) {
            return { valid: false, error: "Todas las habilidades requieren un efecto" };
        }

        return { valid: true };
    }
}

module.exports = AbilityValidator;




