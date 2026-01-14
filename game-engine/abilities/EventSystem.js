/**
 * EventSystem - Sistema de eventos para triggers de habilidades
 * 
 * Este módulo maneja el sistema de eventos que activa los triggers
 * de las habilidades cuando ocurren eventos en el juego.
 */

class EventSystem {
    constructor() {
        this.listeners = new Map();
        this.eventQueue = [];
        this.processing = false;
    }

    /**
     * Registra un listener para un tipo de evento
     * @param {string} eventType - Tipo de evento
     * @param {Function} callback - Función a ejecutar cuando ocurre el evento
     * @returns {Function} Función para desregistrar el listener
     */
    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }

        const listeners = this.listeners.get(eventType);
        listeners.push(callback);

        // Retornar función para desregistrar
        return () => {
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        };
    }

    /**
     * Emite un evento
     * @param {string} eventType - Tipo de evento
     * @param {Object} data - Datos del evento
     */
    emit(eventType, data = {}) {
        const event = {
            type: eventType,
            data: data,
            timestamp: Date.now()
        };

        this.eventQueue.push(event);

        // Procesar eventos si no se está procesando
        if (!this.processing) {
            this._processEvents();
        }
    }

    /**
     * Procesa la cola de eventos
     */
    _processEvents() {
        this.processing = true;

        while (this.eventQueue.length > 0) {
            const event = this.eventQueue.shift();
            this._handleEvent(event);
        }

        this.processing = false;
    }

    /**
     * Maneja un evento individual
     */
    _handleEvent(event) {
        const listeners = this.listeners.get(event.type) || [];

        for (const listener of listeners) {
            try {
                listener(event.data);
            } catch (error) {
                console.error(`Error en listener de evento ${event.type}:`, error);
            }
        }
    }

    /**
     * Limpia todos los listeners
     */
    clear() {
        this.listeners.clear();
        this.eventQueue = [];
    }

    /**
     * Obtiene el número de listeners para un tipo de evento
     */
    getListenerCount(eventType) {
        return (this.listeners.get(eventType) || []).length;
    }
}

module.exports = EventSystem;









