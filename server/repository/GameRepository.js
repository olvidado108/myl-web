const Database = require('better-sqlite3');
const path = require('path');

class GameRepository {
    constructor(dbPath = null) {
        const defaultPath = path.join(__dirname, '..', 'data', 'game.db');
        this.dbPath = dbPath || defaultPath;
        this.db = new Database(this.dbPath);
        this.db.pragma('journal_mode = WAL');
        this._crearTablas();
    }

    _crearTablas() {
        // La tabla partidas ya debería existir si DeckRepository fue inicializado
        // pero la creamos por si acaso
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
            CREATE INDEX IF NOT EXISTS idx_partidas_jugador1 ON partidas(jugador1_id);
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_partidas_jugador2 ON partidas(jugador2_id);
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_partidas_estado ON partidas(estado);
        `);
    }

    /**
     * Crea una nueva partida
     */
    crearPartida(datos) {
        const {
            jugador1_id,
            jugador2_id = null,
            mazo1_id,
            mazo2_id = null,
            estado_juego
        } = datos;

        const id = `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const estadoJuegoJson = estado_juego ? JSON.stringify(estado_juego) : null;

        this.db.prepare(`
            INSERT INTO partidas (
                id, jugador1_id, jugador2_id, mazo1_id, mazo2_id,
                estado, estado_juego, turnos
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            id,
            jugador1_id,
            jugador2_id,
            mazo1_id,
            mazo2_id,
            'en_curso',
            estadoJuegoJson,
            0
        );

        return this.buscarPorId(id);
    }

    /**
     * Busca una partida por ID
     */
    buscarPorId(id) {
        const partida = this.db.prepare('SELECT * FROM partidas WHERE id = ?').get(id);
        
        if (!partida) {
            return null;
        }

        // Parsear estado_juego si existe
        if (partida.estado_juego) {
            try {
                partida.estado_juego = JSON.parse(partida.estado_juego);
            } catch (e) {
                partida.estado_juego = null;
            }
        }

        return partida;
    }

    /**
     * Actualiza el estado de una partida
     */
    actualizarPartida(id, datos) {
        const campos = [];
        const valores = [];

        if (datos.estado !== undefined) {
            campos.push('estado = ?');
            valores.push(datos.estado);
        }

        if (datos.estado_juego !== undefined) {
            campos.push('estado_juego = ?');
            valores.push(JSON.stringify(datos.estado_juego));
        }

        if (datos.ganador_id !== undefined) {
            campos.push('ganador_id = ?');
            valores.push(datos.ganador_id);
        }

        if (datos.resultado !== undefined) {
            campos.push('resultado = ?');
            valores.push(datos.resultado);
        }

        if (datos.turnos !== undefined) {
            campos.push('turnos = ?');
            valores.push(datos.turnos);
        }

        if (datos.duracion_segundos !== undefined) {
            campos.push('duracion_segundos = ?');
            valores.push(datos.duracion_segundos);
        }

        if (datos.fecha_fin !== undefined) {
            campos.push('fecha_fin = ?');
            valores.push(datos.fecha_fin);
        }

        if (campos.length === 0) {
            return this.buscarPorId(id);
        }

        valores.push(id);
        this.db.prepare(`
            UPDATE partidas 
            SET ${campos.join(', ')}
            WHERE id = ?
        `).run(...valores);

        return this.buscarPorId(id);
    }

    /**
     * Finaliza una partida
     */
    finalizarPartida(id, ganadorId, resultado, turnos) {
        const fechaInicio = this.db.prepare('SELECT fecha_inicio FROM partidas WHERE id = ?').get(id);
        const duracion = fechaInicio 
            ? Math.floor((Date.now() - new Date(fechaInicio.fecha_inicio).getTime()) / 1000)
            : null;

        return this.actualizarPartida(id, {
            estado: 'finalizada',
            ganador_id: ganadorId,
            resultado: resultado,
            turnos: turnos,
            duracion_segundos: duracion,
            fecha_fin: new Date().toISOString()
        });
    }

    /**
     * Lista partidas de un usuario
     */
    listarPorUsuario(userId, filtros = {}) {
        let query = `
            SELECT * FROM partidas 
            WHERE (jugador1_id = ? OR jugador2_id = ?)
        `;
        const params = [userId, userId];

        if (filtros.estado) {
            query += ' AND estado = ?';
            params.push(filtros.estado);
        }

        query += ' ORDER BY fecha_inicio DESC LIMIT ? OFFSET ?';
        const limite = filtros.limite || 50;
        const offset = filtros.offset || 0;
        params.push(limite, offset);

        const partidas = this.db.prepare(query).all(...params);

        // Parsear estado_juego para cada partida
        return partidas.map(partida => {
            if (partida.estado_juego) {
                try {
                    partida.estado_juego = JSON.parse(partida.estado_juego);
                } catch (e) {
                    partida.estado_juego = null;
                }
            }
            return partida;
        });
    }

    /**
     * Cierra la conexión a la base de datos
     */
    cerrar() {
        this.db.close();
    }
}

module.exports = GameRepository;








