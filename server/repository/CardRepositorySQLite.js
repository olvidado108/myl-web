/**
 * Repositorio de Cartas usando SQLite
 * Implementa la misma interfaz que CardRepository para compatibilidad
 */

const Database = require('better-sqlite3');
const path = require('path');

class CardRepositorySQLite {
    constructor(dbPath = null) {
        // Usar la base de datos unificada por defecto
        const defaultPath = path.join(__dirname, '..', 'data', 'game.db');
        this.dbPath = dbPath || defaultPath;
        this.db = new Database(this.dbPath, { readonly: false });
        
        // Habilitar WAL mode para mejor rendimiento
        this.db.pragma('journal_mode = WAL');
        
        // Crear índices si no existen
        this._crearIndices();
        this._asegurarColumnaIsVerificada();
        
        this.cargado = true;
    }

    /**
     * Crea índices para mejorar el rendimiento de las búsquedas
     */
    _crearIndices() {
        const indices = [
            'CREATE INDEX IF NOT EXISTS idx_tipo ON cartas(tipo)',
            'CREATE INDEX IF NOT EXISTS idx_raza ON cartas(raza)',
            'CREATE INDEX IF NOT EXISTS idx_edicion ON cartas(edicion)',
            'CREATE INDEX IF NOT EXISTS idx_rareza ON cartas(rareza)',
            'CREATE INDEX IF NOT EXISTS idx_nombre_normalizado ON cartas(nombreNormalizado)',
            'CREATE INDEX IF NOT EXISTS idx_nombre ON cartas(nombre)'
        ];
        
        indices.forEach(sql => {
            try {
                this.db.exec(sql);
            } catch (error) {
                console.warn(`Error creando índice: ${error.message}`);
            }
        });
        
        // Asegurar que la columna fuerza existe
        this._asegurarColumnaFuerza();
    }

    /**
     * Convierte una fila de la BD a un objeto carta
     */
    _filaACarta(row) {
        // Compatibilidad: si existe fuerza, usarla; si no, usar ataque o defensa
        const fuerza = row.fuerza !== undefined && row.fuerza !== null 
            ? row.fuerza 
            : (row.ataque || row.defensa || 0);
        
        // Normalizar textoHabilidad al leer de la base de datos
        const textoHabilidad = this._normalizarTextoHabilidad(row.textoHabilidad);
        
        // Parsear abilities_json si existe
        let abilities = [];
        let abilitiesValid = false;
        if (row.abilities_json) {
            try {
                const abilitiesData = JSON.parse(row.abilities_json);
                abilities = abilitiesData.abilities || [];
                abilitiesValid = true;
            } catch (error) {
                console.warn(`Error parseando abilities_json para carta ${row.id}:`, error.message);
                abilities = [];
                abilitiesValid = false;
            }
        }
        
        return {
            id: row.id,
            nombre: row.nombre,
            tipo: row.tipo,
            coste: row.coste || 0,
            fuerza: fuerza,
            textoHabilidad: textoHabilidad,
            imagen: row.imagen || '',
            imagenUrl: row.imagenUrl || '',
            edicion: row.edicion || null,
            raza: row.raza || null,
            rareza: row.rareza || null,
            kit: row.kit || '',
            orden: row.orden || 0,
            esUnica: Boolean(row.esUnica),
            esOroInicial: Boolean(row.esOroInicial),
            link: row.link || '',
            nombreNormalizado: row.nombreNormalizado || '',
            tipoNormalizado: row.tipoNormalizado || '',
            isVerified: Boolean(row.is_verified),
            // Habilidades estructuradas
            abilities: abilities,
            abilitiesValid: abilitiesValid,
            abilitiesVersion: row.abilities_version || null,
            abilitiesProcessedAt: row.abilities_processed_at || null
        };
    }

    /**
     * Busca una carta por ID
     */
    buscarPorId(id) {
        const stmt = this.db.prepare('SELECT * FROM cartas WHERE id = ?');
        const row = stmt.get(id);
        return row ? this._filaACarta(row) : null;
    }

