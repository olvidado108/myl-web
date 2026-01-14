/**
 * Repositorio de Cartas - Gestión centralizada de todas las cartas del juego
 * Usa JSON con indexación en memoria para búsquedas rápidas
 * 
 * Para proyectos más grandes, considera migrar a SQLite
 */

const fs = require('fs');
const path = require('path');

class CardRepository {
    constructor() {
        this.cartas = new Map(); // ID -> Carta
        this.indices = {
            porTipo: new Map(),      // tipo -> Set de IDs
            porRaza: new Map(),       // raza -> Set de IDs
            porEdicion: new Map(),   // edicion -> Set de IDs
            porNombre: new Map(),    // nombre normalizado -> Set de IDs
            porRareza: new Map()     // rareza -> Set de IDs
        };
        this.cargado = false;
    }

    /**
     * Carga cartas desde archivos JSON
     * @param {string|string[]} rutasArchivos - Ruta(s) a archivo(s) JSON
     */
    cargarDesdeJSON(rutasArchivos) {
        const rutas = Array.isArray(rutasArchivos) ? rutasArchivos : [rutasArchivos];
        let totalCargadas = 0;

        for (const ruta of rutas) {
            const rutaCompleta = path.isAbsolute(ruta) 
                ? ruta 
                : path.join(__dirname, '..', 'data', 'cards', ruta);
            
            if (!fs.existsSync(rutaCompleta)) {
                console.warn(`⚠️  Archivo no encontrado: ${rutaCompleta}`);
                continue;
            }

            const datos = JSON.parse(fs.readFileSync(rutaCompleta, 'utf-8'));
            const cartas = Array.isArray(datos) ? datos : [datos];
            
            for (const carta of cartas) {
                this._agregarCarta(carta);
                totalCargadas++;
            }
            
            console.log(`✅ Cargadas ${cartas.length} cartas desde ${path.basename(rutaCompleta)}`);
        }

        this.cargado = true;
        return totalCargadas;
    }

    /**
     * Carga automáticamente todas las cartas desde los archivos JSON disponibles
     */
    cargarTodas() {
        if (this.cargado) return;

        const cardsDir = path.join(__dirname, '..', 'data', 'cards');
        const archivos = fs.readdirSync(cardsDir)
            .filter(f => f.endsWith('.json') && f !== 'todas_las_cartas.json')
            .map(f => path.join(cardsDir, f));

        if (archivos.length === 0) {
            console.warn('⚠️  No se encontraron archivos JSON de cartas');
            return 0;
        }

        return this.cargarDesdeJSON(archivos);
    }

    /**
     * Agrega una carta al repositorio e indexa
     */
    _agregarCarta(carta) {
        if (!carta.id) {
            console.warn('⚠️  Carta sin ID, omitiendo:', carta.nombre);
            return;
        }

        // Agregar al mapa principal
        this.cartas.set(carta.id, carta);

        // Indexar por tipo
        const tipo = carta.tipo || 'desconocido';
        if (!this.indices.porTipo.has(tipo)) {
            this.indices.porTipo.set(tipo, new Set());
        }
        this.indices.porTipo.get(tipo).add(carta.id);

        // Indexar por raza
        const raza = carta.raza || null;
        if (raza) {
            if (!this.indices.porRaza.has(raza)) {
                this.indices.porRaza.set(raza, new Set());
            }
            this.indices.porRaza.get(raza).add(carta.id);
        }

        // Indexar por edición
        const edicion = carta.edicion || null;
        if (edicion) {
            if (!this.indices.porEdicion.has(edicion)) {
                this.indices.porEdicion.set(edicion, new Set());
            }
            this.indices.porEdicion.get(edicion).add(carta.id);
        }

        // Indexar por nombre normalizado
        const nombreNorm = (carta.nombreNormalizado || carta.nombre || '').toLowerCase();
        if (nombreNorm) {
            if (!this.indices.porNombre.has(nombreNorm)) {
                this.indices.porNombre.set(nombreNorm, new Set());
            }
            this.indices.porNombre.get(nombreNorm).add(carta.id);
        }

        // Indexar por rareza
        const rareza = carta.rareza || null;
        if (rareza) {
            if (!this.indices.porRareza.has(rareza)) {
                this.indices.porRareza.set(rareza, new Set());
            }
            this.indices.porRareza.get(rareza).add(carta.id);
        }
    }

    /**
     * Busca una carta por ID
     */
    buscarPorId(id) {
        return this.cartas.get(id) || null;
    }

