# 🤖 Instrucciones para el Agente: Implementar Fase 3 - Funcionalidades Avanzadas

**Objetivo:** Implementar funcionalidades avanzadas: rankings, replay de partidas, modo práctica vs IA  
**Tiempo estimado:** 3-4 semanas  
**Prioridad:** 🟢 BAJA (pero importante para completar el proyecto)

---

## 📋 Resumen de la Tarea

Implementar funcionalidades avanzadas que incluyen:
- ✅ Sistema de rankings y estadísticas
- ✅ Replay de partidas (grabar y reproducir)
- ✅ Modo de práctica vs IA
- ✅ Perfil de jugador mejorado

---

## 📚 Documentos de Referencia

**LEER PRIMERO estos documentos en orden:**

1. **`docs/ANALISIS_DUELING_NEXUS.md`**
   - Sección "Plan de Implementación Priorizado"
   - Contexto general del análisis

2. **`docs/ARCHITECTURE.md`**
   - Principios arquitectónicos del proyecto
   - Estructura de carpetas
   - Convenciones de código

3. **Código existente:**
   - `server/controllers/GameController.js` - Ver cómo se manejan las partidas
   - `server/repository/UserRepository.js` - Ver cómo se manejan usuarios
   - `public/js/game.js` - Ver cómo funciona el juego

---

## 🎯 Tareas Específicas a Implementar

### Tarea 1: Sistema de Rankings y Estadísticas

**Archivos a crear/modificar:**
- `server/repository/StatsRepository.js` (nuevo)
- `server/controllers/StatsController.js` (nuevo)
- `server/routes/stats.js` (nuevo)
- `server/models/UserStats.js` (nuevo)

**Qué debe hacer:**

#### 1.1 Crear Modelo de Estadísticas

**Archivo:** `server/models/UserStats.js`

```javascript
/**
 * Modelo de estadísticas de usuario
 */
class UserStats {
    constructor(data = {}) {
        this.userId = data.userId || null;
        this.wins = data.wins || 0;
        this.losses = data.losses || 0;
        this.draws = data.draws || 0;
        this.totalGames = data.totalGames || 0;
        this.winRate = data.winRate || 0;
        this.rating = data.rating || 1000; // Sistema ELO básico
        this.bestWinStreak = data.bestWinStreak || 0;
        this.currentWinStreak = data.currentWinStreak || 0;
        this.favoriteDeck = data.favoriteDeck || null;
        this.lastPlayed = data.lastPlayed || null;
    }

    /**
     * Calcula el win rate
     */
    calculateWinRate() {
        if (this.totalGames === 0) return 0;
        return (this.wins / this.totalGames) * 100;
    }

    /**
     * Actualiza estadísticas después de una partida
     */
    updateAfterGame(result, gameMode = 'ranked') {
        this.totalGames++;
        this.lastPlayed = new Date().toISOString();

        if (result === 'win') {
            this.wins++;
            this.currentWinStreak++;
            if (this.currentWinStreak > this.bestWinStreak) {
                this.bestWinStreak = this.currentWinStreak;
            }
            // Aumentar rating (sistema ELO simple)
            if (gameMode === 'ranked') {
                this.rating += 20;
            }
        } else if (result === 'loss') {
            this.losses++;
            this.currentWinStreak = 0;
            // Disminuir rating
            if (gameMode === 'ranked') {
                this.rating = Math.max(0, this.rating - 15);
            }
        } else {
            this.draws++;
            // Rating no cambia en empates
        }

        this.winRate = this.calculateWinRate();
    }

    /**
     * Convierte a objeto plano
     */
    toJSON() {
        return {
            userId: this.userId,
            wins: this.wins,
            losses: this.losses,
            draws: this.draws,
            totalGames: this.totalGames,
            winRate: this.winRate,
            rating: this.rating,
            bestWinStreak: this.bestWinStreak,
            currentWinStreak: this.currentWinStreak,
            favoriteDeck: this.favoriteDeck,
            lastPlayed: this.lastPlayed
        };
    }
}

module.exports = UserStats;
```

#### 1.2 Crear StatsRepository

**Archivo:** `server/repository/StatsRepository.js`

