# 💻 Ejemplos de Código: Módulo de Usuarios

Este documento contiene ejemplos prácticos de implementación para el módulo de usuarios.

---

## 🔐 1. Autenticación

### 1.1 UserRepository (server/repository/UserRepository.js)

```javascript
const Database = require('better-sqlite3');
const bcrypt = require('bcrypt');
const path = require('path');

class UserRepository {
    constructor(dbPath = null) {
        const defaultPath = path.join(__dirname, '..', 'data', 'users', 'users.db');
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
                experiencia INTEGER DEFAULT 0
            )
        `);

        // Tabla estadísticas
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS estadisticas_usuario (
                usuario_id TEXT PRIMARY KEY,
                partidas_jugadas INTEGER DEFAULT 0,
                partidas_ganadas INTEGER DEFAULT 0,
                partidas_perdidas INTEGER DEFAULT 0,
                partidas_empatadas INTEGER DEFAULT 0,
                puntos_totales INTEGER DEFAULT 0,
                racha_victorias INTEGER DEFAULT 0,
                mejor_racha_victorias INTEGER DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);

        // Índices
        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
            CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
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

        // Insertar usuario
        const insertUsuario = this.db.prepare(`
            INSERT INTO usuarios (id, username, email, password_hash, nombre_completo)
            VALUES (?, ?, ?, ?, ?)
        `);
        insertUsuario.run(id, username, email, password_hash, nombre_completo || null);

        // Crear estadísticas iniciales
        const insertStats = this.db.prepare(`
            INSERT INTO estadisticas_usuario (usuario_id)
            VALUES (?)
        `);
        insertStats.run(id);

        return this.buscarPorId(id);
    }

    buscarPorId(id) {
        return this.db.prepare('SELECT id, username, email, nombre_completo, avatar_url, nivel, experiencia FROM usuarios WHERE id = ?')
            .get(id);
    }

    buscarPorUsername(username) {
        return this.db.prepare('SELECT * FROM usuarios WHERE username = ?')
            .get(username);
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

        if (campos.length === 0) return this.buscarPorId(id);

        valores.push(id);
        const sql = `UPDATE usuarios SET ${campos.join(', ')} WHERE id = ?`;
        this.db.prepare(sql).run(...valores);

        return this.buscarPorId(id);
    }

    cerrar() {
        this.db.close();
    }
}

module.exports = UserRepository;
```

### 1.2 AuthController (server/controllers/AuthController.js)

```javascript
const jwt = require('jsonwebtoken');
const UserRepository = require('../repository/UserRepository');

const JWT_SECRET = process.env.JWT_SECRET || 'tu_secreto_super_seguro_cambiar_en_produccion';
const JWT_EXPIRATION = '24h';

class AuthController {
    constructor() {
        this.userRepo = new UserRepository();
    }

