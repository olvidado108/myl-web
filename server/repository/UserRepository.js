const Database = require('better-sqlite3');
const bcrypt = require('bcrypt');
const path = require('path');

class UserRepository {
    constructor(dbPath = null) {
        const defaultPath = process.env.DATABASE_PATH || path.join(__dirname, '..', 'data', 'game.db');
        this.dbPath = dbPath || defaultPath;
        this.db = new Database(this.dbPath);
        this.db.pragma('journal_mode = WAL');
        this._crearTablas();
    }

    _crearTablas() {
        // Tabla usuarios
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT,
                avatar_url TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso DATETIME,
                activo BOOLEAN DEFAULT 1,
                nivel INTEGER DEFAULT 1,
                experiencia INTEGER DEFAULT 0,
                isAdmin BOOLEAN DEFAULT 0
            )
        `);
        
        // Migración: agregar columna 'isAdmin' si no existe (para bases de datos existentes)
        try {
            const columns = this.db.prepare("PRAGMA table_info(usuarios)").all();
            const hasIsAdmin = columns.some(col => col.name === 'isAdmin');
            if (!hasIsAdmin) {
                this.db.exec(`ALTER TABLE usuarios ADD COLUMN isAdmin BOOLEAN DEFAULT 0`);
                console.log('✅ Columna "isAdmin" agregada a la tabla usuarios');
            }
        } catch (error) {
            console.warn('⚠️ Advertencia al verificar/agregar columna isAdmin:', error.message);
        }

        // Tabla estadísticas
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS estadisticas_usuario (
                usuario_id TEXT PRIMARY KEY,
                partidas_jugadas INTEGER DEFAULT 0,
                partidas_ganadas INTEGER DEFAULT 0,
                partidas_perdidas INTEGER DEFAULT 0,
                partidas_empatadas INTEGER DEFAULT 0,
                partidas_abandonadas INTEGER DEFAULT 0,
                puntos_totales INTEGER DEFAULT 0,
                racha_victorias INTEGER DEFAULT 0,
                mejor_racha_victorias INTEGER DEFAULT 0,
                cartas_jugadas_totales INTEGER DEFAULT 0,
                turnos_jugados_totales INTEGER DEFAULT 0,
                tiempo_jugado_segundos INTEGER DEFAULT 0,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);

        // Tabla sesiones (para JWT tokens)
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS sesiones (
                id TEXT PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion DATETIME NOT NULL,
                activa BOOLEAN DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);

        // Tabla favoritos
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS favoritos (
                usuario_id TEXT NOT NULL,
                carta_id TEXT NOT NULL,
                fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, carta_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);

        // Índices
        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
            CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token_hash);
            CREATE INDEX IF NOT EXISTS idx_favoritos_usuario ON favoritos(usuario_id);
        `);
    }

    async crearUsuario(datos) {
        const { username, email, password, nombre_completo } = datos;
        
        // Verificar que no exista
        const existente = this.db.prepare('SELECT id FROM usuarios WHERE username = ? OR email = ?')
            .get(username, email);
        if (existente) {
            throw new Error('Usuario o email ya existe');
        }

        // Hash de contraseña
        const password_hash = await bcrypt.hash(password, 10);
        
        // Generar ID
        const id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Insertar usuario (por defecto isAdmin = false)
        const insertUsuario = this.db.prepare(`
            INSERT INTO usuarios (id, username, email, password_hash, nombre_completo, isAdmin)
            VALUES (?, ?, ?, ?, ?, ?)
        `);
        insertUsuario.run(id, username, email, password_hash, nombre_completo || null, 0);

        // Crear estadísticas iniciales
        const insertStats = this.db.prepare(`
            INSERT INTO estadisticas_usuario (usuario_id)
            VALUES (?)
        `);
        insertStats.run(id);

        return this.buscarPorId(id);
    }

    buscarPorId(id) {
        return this.db.prepare('SELECT id, username, email, nombre_completo, avatar_url, nivel, experiencia, fecha_registro, ultimo_acceso, isAdmin, activo FROM usuarios WHERE id = ?')
            .get(id);
    }

    buscarPorUsername(username) {
        return this.db.prepare('SELECT * FROM usuarios WHERE username = ?')
            .get(username);
    }

    buscarPorEmail(email) {
        return this.db.prepare('SELECT * FROM usuarios WHERE email = ?')
            .get(email);
    }

    async verificarPassword(username, password) {
        const usuario = this.buscarPorUsername(username);
        if (!usuario) {
            return null;
        }

        const esValida = await bcrypt.compare(password, usuario.password_hash);
        if (!esValida) {
            return null;
        }

        // Actualizar último acceso
        this.db.prepare('UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?')
            .run(usuario.id);

        return usuario;
    }

    actualizarUsuario(id, datos) {
        const campos = [];
        const valores = [];

        if (datos.nombre_completo !== undefined) {
            campos.push('nombre_completo = ?');
            valores.push(datos.nombre_completo);
        }
        if (datos.avatar_url !== undefined) {
            campos.push('avatar_url = ?');
            valores.push(datos.avatar_url);
        }
        if (datos.nivel !== undefined) {
            campos.push('nivel = ?');
            valores.push(datos.nivel);
        }
        if (datos.experiencia !== undefined) {
            campos.push('experiencia = ?');
            valores.push(datos.experiencia);
        }
        if (datos.isAdmin !== undefined) {
            campos.push('isAdmin = ?');
            valores.push(datos.isAdmin ? 1 : 0);
        }
        if (datos.activo !== undefined) {
            campos.push('activo = ?');
            valores.push(datos.activo ? 1 : 0);
        }

        if (campos.length === 0) return this.buscarPorId(id);

        valores.push(id);
        const sql = `UPDATE usuarios SET ${campos.join(', ')} WHERE id = ?`;
        this.db.prepare(sql).run(...valores);

        return this.buscarPorId(id);
    }
    
    /**
     * Lista todos los usuarios (para administradores)
     */
    listarTodos() {
        return this.db.prepare('SELECT id, username, email, nombre_completo, avatar_url, nivel, experiencia, fecha_registro, ultimo_acceso, activo, isAdmin FROM usuarios ORDER BY fecha_registro DESC')
            .all();
    }

    obtenerEstadisticas(usuarioId) {
        return this.db.prepare('SELECT * FROM estadisticas_usuario WHERE usuario_id = ?')
            .get(usuarioId);
    }

    cerrar() {
        this.db.close();
    }
}

module.exports = UserRepository;











