const { Server } = require('socket.io');
const { verificarToken } = require('../utils/jwtUtils');
const GameController = require('../controllers/GameController');

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

    // Middleware de autenticación por socket
    io.use((socket, next) => {
        try {
            const authHeader = socket.handshake.headers?.authorization;
            const tokenFromHeader = authHeader && authHeader.startsWith('Bearer ') ? authHeader.substring(7) : null;
            const token = socket.handshake.auth?.token || socket.handshake.query?.token || tokenFromHeader;
            const decoded = token ? verificarToken(token) : null;
            if (!decoded) {
                return next(new Error('Unauthorized'));
            }
            socket.data.userId = decoded.userId;
            next();
        } catch (err) {
            next(new Error('Unauthorized'));
        }
    });

    io.on('connection', (socket) => {
        const userId = socket.data.userId;
        console.log(`🔌 WS conectado: ${socket.id} usuario ${userId}`);

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

        socket.on('disconnect', (reason) => {
            console.log(`🔌 WS desconectado ${socket.id}: ${reason}`);
                clearInterval(heartbeatTimer);
        });
    });

    return io;
}

module.exports = { initGameSocket };
