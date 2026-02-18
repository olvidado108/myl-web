# 🚀 Guía de Implementación: Sistema de Lobby y Emparejamiento

**Basado en el análisis de Dueling Nexus**  
**Fecha:** 2025-01-27

---

## 📋 Objetivo

Implementar un sistema de lobby y emparejamiento de jugadores similar a Dueling Nexus, permitiendo:
- Búsqueda rápida de partidas
- Creación de partidas privadas
- Lista de partidas disponibles
- Emparejamiento automático

---

## 🏗️ Arquitectura

```
Cliente (lobby.html)
    ↓ WebSocket
Servidor (gameSocket.js)
    ↓
LobbyManager (nuevo módulo)
    ↓
GameController (existente)
```

---

## 📦 Paso 1: Crear Módulo de Lobby Manager

**Archivo:** `server/ws/lobbyManager.js`

```javascript
/**
 * LobbyManager - Gestiona jugadores en lobby y emparejamiento
 */

class LobbyManager {
    constructor() {
        this.players = new Map(); // userId -> PlayerInfo
        this.matchmakingQueue = new Map(); // userId -> MatchmakingInfo
        this.availableGames = new Map(); // gameId -> GameInfo
    }

    /**
     * Agrega un jugador al lobby
     */
    addPlayer(userId, socketId, playerInfo = {}) {
        this.players.set(userId, {
            socketId,
            userId,
            gameId: null,
            lookingForGame: false,
            ...playerInfo,
            joinedAt: Date.now()
        });
        
        return this.getLobbyStats();
    }

    /**
     * Remueve un jugador del lobby
     */
    removePlayer(userId) {
        this.players.delete(userId);
        this.matchmakingQueue.delete(userId);
        return this.getLobbyStats();
    }

    /**
     * Agrega un jugador a la cola de emparejamiento
     */
    addToMatchmaking(userId, matchmakingInfo) {
        const player = this.players.get(userId);
        if (!player) {
            throw new Error('Jugador no está en el lobby');
        }

        this.matchmakingQueue.set(userId, {
            userId,
            deckId: matchmakingInfo.deckId,
            gameMode: matchmakingInfo.gameMode || 'ranked',
            startedAt: Date.now(),
            socketId: player.socketId
        });

        player.lookingForGame = true;
        
        // Intentar emparejar inmediatamente
        return this.tryMatchmaking(userId);
    }

    /**
     * Intenta emparejar un jugador con otro disponible
     */
    tryMatchmaking(userId) {
        const requester = this.matchmakingQueue.get(userId);
        if (!requester) return null;

        // Buscar oponente disponible
        for (const [opponentId, opponent] of this.matchmakingQueue.entries()) {
            if (opponentId === userId) continue;
            if (opponent.gameMode !== requester.gameMode) continue;
            
            // Emparejamiento encontrado
            this.matchmakingQueue.delete(userId);
            this.matchmakingQueue.delete(opponentId);
            
            const requesterPlayer = this.players.get(userId);
            const opponentPlayer = this.players.get(opponentId);
            
            if (requesterPlayer) requesterPlayer.lookingForGame = false;
            if (opponentPlayer) opponentPlayer.lookingForGame = false;
            
            return {
                player1: {
                    userId: requester.userId,
                    socketId: requester.socketId,
                    deckId: requester.deckId
                },
                player2: {
                    userId: opponent.userId,
                    socketId: opponent.socketId,
                    deckId: opponent.deckId
                }
            };
        }

        return null; // No se encontró oponente
    }

    /**
     * Remueve un jugador de la cola de emparejamiento
     */
    removeFromMatchmaking(userId) {
        this.matchmakingQueue.delete(userId);
        const player = this.players.get(userId);
        if (player) {
            player.lookingForGame = false;
        }
    }

    /**
     * Obtiene estadísticas del lobby
     */
    getLobbyStats() {
        return {
            playersOnline: this.players.size,
            playersInQueue: this.matchmakingQueue.size,
            availableGames: Array.from(this.availableGames.values())
        };
    }

    /**
     * Registra una partida disponible
     */
    registerGame(gameId, gameInfo) {
        this.availableGames.set(gameId, {
            gameId,
            ...gameInfo,
            createdAt: Date.now()
        });
    }

    /**
     * Remueve una partida
     */
    unregisterGame(gameId) {
        this.availableGames.delete(gameId);
    }

    /**
     * Obtiene información de un jugador
     */
    getPlayer(userId) {
        return this.players.get(userId);
    }
}

// Singleton
const lobbyManager = new LobbyManager();

module.exports = lobbyManager;
```

