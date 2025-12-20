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
    constructor(id, nombre, tipo, coste, fuerza, textoHabilidad, imagen) {
        this.id = id;
        this.nombre = nombre;
        // Tipos válidos: Aliado, Talisman, Oro, Totem, Arma
        this.tipo = tipo;
        this.coste = coste; // Coste en recursos (generados por Oros)
        this.fuerza = fuerza || 0; // Solo para Aliados - representa tanto ataque como defensa
        this.textoHabilidad = textoHabilidad || '';
        this.imagen = imagen || '';
        // Estado de la carta (para Aliados)
        this.girada = false; // Si está girada (usado, no puede atacar)
        this.equipada = false; // Si tiene un Arma equipada
        // Sistema de habilidades estructuradas
        this.abilities = []; // Array de habilidades en formato JSON estructurado
        this.abilitiesValid = false; // Si las habilidades han sido validadas
    }

    /**
     * Crea una carta desde un objeto JSON
     */
    static fromJSON(json) {
        // Compatibilidad: si viene fuerza, usarla; si no, usar ataque o defensa
        const fuerza = json.fuerza !== undefined && json.fuerza !== null
            ? json.fuerza
            : (json.ataque || json.defensa || 0);
        
        const carta = new Carta(
            json.id,
            json.nombre,
            json.tipo,
            json.coste,
            fuerza,
            json.textoHabilidad,
            json.imagen
        );
        
        // Cargar habilidades si vienen en el JSON (desde BD)
        if (json.abilities !== undefined) {
            carta.abilities = json.abilities;
            carta.abilitiesValid = json.abilitiesValid !== undefined ? json.abilitiesValid : true;
        } else if (json.abilities_json) {
            // Si viene como JSON string desde BD
            carta.loadAbilitiesFromJSON(json.abilities_json);
        }
        
        return carta;
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
            fuerza: this.fuerza,
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
     * Nota: En Mitos y Leyendas, la fuerza se reduce cuando recibe daño
     */
    recibirDano(cantidad) {
        if (this.esAliado()) {
            this.fuerza -= cantidad;
            return this.fuerza <= 0; // Retorna true si fue destruido
        }
        return false;
    }

    /**
     * Verifica si el Aliado está destruido
     */
    estaDestruido() {
        return this.esAliado() && this.fuerza <= 0;
    }

    /**
     * Procesa las habilidades de la carta usando el AbilityManager
     * @param {AbilityManager} abilityManager - Gestor de habilidades
     * @param {boolean} force - Si true, reprocesa incluso si ya tiene habilidades
     */
    processAbilities(abilityManager, force = false) {
        if (!abilityManager) {
            return;
        }

        // Si ya tiene habilidades válidas y no es forzado, no reprocesar
        if (!force && this.abilities && this.abilities.length >= 0 && this.abilitiesValid) {
            return;
        }

        const processed = abilityManager.processCard(this);
        this.abilities = processed.abilities;
        this.abilitiesValid = processed.abilitiesValid;
        
        if (processed.abilitiesErrors && processed.abilitiesErrors.length > 0) {
            console.warn(`Errores al procesar habilidades de ${this.nombre}:`, processed.abilitiesErrors);
        }
    }
    
    /**
     * Carga habilidades desde JSON (cuando vienen de la BD)
     * @param {string|Object} abilitiesData - JSON string o objeto con habilidades
     */
    loadAbilitiesFromJSON(abilitiesData) {
        if (!abilitiesData) {
            this.abilities = [];
            this.abilitiesValid = false;
            return;
        }
        
        try {
            const data = typeof abilitiesData === 'string' 
                ? JSON.parse(abilitiesData) 
                : abilitiesData;
            
            this.abilities = data.abilities || [];
            this.abilitiesValid = this.abilities.length > 0 || !this.textoHabilidad;
        } catch (error) {
            console.warn(`Error cargando habilidades para ${this.nombre}:`, error.message);
            this.abilities = [];
            this.abilitiesValid = false;
        }
    }

    /**
     * Obtiene habilidades de un tipo específico
     * @param {string} type - Tipo de habilidad (triggered, static, activated, response)
     * @returns {Array} Habilidades del tipo especificado
     */
    getAbilitiesByType(type) {
        if (!Array.isArray(this.abilities)) {
            return [];
        }
        return this.abilities.filter(ability => ability.type === type);
    }

    /**
     * Obtiene habilidades que se activan con un trigger específico
     * @param {string} triggerType - Tipo de trigger
     * @returns {Array} Habilidades con ese trigger
     */
    getAbilitiesByTrigger(triggerType) {
        if (!Array.isArray(this.abilities)) {
            return [];
        }
        return this.abilities.filter(ability => 
            (ability.type === 'triggered' || ability.type === 'response') &&
            ability.trigger &&
            ability.trigger.type === triggerType
        );
    }
}

module.exports = Carta;

