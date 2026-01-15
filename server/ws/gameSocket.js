const { Server } = require('socket.io');
const { verificarToken } = require('../utils/jwtUtils');
const GameController = require('../controllers/GameController');
const lobbyManager = require('./lobbyManager');
const UserRepository = require('../repository/UserRepository');
const userRepo = new UserRepository();

// Configuración de heartbeat (para detectar desconexiones)
const HEARTBEAT_INTERVAL_MS = Number(process.env.WS_HEARTBEAT_MS || 25000); // 25s por defecto
const HEARTBEAT_GRACE_MS = Number(process.env.WS_HEARTBEAT_GRACE_MS || 10000); // tolerancia extra

/**
 * Inicializa el servidor WebSocket para partidas
 * Eventos:
 * - connection (auth por token)
 * - join_game { gameId }
 * - action { gameId?, accion, datos }
 * Respuestas:
 * - state { gameState, finalizado, ganador, resultado? }
 * - error { message }
 */
function initGameSocket(httpServer) {
    const allowedOriginsEnv = process.env.WS_ALLOWED_ORIGINS || '*';
    const allowedOrigins = allowedOriginsEnv === '*'
        ? '*'
        : allowedOriginsEnv.split(',').map(o => o.trim()).filter(Boolean);

    const io = new Server(httpServer, {
        path: '/ws',
        cors: {
            origin: allowedOrigins,
            methods: ['GET', 'POST']
        }
    });

    const roomName = (gameId) => `game:${gameId}`;
    const emitLobbyState = () => {
        const stats = lobbyManager.getLobbyStats();
        lobbyManager.players.forEach((player) => {
            const lobbySocket = io.sockets.sockets.get(player.socketId);
            if (lobbySocket) {
                lobbySocket.emit('lobby_state', stats);
            }
        });
    };
    const generateInviteCode = (seed) => {
        return (seed || Math.random().toString(36).substring(2, 10)).substring(0, 8).toUpperCase();
    };

    // Middleware de autenticación por socket
    io.use((socket, next) => {
        try {
            const authHeader = socket.handshake.headers?.authorization;
            const tokenFromHeader = authHeader && authHeader.startsWith('Bearer ') ? authHeader.substring(7) : authHeader;
            const rawAuthToken = socket.handshake.auth?.token || socket.handshake.query?.token || tokenFromHeader;
            const token = rawAuthToken && rawAuthToken.startsWith('Bearer ')
                ? rawAuthToken.substring(7)
                : rawAuthToken;

            const decoded = token ? verificarToken(token) : null;
            if (!decoded) {
                console.warn('WS auth falló: token inválido o ausente');
                return next(new Error('Unauthorized'));
            }
            socket.data.userId = decoded.userId;
            next();
        } catch (err) {
            console.warn('WS auth error:', err.message);
            next(new Error('Unauthorized'));
        }
    });

    io.on('connection', (socket) => {
        const userId = socket.data.userId;
        console.log(`🔌 WS conectado: ${socket.id} usuario ${userId}`);
        // Estado temporal para RPS por socket
        socket.data.gameId = null;

        // Heartbeat simple usando eventos personalizados (socket.io ya tiene ping/pong,
        // pero esto da visibilidad y control de expiración).
        let lastPong = Date.now();
        const heartbeatTimer = setInterval(() => {
            const sinceLastPong = Date.now() - lastPong;
            if (sinceLastPong > HEARTBEAT_INTERVAL_MS + HEARTBEAT_GRACE_MS) {
                console.warn(`⏱️  WS sin pong por ${sinceLastPong}ms, cerrando socket ${socket.id}`);
                socket.disconnect(true);
                return;
            }
            socket.emit('heartbeat');
        }, HEARTBEAT_INTERVAL_MS);

        socket.on('heartbeat', () => {
            lastPong = Date.now();
        });

        // ========== EVENTOS DE LOBBY ==========
        socket.on('join_lobby', async () => {
            try {
                const stats = lobbyManager.addPlayer(userId, socket.id);
                socket.emit('lobby_state', stats);
                emitLobbyState();
                console.log(`👤 Usuario ${userId} se unió al lobby`);
            } catch (error) {
                socket.emit('error', { message: error.message });
            }
        });

        socket.on('find_match', async (payload = {}) => {
            try {
                const { deckId, gameMode = 'ranked' } = payload;

                if (!deckId) {
                    socket.emit('error', { message: 'deckId requerido' });
                    return;
                }

                if (!lobbyManager.getPlayer(userId)) {
                    lobbyManager.addPlayer(userId, socket.id);
                }

                lobbyManager.addToMatchmaking(userId, socket.id, { deckId, gameMode });
                console.log(`🔍 ${userId} encola deck=${deckId} modo=${gameMode}. Cola:`, lobbyManager.matchmakingQueue.length);
                emitLobbyState();

                const match = lobbyManager.tryMatchmaking();

                if (match) {
                    console.log(`🤝 Match encontrado: ${match.player1.userId} vs ${match.player2.userId}`);
                    const gameResponse = await GameController.createGameForLobby(
                        match.player1.userId,
                        match.player2.userId,
                        match.player1.deckId,
                        match.player2.deckId
                    );

                    if (!gameResponse.success) {
                        console.error('❌ Error al crear partida:', gameResponse.error);
                        // Re-encolar a ambos si falló la creación de partida
                        lobbyManager.addToMatchmaking(match.player1.userId, match.player1.socketId, {
                            deckId: match.player1.deckId,
                            gameMode
                        });
                        lobbyManager.addToMatchmaking(match.player2.userId, match.player2.socketId, {
                            deckId: match.player2.deckId,
                            gameMode
                        });
                        emitLobbyState();
                        const errorMsg = gameResponse.error || 'Error al crear partida';
                        io.to(match.player1.socketId).emit('error', { message: errorMsg });
                        io.to(match.player2.socketId).emit('error', { message: errorMsg });
                        console.error('❌ Reencolando tras fallo de creación:', {
                            p1: match.player1.userId,
                            p2: match.player2.userId,
                            error: errorMsg
                        });
                        socket.emit('searching', {
                            message: 'Reintentando emparejar...',
                            queuePosition: lobbyManager.matchmakingQueue.size
                        });
                        return;
                    }

                    const gameId = gameResponse.data.partida.id;
                    console.log(`🎮 Partida creada ${gameId} entre ${match.player1.userId} y ${match.player2.userId}`);

                    const socket1 = io.sockets.sockets.get(match.player1.socketId);
                    const socket2 = io.sockets.sockets.get(match.player2.socketId);

                    const name1 = userRepo.buscarPorId?.(match.player1.userId)?.username || match.player1.userId;
                    const name2 = userRepo.buscarPorId?.(match.player2.userId)?.username || match.player2.userId;

                    // Preparar estado RPS en memoria
                    if (!lobbyManager.rps) lobbyManager.rps = {};
                    lobbyManager.rps[gameId] = {
                        choices: {},
                        winner: null,
                        starter: null,
                        players: {
                            p1: { userId: match.player1.userId, deckId: match.player1.deckId, socketId: match.player1.socketId },
                            p2: { userId: match.player2.userId, deckId: match.player2.deckId, socketId: match.player2.socketId }
                        },
                        names: {
                            [match.player1.userId]: name1,
                            [match.player2.userId]: name2
                        }
                    };

                    if (socket1) {
                        socket1.join(roomName(gameId));
                        socket1.data.gameId = gameId;
                        socket1.emit('match_found', {
                            gameId,
                            opponent: match.player2.userId,
                            opponentName: name2
                        });
                    }

                    if (socket2) {
                        socket2.join(roomName(gameId));
                        socket2.data.gameId = gameId;
                        socket2.emit('match_found', {
                            gameId,
                            opponent: match.player1.userId,
                            opponentName: name1
                        });
                    }

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
                    emitLobbyState();
                } else {
                    socket.emit('searching', {
                        message: 'Buscando oponente...',
                        queuePosition: lobbyManager.matchmakingQueue.size
                    });
                }
            } catch (error) {
                console.error('Error en find_match:', error);
                // Re-encolar en caso de error inesperado
                lobbyManager.addToMatchmaking(userId, socket.id, { deckId: payload.deckId, gameMode: payload.gameMode || 'ranked' });
                emitLobbyState();
                socket.emit('error', { message: error.message });
            }
        });

        /**
         * Elección piedra-papel-tijera
         */
        socket.on('rps_choice', (payload = {}) => {
            const { gameId, choice } = payload;
            if (!gameId || !choice) return;
            if (!lobbyManager.rps || !lobbyManager.rps[gameId]) {
                socket.emit('error', { message: 'Estado RPS no disponible' });
                return;
            }

            const state = lobbyManager.rps[gameId];
            state.choices[userId] = choice;
            const count = Object.keys(state.choices).length;
            console.log(`🎲 RPS choice game=${gameId} user=${userId} choice=${choice} totalChoices=${count}`);
            io.to(roomName(gameId)).emit('rps_status', { choices: count });

            // Si tenemos dos elecciones, evaluar
            const userIds = Object.keys(state.choices);
            if (userIds.length < 2) return;

            const [u1, u2] = userIds;
            const c1 = state.choices[u1];
            const c2 = state.choices[u2];

            const beats = { rock: 'scissors', paper: 'rock', scissors: 'paper' };
            if (c1 === c2) {
                // Empate, reset choices
                state.choices = {};
                io.to(roomName(gameId)).emit('rps_result', { tie: true });
                return;
            }

            const winner = beats[c1] === c2 ? u1 : u2;
            const loser = winner === u1 ? u2 : u1;
            state.winner = winner;
            io.to(roomName(gameId)).emit('rps_result', {
                tie: false,
                winner,
                loser,
                winnerName: state.names?.[winner] || winner,
                loserName: state.names?.[loser] || loser
            });
        });

        /**
         * Decidir quién empieza
         */
        socket.on('rps_decide_first', (payload = {}) => {
            const { gameId, starter } = payload; // starter = userId que inicia
            if (!gameId || !starter) return;
            if (!lobbyManager.rps || !lobbyManager.rps[gameId]) return;

            const state = lobbyManager.rps[gameId];
            if (state.winner && state.winner !== userId) {
                socket.emit('error', { message: 'Solo el ganador del RPS puede decidir' });
                return;
            }
            state.starter = starter;
            io.to(roomName(gameId)).emit('rps_final', {
                starter,
                starterName: state.names?.[starter] || starter
            });
        });

        /**
         * Confirmar inicio de partida con quien empieza (desde /game)
         */
        socket.on('confirm_starter', async (payload = {}) => {
            const { gameId } = payload;
            if (!gameId) return;
            if (!lobbyManager.rps || !lobbyManager.rps[gameId]) return;
            const state = lobbyManager.rps[gameId];
            if (!state.starter) return;

            // Ajustar turno inicial en GameController
            try {
                const partida = GameController.gameRepo.buscarPorId(gameId);
                if (partida) {
                    const gameState = GameController._cargarGameState(partida.estado_juego, partida.jugador1_id, partida.jugador2_id);
                    // Establecer turnoActual al starter
                    const starterId = state.starter;
                    const starterKey = gameState.getKeyPorId(starterId) || gameState.turnoActual;
                    gameState.turnoActual = starterKey;
                    gameState.jugadorInicialKey = starterKey;
                    gameState.turnoNumero = 1;
                    // Guardar en BD
                    GameController.gameRepo.actualizarPartida(gameId, {
                        estado_juego: gameState.toJSON()
                    });
                }
            } catch (e) {
                console.warn('No se pudo ajustar turno inicial:', e.message);
            }

            // Limpiar estado RPS
            delete lobbyManager.rps[gameId];
        });

        socket.on('cancel_matchmaking', () => {
            lobbyManager.removeFromMatchmakingBySocket(socket.id);
            socket.emit('matchmaking_cancelled');
            emitLobbyState();
        });

        socket.on('get_lobby_state', () => {
            const stats = lobbyManager.getLobbyStats();
            socket.emit('lobby_state', stats);
        });

        socket.on('create_private_game', (payload = {}) => {
            try {
                const { deckId, maxPlayers = 2 } = payload;

                if (!deckId) {
                    socket.emit('error', { message: 'deckId requerido' });
                    return;
                }

                const customInvite = payload.inviteCode && String(payload.inviteCode).trim();
                const gameId = `private_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
                const inviteCode = customInvite || generateInviteCode(gameId);

                lobbyManager.registerGame(gameId, {
                    host: userId,
                    hostSocketId: socket.id,
                    hostDeckId: deckId,
                    maxPlayers,
                    isPrivate: true,
                    players: [userId],
                    inviteCode
                });

                socket.emit('private_game_created', {
                    gameId,
                    inviteCode
                });
                emitLobbyState();
            } catch (error) {
                socket.emit('error', { message: error.message });
            }
        });

        socket.on('join_private_game', async (payload = {}) => {
            try {
                const { gameId, inviteCode, deckId } = payload;

                if (!deckId) {
                    socket.emit('error', { message: 'deckId requerido' });
                    return;
                }

                let gameInfo = gameId ? lobbyManager.getGame(gameId) : null;
                if (!gameInfo && inviteCode) {
                    gameInfo = lobbyManager.findGameByInviteCode(inviteCode);
                }

                if (!gameInfo) {
                    socket.emit('error', { message: 'Partida no encontrada' });
                    return;
                }

                if (gameInfo.isPrivate && gameInfo.inviteCode && gameInfo.inviteCode !== inviteCode) {
                    socket.emit('error', { message: 'Código de invitación inválido' });
                    return;
                }

                const hostSocket = io.sockets.sockets.get(gameInfo.hostSocketId);
                if (!hostSocket) {
                    lobbyManager.unregisterGame(gameInfo.gameId);
                    emitLobbyState();
                    socket.emit('error', { message: 'El anfitrión ya no está en línea' });
                    return;
                }
                const gameResponse = await GameController.createGameForLobby(
                    gameInfo.host,
                    userId,
                    gameInfo.hostDeckId,
                    deckId
                );

                if (!gameResponse.success) {
                    socket.emit('error', { message: gameResponse.error || 'Error al crear partida privada' });
                    return;
                }

                const nameHost = userRepo.buscarPorId?.(gameInfo.host)?.username || gameInfo.host;
                const nameGuest = userRepo.buscarPorId?.(userId)?.username || userId;

                const createdGameId = gameResponse.data.partida.id;
                // Preparar estado RPS para partida privada
                if (!lobbyManager.rps) lobbyManager.rps = {};
                lobbyManager.rps[createdGameId] = {
                    choices: {},
                    winner: null,
                    starter: null,
                    players: {
                        p1: { userId: gameInfo.host, deckId: gameInfo.hostDeckId, socketId: gameInfo.hostSocketId },
                        p2: { userId, deckId, socketId: socket.id }
                    },
                    names: {
                        [gameInfo.host]: nameHost,
                        [userId]: nameGuest
                    }
                };

                lobbyManager.unregisterGame(gameInfo.gameId);
                emitLobbyState();

                const socketsToNotify = [
                    { socket: hostSocket, opponent: userId, opponentName: nameGuest },
                    { socket, opponent: gameInfo.host, opponentName: nameHost }
                ];

                socketsToNotify.forEach(({ socket: s, opponent }) => {
                    if (!s) return;
                    s.join(roomName(createdGameId));
                    s.data.gameId = createdGameId;
                    s.emit('match_found', { gameId: createdGameId, opponent, opponentName: opponent === gameInfo.host ? nameHost : nameGuest });
                });

                const estadoHost = hostSocket ? GameController.obtenerEstadoParaJugador(createdGameId, gameInfo.host) : null;
                const estadoGuest = GameController.obtenerEstadoParaJugador(createdGameId, userId);

                if (hostSocket && estadoHost?.success) {
                    hostSocket.emit('state', {
                        gameState: estadoHost.gameStateFiltrado,
                        finalizado: estadoHost.gameState?.finalizado,
                        ganador: estadoHost.gameState?.ganador
                    });
                }
                if (estadoGuest?.success) {
                    socket.emit('state', {
                        gameState: estadoGuest.gameStateFiltrado,
                        finalizado: estadoGuest.gameState?.finalizado,
                        ganador: estadoGuest.gameState?.ganador
                    });
                }

                socket.emit('joined_private_game', { gameId: createdGameId });
            } catch (error) {
                console.error('Error en join_private_game:', error);
                socket.emit('error', { message: error.message });
            }
        });
        // ========== FIN EVENTOS DE LOBBY ==========

        socket.on('join_game', async (payload = {}) => {
            const { gameId } = payload;
            if (!gameId) {
                socket.emit('error', { message: 'gameId requerido para unirse' });
                return;
            }

            const estado = GameController.obtenerEstadoParaJugador(gameId, userId);
            if (!estado.success) {
                socket.emit('error', { message: estado.error });
                return;
            }

            socket.join(roomName(gameId));
            socket.data.gameId = gameId;

            socket.emit('state', {
                gameState: estado.gameStateFiltrado,
                finalizado: estado.gameState?.finalizado,
                ganador: estado.gameState?.ganador
            });
        });

        socket.on('action', async (payload = {}) => {
            const gameId = payload.gameId || socket.data.gameId;
            const { accion, datos } = payload;

            if (!gameId) {
                socket.emit('error', { message: 'gameId requerido para acciones' });
                return;
            }
            if (!accion) {
                socket.emit('error', { message: 'accion requerida' });
                return;
            }

            const response = await GameController._ejecutarAccionInterna(gameId, userId, accion, datos);
            if (!response.success) {
                socket.emit('error', { message: response.error });
                return;
            }

            const room = io.sockets.adapter.rooms.get(roomName(gameId));
            if (room) {
                for (const socketId of room) {
                    const s = io.sockets.sockets.get(socketId);
                    const targetUserId = s?.data?.userId;
                    if (!s || !targetUserId) continue;
                    const filtrado = GameController._filtrarEstadoParaJugador(response.gameState, targetUserId);
                    s.emit('state', {
                        gameState: filtrado,
                        finalizado: response.finalizado,
                        ganador: response.ganador,
                        resultado: response.resultado
                    });
                }
            } else {
                socket.emit('state', {
                    gameState: response.gameStateFiltrado,
                    finalizado: response.finalizado,
                    ganador: response.ganador,
                    resultado: response.resultado
                });
            }
        });

        socket.on('chat_message', (payload = {}) => {
            const { gameId: payloadGameId, message } = payload;
            const gameId = payloadGameId || socket.data.gameId;
            const userId = socket.data.userId;

            const room = gameId ? io.sockets.adapter.rooms.get(roomName(gameId)) : null;
            if (!room || !room.has(socket.id)) {
                socket.emit('error', { message: 'No estás en esta partida' });
                return;
            }

            if (!message || message.trim().length === 0) {
                socket.emit('error', { message: 'El mensaje no puede estar vacío' });
                return;
            }

            if (message.length > 200) {
                socket.emit('error', { message: 'El mensaje es demasiado largo (máx 200 caracteres)' });
                return;
            }

            const username = userRepo.buscarPorId?.(userId)?.username || userId;

            io.to(roomName(gameId)).emit('chat_message', {
                userId,
                username,
                message: message.trim(),
                timestamp: Date.now()
            });
        });

        socket.on('disconnect', (reason) => {
            console.log(`🔌 WS desconectado ${socket.id}: ${reason}`);
            clearInterval(heartbeatTimer);
            lobbyManager.removeFromMatchmakingBySocket(socket.id);
            lobbyManager.removePlayer(userId);
            lobbyManager.availableGames.forEach((game) => {
                if (game.host === userId) {
                    lobbyManager.unregisterGame(game.gameId);
                }
            });
            emitLobbyState();
        });
    });

    return io;
}

module.exports = { initGameSocket };