---

## 📦 Paso 2: Extender gameSocket.js

**Archivo:** `server/ws/gameSocket.js` (modificar)

```javascript
const lobbyManager = require('./lobbyManager');
const GameController = require('../controllers/GameController');

// ... código existente ...

io.on('connection', (socket) => {
    const userId = socket.data.userId;
    console.log(`🔌 WS conectado: ${socket.id} usuario ${userId}`);

    // ... código existente de heartbeat ...

    // ========== EVENTOS DE LOBBY ==========
    
    /**
     * Unirse al lobby
     */
    socket.on('join_lobby', async () => {
        try {
            const stats = lobbyManager.addPlayer(userId, socket.id);
            socket.emit('lobby_state', stats);
            console.log(`👤 Usuario ${userId} se unió al lobby`);
        } catch (error) {
            socket.emit('error', { message: error.message });
        }
    });

    /**
     * Buscar partida
     */
    socket.on('find_match', async (payload) => {
        try {
            const { deckId, gameMode = 'ranked' } = payload;
            
            if (!deckId) {
                socket.emit('error', { message: 'deckId requerido' });
                return;
            }

            // Agregar a cola de emparejamiento
            lobbyManager.addToMatchmaking(userId, { deckId, gameMode });
            
            // Intentar emparejar
            const match = lobbyManager.tryMatchmaking(userId);
            
            if (match) {
                // Crear partida
                const gameResponse = await GameController.createGame(
                    match.player1.userId,
                    match.player2.userId,
                    match.player1.deckId,
                    match.player2.deckId
                );

                if (gameResponse.success) {
                    const gameId = gameResponse.data.partida.id;
                    
                    // Notificar a ambos jugadores
                    io.to(match.player1.socketId).emit('match_found', {
                        gameId,
                        opponent: match.player2.userId
                    });
                    
                    io.to(match.player2.socketId).emit('match_found', {
                        gameId,
                        opponent: match.player1.userId
                    });
                    
                    // Unirse automáticamente a la partida
                    const socket1 = io.sockets.sockets.get(match.player1.socketId);
                    const socket2 = io.sockets.sockets.get(match.player2.socketId);
                    
                    if (socket1) {
                        socket1.join(roomName(gameId));
                        socket1.data.gameId = gameId;
                    }
                    if (socket2) {
                        socket2.join(roomName(gameId));
                        socket2.data.gameId = gameId;
                    }
                    
                    // Enviar estado inicial
                    const estado1 = GameController.obtenerEstadoParaJugador(gameId, match.player1.userId);
                    const estado2 = GameController.obtenerEstadoParaJugador(gameId, match.player2.userId);
                    
                    if (socket1 && estado1.success) {
                        socket1.emit('state', {
                            gameState: estado1.gameStateFiltrado,
                            finalizado: estado1.gameState?.finalizado,
                            ganador: estado1.gameState?.ganador
                        });
                    }
                    
                    if (socket2 && estado2.success) {
                        socket2.emit('state', {
                            gameState: estado2.gameStateFiltrado,
                            finalizado: estado2.gameState?.finalizado,
                            ganador: estado2.gameState?.ganador
                        });
                    }
                    
                    console.log(`🎮 Partida creada: ${gameId} entre ${match.player1.userId} y ${match.player2.userId}`);
                } else {
                    socket.emit('error', { message: 'Error al crear partida' });
                }
            } else {
                // No se encontró oponente, esperar
                socket.emit('searching', {
                    message: 'Buscando oponente...',
                    queuePosition: lobbyManager.matchmakingQueue.size
                });
            }
        } catch (error) {
            console.error('Error en find_match:', error);
            socket.emit('error', { message: error.message });
        }
    });

    /**
     * Cancelar búsqueda de partida
     */
    socket.on('cancel_matchmaking', () => {
        lobbyManager.removeFromMatchmaking(userId);
        socket.emit('matchmaking_cancelled');
    });

    /**
     * Obtener estado del lobby
     */
    socket.on('get_lobby_state', () => {
        const stats = lobbyManager.getLobbyStats();
        socket.emit('lobby_state', stats);
    });

    /**
     * Crear partida privada
     */
    socket.on('create_private_game', async (payload) => {
        try {
            const { deckId, maxPlayers = 2 } = payload;
            
            // Crear partida con solo el jugador actual
            const gameResponse = await GameController.createGame(
                userId,
                null, // Oponente será null hasta que se una
                deckId,
                null
            );

            if (gameResponse.success) {
                const gameId = gameResponse.data.partida.id;
                
                // Registrar como partida disponible
                lobbyManager.registerGame(gameId, {
                    host: userId,
                    maxPlayers,
                    isPrivate: true,
                    players: [userId]
                });
                
                socket.emit('private_game_created', {
                    gameId,
                    inviteCode: generateInviteCode(gameId)
                });
            }
        } catch (error) {
            socket.emit('error', { message: error.message });
        }
    });

    /**
     * Unirse a partida privada
     */
    socket.on('join_private_game', async (payload) => {
        try {
            const { gameId, inviteCode, deckId } = payload;
            
            const gameInfo = lobbyManager.availableGames.get(gameId);
            if (!gameInfo) {
                socket.emit('error', { message: 'Partida no encontrada' });
                return;
            }

            // Validar código de invitación si es privada
            if (gameInfo.isPrivate && gameInfo.inviteCode !== inviteCode) {
                socket.emit('error', { message: 'Código de invitación inválido' });
                return;
            }

            // Agregar jugador a la partida
            // (Implementar lógica según tu GameController)
            
            socket.emit('joined_private_game', { gameId });
        } catch (error) {
            socket.emit('error', { message: error.message });
        }
    });

    /**
     * Desconexión
     */
    socket.on('disconnect', (reason) => {
        console.log(`🔌 WS desconectado ${socket.id}: ${reason}`);
        clearInterval(heartbeatTimer);
        
        // Remover del lobby
        lobbyManager.removePlayer(userId);
    });

    // ... resto del código existente ...
});

/**
 * Genera un código de invitación para partidas privadas
 */
function generateInviteCode(gameId) {
    return gameId.substring(0, 8).toUpperCase();
}
```