    /**
     * Busca cartas por nombre (exacto o parcial)
     */
    buscarPorNombre(nombre, exacto = false) {
        if (exacto) {
            const stmt = this.db.prepare('SELECT * FROM cartas WHERE nombreNormalizado = ? OR nombre = ? COLLATE NOCASE');
            const rows = stmt.all(nombre.toLowerCase(), nombre);
            return rows.map(row => this._filaACarta(row));
        } else {
            const stmt = this.db.prepare(`
                SELECT * FROM cartas 
                WHERE nombre LIKE ? OR nombreNormalizado LIKE ? 
                ORDER BY nombre COLLATE NOCASE
            `);
            const searchTerm = `%${nombre}%`;
            const rows = stmt.all(searchTerm, searchTerm.toLowerCase());
            return rows.map(row => this._filaACarta(row));
        }
    }

    /**
     * Busca cartas por tipo
     */
    buscarPorTipo(tipo) {
        const stmt = this.db.prepare('SELECT * FROM cartas WHERE tipo = ? ORDER BY nombre COLLATE NOCASE');
        const rows = stmt.all(tipo);
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Busca cartas por raza
     */
    buscarPorRaza(raza) {
        const stmt = this.db.prepare('SELECT * FROM cartas WHERE raza = ? ORDER BY nombre COLLATE NOCASE');
        const rows = stmt.all(raza);
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Busca cartas por edición
     */
    buscarPorEdicion(edicion) {
        const stmt = this.db.prepare('SELECT * FROM cartas WHERE edicion = ? ORDER BY nombre COLLATE NOCASE');
        const rows = stmt.all(edicion);
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Búsqueda avanzada con múltiples filtros
     */
    buscar(filtros = {}) {
        let sql = 'SELECT * FROM cartas WHERE 1=1';
        const params = [];

        if (filtros.tipo) {
            sql += ' AND tipo = ?';
            params.push(filtros.tipo);
        }

        if (filtros.raza !== undefined) {
            if (filtros.raza === null) {
                sql += ' AND (raza IS NULL OR raza = "")';
            } else {
                sql += ' AND raza = ?';
                params.push(filtros.raza);
            }
        }

        if (filtros.edicion) {
            sql += ' AND edicion = ?';
            params.push(filtros.edicion);
        }

        if (filtros.rareza) {
            sql += ' AND rareza = ?';
            params.push(filtros.rareza);
        }

        if (filtros.nombre) {
            sql += ' AND (nombre LIKE ? OR nombreNormalizado LIKE ?)';
            const searchTerm = `%${filtros.nombre}%`;
            params.push(searchTerm, searchTerm.toLowerCase());
        }

        if (filtros.esUnica !== undefined) {
            sql += ' AND esUnica = ?';
            params.push(filtros.esUnica ? 1 : 0);
        }

        if (filtros.esOroInicial !== undefined) {
            sql += ' AND esOroInicial = ?';
            params.push(filtros.esOroInicial ? 1 : 0);
        }

        if (filtros.excluirVariantes) {
            sql += ' AND (tieneVariantes = 0 OR tieneVariantes IS NULL)';
        }

        sql += ' ORDER BY nombre COLLATE NOCASE';

        if (filtros.limite) {
            sql += ' LIMIT ?';
            params.push(filtros.limite);
        }

        const stmt = this.db.prepare(sql);
        const rows = stmt.all(...params);
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Obtiene todas las cartas
     */
    obtenerTodas(excluirVariantes = false) {
        if (excluirVariantes) {
            return this.buscar({ excluirVariantes: true });
        }
        const stmt = this.db.prepare('SELECT * FROM cartas ORDER BY nombre COLLATE NOCASE');
        const rows = stmt.all();
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Busca cartas sin habilidad (textoHabilidad vacío, null, "NaN", o "null")
     * @param {Object} filtros - Filtros opcionales (limite, excluirVariantes, etc.)
     * @returns {Array} Array de cartas sin habilidad
     */
    buscarSinHabilidad(filtros = {}) {
        let sql = `
            SELECT * FROM cartas 
            WHERE textoHabilidad IS NULL 
               OR textoHabilidad = '' 
               OR TRIM(textoHabilidad) = ''
               OR textoHabilidad = 'NaN'
               OR textoHabilidad = 'null'
        `;
        const params = [];

        if (filtros.excluirVariantes) {
            sql += ' AND (tieneVariantes = 0 OR tieneVariantes IS NULL)';
        }

        sql += ' ORDER BY nombre COLLATE NOCASE';

        if (filtros.limite) {
            sql += ' LIMIT ?';
            params.push(filtros.limite);
        }

        const stmt = this.db.prepare(sql);
        const rows = params.length > 0 ? stmt.all(...params) : stmt.all();
        return rows.map(row => this._filaACarta(row));
    }

    /**
     * Cuenta el total de cartas
     */
    contarCartas(excluirVariantes = false) {
        if (excluirVariantes) {
            const stmt = this.db.prepare('SELECT COUNT(*) as count FROM cartas WHERE (tieneVariantes = 0 OR tieneVariantes IS NULL)');
            return stmt.get().count;
        }
        const stmt = this.db.prepare('SELECT COUNT(*) as count FROM cartas');
        return stmt.get().count;
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
        const tipos = this.db.prepare('SELECT tipo, COUNT(*) as count FROM cartas GROUP BY tipo').all();
        tipos.forEach(row => {
            stats.porTipo[row.tipo] = row.count;
        });

        // Contar por raza
        const razas = this.db.prepare('SELECT raza, COUNT(*) as count FROM cartas WHERE raza IS NOT NULL AND raza != \'\' GROUP BY raza').all();
        razas.forEach(row => {
            stats.porRaza[row.raza] = row.count;
        });

        // Contar por edición
        const ediciones = this.db.prepare('SELECT edicion, COUNT(*) as count FROM cartas WHERE edicion IS NOT NULL GROUP BY edicion').all();
        ediciones.forEach(row => {
            stats.porEdicion[row.edicion] = row.count;
        });

        // Contar por rareza
        const rarezas = this.db.prepare('SELECT rareza, COUNT(*) as count FROM cartas WHERE rareza IS NOT NULL AND rareza != \'\' GROUP BY rareza').all();
        rarezas.forEach(row => {
            stats.porRareza[row.rareza] = row.count;
        });

        return stats;
    }

    /**
     * Normaliza el textoHabilidad: convierte "NaN", "null", strings vacíos a cadena vacía
     */
    _normalizarTextoHabilidad(texto) {
        // Si es null, undefined, o no es string, retornar cadena vacía
        if (texto === null || texto === undefined || typeof texto !== 'string') {
            return '';
        }
        // Si es "NaN" o "null" como string, retornar cadena vacía
        if (texto === 'NaN' || texto === 'null' || texto.trim() === '') {
            return '';
        }
        return texto.trim();
    }

    /**
     * Agrega o actualiza una carta
     */
    guardarCarta(carta) {
        if (!carta.id) {
            throw new Error('La carta debe tener un ID');
        }

        // Compatibilidad: obtener fuerza de carta.fuerza, o de carta.ataque/defensa
        const fuerza = carta.fuerza !== undefined && carta.fuerza !== null
            ? carta.fuerza
            : (carta.ataque || carta.defensa || 0);

        // Normalizar textoHabilidad antes de guardar
        const textoHabilidadNormalizado = this._normalizarTextoHabilidad(carta.textoHabilidad);

        // Verificar si la columna fuerza existe, si no, crearla
        this._asegurarColumnaFuerza();
        
        // Asegurar que la columna abilities_json existe
        this._asegurarColumnaAbilities();

        // Preparar abilities_json si viene en la carta
        let abilitiesJson = null;
        if (carta.abilities && Array.isArray(carta.abilities)) {
            abilitiesJson = JSON.stringify({
                version: carta.abilitiesVersion || "1.0",
                abilities: carta.abilities
            });
        } else if (carta.abilities_json) {
            // Si ya viene como JSON string, usarlo directamente
            abilitiesJson = carta.abilities_json;
        }

        // Construir query dinámicamente según qué columnas existen
        const tableInfo = this.db.prepare("PRAGMA table_info(cartas)").all();
        const tieneAbilitiesJson = tableInfo.some(col => col.name === 'abilities_json');
        
        let sql, values;
        
        if (tieneAbilitiesJson) {
            sql = `
                INSERT INTO cartas (
                    id, nombre, tipo, coste, fuerza,
                    textoHabilidad, imagen, imagenUrl, edicion, raza, rareza,
                    kit, orden, esUnica, esOroInicial, link, nombreNormalizado, tipoNormalizado,
                    abilities_json, abilities_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nombre = excluded.nombre,
                    tipo = excluded.tipo,
                    coste = excluded.coste,
                    fuerza = excluded.fuerza,
                    textoHabilidad = excluded.textoHabilidad,
                    imagen = excluded.imagen,
                    imagenUrl = excluded.imagenUrl,
                    edicion = excluded.edicion,
                    raza = excluded.raza,
                    rareza = excluded.rareza,
                    kit = excluded.kit,
                    orden = excluded.orden,
                    esUnica = excluded.esUnica,
                    esOroInicial = excluded.esOroInicial,
                    link = excluded.link,
                    nombreNormalizado = excluded.nombreNormalizado,
                    tipoNormalizado = excluded.tipoNormalizado,
                    abilities_json = COALESCE(excluded.abilities_json, cartas.abilities_json),
                    abilities_version = COALESCE(excluded.abilities_version, cartas.abilities_version)
            `;
            
            values = [
                carta.id,
                carta.nombre,
                carta.tipo,
                carta.coste || 0,
                fuerza,
                textoHabilidadNormalizado,
                carta.imagen || '',
                carta.imagenUrl || '',
                carta.edicion || null,
                carta.raza || null,
                carta.rareza || null,
                carta.kit || '',
                carta.orden || 0,
                carta.esUnica ? 1 : 0,
                carta.esOroInicial ? 1 : 0,
                carta.link || '',
                carta.nombreNormalizado || (carta.nombre ? carta.nombre.toLowerCase() : ''),
                carta.tipoNormalizado || (carta.tipo ? carta.tipo.toLowerCase() : ''),
                abilitiesJson,
                carta.abilitiesVersion || "1.0"
            ];
        } else {
            // Sin abilities_json (compatibilidad con BD antigua)
            sql = `
                INSERT INTO cartas (
                    id, nombre, tipo, coste, fuerza,
                    textoHabilidad, imagen, imagenUrl, edicion, raza, rareza,
                    kit, orden, esUnica, esOroInicial, link, nombreNormalizado, tipoNormalizado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nombre = excluded.nombre,
                    tipo = excluded.tipo,
                    coste = excluded.coste,
                    fuerza = excluded.fuerza,
                    textoHabilidad = excluded.textoHabilidad,
                    imagen = excluded.imagen,
                    imagenUrl = excluded.imagenUrl,
                    edicion = excluded.edicion,
                    raza = excluded.raza,
                    rareza = excluded.rareza,
                    kit = excluded.kit,
                    orden = excluded.orden,
                    esUnica = excluded.esUnica,
                    esOroInicial = excluded.esOroInicial,
                    link = excluded.link,
                    nombreNormalizado = excluded.nombreNormalizado,
                    tipoNormalizado = excluded.tipoNormalizado
            `;
            
            values = [
                carta.id,
                carta.nombre,
                carta.tipo,
                carta.coste || 0,
                fuerza,
                textoHabilidadNormalizado,
                carta.imagen || '',
                carta.imagenUrl || '',
                carta.edicion || null,
                carta.raza || null,
                carta.rareza || null,
                carta.kit || '',
                carta.orden || 0,
                carta.esUnica ? 1 : 0,
                carta.esOroInicial ? 1 : 0,
                carta.link || '',
                carta.nombreNormalizado || (carta.nombre ? carta.nombre.toLowerCase() : ''),
                carta.tipoNormalizado || (carta.tipo ? carta.tipo.toLowerCase() : '')
            ];
        }

        const stmt = this.db.prepare(sql);
        stmt.run(...values);

        return this.buscarPorId(carta.id);
    }
    
    /**
     * Asegura que la columna abilities_json existe en la tabla
     */
    _asegurarColumnaAbilities() {
        try {
            const tableInfo = this.db.prepare("PRAGMA table_info(cartas)").all();
            const tieneAbilitiesJson = tableInfo.some(col => col.name === 'abilities_json');
            
            if (!tieneAbilitiesJson) {
                this.db.exec('ALTER TABLE cartas ADD COLUMN abilities_json TEXT');
                this.db.exec('ALTER TABLE cartas ADD COLUMN abilities_version TEXT DEFAULT "1.0"');
                this.db.exec('ALTER TABLE cartas ADD COLUMN abilities_processed_at DATETIME');
            }
        } catch (error) {
            // Si hay error, probablemente la columna ya existe
            console.warn('Advertencia al verificar columna abilities_json:', error.message);
        }
    }
    
    /**
     * Actualiza las habilidades de una carta
     * @param {string} cardId - ID de la carta
     * @param {Array} abilities - Array de habilidades estructuradas
     * @param {string} version - Versión del formato (opcional)
     */
    actualizarHabilidades(cardId, abilities, version = "1.0") {
        this._asegurarColumnaAbilities();
        
        const abilitiesJson = JSON.stringify({
            version: version,
            abilities: abilities
        });
        
        const stmt = this.db.prepare(`
            UPDATE cartas 
            SET abilities_json = ?,
                abilities_version = ?,
                abilities_processed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        `);
        
        stmt.run(abilitiesJson, version, cardId);
        
        return this.buscarPorId(cardId);
    }

    /**
     * Asegura que la columna fuerza existe en la tabla
     */
    _asegurarColumnaFuerza() {
        try {
            // Verificar si la columna fuerza existe
            const tableInfo = this.db.prepare("PRAGMA table_info(cartas)").all();
            const tieneFuerza = tableInfo.some(col => col.name === 'fuerza');
            
            if (!tieneFuerza) {
                // Agregar columna fuerza
                this.db.exec('ALTER TABLE cartas ADD COLUMN fuerza INTEGER DEFAULT 0');
                
                // Migrar datos: usar ataque o defensa para poblar fuerza
                this.db.exec(`
                    UPDATE cartas 
                    SET fuerza = COALESCE(ataque, defensa, 0)
                    WHERE fuerza IS NULL OR fuerza = 0
                `);
                
                console.log('✅ Columna "fuerza" agregada y datos migrados');
            }
        } catch (error) {
            // Si hay error, probablemente la columna ya existe o hay otro problema
            console.warn('Advertencia al verificar columna fuerza:', error.message);
        }
    }

    /**
     * Elimina una carta
     */
    eliminarCarta(id) {
        const stmt = this.db.prepare('DELETE FROM cartas WHERE id = ?');
        const result = stmt.run(id);
        return result.changes > 0;
    }

    /**
     * Limpia valores "NaN" y "null" en textoHabilidad de todas las cartas
     * También sincroniza habilidades entre cartas con el mismo nombre
     */
    limpiarYNormalizarHabilidades() {
        console.log('🧹 Limpiando y normalizando habilidades en la base de datos...');
        
        // Primero, limpiar todos los "NaN" y "null" en textoHabilidad
        const stmtLimpieza = this.db.prepare(`
            UPDATE cartas 
            SET textoHabilidad = '' 
            WHERE textoHabilidad = 'NaN' 
               OR textoHabilidad = 'null' 
               OR textoHabilidad IS NULL
               OR TRIM(textoHabilidad) = ''
        `);
        const resultadoLimpieza = stmtLimpieza.run();
        console.log(`   ✅ Limpiados ${resultadoLimpieza.changes} registros con valores inválidos`);

        // Obtener todas las cartas agrupadas por nombre
        const stmtCartas = this.db.prepare('SELECT * FROM cartas ORDER BY nombre COLLATE NOCASE');
        const todasLasCartas = stmtCartas.all();
        
        // Agrupar por nombre normalizado (manejar variantes)
        const cartasPorNombre = {};
        todasLasCartas.forEach(row => {
            // Normalizar nombre: remover "(Variante)" y espacios extra
            let nombreNormalizado = (row.nombre || '').toLowerCase().trim();
            // Remover "(variante)" o "(Variante)" del nombre para agrupar correctamente
            nombreNormalizado = nombreNormalizado.replace(/\s*\(variante\)\s*$/i, '').trim();
            
            if (!cartasPorNombre[nombreNormalizado]) {
                cartasPorNombre[nombreNormalizado] = [];
            }
            cartasPorNombre[nombreNormalizado].push(row);
        });

        // Sincronizar habilidades entre cartas con el mismo nombre
        let cartasActualizadas = 0;
        const stmtActualizacion = this.db.prepare('UPDATE cartas SET textoHabilidad = ? WHERE id = ?');

        Object.values(cartasPorNombre).forEach(grupo => {
            if (grupo.length <= 1) return; // No hay nada que sincronizar si solo hay una carta

            // Encontrar la habilidad más completa (no vacía, no NaN)
            let habilidadComun = null;
            for (const carta of grupo) {
                const habilidad = this._normalizarTextoHabilidad(carta.textoHabilidad);
                if (habilidad) {
                    habilidadComun = habilidad;
                    break; // Usar la primera habilidad válida encontrada
                }
            }

            // Si encontramos una habilidad común, aplicarla a todas las cartas del grupo que no la tengan
            if (habilidadComun) {
                grupo.forEach(carta => {
                    const habilidadActual = this._normalizarTextoHabilidad(carta.textoHabilidad);
                    if (!habilidadActual) {
                        stmtActualizacion.run(habilidadComun, carta.id);
                        cartasActualizadas++;
                    }
                });
            }
        });

        console.log(`   ✅ Sincronizadas ${cartasActualizadas} cartas con habilidades de otras versiones`);
        console.log(`✨ Limpieza y normalización completada`);
        
        return {
            limpiados: resultadoLimpieza.changes,
            sincronizadas: cartasActualizadas
        };
    }

    /**
     * Cierra la conexión a la base de datos
     */
    cerrar() {
        if (this.db) {
            this.db.close();
        }
    }

    /**
     * Asegura que la columna suggested exista en carta_tags
     */
    _asegurarColumnaSuggested() {
        const cols = this.db.prepare("PRAGMA table_info('carta_tags')").all();
        const has = cols.some(c => c.name === 'suggested');
        if (!has) {
            this.db.exec("ALTER TABLE carta_tags ADD COLUMN suggested INTEGER DEFAULT 0");
        }
    }

    /**
     * Asegura columna is_verified en cartas
     */
    _asegurarColumnaIsVerificada() {
        const cols = this.db.prepare("PRAGMA table_info('cartas')").all();
        const has = cols.some(c => c.name === 'is_verified');
        if (!has) {
            this.db.exec("ALTER TABLE cartas ADD COLUMN is_verified INTEGER DEFAULT 0");
        }
    }

    /**
     * Lista el catálogo de tags
     */
    listarTags() {
        return this.db.prepare('SELECT id, slug, nombre, categoria, descripcion FROM tags ORDER BY slug').all();
    }

    /**
     * Marca o desmarca una carta como verificada
     */
    marcarVerificada(cartaId, valor = true) {
        this._asegurarColumnaIsVerificada();
        const res = this.db.prepare('UPDATE cartas SET is_verified = ? WHERE id = ?').run(valor ? 1 : 0, cartaId);
        return res.changes > 0;
    }

    /**
     * Crea o actualiza un tag
     */
    crearOActualizarTag({ slug, nombre, categoria = null, descripcion = null }) {
        const stmt = this.db.prepare(`
            INSERT INTO tags (slug, nombre, categoria, descripcion)
            VALUES (@slug, @nombre, @categoria, @descripcion)
            ON CONFLICT(slug) DO UPDATE SET
                nombre = excluded.nombre,
                categoria = excluded.categoria,
                descripcion = excluded.descripcion
        `);
        stmt.run({ slug, nombre, categoria, descripcion });
        return this.db.prepare('SELECT id, slug, nombre, categoria, descripcion FROM tags WHERE slug = ?').get(slug);
    }

    _tagIdFromSlugOrId(tag) {
        if (typeof tag === 'number') return tag;
        const row = this.db.prepare('SELECT id FROM tags WHERE slug = ?').get(tag);
        if (!row) throw new Error(`Tag no encontrado: ${tag}`);
        return row.id;
    }

    /**
     * Asigna un tag a una carta (por slug o id de tag)
     * @param {string|number} tag - slug o id de tag
     * @param {number|string} cartaId - id de la carta
     * @param {number} suggested - 1 si es sugerido, 0 si es confirmado
     */
    asignarTagACarta(tag, cartaId, suggested = 0) {
        this._asegurarColumnaSuggested();
        const tagId = this._tagIdFromSlugOrId(tag);
        const stmt = this.db.prepare(`
            INSERT INTO carta_tags (carta_id, tag_id, suggested)
            VALUES (?, ?, ?)
            ON CONFLICT(carta_id, tag_id) DO UPDATE SET suggested=excluded.suggested
        `);
        stmt.run(cartaId, tagId, suggested);
        return true;
    }

    /**
     * Confirma todos los tags de una carta (pasa suggested=0)
     */
    confirmarTagsDeCarta(cartaId) {
        this._asegurarColumnaSuggested();
        const res = this.db.prepare('UPDATE carta_tags SET suggested = 0 WHERE carta_id = ?').run(cartaId);
        return res.changes;
    }

    /**
     * Obtiene tags de una carta con el estado suggested
     */
    obtenerTagsDeCarta(cartaId) {
        this._asegurarColumnaSuggested();
        const rows = this.db.prepare(`
            SELECT t.slug, t.nombre, t.categoria, t.descripcion, ct.suggested
            FROM carta_tags ct
            JOIN tags t ON t.id = ct.tag_id
            WHERE ct.carta_id = ?
            ORDER BY t.slug
        `).all(cartaId);
        return rows;
    }

    /**
     * Lista cartas que tienen tags sugeridos (suggested=1)
     */
    obtenerCartasConTagsSugeridos({ limite = 50, offset = 0, search = null } = {}) {
        this._asegurarColumnaSuggested();
        const params = [];
        let sql = `
            SELECT c.id, c.nombre, c.tipo, c.textoHabilidad,
                   GROUP_CONCAT(t.slug, ',') AS tags,
                   GROUP_CONCAT(t.nombre, ',') AS tags_nombres
            FROM cartas c
            JOIN carta_tags ct ON ct.carta_id = c.id
            JOIN tags t ON t.id = ct.tag_id
            WHERE ct.suggested = 1
        `;
        if (search) {
            sql += ` AND (c.nombre LIKE ? OR c.id LIKE ?) `;
            const term = `%${search}%`;
            params.push(term, term);
        }
        sql += `
            GROUP BY c.id
            ORDER BY c.nombre COLLATE NOCASE
            LIMIT ? OFFSET ?
        `;
        params.push(limite, offset);
        const rows = this.db.prepare(sql).all(...params);
        return rows.map(r => ({
            id: r.id,
            nombre: r.nombre,
            tipo: r.tipo,
            textoHabilidad: r.textoHabilidad || '',
            tags: (r.tags || '').split(',').filter(Boolean),
            tagsNombres: (r.tags_nombres || '').split(',').filter(Boolean)
        }));
    }
}

module.exports = CardRepositorySQLite;




