/**
 * Clase que representa una carta del juego
 */
class Carta {
    constructor(id, nombre, tipo, coste, ataque, defensa, textoHabilidad, imagen) {
        this.id = id;
        this.nombre = nombre;
        this.tipo = tipo; // Ej: "Aliado", "Hechizo", "Artefacto"
        this.coste = coste;
        this.ataque = ataque || 0;
        this.defensa = defensa || 0;
        this.textoHabilidad = textoHabilidad || '';
        this.imagen = imagen || '';
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
     * Verifica si la carta puede ser jugada con el maná disponible
     */
    puedeJugarse(manaDisponible) {
        return manaDisponible >= this.coste;
    }
}

module.exports = Carta;