---

## 📦 Paso 3: Crear Página de Lobby

**Archivo:** `public/lobby.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lobby - Mitos y Leyendas</title>
    <link rel="stylesheet" href="css/auth.css">
    <link rel="stylesheet" href="css/navbar.css">
    <link rel="stylesheet" href="css/lobby.css">
</head>
<body>
    <!-- Barra de navegación -->
    <nav class="navbar">
        <div class="navbar-container" id="navbar-container"></div>
    </nav>

    <div class="lobby-container">
        <h1>🎮 Lobby de Partidas</h1>
        
        <!-- Estadísticas del lobby -->
        <div class="lobby-stats">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-info">
                    <div class="stat-value" id="playersOnline">0</div>
                    <div class="stat-label">Jugadores Online</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-info">
                    <div class="stat-value" id="playersInQueue">0</div>
                    <div class="stat-label">Buscando Partida</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚔️</div>
                <div class="stat-info">
                    <div class="stat-value" id="activeGames">0</div>
                    <div class="stat-label">Partidas Activas</div>
                </div>
            </div>
        </div>

        <!-- Búsqueda rápida -->
        <div class="lobby-section">
            <h2>⚡ Búsqueda Rápida</h2>
            <div class="quick-match-form">
                <select id="quickMatchDeck" class="form-control">
                    <option value="">Cargando mazos...</option>
                </select>
                <select id="gameMode" class="form-control">
                    <option value="ranked">Competitivo</option>
                    <option value="casual">Casual</option>
                </select>
                <button id="findMatchBtn" class="btn btn-primary">
                    <span id="findMatchText">Buscar Partida</span>
                    <span id="findMatchSpinner" class="spinner" style="display: none;"></span>
                </button>
                <button id="cancelMatchBtn" class="btn btn-secondary" style="display: none;">
                    Cancelar Búsqueda
                </button>
            </div>
            <div id="matchmakingStatus" class="matchmaking-status" style="display: none;">
                <p id="matchmakingMessage">Buscando oponente...</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
        </div>

        <!-- Partidas disponibles -->
        <div class="lobby-section">
            <h2>📋 Partidas Disponibles</h2>
            <button id="refreshGamesBtn" class="btn btn-sm">🔄 Actualizar</button>
            <div id="availableGamesList" class="games-list">
                <p class="empty-message">Cargando partidas...</p>
            </div>
        </div>

        <!-- Crear partida privada -->
        <div class="lobby-section">
            <h2>🔒 Crear Partida Privada</h2>
            <div class="private-game-form">
                <select id="privateGameDeck" class="form-control">
                    <option value="">Cargando mazos...</option>
                </select>
                <button id="createPrivateGameBtn" class="btn btn-secondary">
                    Crear Partida Privada
                </button>
            </div>
            <div id="privateGameInfo" class="private-game-info" style="display: none;">
                <p>Partida creada exitosamente!</p>
                <div class="invite-code">
                    <label>Código de Invitación:</label>
                    <input type="text" id="inviteCode" readonly>
                    <button id="copyInviteCodeBtn" class="btn btn-sm">📋 Copiar</button>
                </div>
                <p><small>Comparte este código con tu oponente</small></p>
            </div>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/navbar.js"></script>
    <script src="/socket.io/socket.io.js"></script>
    <script src="js/lobby.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            await checkAuth(true);
            await initNavbar();
            await initLobby();
        });
    </script>
</body>
</html>
```

