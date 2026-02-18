const Database = require('better-sqlite3');
const path = require('path');

class DeckRepository {
    constructor(dbPath = null) {
        const defaultPath = process.env.DATABASE_PATH || path.join(__dirname, '..', 'data', 'game.db');
        this.dbPath = dbPath || defaultPath;
        this.db = new Database(this.dbPath);
        this.db.pragma('journal_mode = WAL');
        this._crearTablas();
    }

    _crearTablas() {
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS mazos (
                id TEXT PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                formato TEXT,
                raza TEXT,
                edicion_original TEXT,
                cartas TEXT NOT NULL,
                oro_inicial_id TEXT,
                es_publico BOOLEAN DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                veces_usado INTEGER DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_mazos_usuario ON mazos(usuario_id);
        `);

        // Crear tabla de partidas si no existe
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS partidas (
                id TEXT PRIMARY KEY,
                jugador1_id TEXT NOT NULL,
                jugador2_id TEXT,
                mazo1_id TEXT,
                mazo2_id TEXT,
                estado TEXT NOT NULL,
                ganador_id TEXT,
                resultado TEXT,
                turnos INTEGER DEFAULT 0,
                duracion_segundos INTEGER,
                fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_fin DATETIME,
                estado_juego TEXT,
                FOREIGN KEY (jugador1_id) REFERENCES usuarios(id),
                FOREIGN KEY (jugador2_id) REFERENCES usuarios(id),
                FOREIGN KEY (mazo1_id) REFERENCES mazos(id),
                FOREIGN KEY (mazo2_id) REFERENCES mazos(id)
            )
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_partidas_mazo1 ON partidas(mazo1_id);
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_partidas_mazo2 ON partidas(mazo2_id);
        `);
    }

    crearMazo(datos) {
        const {
            usuario_id,
            nombre,
            descripcion,
            formato,
            raza,
            edicion_original,
            cartas,
            oro_inicial_id,
            es_publico = false
        } = datos;

        const id = `deck_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const cartasJson = JSON.stringify(cartas || []);

        this.db.prepare(`
            INSERT INTO mazos (
                id, usuario_id, nombre, descripcion, formato, raza,
                edicion_original, cartas, oro_inicial_id, es_publico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            id, usuario_id, nombre, descripcion || null,
            formato || null, raza || null, edicion_original || null,
            cartasJson, oro_inicial_id || null, es_publico ? 1 : 0
        );

        return this.buscarPorId(id);
    }

    buscarPorId(id) {
        const mazo = this.db.prepare('SELECT * FROM mazos WHERE id = ?').get(id);
        if (mazo) {
            mazo.cartas = JSON.parse(mazo.cartas);
            mazo.es_publico = Boolean(mazo.es_publico);
        }
        return mazo;
    }

    listarPorUsuario(usuario_id, incluirPublicos = false) {
        let sql = 'SELECT * FROM mazos WHERE usuario_id = ?';
        const params = [usuario_id];

        if (incluirPublicos) {
            sql += ' OR es_publico = 1';
        }

        sql += ' ORDER BY fecha_actualizacion DESC';

        const mazos = this.db.prepare(sql).all(...params);
        return mazos.map(mazo => {
            mazo.cartas = JSON.parse(mazo.cartas);
            mazo.es_publico = Boolean(mazo.es_publico);
            return mazo;
        });
    }

    actualizarMazo(id, datos) {
        const campos = [];
        const valores = [];

        if (datos.nombre !== undefined) {
            campos.push('nombre = ?');
            valores.push(datos.nombre);
        }
        if (datos.descripcion !== undefined) {
            campos.push('descripcion = ?');
            valores.push(datos.descripcion);
        }
        if (datos.formato !== undefined) {
            campos.push('formato = ?');
            valores.push(datos.formato);
        }
        if (datos.raza !== undefined) {
            campos.push('raza = ?');
            valores.push(datos.raza);
        }
        if (datos.edicion_original !== undefined) {
            campos.push('edicion_original = ?');
            valores.push(datos.edicion_original);
        }
        if (datos.cartas !== undefined) {
            campos.push('cartas = ?');
            valores.push(JSON.stringify(datos.cartas));
        }
        if (datos.oro_inicial_id !== undefined) {
            campos.push('oro_inicial_id = ?');
            valores.push(datos.oro_inicial_id);
        }
        if (datos.es_publico !== undefined) {
            campos.push('es_publico = ?');
            valores.push(datos.es_publico ? 1 : 0);
        }

        campos.push('fecha_actualizacion = CURRENT_TIMESTAMP');
        valores.push(id);

        if (campos.length === 1) return this.buscarPorId(id);

        const sql = `UPDATE mazos SET ${campos.join(', ')} WHERE id = ?`;
        this.db.prepare(sql).run(...valores);

        return this.buscarPorId(id);
    }