```javascript
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const UserStats = require('../models/UserStats');

class StatsRepository {
    constructor() {
        const dbPath = path.join(__dirname, '../data/users/stats.db');
        this.db = new sqlite3.Database(dbPath, (err) => {
            if (err) {
                console.error('Error abriendo base de datos de estadísticas:', err);
            } else {
                console.log('✅ Base de datos de estadísticas conectada');
                this.initTables();
            }
        });
    }

    /**
     * Inicializa las tablas necesarias
     */
    initTables() {
        this.db.run(`
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                rating INTEGER DEFAULT 1000,
                best_win_streak INTEGER DEFAULT 0,
                current_win_streak INTEGER DEFAULT 0,
                favorite_deck TEXT,
                last_played TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Crear tabla de rankings
        this.db.run(`
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                rank_position INTEGER,
                season TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_stats(user_id)
            )
        `);
    }

    /**
     * Obtiene estadísticas de un usuario
     */
    getStats(userId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM user_stats WHERE user_id = ?',
                [userId],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else if (row) {
                        resolve(new UserStats(row));
                    } else {
                        // Crear estadísticas iniciales
                        const newStats = new UserStats({ userId });
                        this.saveStats(newStats).then(resolve).catch(reject);
                    }
                }
            );
        });
    }

    /**
     * Guarda estadísticas de un usuario
     */
    saveStats(stats) {
        return new Promise((resolve, reject) => {
            const data = stats.toJSON();
            this.db.run(
                `INSERT OR REPLACE INTO user_stats 
                (user_id, wins, losses, draws, total_games, win_rate, rating, 
                 best_win_streak, current_win_streak, favorite_deck, last_played, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)`,
                [
                    data.userId,
                    data.wins,
                    data.losses,
                    data.draws,
                    data.totalGames,
                    data.winRate,
                    data.rating,
                    data.bestWinStreak,
                    data.currentWinStreak,
                    data.favoriteDeck,
                    data.lastPlayed
                ],
                function(err) {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(stats);
                    }
                }
            );
        });
    }

    /**
     * Actualiza estadísticas después de una partida
     */
    async updateAfterGame(userId, result, gameMode = 'ranked') {
        const stats = await this.getStats(userId);
        stats.updateAfterGame(result, gameMode);
        return await this.saveStats(stats);
    }

    /**
     * Obtiene el ranking de jugadores
     */
    getRankings(limit = 100, offset = 0) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT user_id, rating, wins, losses, total_games, win_rate, 
                 best_win_streak, current_win_streak
                 FROM user_stats
                 WHERE total_games > 0
                 ORDER BY rating DESC, win_rate DESC
                 LIMIT ? OFFSET ?`,
                [limit, offset],
                (err, rows) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(rows.map((row, index) => ({
                            ...row,
                            rank: offset + index + 1
                        })));
                    }
                }
            );
        });
    }

    /**
     * Obtiene la posición de un usuario en el ranking
     */
    getRankPosition(userId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                `SELECT COUNT(*) + 1 as position
                 FROM user_stats
                 WHERE rating > (SELECT rating FROM user_stats WHERE user_id = ?)
                 AND total_games > 0`,
                [userId],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(row ? row.position : null);
                    }
                }
            );
        });
    }

    /**
     * Cierra la conexión a la base de datos
     */
    close() {
        return new Promise((resolve) => {
            this.db.close((err) => {
                if (err) {
                    console.error('Error cerrando base de datos:', err);
                }
                resolve();
            });
        });
    }
}

module.exports = StatsRepository;
```

#### 1.3 Crear StatsController

**Archivo:** `server/controllers/StatsController.js`

```javascript
const StatsRepository = require('../repository/StatsRepository');

const statsRepo = new StatsRepository();

class StatsController {
    /**
     * Obtiene estadísticas de un usuario
     */
    static async getStats(req, res) {
        try {
            const userId = req.params.userId || req.user?.userId;
            if (!userId) {
                return res.status(400).json({
                    success: false,
                    error: 'userId requerido'
                });
            }

            const stats = await statsRepo.getStats(userId);
            const rankPosition = await statsRepo.getRankPosition(userId);

            res.json({
                success: true,
                data: {
                    ...stats.toJSON(),
                    rankPosition
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Obtiene el ranking de jugadores
     */
    static async getRankings(req, res) {
        try {
            const limit = parseInt(req.query.limit) || 100;
            const offset = parseInt(req.query.offset) || 0;

            const rankings = await statsRepo.getRankings(limit, offset);

            res.json({
                success: true,
                count: rankings.length,
                data: rankings
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Actualiza estadísticas después de una partida
     */
    static async updateAfterGame(userId, result, gameMode = 'ranked') {
        try {
            return await statsRepo.updateAfterGame(userId, result, gameMode);
        } catch (error) {
            console.error('Error actualizando estadísticas:', error);
            throw error;
        }
    }
}

module.exports = StatsController;
```

