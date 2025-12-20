/**
 * Módulo principal del sistema de habilidades
 * Exporta todos los componentes principales
 */

const AbilityValidator = require('./abilities/AbilityValidator');
const AbilityExecutor = require('./abilities/AbilityExecutor');
const AbilityManager = require('./abilities/AbilityManager');
const EventSystem = require('./abilities/EventSystem');

module.exports = {
    AbilityValidator,
    AbilityExecutor,
    AbilityManager,
    EventSystem
};