    eliminarMazo(id) {
        const result = this.db.prepare('DELETE FROM mazos WHERE id = ?').run(id);
        return result.changes > 0;
    }

    incrementarUso(id) {
        this.db.prepare('UPDATE mazos SET veces_usado = veces_usado + 1 WHERE id = ?').run(id);
    }

    /**
     * Obtiene estadísticas de juego para un mazo específico
     */
    obtenerEstadisticasMazo(mazoId, usuarioId) {
        const stats = {
            partidas_jugadas: 0,
            partidas_ganadas: 0,
            partidas_perdidas: 0,
            partidas_empatadas: 0,
            partidas_abandonadas: 0,
            porcentaje_victorias: 0
        };

        // Verificar que el mazo pertenece al usuario
        const mazo = this.buscarPorId(mazoId);
        if (!mazo || mazo.usuario_id !== usuarioId) {
            return stats;
        }

        // Contar partidas donde este mazo fue usado (como mazo1 o mazo2)
        // y donde el usuario es el dueño del mazo
        const partidas = this.db.prepare(`
            SELECT 
                estado,
                ganador_id,
                resultado,
                mazo1_id,
                mazo2_id,
                jugador1_id,
                jugador2_id
            FROM partidas
            WHERE estado = 'finalizada'
            AND (
                (mazo1_id = ? AND jugador1_id = ?) OR
                (mazo2_id = ? AND jugador2_id = ?)
            )
        `).all(mazoId, usuarioId, mazoId, usuarioId);

        stats.partidas_jugadas = partidas.length;

        partidas.forEach(partida => {
            const esMazo1 = partida.mazo1_id === mazoId;
            const esJugadorDelMazo = (esMazo1 && partida.jugador1_id === usuarioId) || 
                                     (!esMazo1 && partida.jugador2_id === usuarioId);
            
            if (!esJugadorDelMazo) return; // Solo contar si el usuario es dueño del mazo

            const esGanador = partida.ganador_id === usuarioId;

            if (partida.resultado === 'abandono') {
                stats.partidas_abandonadas++;
            } else if (partida.resultado === 'empate') {
                stats.partidas_empatadas++;
            } else if (esGanador) {
                stats.partidas_ganadas++;
            } else {
                stats.partidas_perdidas++;
            }
        });

        // Calcular porcentaje de victorias (excluyendo abandonos y empates)
        const partidasConResultado = stats.partidas_jugadas - stats.partidas_abandonadas - stats.partidas_empatadas;
        if (partidasConResultado > 0) {
            stats.porcentaje_victorias = Math.round(
                (stats.partidas_ganadas / partidasConResultado) * 100
            );
        } else if (stats.partidas_jugadas > 0) {
            // Si todas fueron empates o abandonos, el porcentaje es 0
            stats.porcentaje_victorias = 0;
        }

        return stats;
    }

    /**
     * Lista mazos con sus estadísticas incluidas
     */
    listarPorUsuarioConEstadisticas(usuario_id, incluirPublicos = false) {
        const mazos = this.listarPorUsuario(usuario_id, incluirPublicos);
        
        return mazos.map(mazo => {
            const estadisticas = this.obtenerEstadisticasMazo(mazo.id, usuario_id);
            return {
                ...mazo,
                estadisticas
            };
        });
    }

    cerrar() {
        this.db.close();
    }
}

module.exports = DeckRepository;