    /**
     * Busca cartas por nombre (exacto o parcial)
     */
    buscarPorNombre(nombre, exacto = false) {
        if (exacto) {
            const nombreNorm = nombre.toLowerCase();
            const ids = this.indices.porNombre.get(nombreNorm);
            if (!ids) return [];
            return Array.from(ids).map(id => this.cartas.get(id));
        } else {
            // Búsqueda parcial
            const nombreLower = nombre.toLowerCase();
            const resultados = [];
            
            for (const [nombreNorm, ids] of this.indices.porNombre.entries()) {
                if (nombreNorm.includes(nombreLower)) {
                    for (const id of ids) {
                        resultados.push(this.cartas.get(id));
                    }
                }
            }
            
            // También buscar en nombres completos (por si no está normalizado)
            for (const carta of this.cartas.values()) {
                const nombreCarta = (carta.nombre || '').toLowerCase();
                if (nombreCarta.includes(nombreLower) && !resultados.find(c => c.id === carta.id)) {
                    resultados.push(carta);
                }
            }
            
            return resultados.sort((a, b) => a.nombre.localeCompare(b.nombre));
        }
    }

    /**
     * Busca cartas por tipo
     */
    buscarPorTipo(tipo) {
        const ids = this.indices.porTipo.get(tipo);
        if (!ids) return [];
        return Array.from(ids)
            .map(id => this.cartas.get(id))
            .sort((a, b) => a.nombre.localeCompare(b.nombre));
    }

    /**
     * Busca cartas por raza
     */
    buscarPorRaza(raza) {
        const ids = this.indices.porRaza.get(raza);
        if (!ids) return [];
        return Array.from(ids)
            .map(id => this.cartas.get(id))
            .sort((a, b) => a.nombre.localeCompare(b.nombre));
    }

    /**
     * Busca cartas por edición
     */
    buscarPorEdicion(edicion) {
        const ids = this.indices.porEdicion.get(edicion);
        if (!ids) return [];
        return Array.from(ids)
            .map(id => this.cartas.get(id))
            .sort((a, b) => a.nombre.localeCompare(b.nombre));
    }

    /**
     * Búsqueda avanzada con múltiples filtros
     */
    buscar(filtros = {}) {
        let candidatos = new Set(this.cartas.keys());

        // Filtrar por tipo
        if (filtros.tipo) {
            const idsTipo = this.indices.porTipo.get(filtros.tipo) || new Set();
            candidatos = new Set([...candidatos].filter(id => idsTipo.has(id)));
        }

        // Filtrar por raza
        if (filtros.raza !== undefined) {
            if (filtros.raza === null) {
                // Cartas sin raza
                candidatos = new Set([...candidatos].filter(id => {
                    const carta = this.cartas.get(id);
                    return !carta.raza;
                }));
            } else {
                const idsRaza = this.indices.porRaza.get(filtros.raza) || new Set();
                candidatos = new Set([...candidatos].filter(id => idsRaza.has(id)));
            }
        }

        // Filtrar por edición
        if (filtros.edicion) {
            const idsEdicion = this.indices.porEdicion.get(filtros.edicion) || new Set();
            candidatos = new Set([...candidatos].filter(id => idsEdicion.has(id)));
        }

        // Filtrar por rareza
        if (filtros.rareza) {
            const idsRareza = this.indices.porRareza.get(filtros.rareza) || new Set();
            candidatos = new Set([...candidatos].filter(id => idsRareza.has(id)));
        }

        // Filtrar por nombre (parcial)
        if (filtros.nombre) {
            const nombreLower = filtros.nombre.toLowerCase();
            candidatos = new Set([...candidatos].filter(id => {
                const carta = this.cartas.get(id);
                const nombre = (carta.nombre || '').toLowerCase();
                const nombreNorm = (carta.nombreNormalizado || '').toLowerCase();
                return nombre.includes(nombreLower) || nombreNorm.includes(nombreLower);
            }));
        }

        // Filtrar por esUnica
        if (filtros.esUnica !== undefined) {
            candidatos = new Set([...candidatos].filter(id => {
                const carta = this.cartas.get(id);
                return Boolean(carta.esUnica) === filtros.esUnica;
            }));
        }

        // Filtrar por esOroInicial
        if (filtros.esOroInicial !== undefined) {
            candidatos = new Set([...candidatos].filter(id => {
                const carta = this.cartas.get(id);
                return Boolean(carta.esOroInicial) === filtros.esOroInicial;
            }));
        }

        // Excluir variantes si se solicita
        if (filtros.excluirVariantes) {
            candidatos = new Set([...candidatos].filter(id => {
                const carta = this.cartas.get(id);
                return !carta.esVariante;
            }));
        }

        // Convertir a array y ordenar
        let resultados = Array.from(candidatos)
            .map(id => this.cartas.get(id))
            .sort((a, b) => a.nombre.localeCompare(b.nombre));

        // Aplicar límite
        if (filtros.limite) {
            resultados = resultados.slice(0, filtros.limite);
        }

        return resultados;
    }