#### 1.4 Crear Rutas de Stats

**Archivo:** `server/routes/stats.js`

```javascript
const express = require('express');
const router = express.Router();
const StatsController = require('../controllers/StatsController');
const { authenticateToken } = require('../middleware/auth');

// GET /api/stats/rankings - Obtener ranking
router.get('/rankings', StatsController.getRankings);

// GET /api/stats/:userId - Obtener estadísticas de un usuario
router.get('/:userId', StatsController.getStats);

// GET /api/stats - Obtener estadísticas del usuario actual
router.get('/', authenticateToken, (req, res) => {
    req.params.userId = req.user.userId;
    return StatsController.getStats(req, res);
});

module.exports = router;
```

#### 1.5 Integrar en GameController

**Archivo:** `server/controllers/GameController.js` (modificar)

```javascript
const StatsController = require('./StatsController');

// En la función que finaliza una partida, agregar:
async function finalizarPartida(gameId, ganadorId) {
    // ... código existente ...
    
    // Actualizar estadísticas
    const jugadores = Object.values(gameState.jugadores);
    for (const jugador of jugadores) {
        const result = jugador.id === ganadorId ? 'win' : 'loss';
        await StatsController.updateAfterGame(
            jugador.id,
            result,
            gameState.gameMode || 'ranked'
        );
    }
    
    // ... resto del código ...
}
```

#### 1.6 Agregar Ruta en server.js

**Archivo:** `server/server.js` (modificar)

```javascript
// Agregar después de otras rutas
const statsRoutes = require('./routes/stats');
app.use('/api/stats', statsRoutes);
```

**Verificación:**
- Debe poder obtener estadísticas de un usuario
- Debe poder obtener el ranking
- Las estadísticas deben actualizarse después de partidas

---

### Tarea 2: Sistema de Replay de Partidas

**Archivos a crear/modificar:**
- `server/repository/ReplayRepository.js` (nuevo)
- `server/controllers/ReplayController.js` (nuevo)
- `server/routes/replays.js` (nuevo)
- `public/replay.html` (nuevo)
- `public/js/replay.js` (nuevo)

**Qué debe hacer:**

#### 2.1 Crear ReplayRepository

**Archivo:** `server/repository/ReplayRepository.js`

```javascript
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class ReplayRepository {
    constructor() {
        const dbPath = path.join(__dirname, '../data/game/replays.db');
        this.db = new sqlite3.Database(dbPath, (err) => {
            if (err) {
                console.error('Error abriendo base de datos de replays:', err);
            } else {
                console.log('✅ Base de datos de replays conectada');
                this.initTables();
            }
        });
    }

    initTables() {
        this.db.run(`
            CREATE TABLE IF NOT EXISTS replays (
                id TEXT PRIMARY KEY,
                game_id TEXT NOT NULL,
                player1_id TEXT NOT NULL,
                player2_id TEXT NOT NULL,
                game_mode TEXT,
                winner_id TEXT,
                duration INTEGER,
                moves TEXT NOT NULL,
                initial_state TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);
    }

    /**
     * Guarda un replay
     */
    saveReplay(replayData) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT INTO replays 
                (id, game_id, player1_id, player2_id, game_mode, winner_id, duration, moves, initial_state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    replayData.id,
                    replayData.gameId,
                    replayData.player1Id,
                    replayData.player2Id,
                    replayData.gameMode || 'ranked',
                    replayData.winnerId,
                    replayData.duration,
                    JSON.stringify(replayData.moves),
                    JSON.stringify(replayData.initialState)
                ],
                function(err) {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(replayData.id);
                    }
                }
            );
        });
    }

    /**
     * Obtiene un replay por ID
     */
    getReplay(replayId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM replays WHERE id = ?',
                [replayId],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else if (row) {
                        resolve({
                            ...row,
                            moves: JSON.parse(row.moves),
                            initialState: JSON.parse(row.initial_state)
                        });
                    } else {
                        resolve(null);
                    }
                }
            );
        });
    }

    /**
     * Obtiene replays de un usuario
     */
    getUserReplays(userId, limit = 50) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT * FROM replays 
                 WHERE player1_id = ? OR player2_id = ?
                 ORDER BY created_at DESC
                 LIMIT ?`,
                [userId, userId, limit],
                (err, rows) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(rows.map(row => ({
                            ...row,
                            moves: JSON.parse(row.moves),
                            initialState: JSON.parse(row.initial_state)
                        })));
                    }
                }
            );
        });
    }

    close() {
        return new Promise((resolve) => {
            this.db.close((err) => {
                if (err) console.error('Error cerrando DB:', err);
                resolve();
            });
        });
    }
}

module.exports = ReplayRepository;
```

