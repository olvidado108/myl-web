/**
 * Estado de la partida - Fuente de la verdad del juego
 * Basado en las reglas oficiales de Mitos y Leyendas
 */
class GameState {
    constructor(jugador1Id = 'jugador1', jugador2Id = 'jugador2') {
        // Fases oficiales simplificadas: reagrupar, comienzo_vigilia, vigilia, batalla, final
        this.fase = 'reagrupar';
        this.turnoNumero = 1;
        
        // Si ambos jugadores tienen el mismo ID (modo práctica), crear IDs únicos internos
        // pero mantener el ID del usuario para referencia
        const jugador1Key = jugador1Id === jugador2Id ? `${jugador1Id}_1` : jugador1Id;
        const jugador2Key = jugador1Id === jugador2Id ? `${jugador2Id}_2` : jugador2Id;
        // El turno siempre se almacena usando la clave interna del jugador
        this.turnoActual = jugador1Key;
        this.jugadorInicialKey = jugador1Key;
        
        this.jugadores = {
            [jugador1Key]: {
                id: jugador1Id, // Mantener el ID original del usuario
                key: jugador1Key, // Clave única interna
                // Sistema de mazo (Castillo) - objetivo: reducir a 0
                mazo: [], // Mazo Castillo (50 cartas)
                mano: [], // Cartas en mano (máximo 8 después de la Fase de Robo)
                // Áreas de juego según reglas oficiales
                lineaDefensa: [], // Aliados en defensa
                lineaAtaque: [], // Aliados que declararon ataque este turno
                lineaApoyo: [], // Tótems y Armas
                reservaOro: [], // Oros (generan recursos)
                cementerio: [], // Cartas descartadas/destruidas
                // Recursos (generados por Oros, no "maná" tradicional)
                recursos: 0, // Recursos disponibles este turno
                recursosTotales: 0 // Recursos totales generados por Oros
            },
            [jugador2Key]: {
                id: jugador2Id, // Mantener el ID original del usuario
                key: jugador2Key, // Clave única interna
                mazo: [],
                mano: [],
                lineaDefensa: [],
                lineaAtaque: [],
                lineaApoyo: [],
                reservaOro: [],
                cementerio: [],
                recursos: 0,
                recursosTotales: 0
            }
        };

        // Conteo de mulligans por jugador (0 inicial)
        this.mulligans = {
            [jugador1Key]: 0,
            [jugador2Key]: 0
        };
        // Indicador de si cada jugador ya confirmó su mano inicial
        this.mulliganListo = {
            [jugador1Key]: false,
            [jugador2Key]: false
        };
        // Flag global: true solo cuando ambos jugadores confirmaron
        this.mulliganCompletado = false;
        
        // Control de acciones por turno
        this.oroJugadoEnTurno = {
            [jugador1Key]: false,
            [jugador2Key]: false
        };
        // Flag para la excepción de robo en el primer turno del jugador inicial
        this.roboInicialSaltado = false;
        
        // Mapeo de IDs de usuario a claves internas (para búsqueda rápida)
        // Si ambos jugadores tienen el mismo ID, necesitamos un mapeo especial
        if (jugador1Id === jugador2Id) {
            // Para modo práctica, mapear a ambas claves usando un array
            this.userIdToKey = {
                [jugador1Id]: [jugador1Key, jugador2Key] // Array con ambas claves
            };
            // También mantener un mapeo directo para acceso rápido
            this.userIdToKeyArray = [jugador1Key, jugador2Key];
        } else {
            this.userIdToKey = {
                [jugador1Id]: jugador1Key,
                [jugador2Id]: jugador2Key
            };
            this.userIdToKeyArray = null;
        }
        
        this.ganador = null;
        this.finalizado = false;
    }

    /**
     * Obtiene un jugador por su ID de usuario (no por clave interna)
     * Si hay múltiples jugadores con el mismo ID, retorna el primero
     */
    getJugadorPorId(userId) {
        const key = this.getKeyPorId(userId);
        return key ? this.jugadores[key] : null;
    }

    /**
     * Obtiene la clave interna de un jugador por su ID de usuario
     * Si hay múltiples jugadores con el mismo ID, retorna la primera clave
     */
    getKeyPorId(userId, index = 0) {
        const mapping = this.userIdToKey[userId];
        if (Array.isArray(mapping)) {
            // Si es un array (modo práctica), retornar la clave en el índice especificado
            return mapping[index] || mapping[0] || null;
        }
        return mapping || null;
    }
    
