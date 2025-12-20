/**
 * Smoke test para WebSocket de partidas usando socket.io-client.
 *
 * Requisitos:
 *   - Tener el servidor levantado (PORT o 3000 por defecto).
 *   - Un token JWT válido para un usuario que pertenezca a la partida.
 *   - Un gameId existente (devuelto por createGame).
 *
 * Uso:
 *   node scripts/ws_smoketest.js --gameId=ID --token=JWT \
 *        [--url=ws://localhost:3000/ws] [--action=pasar_fase] [--datos='{}']
 *
 * También puedes usar variables de entorno:
 *   WS_URL, AUTH_TOKEN, GAME_ID, ACTION, DATOS
 */

const { io } = require('socket.io-client');

function parseArgs() {
    const args = {};
    for (const arg of process.argv.slice(2)) {
        const [k, ...rest] = arg.replace(/^--/, '').split('=');
        args[k] = rest.join('=') || true;
    }
    return args;
}

const argv = parseArgs();
const WS_URL = argv.url || process.env.WS_URL || 'ws://localhost:3000/ws';
const AUTH_TOKEN = argv.token || process.env.AUTH_TOKEN;
const GAME_ID = argv.gameId || process.env.GAME_ID;
const ACTION = argv.action || process.env.ACTION;
const DATOS_RAW = argv.datos || process.env.DATOS || '{}';

if (!AUTH_TOKEN || !GAME_ID) {
    console.error('Faltan AUTH_TOKEN o GAME_ID. Usa --token y --gameId o variables de entorno.');
    process.exit(1);
}

let DATOS = {};
try {
    DATOS = JSON.parse(DATOS_RAW);
} catch (err) {
    console.warn('No se pudo parsear DATOS, usando objeto vacío. Error:', err.message);
    DATOS = {};
}

const urlObj = new URL(WS_URL);
const path = urlObj.pathname === '/' ? '/ws' : urlObj.pathname;
const base = `${urlObj.protocol}//${urlObj.host}`;

function connectClient(label) {
    const socket = io(base, {
        path,
        transports: ['websocket'],
        auth: { token: AUTH_TOKEN },
        extraHeaders: { Authorization: `Bearer ${AUTH_TOKEN}` },
        reconnectionAttempts: 2,
        reconnectionDelay: 500
    });

    socket.on('connect', () => {
        console.log(`[${label}] conectado ${socket.id}`);
        socket.emit('join_game', { gameId: GAME_ID });
    });

    socket.on('state', (msg) => {
        console.log(`[${label}] state`, JSON.stringify(msg));
    });

    socket.on('error', (err) => {
        console.error(`[${label}] error`, err);
    });

    socket.on('heartbeat', () => {
        // Responder heartbeat para no caer
        socket.emit('heartbeat');
    });

    socket.on('disconnect', (reason) => {
        console.log(`[${label}] disconnect: ${reason}`);
    });

    return socket;
}

const a = connectClient('A');
const b = connectClient('B');

// Enviar acción opcional desde el cliente A después de un pequeño delay
if (ACTION) {
    setTimeout(() => {
        console.log(`[A] enviando acción ${ACTION} con datos`, DATOS);
        a.emit('action', { gameId: GAME_ID, accion: ACTION, datos: DATOS });
    }, 1000);
}

// Cerrar después de 10 segundos
setTimeout(() => {
    console.log('Cerrando sockets...');
    a.close();
    b.close();
    process.exit(0);
}, 10000);