---

## 📦 Paso 4: Crear JavaScript del Lobby

**Archivo:** `public/js/lobby.js`

```javascript
/**
 * Lógica del Lobby
 */

let socket = null;
let isSearching = false;
let searchStartTime = null;

/**
 * Inicializa el lobby
 */
async function initLobby() {
    try {
        console.log('🎮 Inicializando lobby...');
        
        // Cargar mazos
        await loadDecks();
        
        // Conectar WebSocket
        await connectWebSocket();
        
        // Configurar event listeners
        setupEventListeners();
        
        // Solicitar estado inicial
        socket.emit('get_lobby_state');
        
        console.log('✅ Lobby inicializado');
    } catch (error) {
        console.error('❌ Error al inicializar lobby:', error);
        showError('Error al inicializar lobby: ' + error.message);
    }
}

/**
 * Conecta al WebSocket
 */
async function connectWebSocket() {
    const token = localStorage.getItem('token');
    
    socket = io('/ws', {
        auth: { token },
        path: '/ws'
    });
    
    socket.on('connect', () => {
        console.log('✅ Conectado al servidor');
        socket.emit('join_lobby');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Desconectado del servidor');
        showError('Desconectado del servidor. Intentando reconectar...');
    });
    
    socket.on('lobby_state', (data) => {
        updateLobbyStats(data);
    });
    
    socket.on('match_found', (data) => {
        console.log('🎯 Partida encontrada:', data);
        handleMatchFound(data);
    });
    
    socket.on('searching', (data) => {
        console.log('🔍 Buscando oponente...', data);
        handleSearching(data);
    });
    
    socket.on('matchmaking_cancelled', () => {
        handleMatchmakingCancelled();
    });
    
    socket.on('private_game_created', (data) => {
        handlePrivateGameCreated(data);
    });
    
    socket.on('error', (data) => {
        console.error('❌ Error del servidor:', data);
        showError(data.message || 'Error desconocido');
    });
}

/**
 * Carga los mazos disponibles
 */
async function loadDecks() {
    try {
        const response = await api.getDecks();
        
        if (response.success && response.data) {
            const quickMatchDeck = document.getElementById('quickMatchDeck');
            const privateGameDeck = document.getElementById('privateGameDeck');
            
            // Limpiar opciones
            quickMatchDeck.innerHTML = '<option value="">Selecciona un mazo...</option>';
            privateGameDeck.innerHTML = '<option value="">Selecciona un mazo...</option>';
            
            // Agregar mazos
            response.data.forEach(deck => {
                const cantidadCartas = Array.isArray(deck.cartas) 
                    ? deck.cartas.length 
                    : (typeof deck.cartas === 'string' ? JSON.parse(deck.cartas).length : 0);
                
                const option = document.createElement('option');
                option.value = deck.id;
                option.textContent = `${deck.nombre} (${cantidadCartas} cartas)`;
                
                quickMatchDeck.appendChild(option.cloneNode(true));
                privateGameDeck.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar mazos:', error);
    }
}

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    document.getElementById('findMatchBtn').onclick = findQuickMatch;
    document.getElementById('cancelMatchBtn').onclick = cancelMatchmaking;
    document.getElementById('refreshGamesBtn').onclick = refreshAvailableGames;
    document.getElementById('createPrivateGameBtn').onclick = createPrivateGame;
    document.getElementById('copyInviteCodeBtn').onclick = copyInviteCode;
}

/**
 * Busca una partida rápida
 */
function findQuickMatch() {
    const deckId = document.getElementById('quickMatchDeck').value;
    const gameMode = document.getElementById('gameMode').value;
    
    if (!deckId) {
        showError('Por favor selecciona un mazo');
        return;
    }
    
    if (isSearching) {
        cancelMatchmaking();
        return;
    }
    
    socket.emit('find_match', { deckId, gameMode });
    isSearching = true;
    searchStartTime = Date.now();
    
    // Actualizar UI
    document.getElementById('findMatchBtn').disabled = true;
    document.getElementById('cancelMatchBtn').style.display = 'inline-block';
    document.getElementById('matchmakingStatus').style.display = 'block';
    document.getElementById('findMatchText').textContent = 'Buscando...';
    document.getElementById('findMatchSpinner').style.display = 'inline-block';
    
    // Iniciar animación de progreso
    startProgressAnimation();
}

/**
 * Cancela la búsqueda de partida
 */
function cancelMatchmaking() {
    socket.emit('cancel_matchmaking');
    handleMatchmakingCancelled();
}

/**
 * Maneja cuando se encuentra una partida
 */
function handleMatchFound(data) {
    // Redirigir a la partida
    window.location.href = `/game?gameId=${data.gameId}`;
}

/**
 * Maneja el estado de búsqueda
 */
function handleSearching(data) {
    const messageEl = document.getElementById('matchmakingMessage');
    if (data.queuePosition) {
        messageEl.textContent = `Buscando oponente... (Posición en cola: ${data.queuePosition})`;
    } else {
        messageEl.textContent = data.message || 'Buscando oponente...';
    }
}

/**
 * Maneja cuando se cancela la búsqueda
 */
function handleMatchmakingCancelled() {
    isSearching = false;
    searchStartTime = null;
    
    document.getElementById('findMatchBtn').disabled = false;
    document.getElementById('cancelMatchBtn').style.display = 'none';
    document.getElementById('matchmakingStatus').style.display = 'none';
    document.getElementById('findMatchText').textContent = 'Buscar Partida';
    document.getElementById('findMatchSpinner').style.display = 'none';
}

/**
 * Crea una partida privada
 */
function createPrivateGame() {
    const deckId = document.getElementById('privateGameDeck').value;
    
    if (!deckId) {
        showError('Por favor selecciona un mazo');
        return;
    }
    
    socket.emit('create_private_game', { deckId });
}

/**
 * Maneja cuando se crea una partida privada
 */
function handlePrivateGameCreated(data) {
    document.getElementById('inviteCode').value = data.inviteCode;
    document.getElementById('privateGameInfo').style.display = 'block';
}

/**
 * Copia el código de invitación
 */
function copyInviteCode() {
    const inviteCode = document.getElementById('inviteCode');
    inviteCode.select();
    document.execCommand('copy');
    
    const btn = document.getElementById('copyInviteCodeBtn');
    const originalText = btn.textContent;
    btn.textContent = '✅ Copiado!';
    setTimeout(() => {
        btn.textContent = originalText;
    }, 2000);
}

/**
 * Actualiza las estadísticas del lobby
 */
function updateLobbyStats(data) {
    document.getElementById('playersOnline').textContent = data.playersOnline || 0;
    document.getElementById('playersInQueue').textContent = data.playersInQueue || 0;
    document.getElementById('activeGames').textContent = data.availableGames?.length || 0;
    
    // Actualizar lista de partidas disponibles
    if (data.availableGames) {
        updateAvailableGamesList(data.availableGames);
    }
}

/**
 * Actualiza la lista de partidas disponibles
 */
function updateAvailableGamesList(games) {
    const listEl = document.getElementById('availableGamesList');
    
    if (!games || games.length === 0) {
        listEl.innerHTML = '<p class="empty-message">No hay partidas disponibles</p>';
        return;
    }
    
    listEl.innerHTML = games.map(game => `
        <div class="game-item">
            <div class="game-info">
                <h4>Partida ${game.gameId.substring(0, 8)}</h4>
                <p>Jugadores: ${game.players?.length || 0}/${game.maxPlayers || 2}</p>
                <p>Modo: ${game.isPrivate ? 'Privada' : 'Pública'}</p>
            </div>
            <button class="btn btn-sm" onclick="joinGame('${game.gameId}')">
                Unirse
            </button>
        </div>
    `).join('');
}

/**
 * Actualiza la lista de partidas disponibles
 */
function refreshAvailableGames() {
    socket.emit('get_lobby_state');
}

/**
 * Se une a una partida
 */
function joinGame(gameId) {
    window.location.href = `/game?gameId=${gameId}`;
}

/**
 * Inicia la animación de progreso
 */
function startProgressAnimation() {
    const progressFill = document.getElementById('progressFill');
    let progress = 0;
    
    const interval = setInterval(() => {
        if (!isSearching) {
            clearInterval(interval);
            progressFill.style.width = '0%';
            return;
        }
        
        progress = (progress + 2) % 100;
        progressFill.style.width = progress + '%';
    }, 100);
}

/**
 * Muestra un error
 */
function showError(message) {
    alert(message); // TODO: Implementar sistema de notificaciones mejor
}

/**
 * Muestra un mensaje
 */
function showMessage(message, type = 'info') {
    console.log(`[${type}] ${message}`);
    // TODO: Implementar sistema de notificaciones
}
```

