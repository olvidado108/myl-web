/**
 * AbilityManager - Gestor principal del sistema de habilidades
 * 
 * Este módulo coordina el parser, validador y ejecutor de habilidades,
 * proporcionando una interfaz unificada para trabajar con habilidades.
 */

const AbilityValidator = require('./AbilityValidator');
const AbilityExecutor = require('./AbilityExecutor');

class AbilityManager {
    constructor(gameState = null) {
        this.validator = new AbilityValidator();
        this.executor = gameState ? new AbilityExecutor(gameState) : null;
    }

    /**
     * NOTA: El parsing automático ha sido removido.
     * Las habilidades deben ser creadas manualmente y guardadas en abilities_json.
     * Este método ahora solo valida habilidades ya estructuradas.
     */
    parse(textoHabilidad) {
        console.warn('AbilityManager.parse() está deprecado. Las habilidades deben crearse manualmente.');
        return {
            version: "1.0",
            abilities: []
        };
    }

    /**
     * Valida un objeto de habilidades
     * @param {Object} abilitiesData - Objeto con habilidades
     * @returns {Object} { valid: boolean, errors: Array }
     */
    validate(abilitiesData) {
        return this.validator.validate(abilitiesData);
    }

    /**
     * Valida habilidades ya estructuradas (no parsea texto)
     * @param {Object|string} abilitiesData - Objeto con habilidades o JSON string
     * @returns {Object} { valid: boolean, abilities: Array, errors: Array }
     */
    parseAndValidate(abilitiesData) {
        let parsed;
        
        if (typeof abilitiesData === 'string') {
            try {
                parsed = JSON.parse(abilitiesData);
            } catch (error) {
                return {
                    valid: false,
                    abilities: [],
                    errors: [`JSON inválido: ${error.message}`]
                };
            }
        } else {
            parsed = abilitiesData;
        }
        
        const validation = this.validate(parsed);

        return {
            valid: validation.valid,
            abilities: parsed.abilities || [],
            errors: validation.errors
        };
    }

    /**
     * Ejecuta una habilidad
     * @param {Object} ability - Habilidad a ejecutar
     * @param {Object} context - Contexto de ejecución
     * @returns {Object} Resultado de la ejecución
     */
    execute(ability, context) {
        if (!this.executor) {
            throw new Error("AbilityExecutor no está inicializado. Pasa gameState al constructor.");
        }

        // Validar antes de ejecutar
        const validation = this.validator.validateQuick(ability);
        if (!validation.valid) {
            return {
                success: false,
                error: validation.error
            };
        }

        return this.executor.execute(ability, context);
    }

    /**
     * Valida habilidades de una carta (no las crea)
     * Las habilidades deben venir ya en card.abilities o card.abilities_json
     * @param {Object} card - Carta con abilities o abilities_json
     * @returns {Object} Carta con validación de habilidades
     */
    processCard(card) {
        // Si ya tiene abilities_json, validarlo
        if (card.abilities_json) {
            const result = this.parseAndValidate(card.abilities_json);
            return {
                ...card,
                abilities: result.abilities,
                abilitiesValid: result.valid,
                abilitiesErrors: result.errors
            };
        }
        
        // Si ya tiene abilities, validarlas
        if (card.abilities && Array.isArray(card.abilities)) {
            const validation = this.validate({
                version: "1.0",
                abilities: card.abilities
            });
            return {
                ...card,
                abilities: card.abilities,
                abilitiesValid: validation.valid,
                abilitiesErrors: validation.errors
            };
        }
        
        // Sin habilidades
        return {
            ...card,
            abilities: [],
            abilitiesValid: false
        };
    }

    /**
     * Inicializa el ejecutor con un nuevo gameState
     * @param {Object} gameState - Estado del juego
     */
    setGameState(gameState) {
        this.executor = new AbilityExecutor(gameState);
    }

    /**
     * Obtiene todas las habilidades de un tipo específico
     * @param {Array} abilities - Array de habilidades
     * @param {string} type - Tipo de habilidad (triggered, static, activated, response)
     * @returns {Array} Habilidades del tipo especificado
     */
    getAbilitiesByType(abilities, type) {
        if (!Array.isArray(abilities)) {
            return [];
        }
        return abilities.filter(ability => ability.type === type);
    }

    /**
     * Obtiene habilidades que se activan con un trigger específico
     * @param {Array} abilities - Array de habilidades
     * @param {string} triggerType - Tipo de trigger
     * @returns {Array} Habilidades con ese trigger
     */
    getAbilitiesByTrigger(abilities, triggerType) {
        if (!Array.isArray(abilities)) {
            return [];
        }
        return abilities.filter(ability => 
            (ability.type === 'triggered' || ability.type === 'response') &&
            ability.trigger &&
            ability.trigger.type === triggerType
        );
    }
}

module.exports = AbilityManager;

