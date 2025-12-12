/**
 * Clase que representa una carta del juego
 * Basado en las reglas oficiales de Mitos y Leyendas
 * 
 * Tipos de cartas:
 * - "Aliado": Criaturas que luchan (van a Línea de Defensa)
 * - "Talisman": Hechizos de un solo uso (efectos inmediatos)
 * - "Oro": Recursos para jugar cartas (van a Reserva de Oro)
 * - "Totem": Permanentes con efectos continuos (van a Línea de Apoyo)
 * - "Arma": Equipamientos para Aliados (van a Línea de Apoyo)
 */
class Carta {
    constructor(id, nombre, tipo, coste, ataque, defensa, textoHabilidad, imagen) {
        this.id = id;
        this.nombre = nombre;
        // Tipos válidos: Aliado, Talisman, Oro, Totem, Arma
        this.tipo = tipo;
        this.coste = coste; // Coste en recursos (generados por Oros)
        this.ataque = ataque || 0; // Solo para Aliados
        this.defensa = defensa || 0; // Solo para Aliados (defensa actual, puede reducirse)
        this.defensaMaxima = defensa || 0; // Defensa máxima original
        this.textoHabilidad = textoHabilidad || '';
        this.imagen = imagen || '';
        // Estado de la carta (para Aliados)
        this.girada = false; // Si está girada (usado, no puede atacar)
        this.equipada = false; // Si tiene un Arma equipada
    }

    /**
     * Crea una carta desde un objeto JSON
     */
    static fromJSON(json) {
        return new Carta(
            json.id,
            json.nombre,
            json.tipo,
            json.coste,
            json.ataque,
            json.defensa,
            json.textoHabilidad,
            json.imagen
        );
    }

    /**
     * Convierte la carta a un objeto JSON
     */
    toJSON() {
        return {
            id: this.id,
            nombre: this.nombre,
            tipo: this.tipo,
            coste: this.coste,
            ataque: this.ataque,
            defensa: this.defensa,
            textoHabilidad: this.textoHabilidad,
            imagen: this.imagen
        };
    }

    /**
     * Verifica si la carta puede ser jugada con los recursos disponibles
     */
    puedeJugarse(recursosDisponibles) {
        return recursosDisponibles >= this.coste;
    }

    /**
     * Verifica si la carta es un Aliado
     */
    esAliado() {
        return this.tipo === 'Aliado';
    }

    /**
     * Verifica si la carta es un Oro
     */
    esOro() {
        return this.tipo === 'Oro';
    }

    /**
     * Aplica daño a un Aliado
     */
    recibirDano(cantidad) {
        if (this.esAliado()) {
            this.defensa -= cantidad;
            return this.defensa <= 0; // Retorna true si fue destruido
        }
        return false;
    }

    /**
     * Verifica si el Aliado está destruido
     */
    estaDestruido() {
        return this.esAliado() && this.defensa <= 0;
    }
}

module.exports = Carta;