#### 2.2 Modificar GameController para Grabar Replays

**Archivo:** `server/controllers/GameController.js` (modificar)

```javascript
const ReplayRepository = require('../repository/ReplayRepository');
const { v4: uuidv4 } = require('uuid');

const replayRepo = new ReplayRepository();

// Agregar al inicio de la clase
static gameMoves = new Map(); // gameId -> moves[]

// En la función que ejecuta una acción, agregar:
static _ejecutarAccionInterna(gameId, userId, accion, datos) {
    // ... código existente ...
    
    // Grabar movimiento para replay
    if (!this.gameMoves.has(gameId)) {
        this.gameMoves.set(gameId, []);
    }
    
    this.gameMoves.get(gameId).push({
        timestamp: Date.now(),
        userId,
        accion,
        datos,
        gameState: JSON.parse(JSON.stringify(gameState)) // Snapshot
    });
    
    // ... resto del código ...
}

// Al finalizar partida, guardar replay
static async finalizarPartida(gameId) {
    // ... código existente ...
    
    // Guardar replay
    const moves = this.gameMoves.get(gameId) || [];
    const gameState = await this.obtenerEstado(gameId);
    
    if (moves.length > 0 && gameState) {
        const replayId = uuidv4();
        await replayRepo.saveReplay({
            id: replayId,
            gameId,
            player1Id: Object.values(gameState.jugadores)[0]?.id,
            player2Id: Object.values(gameState.jugadores)[1]?.id,
            gameMode: gameState.gameMode,
            winnerId: gameState.ganador,
            duration: Date.now() - new Date(gameState.fecha_inicio).getTime(),
            moves,
            initialState: gameState.estadoInicial || gameState
        });
    }
    
    // Limpiar movimientos
    this.gameMoves.delete(gameId);
    
    // ... resto del código ...
}
```

#### 2.3 Crear ReplayController

**Archivo:** `server/controllers/ReplayController.js`

```javascript
const ReplayRepository = require('../repository/ReplayRepository');

const replayRepo = new ReplayRepository();

class ReplayController {
    /**
     * Obtiene un replay por ID
     */
    static async getReplay(req, res) {
        try {
            const { replayId } = req.params;
            const replay = await replayRepo.getReplay(replayId);
            
            if (!replay) {
                return res.status(404).json({
                    success: false,
                    error: 'Replay no encontrado'
                });
            }
            
            res.json({
                success: true,
                data: replay
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Obtiene replays de un usuario
     */
    static async getUserReplays(req, res) {
        try {
            const userId = req.params.userId || req.user?.userId;
            const limit = parseInt(req.query.limit) || 50;
            
            const replays = await replayRepo.getUserReplays(userId, limit);
            
            res.json({
                success: true,
                count: replays.length,
                data: replays
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = ReplayController;
```

#### 2.4 Crear Rutas de Replay

**Archivo:** `server/routes/replays.js`

```javascript
const express = require('express');
const router = express.Router();
const ReplayController = require('../controllers/ReplayController');
const { authenticateToken } = require('../middleware/auth');

// GET /api/replays/:replayId - Obtener un replay
router.get('/:replayId', ReplayController.getReplay);

// GET /api/replays/user/:userId - Obtener replays de un usuario
router.get('/user/:userId', ReplayController.getUserReplays);

// GET /api/replays/user - Obtener replays del usuario actual
router.get('/user', authenticateToken, (req, res) => {
    req.params.userId = req.user.userId;
    return ReplayController.getUserReplays(req, res);
});

module.exports = router;
```