    /**
     * Obtiene todas las cartas
     */
    obtenerTodas(excluirVariantes = false) {
        if (excluirVariantes) {
            return this.buscar({ excluirVariantes: true });
        }
        return Array.from(this.cartas.values())
            .sort((a, b) => a.nombre.localeCompare(b.nombre));
    }

    /**
     * Cuenta el total de cartas
     */
    contarCartas(excluirVariantes = false) {
        if (excluirVariantes) {
            return Array.from(this.cartas.values())
                .filter(c => !c.esVariante).length;
        }
        return this.cartas.size;
    }

    /**
     * Obtiene estadísticas de la base de datos
     */
    obtenerEstadisticas() {
        const stats = {
            total: this.contarCartas(),
            porTipo: {},
            porRaza: {},
            porEdicion: {},
            porRareza: {}
        };

        // Contar por tipo
        for (const [tipo, ids] of this.indices.porTipo.entries()) {
            stats.porTipo[tipo] = ids.size;
        }

        // Contar por raza
        for (const [raza, ids] of this.indices.porRaza.entries()) {
            stats.porRaza[raza] = ids.size;
        }

        // Contar por edición
        for (const [edicion, ids] of this.indices.porEdicion.entries()) {
            stats.porEdicion[edicion] = ids.size;
        }

        // Contar por rareza
        for (const [rareza, ids] of this.indices.porRareza.entries()) {
            stats.porRareza[rareza] = ids.size;
        }

        return stats;
    }

    /**
     * Agrega o actualiza una carta
     */
    guardarCarta(carta) {
        if (!carta.id) {
            throw new Error('La carta debe tener un ID');
        }
        
        // Si ya existe, eliminar de los índices primero
        if (this.cartas.has(carta.id)) {
            this._eliminarDeIndices(carta.id);
        }
        
        // Agregar/actualizar la carta
        this._agregarCarta(carta);
        return carta;
    }

    /**
     * Elimina una carta del repositorio
     */
    eliminarCarta(id) {
        if (!this.cartas.has(id)) {
            return false;
        }
        
        this._eliminarDeIndices(id);
        this.cartas.delete(id);
        return true;
    }

    /**
     * Elimina una carta de todos los índices
     */
    _eliminarDeIndices(id) {
        const carta = this.cartas.get(id);
        if (!carta) return;

        // Eliminar de índice por tipo
        const tipo = carta.tipo || 'desconocido';
        if (this.indices.porTipo.has(tipo)) {
            this.indices.porTipo.get(tipo).delete(id);
        }

        // Eliminar de índice por raza
        const raza = carta.raza || null;
        if (raza && this.indices.porRaza.has(raza)) {
            this.indices.porRaza.get(raza).delete(id);
        }

        // Eliminar de índice por edición
        const edicion = carta.edicion || null;
        if (edicion && this.indices.porEdicion.has(edicion)) {
            this.indices.porEdicion.get(edicion).delete(id);
        }

        // Eliminar de índice por nombre
        const nombreNorm = (carta.nombreNormalizado || carta.nombre || '').toLowerCase();
        if (nombreNorm && this.indices.porNombre.has(nombreNorm)) {
            this.indices.porNombre.get(nombreNorm).delete(id);
        }

        // Eliminar de índice por rareza
        const rareza = carta.rareza || null;
        if (rareza && this.indices.porRareza.has(rareza)) {
            this.indices.porRareza.get(rareza).delete(id);
        }
    }

    /**
     * Guarda todas las cartas en el archivo todas_las_cartas.json
     */
    guardarATodasLasCartas() {
        const rutaArchivo = path.join(__dirname, '..', 'data', 'cards', 'todas_las_cartas.json');
        const todasLasCartas = this.obtenerTodas();
        
        fs.writeFileSync(
            rutaArchivo,
            JSON.stringify(todasLasCartas, null, 2),
            'utf-8'
        );
        
        return todasLasCartas.length;
    }
}

module.exports = CardRepository;












