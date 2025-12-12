/**
 * Estado de la partida - Fuente de la verdad del juego
 * Basado en las reglas oficiales de Mitos y Leyendas
 */
class GameState {
    constructor(jugador1Id = 'jugador1', jugador2Id = 'jugador2') {
        this.turnoActual = jugador1Id;
        // Fases: inicio, robo, preparacion, batalla, final
        this.fase = 'inicio';
        this.turnoNumero = 1;
        this.jugadores = {
            [jugador1Id]: {
                id: jugador1Id,
                // Sistema de mazo (Castillo) - objetivo: reducir a 0
                mazo: [], // Mazo Castillo (50 cartas)
                mano: [], // Cartas en mano (máximo 8 después de la Fase de Robo)
                // Áreas de juego según reglas oficiales
                lineaDefensa: [], // Aliados
                lineaApoyo: [], // Tótems y Armas
                reservaOro: [], // Oros (generan recursos)
                cementerio: [], // Cartas descartadas/destruidas
                // Recursos (generados por Oros, no "maná" tradicional)
                recursos: 0, // Recursos disponibles este turno
                recursosTotales: 0 // Recursos totales generados por Oros
            },
            [jugador2Id]: {
                id: jugador2Id,
                mazo: [],
                mano: [],
                lineaDefensa: [],
                lineaApoyo: [],
                reservaOro: [],
                cementerio: [],
                recursos: 0,
                recursosTotales: 0
            }
        };
        this.ganador = null;
        this.finalizado = false;
    }

    /**
     * Obtiene el jugador actual
     */
    getJugadorActual() {
        return this.jugadores[this.turnoActual];
    }

    /**
     * Obtiene el oponente del jugador actual
     */
    getOponente() {
        const ids = Object.keys(this.jugadores);
        return this.jugadores[ids.find(id => id !== this.turnoActual)];
    }

    /**
     * Cambia al siguiente turno
     */
    siguienteTurno() {
        const ids = Object.keys(this.jugadores);
        const indiceActual = ids.indexOf(this.turnoActual);
        this.turnoActual = ids[(indiceActual + 1) % ids.length];
        this.fase = 'inicio';
        
        if (this.turnoActual === ids[0]) {
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
                this.ganador = Object.keys(this.jugadores).find(jid => jid !== id);
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
            ganador: this.ganador,
            finalizado: this.finalizado
        };
    }
}

module.exports = GameState;