#### 2.5 Crear Página de Replay

**Archivo:** `public/replay.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Replay - Mitos y Leyendas</title>
    <link rel="stylesheet" href="css/game.css">
    <link rel="stylesheet" href="css/replay.css">
</head>
<body>
    <div class="replay-container">
        <div class="replay-controls">
            <button id="playPauseBtn" class="btn">▶️ Reproducir</button>
            <button id="prevMoveBtn" class="btn">⏮️ Anterior</button>
            <button id="nextMoveBtn" class="btn">⏭️ Siguiente</button>
            <input type="range" id="speedSlider" min="0.5" max="3" step="0.5" value="1">
            <span id="speedLabel">Velocidad: 1x</span>
            <span id="moveCounter">Movimiento 0 / 0</span>
        </div>
        
        <div id="gameContainer" class="game-board-replay">
            <!-- El tablero de juego se renderizará aquí -->
        </div>
        
        <div class="replay-info">
            <h3>Información del Replay</h3>
            <div id="replayInfo"></div>
        </div>
    </div>
    
    <script src="js/api.js"></script>
    <script src="js/replay.js"></script>
</body>
</html>
```

#### 2.6 Crear JavaScript de Replay

**Archivo:** `public/js/replay.js`

```javascript
let replayData = null;
let currentMoveIndex = 0;
let isPlaying = false;
let playInterval = null;
let playbackSpeed = 1;

/**
 * Inicializa el reproductor de replay
 */
async function initReplay() {
    const replayId = new URLSearchParams(window.location.search).get('id');
    if (!replayId) {
        alert('No se especificó un replay');
        return;
    }

    // Cargar replay
    const response = await api.getReplay(replayId);
    if (response.success) {
        replayData = response.data;
        renderReplayInfo();
        renderInitialState();
        setupControls();
    } else {
        alert('Error al cargar replay: ' + response.error);
    }
}

/**
 * Renderiza información del replay
 */
function renderReplayInfo() {
    const infoEl = document.getElementById('replayInfo');
    infoEl.innerHTML = `
        <p><strong>Jugador 1:</strong> ${replayData.player1_id}</p>
        <p><strong>Jugador 2:</strong> ${replayData.player2_id}</p>
        <p><strong>Ganador:</strong> ${replayData.winner_id || 'Empate'}</p>
        <p><strong>Duración:</strong> ${formatDuration(replayData.duration)}</p>
        <p><strong>Movimientos:</strong> ${replayData.moves.length}</p>
    `;
}

/**
 * Renderiza el estado inicial
 */
function renderInitialState() {
    // Usar la misma lógica de renderGameState de game.js
    // pero adaptada para replay
    currentGameState = replayData.initialState;
    renderGameState();
}

/**
 * Configura los controles
 */
function setupControls() {
    document.getElementById('playPauseBtn').onclick = togglePlayPause;
    document.getElementById('prevMoveBtn').onclick = previousMove;
    document.getElementById('nextMoveBtn').onclick = nextMove;
    document.getElementById('speedSlider').oninput = (e) => {
        playbackSpeed = parseFloat(e.target.value);
        document.getElementById('speedLabel').textContent = `Velocidad: ${playbackSpeed}x`;
        if (isPlaying) {
            restartPlayback();
        }
    };
}

/**
 * Alterna reproducción/pausa
 */
function togglePlayPause() {
    if (isPlaying) {
        pause();
    } else {
        play();
    }
}

/**
 * Reproduce el replay
 */
function play() {
    isPlaying = true;
    document.getElementById('playPauseBtn').textContent = '⏸️ Pausar';
    
    const delay = 2000 / playbackSpeed; // 2 segundos por movimiento (ajustable)
    
    playInterval = setInterval(() => {
        if (currentMoveIndex < replayData.moves.length - 1) {
            nextMove();
        } else {
            pause();
        }
    }, delay);
}

/**
 * Pausa la reproducción
 */
function pause() {
    isPlaying = false;
    document.getElementById('playPauseBtn').textContent = '▶️ Reproducir';
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
}

/**
 * Movimiento anterior
 */
function previousMove() {
    if (currentMoveIndex > 0) {
        currentMoveIndex--;
        applyMove(replayData.moves[currentMoveIndex]);
        updateMoveCounter();
    }
}

/**
 * Siguiente movimiento
 */
function nextMove() {
    if (currentMoveIndex < replayData.moves.length) {
        applyMove(replayData.moves[currentMoveIndex]);
        currentMoveIndex++;
        updateMoveCounter();
    }
}

/**
 * Aplica un movimiento
 */
function applyMove(move) {
    currentGameState = move.gameState;
    renderGameState();
}

/**
 * Actualiza el contador de movimientos
 */
function updateMoveCounter() {
    document.getElementById('moveCounter').textContent = 
        `Movimiento ${currentMoveIndex} / ${replayData.moves.length}`;
}

/**
 * Formatea duración
 */
function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${seconds % 60}`;
}