---

## 📦 Paso 5: Crear Estilos CSS

**Archivo:** `public/css/lobby.css`

```css
.lobby-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.lobby-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.stat-icon {
    font-size: 2.5em;
}

.stat-value {
    font-size: 2em;
    font-weight: bold;
}

.stat-label {
    font-size: 0.9em;
    opacity: 0.9;
}

.lobby-section {
    background: white;
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.lobby-section h2 {
    margin-top: 0;
    color: #333;
}

.quick-match-form,
.private-game-form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}

.matchmaking-status {
    margin-top: 20px;
    padding: 15px;
    background: #f0f0f0;
    border-radius: 5px;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 10px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    width: 0%;
    transition: width 0.3s;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.games-list {
    margin-top: 15px;
}

.game-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 5px;
    margin-bottom: 10px;
    border-left: 4px solid #667eea;
}

.game-info h4 {
    margin: 0 0 5px 0;
    color: #333;
}

.game-info p {
    margin: 5px 0;
    color: #666;
    font-size: 0.9em;
}

.private-game-info {
    margin-top: 20px;
    padding: 15px;
    background: #e8f5e9;
    border-radius: 5px;
}

.invite-code {
    display: flex;
    gap: 10px;
    align-items: center;
    margin: 15px 0;
}

.invite-code input {
    flex: 1;
    padding: 10px;
    border: 2px solid #4caf50;
    border-radius: 5px;
    font-size: 1.2em;
    font-weight: bold;
    text-align: center;
    letter-spacing: 2px;
}

.empty-message {
    text-align: center;
    color: #999;
    padding: 40px;
    font-style: italic;
}

.spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #ffffff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    .quick-match-form,
    .private-game-form {
        flex-direction: column;
    }
    
    .form-control,
    .btn {
        width: 100%;
    }
}
```

