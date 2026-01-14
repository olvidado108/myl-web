/**
 * Pruebas rápidas del flujo de mulligan y confirmación simultánea.
 * Se usa un stub de repositorio en memoria para evitar dependencias de BD.
 */

const GameControllerInstance = require('../controllers/GameController');
const GameControllerClass = GameControllerInstance.constructor;
const GameState = require('../models/GameState');

let passed = 0;
let failed = 0;

function assert(name, condition, extra = '') {
    if (condition) {
        console.log(`✅ ${name}`);
        passed++;
    } else {
        console.error(`❌ ${name}${extra ? ' - ' + extra : ''}`);
        failed++;
    }
}

function createStubbedController(gameState) {
    const gameId = 'game_test';
    const partida = {
        id: gameId,
        estado: 'en_curso',
        jugador1_id: 'p1',
        jugador2_id: 'p2',
        estado_juego: gameState.toJSON(),
        turnos: 1
    };

    const controller = new GameControllerClass();

    // Stub repositorio de partidas (in-memory)
    controller.gameRepo = {
        storage: partida,
        buscarPorId: (id) => (id === gameId ? { ...controller.gameRepo.storage } : null),
        actualizarPartida: (id, data) => {
            if (id !== gameId) return;
            controller.gameRepo.storage = { ...controller.gameRepo.storage, ...data };
        },
        finalizarPartida: () => {}
    };

    return { controller, gameId, partida };
}

async function runTests() {
    // Crear estado base con manos y mazos llenos
    const gs = new GameState('p1', 'p2');
    gs.jugadores[gs.getKeyPorId('p1')].mano = Array.from({ length: 8 }, (_, i) => `c${i + 1}`);
    gs.jugadores[gs.getKeyPorId('p1')].mazo = Array.from({ length: 40 }, (_, i) => `m${i + 1}`);
    gs.jugadores[gs.getKeyPorId('p2')].mano = Array.from({ length: 8 }, (_, i) => `d${i + 1}`);
    gs.jugadores[gs.getKeyPorId('p2')].mazo = Array.from({ length: 40 }, (_, i) => `n${i + 1}`);

    const { controller, gameId } = createStubbedController(gs);

    // 1) Mulligan reduce en 1 carta y marca mulligan sin confirmar
    const r1 = await controller._ejecutarAccionInterna(gameId, 'p1', 'mulligan', {});
    assert('Mulligan responde exito', r1.success === true);
    assert('Mulligan reduce mano a 7', r1.resultado?.mensaje?.includes('7 cartas'));
    assert(
        'Jugador NO está listo tras mulligan',
        r1.gameState.mulliganListo[gs.getKeyPorId('p1')] === false
    );

    // 2) No permite acciones de juego mientras mulligan no se completa
    const r2 = await controller._ejecutarAccionInterna(gameId, 'p1', 'pasar_fase', {});
    assert(
        'Bloquea pasar_fase si mulligan no completado',
        r2.success === false && /mulligan no ha finalizado/i.test(r2.error || '')
    );

    // 3) Confirmar mano jugador 1 deja pendiente al oponente
    const r3 = await controller._ejecutarAccionInterna(gameId, 'p1', 'confirmar_mano', {});
    assert('Confirmar mano jugador 1 exito', r3.success === true);
    assert(
        'Aún no completado tras 1 confirmación',
        r3.gameState.mulliganCompletado === false
    );

    // 4) Confirmar mano jugador 2 completa el mulligan
    const r4 = await controller._ejecutarAccionInterna(gameId, 'p2', 'confirmar_mano', {});
    assert('Confirmar mano jugador 2 exito', r4.success === true);
    assert('Mulligan completado al confirmar ambos', r4.gameState.mulliganCompletado === true);

    // 5) Ahora permitir pasar_fase
    const r5 = await controller._ejecutarAccionInterna(gameId, 'p1', 'pasar_fase', {});
    assert('Permite pasar_fase tras mulligan completado', r5.success === true);

    console.log('\n' + '='.repeat(50));
    console.log(`📊 Resumen: ${passed} exitosas, ${failed} fallidas`);
    if (failed > 0) {
        process.exit(1);
    }
}

runTests().catch((err) => {
    console.error('❌ Error ejecutando pruebas:', err);
    process.exit(1);
});