    async register(req, res) {
        try {
            const { username, email, password, nombre_completo } = req.body;

            // Validaciones
            if (!username || !email || !password) {
                return res.status(400).json({
                    success: false,
                    error: 'Username, email y password son requeridos'
                });
            }

            if (password.length < 8) {
                return res.status(400).json({
                    success: false,
                    error: 'La contraseña debe tener al menos 8 caracteres'
                });
            }

            // Crear usuario
            const usuario = await this.userRepo.crearUsuario({
                username,
                email,
                password,
                nombre_completo
            });

            // Generar token
            const token = jwt.sign(
                { userId: usuario.id, username: usuario.username },
                JWT_SECRET,
                { expiresIn: JWT_EXPIRATION }
            );

            res.status(201).json({
                success: true,
                data: {
                    user: {
                        id: usuario.id,
                        username: usuario.username,
                        email: usuario.email,
                        nombre_completo: usuario.nombre_completo
                    },
                    token
                }
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }

    async login(req, res) {
        try {
            const { username, password } = req.body;

            if (!username || !password) {
                return res.status(400).json({
                    success: false,
                    error: 'Username y password son requeridos'
                });
            }

            const usuario = await this.userRepo.verificarPassword(username, password);
            if (!usuario) {
                return res.status(401).json({
                    success: false,
                    error: 'Credenciales inválidas'
                });
            }

            // Generar token
            const token = jwt.sign(
                { userId: usuario.id, username: usuario.username },
                JWT_SECRET,
                { expiresIn: JWT_EXPIRATION }
            );

            res.json({
                success: true,
                data: {
                    user: {
                        id: usuario.id,
                        username: usuario.username,
                        email: usuario.email,
                        nombre_completo: usuario.nombre_completo
                    },
                    token
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    async me(req, res) {
        try {
            const usuario = this.userRepo.buscarPorId(req.user.userId);
            if (!usuario) {
                return res.status(404).json({
                    success: false,
                    error: 'Usuario no encontrado'
                });
            }

            res.json({
                success: true,
                data: usuario
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new AuthController();
```

### 1.3 Middleware de Autenticación (server/middleware/auth.js)

```javascript
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'tu_secreto_super_seguro_cambiar_en_produccion';

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({
            success: false,
            error: 'Token de autenticación requerido'
        });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({
                success: false,
                error: 'Token inválido o expirado'
            });
        }

        req.user = user;
        next();
    });
}

function optionalAuth(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
        jwt.verify(token, JWT_SECRET, (err, user) => {
            if (!err) {
                req.user = user;
            }
        });
    }

    next();
}

module.exports = { authenticateToken, optionalAuth };
```

### 1.4 Rutas de Autenticación (server/routes/auth.js)

```javascript
const express = require('express');
const router = express.Router();
const authController = require('../controllers/AuthController');
const { authenticateToken } = require('../middleware/auth');

router.post('/register', authController.register.bind(authController));
router.post('/login', authController.login.bind(authController));
router.get('/me', authenticateToken, authController.me.bind(authController));

module.exports = router;
```

---

## 🃏 2. Sistema de Mazos

### 2.1 DeckRepository (server/repository/DeckRepository.js)

```javascript
const Database = require('better-sqlite3');
const path = require('path');

class DeckRepository {
    constructor(dbPath = null) {
        const defaultPath = path.join(__dirname, '..', 'data', 'users', 'users.db');
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
        const cartasJson = JSON.stringify(cartas);

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
        if (datos.cartas !== undefined) {
            campos.push('cartas = ?');
            valores.push(JSON.stringify(datos.cartas));
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

    cerrar() {
        this.db.close();
    }
}

module.exports = DeckRepository;
```

### 2.2 Validador de Mazos (server/utils/deckValidator.js)

```javascript
class DeckValidator {
    constructor(cardRepository) {
        this.cardRepo = cardRepository;
    }

    validarTamañoMazo(mazo) {
        return mazo.cartas.length === 50;
    }

    validarOroInicial(mazo) {
        if (!mazo.oro_inicial_id) {
            return { valido: false, error: 'Debe incluir un Oro Inicial' };
        }

        // Verificar que la carta de oro inicial existe
        const oroInicial = this.cardRepo.buscarPorId(mazo.oro_inicial_id);
        if (!oroInicial || oroInicial.tipo !== 'Oro') {
            return { valido: false, error: 'El Oro Inicial debe ser una carta de tipo Oro' };
        }

        return { valido: true };
    }

    validarCopias(mazo) {
        const conteo = {};
        const errores = [];

        // Contar todas las cartas (incluyendo oro inicial si está en el mazo)
        mazo.cartas.forEach(cartaId => {
            const carta = this.cardRepo.buscarPorId(cartaId);
            if (!carta) {
                errores.push(`Carta ${cartaId} no encontrada`);
                return;
            }

            const nombre = carta.nombre;
            conteo[nombre] = (conteo[nombre] || 0) + 1;

            // Verificar límites
            if (carta.esUnica && conteo[nombre] > 1) {
                errores.push(`Carta única "${nombre}" tiene más de 1 copia`);
            } else if (!carta.esUnica && conteo[nombre] > 3) {
                errores.push(`Carta "${nombre}" tiene más de 3 copias`);
            }
        });

        return {
            valido: errores.length === 0,
            errores
        };
    }

    validarMinimoAliados(mazo, minimo = 15) {
        const aliados = mazo.cartas.filter(cartaId => {
            const carta = this.cardRepo.buscarPorId(cartaId);
            return carta && carta.tipo === 'Aliado';
        });

        if (aliados.length < minimo) {
            return {
                valido: false,
                error: `Debe tener al menos ${minimo} Aliados (tiene ${aliados.length})`
            };
        }

        return { valido: true };
    }

    validarMazoCompleto(mazo, formato = 'Racial Edición') {
        const errores = [];

        // Validar tamaño
        if (!this.validarTamañoMazo(mazo)) {
            errores.push('El mazo debe tener exactamente 50 cartas');
        }

        // Validar oro inicial
        const oroResult = this.validarOroInicial(mazo);
        if (!oroResult.valido) {
            errores.push(oroResult.error);
        }

        // Validar copias
        const copiasResult = this.validarCopias(mazo);
        if (!copiasResult.valido) {
            errores.push(...copiasResult.errores);
        }

        // Validar mínimo de aliados
        const aliadosResult = this.validarMinimoAliados(mazo);
        if (!aliadosResult.valido) {
            errores.push(aliadosResult.error);
        }

        // Validaciones específicas de formato
        if (formato === 'Racial Edición' || formato === 'Racial Soporte Libre') {
            const razaResult = this.validarRaza(mazo, formato, mazo.raza);
            if (!razaResult.valido) {
                errores.push(razaResult.error);
            }
        }

        return {
            valido: errores.length === 0,
            errores
        };
    }

    validarRaza(mazo, formato, raza) {
        if (!raza) {
            return { valido: false, error: 'Debe especificar una raza' };
        }

        const aliados = mazo.cartas.map(id => this.cardRepo.buscarPorId(id))
            .filter(c => c && c.tipo === 'Aliado');

        const razasDiferentes = [...new Set(aliados.map(a => a.raza).filter(Boolean))];

        if (razasDiferentes.length > 1) {
            return {
                valido: false,
                error: `Todos los Aliados deben ser de la misma raza. Encontradas: ${razasDiferentes.join(', ')}`
            };
        }

        if (razasDiferentes[0] !== raza) {
            return {
                valido: false,
                error: `La raza especificada (${raza}) no coincide con los Aliados del mazo`
            };
        }

        return { valido: true };
    }
}

module.exports = DeckValidator;
```

---

## 📊 3. Estadísticas

### 3.1 StatsRepository (server/repository/StatsRepository.js)

```javascript
const Database = require('better-sqlite3');
const path = require('path');

class StatsRepository {
    constructor(dbPath = null) {
        const defaultPath = path.join(__dirname, '..', 'data', 'users', 'users.db');
        this.dbPath = dbPath || defaultPath;
        this.db = new Database(this.dbPath);
    }

    obtenerEstadisticas(usuario_id) {
        return this.db.prepare(`
            SELECT * FROM estadisticas_usuario WHERE usuario_id = ?
        `).get(usuario_id);
    }

    actualizarEstadisticas(usuario_id, resultado) {
        // resultado: 'victoria', 'derrota', 'empate'
        const stats = this.obtenerEstadisticas(usuario_id);
        if (!stats) return null;

        const updates = {
            partidas_jugadas: stats.partidas_jugadas + 1
        };

        if (resultado === 'victoria') {
            updates.partidas_ganadas = stats.partidas_ganadas + 1;
            updates.puntos_totales = stats.puntos_totales + 10;
            updates.racha_victorias = stats.racha_victorias + 1;
            if (updates.racha_victorias > stats.mejor_racha_victorias) {
                updates.mejor_racha_victorias = updates.racha_victorias;
            }
        } else if (resultado === 'derrota') {
            updates.partidas_perdidas = stats.partidas_perdidas + 1;
            updates.puntos_totales = stats.puntos_totales + 1;
            updates.racha_victorias = 0;
        } else if (resultado === 'empate') {
            updates.partidas_empatadas = stats.partidas_empatadas + 1;
            updates.puntos_totales = stats.puntos_totales + 5;
        }

        this.db.prepare(`
            UPDATE estadisticas_usuario SET
                partidas_jugadas = ?,
                partidas_ganadas = ?,
                partidas_perdidas = ?,
                partidas_empatadas = ?,
                puntos_totales = ?,
                racha_victorias = ?,
                mejor_racha_victorias = ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE usuario_id = ?
        `).run(
            updates.partidas_jugadas,
            updates.partidas_ganadas || stats.partidas_ganadas,
            updates.partidas_perdidas || stats.partidas_perdidas,
            updates.partidas_empatadas || stats.partidas_empatadas,
            updates.puntos_totales,
            updates.racha_victorias,
            updates.mejor_racha_victorias || stats.mejor_racha_victorias,
            usuario_id
        );

        return this.obtenerEstadisticas(usuario_id);
    }

    obtenerLeaderboard(limite = 100) {
        return this.db.prepare(`
            SELECT 
                u.id,
                u.username,
                u.avatar_url,
                s.partidas_jugadas,
                s.partidas_ganadas,
                s.partidas_perdidas,
                s.puntos_totales,
                s.racha_victorias,
                s.mejor_racha_victorias,
                CASE 
                    WHEN s.partidas_jugadas > 0 
                    THEN ROUND((s.partidas_ganadas * 100.0 / s.partidas_jugadas), 2)
                    ELSE 0
                END as porcentaje_victorias
            FROM estadisticas_usuario s
            JOIN usuarios u ON s.usuario_id = u.id
            WHERE u.activo = 1
            ORDER BY s.puntos_totales DESC, s.partidas_ganadas DESC
            LIMIT ?
        `).all(limite);
    }
}

module.exports = StatsRepository;
```

---

## 🎨 4. Frontend - Ejemplos

### 4.1 Cliente API (public/js/api.js)

```javascript
class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error en la petición');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (data.success && data.data.token) {
            this.setToken(data.data.token);
        }
        return data;
    }

    async logout() {
        this.setToken(null);
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Decks
    async getDecks() {
        return this.request('/decks');
    }

    async createDeck(deckData) {
        return this.request('/decks', {
            method: 'POST',
            body: JSON.stringify(deckData)
        });
    }

    async updateDeck(id, deckData) {
        return this.request(`/decks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(deckData)
        });
    }

    async deleteDeck(id) {
        return this.request(`/decks/${id}`, {
            method: 'DELETE'
        });
    }

    async validateDeck(deckData) {
        return this.request('/decks/validate', {
            method: 'POST',
            body: JSON.stringify(deckData)
        });
    }

    // Stats
    async getUserStats(userId = 'me') {
        return this.request(`/stats/user/${userId}`);
    }

    async getLeaderboard() {
        return this.request('/stats/leaderboard');
    }
}

const api = new ApiClient();
```

### 4.2 Login (public/js/auth.js)

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const result = await api.login(username, password);
                if (result.success) {
                    window.location.href = '/profile.html';
                } else {
                    showError(result.error || 'Error al iniciar sesión');
                }
            } catch (error) {
                showError(error.message);
            }
        });
    }
});
```

### 4.3 Gestión de Mazos (public/js/decks.js)

```javascript
let allDecks = [];

async function loadDecks() {
    try {
        const result = await api.getDecks();
        if (result.success) {
            allDecks = result.data;
            displayDecks(allDecks);
        }
    } catch (error) {
        showError('Error al cargar mazos: ' + error.message);
    }
}

async function createDeck() {
    const deckData = {
        nombre: document.getElementById('deckName').value,
        formato: document.getElementById('deckFormat').value,
        raza: document.getElementById('deckRace').value,
        cartas: selectedCards, // Array de IDs de cartas seleccionadas
        oro_inicial_id: selectedOroInicial
    };

    try {
        // Validar primero
        const validation = await api.validateDeck(deckData);
        if (!validation.success || !validation.data.valido) {
            showError('Mazo inválido: ' + validation.data.errores.join(', '));
            return;
        }

        // Crear mazo
        const result = await api.createDeck(deckData);
        if (result.success) {
            showSuccess('Mazo creado correctamente');
            loadDecks();
        }
    } catch (error) {
        showError('Error al crear mazo: ' + error.message);
    }
}
```

---

## 🔧 5. Integración en server.js

```javascript
// Agregar al inicio de server.js
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const deckRoutes = require('./routes/decks');
const statsRoutes = require('./routes/stats');

// Después de app.use(express.json())
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/decks', deckRoutes);
app.use('/api/stats', statsRoutes);
```

---

Estos ejemplos proporcionan una base sólida para implementar el módulo de usuarios. Adaptar según necesidades específicas del proyecto.