    /**
     * Obtiene todas las claves para un ID de usuario (útil cuando hay múltiples jugadores con el mismo ID)
     */
    getAllKeysPorId(userId) {
        const mapping = this.userIdToKey[userId];
        if (Array.isArray(mapping)) {
            return mapping;
        }
        return mapping ? [mapping] : [];
    }

    /**
     * Retorna true si ambos jugadores ya confirmaron su mano de mulligan
     */
    estaMulliganCompletado() {
        const jugadoresKeys = Object.keys(this.jugadores || {});
        const listo = this.mulliganListo || {};
        const completo = jugadoresKeys.length > 0 && jugadoresKeys.every(key => !!listo[key]);
        this.mulliganCompletado = completo;
        return completo;
    }

    /**
     * Obtiene el jugador actual
     */
    getJugadorActual() {
        const key = this.turnoActual;
        return this.jugadores[key];
    }

    /**
     * Devuelve la clave interna del jugador inicial
     */
    getJugadorInicialKey() {
        return this.jugadorInicialKey;
    }

    /**
     * Obtiene el oponente del jugador actual
     */
    getOponente() {
        const keys = Object.keys(this.jugadores);
        const jugadorActualKey = this.turnoActual;
        const oponenteKey = keys.find(key => key !== jugadorActualKey);
        return oponenteKey ? this.jugadores[oponenteKey] : null;
    }

    /**
     * Obtiene datos del jugador en turno (clave interna y objeto)
     */
    getJugadorEnTurno() {
        const key = this.turnoActual;
        return {
            key,
            jugador: this.jugadores[key] || null
        };
    }

    /**
     * Cambia al siguiente turno
     */
    siguienteTurno() {
        const keys = Object.keys(this.jugadores);
        const indiceActual = keys.indexOf(this.turnoActual);
        const indiceSeguro = indiceActual >= 0 ? indiceActual : 0;
        const siguienteIndice = (indiceSeguro + 1) % keys.length;
        this.turnoActual = keys[siguienteIndice];
        this.fase = 'reagrupar';
        
        if (siguienteIndice === 0) {
            this.turnoNumero++;
        }
    }

    /**
     * Verifica si hay un ganador
     * En Mitos y Leyendas, ganas cuando el mazo del oponente queda vacío
     */
    verificarGanador() {
        for (const [id, jugador] of Object.entries(this.jugadores)) {
            // Si el mazo (Castillo) está vacío, el jugador pierde
            if (jugador.mazo.length === 0) {
                const ganadorKey = Object.keys(this.jugadores).find(jid => jid !== id);
                this.ganador = ganadorKey ? (this.jugadores[ganadorKey]?.id || ganadorKey) : null;
                this.finalizado = true;
                return this.ganador;
            }
        }
        return null;
    }

    /**
     * Verifica si el jugador tiene más de 8 cartas en mano
     * (debe descartar después de robar en la Fase de Robo)
     */
    tieneMasDe8CartasEnMano(jugadorId) {
        return this.jugadores[jugadorId].mano.length > 8;
    }

    /**
     * Calcula los recursos totales generados por los Oros
     */
    calcularRecursosTotales(jugadorId) {
        const jugador = this.jugadores[jugadorId];
        // Cada Oro genera 1 recurso (puede ajustarse según la carta)
        jugador.recursosTotales = jugador.reservaOro.length;
        jugador.recursos = jugador.recursosTotales;
        return jugador.recursos;
    }

    /**
     * Convierte el estado a JSON para enviar al cliente
     */
    toJSON() {
        return {
            turnoActual: this.turnoActual,
            fase: this.fase,
            turnoNumero: this.turnoNumero,
            jugadores: this.jugadores,
            jugadorInicialKey: this.jugadorInicialKey,
            oroJugadoEnTurno: this.oroJugadoEnTurno,
            roboInicialSaltado: this.roboInicialSaltado,
            mulligans: this.mulligans,
            mulliganListo: this.mulliganListo,
            mulliganCompletado: this.mulliganCompletado,
            ganador: this.ganador,
            finalizado: this.finalizado
        };
    }
}

module.exports = GameState;

