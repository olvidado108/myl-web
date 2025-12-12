/**
 * Estado de la partida - Fuente de la verdad del juego
 */
class GameState {
    constructor(jugador1Id = 'jugador1', jugador2Id = 'jugador2') {
        this.turnoActual = jugador1Id;
        this.fase = 'inicio'; // inicio, principal, combate, final
        this.turnoNumero = 1;
        this.jugadores = {
            [jugador1Id]: {
                id: jugador1Id,
                vida: 30,
                vidaMaxima: 30,
                mana: 0,
                manaMaximo: 0,
                mano: [],
                campo: [],
                mazo: [],
                cementerio: []
            },
            [jugador2Id]: {
                id: jugador2Id,
                vida: 30,
                vidaMaxima: 30,
                mana: 0,
                manaMaximo: 0,
                mano: [],
                campo: [],
                mazo: [],
                cementerio: []
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
     */
    verificarGanador() {
        for (const [id, jugador] of Object.entries(this.jugadores)) {
            if (jugador.vida <= 0) {
                this.ganador = Object.keys(this.jugadores).find(jid => jid !== id);
                this.finalizado = true;
                return this.ganador;
            }
        }
        return null;
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

