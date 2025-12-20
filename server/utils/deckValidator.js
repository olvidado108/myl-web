/**
 * Validador de mazos.
 * Implementación mínima para permitir arranque del servidor.
 * Extender con reglas reales según formato/edición cuando se definan.
 */
class DeckValidator {
    constructor(cardRepo) {
        this.cardRepo = cardRepo;
    }

    /**
     * Valida un mazo completo.
     * @param {object} mazo - { cartas: [], oro_inicial_id, formato, ... }
     * @param {string} formato - nombre del formato (ej. "Racial Edición")
     * @returns {{valido: boolean, errores: string[]}}
     */
    validarMazoCompleto(mazo = {}, formato = 'Racial Edición') {
        const errores = [];

        // Validación mínima: debe haber arreglo de cartas
        if (!Array.isArray(mazo.cartas)) {
            errores.push('cartas debe ser un arreglo');
        }

        // Validar que oro inicial, si existe, esté en BD
        if (mazo.oro_inicial_id) {
            const oro = this.cardRepo?.buscarPorId?.(mazo.oro_inicial_id);
            if (!oro) {
                errores.push(`Oro inicial no encontrado: ${mazo.oro_inicial_id}`);
            }
        }

        // TODO: agregar reglas de tamaño de mazo, copias máximas, formato, razas, etc.
        return {
            valido: errores.length === 0,
            errores
        };
    }
}

module.exports = DeckValidator;