---

## 📦 Paso 6: Agregar Ruta al Servidor

**Archivo:** `server/server.js` (modificar)

```javascript
// Agregar después de las otras rutas
app.get('/lobby', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/lobby.html'));
});
```

---

## ✅ Checklist de Implementación

- [ ] Crear `server/ws/lobbyManager.js`
- [ ] Modificar `server/ws/gameSocket.js` con eventos de lobby
- [ ] Crear `public/lobby.html`
- [ ] Crear `public/js/lobby.js`
- [ ] Crear `public/css/lobby.css`
- [ ] Agregar ruta `/lobby` en `server/server.js`
- [ ] Probar conexión WebSocket
- [ ] Probar búsqueda de partidas
- [ ] Probar creación de partidas privadas
- [ ] Probar emparejamiento automático

---

## 🧪 Pruebas

1. **Probar Lobby:**
   - Abrir `/lobby` en dos navegadores diferentes
   - Verificar que las estadísticas se actualicen

2. **Probar Emparejamiento:**
   - Iniciar búsqueda en ambos navegadores
   - Verificar que se crea la partida automáticamente
   - Verificar redirección a `/game`

3. **Probar Partidas Privadas:**
   - Crear partida privada
   - Copiar código de invitación
   - Unirse con otro usuario usando el código

---

**Última actualización:** 2025-01-27