// Inicializar al cargar
document.addEventListener('DOMContentLoaded', initReplay);
```

**Verificación:**
- Debe poder cargar un replay
- Debe poder reproducir paso a paso
- Debe poder pausar/reanudar
- Debe poder cambiar velocidad

---

### Tarea 3: Modo de Práctica vs IA (Opcional - Complejo)

**Nota:** Esta tarea es compleja y requiere implementar una IA básica. Se puede posponer o simplificar.

**Archivos a crear:**
- `server/ai/SimpleAI.js` (nuevo)
- Modificar `server/controllers/GameController.js`

**Implementación básica:**

```javascript
// server/ai/SimpleAI.js
class SimpleAI {
    /**
     * Decide qué acción tomar
     */
    static decideAction(gameState, aiPlayerKey) {
        const aiState = gameState.jugadores[aiPlayerKey];
        
        // Estrategia simple: jugar cartas aleatorias válidas
        const validActions = this.getValidActions(gameState, aiPlayerKey);
        
        if (validActions.length === 0) {
            return { accion: 'pasar_turno', datos: {} };
        }
        
        // Seleccionar acción aleatoria
        const randomAction = validActions[Math.floor(Math.random() * validActions.length)];
        return randomAction;
    }

    static getValidActions(gameState, aiPlayerKey) {
        const actions = [];
        const aiState = gameState.jugadores[aiPlayerKey];
        
        // Agregar acciones válidas según fase
        // (implementar lógica según reglas del juego)
        
        return actions;
    }
}
```

**Verificación:**
- La IA debe poder jugar partidas básicas
- Debe tomar decisiones razonables (no solo aleatorias)

---

## ✅ Checklist de Implementación

### Rankings
- [ ] Modelo UserStats creado
- [ ] StatsRepository creado
- [ ] StatsController creado
- [ ] Rutas de stats agregadas
- [ ] Estadísticas se actualizan después de partidas
- [ ] Ranking se puede consultar

### Replay
- [ ] ReplayRepository creado
- [ ] Movimientos se graban durante partidas
- [ ] Replays se guardan al finalizar
- [ ] Página de replay creada
- [ ] Reproductor funciona

### IA (Opcional)
- [ ] SimpleAI implementado
- [ ] IA puede jugar partidas básicas

---

## 🧪 Pruebas a Realizar

### Rankings
1. Jugar varias partidas
2. Verificar que las estadísticas se actualizan
3. Consultar ranking
4. Verificar que aparece en el ranking

### Replay
1. Jugar una partida completa
2. Obtener el ID del replay
3. Abrir `/replay?id=REPLAY_ID`
4. Verificar que se puede reproducir

---

## 📝 Notas Importantes

1. **Performance:**
   - Los replays pueden ser grandes, considerar compresión
   - Limitar número de movimientos grabados si es necesario

2. **Privacidad:**
   - Los replays pueden contener información sensible
   - Considerar opción de hacer replays privados

3. **IA:**
   - La IA básica es solo un punto de partida
   - Se puede mejorar con algoritmos más sofisticados

---

## 🎯 Criterios de Éxito

✅ Rankings funcionan correctamente  
✅ Replays se graban y reproducen  
✅ Estadísticas se actualizan automáticamente  
✅ No se rompe funcionalidad existente  

---

**Última actualización:** 2025-01-27


