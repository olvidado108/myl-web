/**
 * Lógica del juego - Frontend
 */
const GAME_JS_VERSION = 'mul6';
console.log(`💡 Cargando game.js versión ${GAME_JS_VERSION}`);

// Mostrar versión en UI
document.addEventListener('DOMContentLoaded', () => {
    const versionTag = document.createElement('div');
    versionTag.textContent = `game.js ${GAME_JS_VERSION}`;
    versionTag.style.position = 'fixed';
    versionTag.style.right = '10px';
    versionTag.style.bottom = '10px';
    versionTag.style.background = 'rgba(0,0,0,0.7)';
    versionTag.style.color = 'white';
    versionTag.style.padding = '6px 10px';
    versionTag.style.borderRadius = '6px';
    versionTag.style.fontSize = '12px';
    versionTag.style.zIndex = '2000';
    versionTag.style.boxShadow = '0 2px 8px rgba(0,0,0,0.4)';
    document.body.appendChild(versionTag);
});

let currentGameId = null;
let currentGameState = null;
let currentUserId = null;
let gameSocket = null;
let allCardsCache = {};
let selectedCard = null;
let selectedAttacker = null;
let cardsToDiscard = [];
let myPlayerKey = null;
let opponentPlayerKey = null;
let dropZonesInitialized = false;
let chatInitialized = false;
let isResyncingState = false;

/**
 * Inicializa el juego
 */
async function initGame() {
    try {
        console.log('🎮 Inicializando juego...');
        
        const params = new URLSearchParams(window.location.search);
        const gameIdFromUrl = params.get('gameId');
        const starter = params.get('starter');

        const user = await api.getCurrentUser();
        if (user.success) {
            currentUserId = user.data.id;
            console.log('👤 Usuario identificado:', currentUserId);
        } else {
            console.error('❌ No se pudo obtener el usuario');
        }

        // Si viene gameId en la URL, conectar directo al WS y no mostrar modal
        if (gameIdFromUrl) {
            currentGameId = gameIdFromUrl;
            await initNavbar();
            await connectGameSocket(gameIdFromUrl, starter);
            return;
        }

        // Cargar mazos disponibles
        console.log('📋 Cargando mazos...');
        await loadDecks();
        
        // Mostrar modal de configuración
        const setupModal = document.getElementById('gameSetupModal');
        if (setupModal) {
            setupModal.style.display = 'block';
            console.log('✅ Modal de configuración mostrado');
        } else {
            console.error('❌ No se encontró el modal de configuración');
        }

        // Event listeners
        setupEventListeners();
        setupDropZones();
        initChat();
        console.log('✅ Inicialización completa');
    } catch (error) {
        console.error('❌ Error al inicializar:', error);
        showError('Error al inicializar: ' + error.message);
    }
}

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    // Modal de configuración
    document.getElementById('closeSetupModal').onclick = () => {
        document.getElementById('gameSetupModal').style.display = 'none';
    };

    document.getElementById('createGameBtn').onclick = createNewGame;
    document.getElementById('loadGameBtn').onclick = toggleLoadGames;

    // Botones de acciones del juego
    const mulliganBtn = document.getElementById('mulliganBtn');
    if (mulliganBtn) {
        // Enlazar click directo y redundante en render para evitar falta de binding
        mulliganBtn.onclick = () => {
            console.log('🌀 Click mulligan (setup)');
            requestMulligan();
        };
    } else {
        console.warn('⚠️ Botón mulligan no encontrado');
    }

    const confirmHandBtn = document.getElementById('confirmHandBtn');
    if (confirmHandBtn) {
        confirmHandBtn.onclick = () => {
            console.log('✅ Confirmar mano (setup)');
            confirmHand();
        };
    }

    const passPhaseBtn = document.getElementById('passPhaseBtn');
    if (passPhaseBtn) {
        passPhaseBtn.onclick = () => performAction('pasar_fase', {});
    }
    const passTurnBtn = document.getElementById('passTurnBtn');
    if (passTurnBtn) {
        passTurnBtn.onclick = () => performAction('pasar_turno', {});
    }
    const endGameBtn = document.getElementById('endGameBtn');
    if (endGameBtn) {
        endGameBtn.onclick = endCurrentGame;
    }

    // Modal de objetivos
    document.getElementById('closeTargetModal').onclick = () => {
        document.getElementById('targetModal').style.display = 'none';
    };
    document.getElementById('attackCastleBtn').onclick = () => {
        if (selectedAttacker) {
            attackTarget(null);
        }
    };

    // Modal de descarte
    document.getElementById('confirmDiscardBtn').onclick = confirmDiscard;

    // Cerrar modales al hacer click fuera
    window.onclick = (event) => {
        const setupModal = document.getElementById('gameSetupModal');
        const targetModal = document.getElementById('targetModal');
        const discardModal = document.getElementById('discardModal');
        
        if (event.target === setupModal) {
            setupModal.style.display = 'none';
        }
        if (event.target === targetModal) {
            targetModal.style.display = 'none';
        }
        if (event.target === discardModal) {
            discardModal.style.display = 'none';
        }
    };
}

/**
 * Conecta al WebSocket de juego y se une a la partida
 */
async function connectGameSocket(gameId, starter) {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (!token) {
        showError('Sesión no válida, vuelve a iniciar sesión');
        window.location.href = '/login';
        return;
    }

    gameSocket = io({
        auth: { token },
        path: '/ws',
        transports: ['websocket'],
        forceNew: true,
        reconnectionAttempts: 3,
        timeout: 10000
    });

    gameSocket.on('connect', () => {
        console.log('✅ WS juego conectado');
        gameSocket.emit('join_game', { gameId });
        if (starter) {
            gameSocket.emit('confirm_starter', { gameId });
        }
    });

    gameSocket.on('state', async (payload) => {
        console.log('📥 Estado recibido WS', payload);
        currentGameId = gameId;
        currentGameState = payload.gameState;

        // Log mano propia para depurar mulligan
        try {
            const keys = Object.keys(currentGameState?.jugadores || {});
            const myKey = currentGameState?.jugadores
                ? keys.find(k => currentGameState.jugadores[k]?.id === currentUserId) || keys[0]
                : null;
            const myHand = myKey ? currentGameState.jugadores[myKey]?.mano : null;
            console.log('🖐️ Mano en state WS', { myKey, handType: typeof myHand, isArray: Array.isArray(myHand), hand: myHand });
        } catch (e) {
            console.warn('⚠️ No se pudo loguear mano en state', e);
        }

        await renderGameState();
    });

    // Chat de partida
    if (gameSocket.off) {
        gameSocket.off('chat_message');
    }
    gameSocket.on('chat_message', (data) => {
        displayChatMessage(data);
    });

    gameSocket.on('error', (err) => {
        console.error('❌ Error WS juego:', err);
        showError(err?.message || 'Error de WebSocket');
    });

    gameSocket.on('disconnect', () => {
        console.warn('❌ WS juego desconectado');
    });

    // Heartbeat
    gameSocket.on('heartbeat', () => {
        gameSocket.emit('heartbeat');
    });

    initChat();
}

/**
 * Carga los mazos disponibles
 */
async function loadDecks() {
    try {
        const response = await api.getDecks();
        console.log('📋 Respuesta de getDecks():', response);
        
        if (response.success && response.data) {
            const deckSelect = document.getElementById('deckSelect');
            if (!deckSelect) {
                console.error('❌ Elemento deckSelect no encontrado');
                return;
            }
            
            deckSelect.innerHTML = '<option value="">Selecciona un mazo...</option>';
            
            console.log(`📦 Cargando ${response.data.length} mazos en el select`);
            
            response.data.forEach(deck => {
                // deck.cartas puede venir ya como array o como string JSON
                let cantidadCartas = 0;
                if (deck.cartas) {
                    if (Array.isArray(deck.cartas)) {
                        cantidadCartas = deck.cartas.length;
                    } else if (typeof deck.cartas === 'string') {
                        try {
                            cantidadCartas = JSON.parse(deck.cartas).length;
                        } catch (e) {
                            console.warn('Error parseando cartas del mazo:', deck.id, e);
                            cantidadCartas = 0;
                        }
                    }
                }
                
                const option = document.createElement('option');
                option.value = deck.id;
                option.textContent = `${deck.nombre} (${cantidadCartas} cartas)`;
                deckSelect.appendChild(option);
                console.log(`✅ Mazo agregado al select: ${deck.nombre} (${deck.id})`);
            });
            
            console.log(`✅ Total de opciones en select: ${deckSelect.options.length}`);
        } else {
            console.warn('⚠️ No se recibieron mazos o respuesta inválida:', response);
            showError('No se pudieron cargar los mazos');
        }
    } catch (error) {
        console.error('❌ Error al cargar mazos:', error);
        showError('Error al cargar mazos: ' + error.message);
    }
}

/**
 * Crea una nueva partida
 */
async function createNewGame() {
    const deckSelect = document.getElementById('deckSelect');
    const deckId = deckSelect.value;

    if (!deckId) {
        showError('Por favor selecciona un mazo');
        return;
    }

    const sameDeck = document.getElementById('sameDeckCheckbox').checked;

    try {
        const response = await api.createGame(deckId, sameDeck ? deckId : null);
        
        if (response.success) {
            currentGameId = response.data.partida.id;
            currentGameState = response.data.gameState;
            
            console.log('✅ Partida creada:', currentGameId);
            console.log('📊 Estado inicial completo:', currentGameState);
            console.log('📊 Jugadores en estado:', Object.keys(currentGameState.jugadores || {}));
            if (currentGameState.jugadores) {
                Object.keys(currentGameState.jugadores).forEach(jugadorId => {
                    const jugador = currentGameState.jugadores[jugadorId];
                    console.log(`📊 Jugador ${jugadorId}:`, {
                        mano: jugador.mano,
                        manoLength: Array.isArray(jugador.mano) ? jugador.mano.length : 'NO ES ARRAY',
                        mazo: jugador.mazo?.length || 0,
                        tipoMano: typeof jugador.mano
                    });
                });
            }
            
            // Ocultar modal y mostrar juego
            document.getElementById('gameSetupModal').style.display = 'none';
            document.getElementById('gameContainer').style.display = 'block';
            
            // Renderizar estado inicial
            await renderGameState();
            showMessage('¡Partida creada!', 'success');
        }
    } catch (error) {
        showError('Error al crear partida: ' + error.message);
    }
}

/**
 * Alterna mostrar/ocultar lista de partidas existentes
 */
async function toggleLoadGames() {
    const gamesList = document.getElementById('existingGamesList');
    const listContainer = document.getElementById('gamesList');

    if (gamesList.style.display === 'none') {
        try {
            const response = await api.listGames({ estado: 'en_curso' });
            
            if (response.success && response.data && response.data.length > 0) {
                listContainer.innerHTML = '';
                
                response.data.forEach(game => {
                    const gameItem = document.createElement('div');
                    gameItem.className = 'game-item';
                    gameItem.innerHTML = `
                        <div class="game-item-info">
                            <div>
                                <strong>Partida ${game.id.substring(0, 10)}...</strong><br>
                                <small>Creada: ${new Date(game.fecha_inicio).toLocaleString()}</small>
                            </div>
                            <span class="game-item-status ${game.estado}">${game.estado}</span>
                        </div>
                    `;
                    gameItem.onclick = () => loadGame(game.id);
                    listContainer.appendChild(gameItem);
                });
                
                gamesList.style.display = 'block';
            } else {
                listContainer.innerHTML = '<p>No hay partidas en curso</p>';
                gamesList.style.display = 'block';
            }
        } catch (error) {
            showError('Error al cargar partidas: ' + error.message);
        }
    } else {
        gamesList.style.display = 'none';
    }
}

/**
 * Carga una partida existente
 */
async function loadGame(gameId) {
    try {
        const response = await api.getGame(gameId);
        
        if (response.success) {
            currentGameId = gameId;
            currentGameState = response.data.gameState;
            
            // Ocultar modal y mostrar juego
            document.getElementById('gameSetupModal').style.display = 'none';
            document.getElementById('existingGamesList').style.display = 'none';
            document.getElementById('gameContainer').style.display = 'block';
            
            // Renderizar estado
            await renderGameState();
            showMessage('Partida cargada', 'success');
        }
    } catch (error) {
        showError('Error al cargar partida: ' + error.message);
    }
}

/**
 * Renderiza el estado completo del juego
 */
async function renderGameState() {
    if (!currentGameState) return;

    // Actualizar header
    const phaseLabel = document.getElementById('phaseText') || document.getElementById('currentPhase');
    if (phaseLabel) {
        phaseLabel.textContent = `Fase: ${formatPhaseName(currentGameState.fase)}`;
    }
    const turnLabel = document.getElementById('turnText') || document.getElementById('turnNumber');
    if (turnLabel) {
        turnLabel.textContent = `Turno ${currentGameState.turnoNumero}`;
    }
    
    // Obtener claves de jugadores (pueden ser diferentes si tienen el mismo ID de usuario)
    const playerKeys = Object.keys(currentGameState.jugadores);
    console.log('🔍 Claves de jugadores en estado:', playerKeys);
    console.log('🔍 currentUserId:', currentUserId);
    
    // Identificar cuál clave corresponde al usuario y al turno actual
    const keyEnTurno = playerKeys.find(key => key === currentGameState.turnoActual && currentGameState.jugadores[key]?.id === currentUserId);
    const primeraCoincidencia = playerKeys.find(key => currentGameState.jugadores[key]?.id === currentUserId);
    myPlayerKey = keyEnTurno || primeraCoincidencia || playerKeys[0];
    opponentPlayerKey = playerKeys.find(key => key !== myPlayerKey) || playerKeys[1] || myPlayerKey;
    
    console.log('🔍 myPlayerKey seleccionado:', myPlayerKey);
    console.log('🔍 opponentPlayerKey seleccionado:', opponentPlayerKey);

    const starterLabel = document.getElementById('starterStatus');
    if (starterLabel) {
        const starterKey = currentGameState.jugadorInicialKey || currentGameState.turnoActual;
        const starterIsMe = starterKey === myPlayerKey;
        starterLabel.textContent = starterIsMe ? 'Empiezas tú' : 'Empieza el oponente';
    }

    const myState = currentGameState.jugadores[myPlayerKey];
    const opponentState = currentGameState.jugadores[opponentPlayerKey];
    if (!myState || !opponentState) {
        showError('No se pudo obtener el estado de los jugadores');
        return;
    }
    const isMyTurn = currentGameState.turnoActual === myPlayerKey;
    const currentPlayerEl = document.getElementById('currentPlayer');
    if (currentPlayerEl) {
        currentPlayerEl.textContent = isMyTurn ? 'Es tu turno' : 'Turno del oponente';
    }

    console.log('🔍 Estado del jugador (myState):', myState);
    console.log('🔍 Mano del jugador:', myState?.mano);
    console.log('🔍 Tipo de mano:', typeof myState?.mano, Array.isArray(myState?.mano));

    // Renderizar estado del jugador
    await renderPlayerState(myState, 'player', isMyTurn);
    
    // Renderizar estado del oponente
    await renderOpponentState(opponentState, 'opponent', isMyTurn);

    // Actualizar contadores
    const deckCountEl = document.getElementById('playerDeckCount');
    if (deckCountEl) deckCountEl.textContent = myState.mazo.length;

    const playerResourcesEl = document.getElementById('playerResources');
    if (playerResourcesEl) playerResourcesEl.textContent = myState.recursos;

    const playerResourcesTotalEl = document.getElementById('playerResourcesTotal');
    if (playerResourcesTotalEl) playerResourcesTotalEl.textContent = myState.recursosTotales;

    const playerCementerioEl = document.getElementById('playerCementerioCount');
    if (playerCementerioEl) playerCementerioEl.textContent = myState.cementerio.length;

    const playerMazoEl = document.getElementById('playerMazoCount');
    if (playerMazoEl) playerMazoEl.textContent = myState.mazo.length;

    const playerReservaEl = document.getElementById('playerReservaCount');
    if (playerReservaEl) playerReservaEl.textContent = Array.isArray(myState.reservaOro) ? myState.reservaOro.length : '--';

    const playerOroPagadoEl = document.getElementById('playerOroPagadoCount');
    if (playerOroPagadoEl) {
        const usados = (myState.recursosTotales ?? 0) - (myState.recursos ?? 0);
        playerOroPagadoEl.textContent = usados >= 0 ? usados : '--';
    }

    const opponentDeckEl = document.getElementById('opponentDeckCount');
    if (opponentDeckEl) opponentDeckEl.textContent = opponentState.mazo.length;

    const opponentResourcesEl = document.getElementById('opponentResources');
    if (opponentResourcesEl) opponentResourcesEl.textContent = `${opponentState.recursos}/${opponentState.recursosTotales}`;

    const handCountEl = document.getElementById('handCount');
    if (handCountEl) handCountEl.textContent = Array.isArray(myState.mano) ? myState.mano.length : myState.mano;

    const opponentCementerioEl = document.getElementById('opponentCementerioCount');
    if (opponentCementerioEl) opponentCementerioEl.textContent = Array.isArray(opponentState.cementerio) ? opponentState.cementerio.length : '--';

    const opponentReservaEl = document.getElementById('opponentReservaCount');
    if (opponentReservaEl) opponentReservaEl.textContent = Array.isArray(opponentState.reservaOro) ? opponentState.reservaOro.length : '--';

    const opponentOroPagadoEl = document.getElementById('opponentOroPagadoCount');
    if (opponentOroPagadoEl) {
        const usados = (opponentState.recursosTotales ?? 0) - (opponentState.recursos ?? 0);
        opponentOroPagadoEl.textContent = usados >= 0 ? usados : '--';
    }

    // Estado de mulligan
    const mulliganBtn = document.getElementById('mulliganBtn');
    const mulligans = currentGameState.mulligans || {};
    const misMulligans = mulligans[myPlayerKey] || 0;
    const mulliganListo = currentGameState.mulliganListo || {};
    const estoyListo = !!mulliganListo[myPlayerKey];
    const mulliganCompletado = !!currentGameState.mulliganCompletado;
    const canMulligan = currentGameState.turnoNumero === 1 && !currentGameState.finalizado && !estoyListo && !mulliganCompletado;
    if (mulliganBtn) {
        mulliganBtn.onclick = () => {
            console.log('🌀 Click mulligan (render)');
            requestMulligan();
        };
        mulliganBtn.disabled = !canMulligan;
        mulliganBtn.textContent = misMulligans > 0 ? `Mulligan (-${misMulligans})` : 'Mulligan';
        console.log('🌀 Mulligan state', { turno: currentGameState.turnoNumero, fase: currentGameState.fase, misMulligans, canMulligan, estoyListo, mulliganCompletado });
    }

    const confirmHandBtn = document.getElementById('confirmHandBtn');
    const canConfirmHand = currentGameState.turnoNumero === 1 && !currentGameState.finalizado && !estoyListo;
    if (confirmHandBtn) {
        confirmHandBtn.onclick = () => {
            console.log('✅ Confirmar mano (render)');
            confirmHand();
        };
        confirmHandBtn.disabled = !canConfirmHand;
        confirmHandBtn.textContent = estoyListo ? 'Listo ✓' : 'Confirmar mano';
    }

    // Mostrar estado de mulligan para ambos jugadores
    const statusEl = document.getElementById('mulliganStatus');
    if (statusEl) {
        const opponentReady = opponentPlayerKey ? !!mulliganListo[opponentPlayerKey] : false;
        const lines = [];
        lines.push(estoyListo ? 'Tú: Listo' : 'Tú: Mulligan en curso');
        lines.push(opponentReady ? 'Oponente: Listo' : 'Oponente: Mulligan en curso');
        if (!mulliganCompletado) {
            lines.push('El juego comenzará cuando ambos confirmen su mano.');
        } else {
            lines.push('Mulligan completado. ¡Puedes jugar!');
        }
        statusEl.textContent = lines.join(' | ');
    }

    // Si la mano aparece vacía después de un mulligan, intentar resincronizar estado (fallback)
    if (!isResyncingState && Array.isArray(myState.mano) && myState.mano.length === 0 && (misMulligans || 0) > 0) {
        isResyncingState = true;
        console.warn('⚠️ Mano vacía tras mulligan, resincronizando estado vía API...');
        api.getGame(currentGameId)
            .then((resp) => {
                if (resp.success && resp.data?.gameState) {
                    currentGameState = resp.data.gameState;
                    console.log('✅ Estado resincronizado desde API', {
                        mano: currentGameState?.jugadores?.[myPlayerKey]?.mano
                    });
                    renderGameState();
                } else {
                    console.warn('⚠️ No se pudo resincronizar estado:', resp);
                }
            })
            .catch((err) => console.error('❌ Error resincronizando estado', err))
            .finally(() => {
                isResyncingState = false;
            });
    }

    // Habilitar/deshabilitar botones según el turno
    const actionsEnabled = isMyTurn && !currentGameState.finalizado && currentGameState.mulliganCompletado;
    
    // Re-configurar event listeners y estado de botones
    const passPhaseBtn = document.getElementById('passPhaseBtn');
    if (passPhaseBtn) {
        passPhaseBtn.onclick = () => {
            console.log('⏭️ Click pasar fase');
            performAction('pasar_fase', {});
        };
        passPhaseBtn.disabled = !actionsEnabled;
    } else {
        console.warn('⚠️ Botón passPhaseBtn no encontrado');
    }
    
    const passTurnBtn = document.getElementById('passTurnBtn');
    if (passTurnBtn) {
        passTurnBtn.onclick = () => {
            console.log('⏭️ Click pasar turno');
            performAction('pasar_turno', {});
        };
        passTurnBtn.disabled = !actionsEnabled || currentGameState.fase !== 'final';
    } else {
        console.warn('⚠️ Botón passTurnBtn no encontrado');
    }

    // Mostrar mensaje si la partida terminó
    if (currentGameState.finalizado) {
        if (currentGameState.ganador === currentUserId) {
            showMessage('¡Has ganado!', 'success');
        } else {
            showMessage('Has perdido', 'error');
        }
    }
}

/**
 * Mapea un prefijo de jugador y tipo de zona al ID del contenedor en el DOM
 */
function getZoneContainerId(prefix, zoneType) {
    const map = {
        player: {
            hand: 'hand',
            defensa: 'me-defensa',
            ataque: 'me-ataque',
            apoyo: 'me-apoyo',
            oro: 'me-oro'
        },
        opponent: {
            defensa: 'opp-defensa',
            ataque: 'opp-ataque',
            apoyo: 'opp-apoyo',
            oro: 'opp-oro'
        }
    };

    return map[prefix]?.[zoneType];
}

/**
 * Renderiza el estado de un jugador
 */
async function renderPlayerState(playerState, prefix, isMyTurn) {
    // Mano
    await renderZone(playerState.mano, getZoneContainerId(prefix, 'hand'), 'hand', isMyTurn);
    
    // Línea de Defensa
    await renderZone(playerState.lineaDefensa, getZoneContainerId(prefix, 'defensa'), 'defensa', isMyTurn);
    
    // Línea de Ataque
    await renderZone(playerState.lineaAtaque, getZoneContainerId(prefix, 'ataque'), 'ataque', isMyTurn);
    
    // Línea de Apoyo
    await renderZone(playerState.lineaApoyo, getZoneContainerId(prefix, 'apoyo'), 'apoyo', isMyTurn);
    
    // Reserva de Oro
    await renderZone(playerState.reservaOro, getZoneContainerId(prefix, 'oro'), 'oro', isMyTurn);
}

/**
 * Renderiza el estado del oponente (sin mostrar mano)
 */
async function renderOpponentState(opponentState, prefix, isMyTurn) {
    // Línea de Defensa
    await renderZone(opponentState.lineaDefensa, getZoneContainerId(prefix, 'defensa'), 'defensa', isMyTurn, true);
    
    // Línea de Ataque
    await renderZone(opponentState.lineaAtaque, getZoneContainerId(prefix, 'ataque'), 'ataque', isMyTurn, true);
    
    // Línea de Apoyo
    await renderZone(opponentState.lineaApoyo, getZoneContainerId(prefix, 'apoyo'), 'apoyo', isMyTurn);
    
    // Reserva de Oro
    await renderZone(opponentState.reservaOro, getZoneContainerId(prefix, 'oro'), 'oro', isMyTurn);
}

/**
 * Renderiza una zona de cartas
 */
async function renderZone(cardIds, containerId, zoneType, isMyTurn, isOpponentDefense = false) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`❌ Contenedor no encontrado: ${containerId}`);
        return;
    }
    container.innerHTML = '';

    console.log(`🎴 Renderizando zona ${zoneType} en ${containerId}:`, cardIds);
    console.log(`🎴 Tipo de cardIds:`, typeof cardIds, `Es array:`, Array.isArray(cardIds));

    if (!cardIds || (Array.isArray(cardIds) && cardIds.length === 0)) {
        console.log(`⚠️ No hay cartas para renderizar en ${containerId}`);
        container.innerHTML = '<div class="card-placeholder">Vacío</div>';
        return;
    }

    // Si la mano del oponente, solo mostrar cantidad
    if (zoneType === 'hand' && isOpponentDefense) {
        const count = typeof cardIds === 'number' ? cardIds : (Array.isArray(cardIds) ? cardIds.length : 0);
        container.innerHTML = `<div class="card-placeholder">${count} cartas</div>`;
        return;
    }

    const cardIdArray = Array.isArray(cardIds) ? cardIds : [];

    console.log(`📋 Renderizando ${cardIdArray.length} cartas en zona ${zoneType}`);
    console.log(`📋 IDs de cartas:`, cardIdArray);

    let cardsRendered = 0;
    for (const cardId of cardIdArray) {
        console.log(`🔄 Procesando carta ${cardId}...`);
        const card = await getCardData(cardId);
        if (!card) {
            console.warn(`⚠️ No se pudo cargar carta: ${cardId}`);
            continue;
        }

        console.log(`✅ Carta ${cardId} cargada, creando elemento...`);
        const cardElement = createCardElement(card, zoneType, isMyTurn, isOpponentDefense);
        console.log(`✅ Elemento creado para carta ${cardId}, agregando al contenedor...`);
        container.appendChild(cardElement);
        cardsRendered++;
        console.log(`✅ Carta ${cardId} agregada al contenedor. Total renderizadas: ${cardsRendered}`);
    }

    console.log(`✅ ${cardsRendered} cartas renderizadas en zona ${zoneType} (${containerId})`);
    console.log(`✅ Contenedor tiene ${container.children.length} elementos hijos`);
}

/**
 * Configura zonas de drop para drag & drop
 */
function setupDropZones() {
    if (dropZonesInitialized) return;

    const dropZones = document.querySelectorAll('.zone[data-zone-type]');
    if (!dropZones || dropZones.length === 0) {
        console.warn('⚠️ No se encontraron zonas de drop para inicializar');
        return;
    }

    dropZones.forEach(zone => {
        const zoneType = zone.dataset.zoneType;
        const zoneOwner = zone.dataset.owner || 'player';

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            const cardId = e.dataTransfer.getData('cardId');
            const sourceZone = e.dataTransfer.getData('zoneType');
            if (canPlayCardInZone(cardId, zoneType, sourceZone, zoneOwner)) {
                zone.classList.add('drop-target');
            }
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drop-target');
        });

        zone.addEventListener('drop', async (e) => {
            e.preventDefault();
            zone.classList.remove('drop-target');
            const cardId = e.dataTransfer.getData('cardId');
            const sourceZone = e.dataTransfer.getData('zoneType');
            if (canPlayCardInZone(cardId, zoneType, sourceZone, zoneOwner)) {
                await playCardToZone(cardId, zoneType);
            }
        });
    });

    dropZonesInitialized = true;
}

/**
 * Valida si una carta puede jugarse en una zona destino
 */
function canPlayCardInZone(cardId, zoneType, sourceZone = 'hand', zoneOwner = 'player') {
    if (!cardId || !currentGameState) return false;
    if (zoneOwner !== 'player') return false; // no permitir soltar en zonas del oponente
    if (sourceZone !== 'hand') return false; // solo desde la mano
    if (currentGameState.turnoActual !== myPlayerKey) return false;

    const card = allCardsCache[cardId];
    const myState = currentGameState.jugadores?.[myPlayerKey];
    const faseActual = currentGameState.fase;
    const oroJugado = currentGameState.oroJugadoEnTurno?.[myPlayerKey];

    if (!card || !myState) return false;

    const costo = card.coste || 0;

    if (card.tipo === 'Oro') {
        return zoneType === 'oro' && faseActual === 'comienzo_vigilia' && !oroJugado;
    }

    const tieneRecursos = myState.recursos >= costo;

    if (card.tipo === 'Talisman') {
        return (faseActual === 'vigilia' || faseActual === 'batalla') && tieneRecursos && zoneType !== 'oro';
    }

    // Resto de cartas (aliados, armas, etc.) se juegan en vigilia en zonas distintas a oro
    return faseActual === 'vigilia' && tieneRecursos && zoneType !== 'oro';
}

/**
 * Crea un elemento HTML para una carta
 */
function createCardElement(card, zoneType, isMyTurn, isOpponentDefense = false) {
    try {
        const div = document.createElement('div');
        div.className = 'game-card';
        div.dataset.cardId = card.id;
        div.dataset.zoneType = zoneType;
        div.dataset.cardType = card.tipo || '';
        if (card.coste !== undefined) {
            div.dataset.cardCost = card.coste;
        }

        if (isMyTurn && zoneType === 'hand') {
            div.draggable = true;

            div.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('cardId', card.id);
                e.dataTransfer.setData('zoneType', zoneType);
                div.classList.add('dragging');
            });

            div.addEventListener('dragend', () => {
                div.classList.remove('dragging');
                document.querySelectorAll('.zone').forEach(z => z.classList.remove('drop-target'));
            });
        }

        // Mostrar imagen si está disponible
        if (card.imagenUrl) {
            const img = document.createElement('img');
            img.src = card.imagenUrl;
            img.alt = card.nombre;
            img.onerror = () => {
                img.style.display = 'none';
                div.textContent = card.nombre.substring(0, 10);
            };
            div.appendChild(img);
        } else {
            div.textContent = card.nombre.substring(0, 10);
        }

        // Información de la carta
        const info = document.createElement('div');
        info.className = 'card-info';
        let infoText = card.nombre;
        if (card.fuerza) infoText += ` (${card.fuerza})`;
        if (card.coste !== undefined) infoText += ` [${card.coste}]`;
        info.textContent = infoText;
        div.appendChild(info);

        // Agregar funcionalidad según la zona y si es mi turno
        if (isMyTurn) {
            const faseActual = currentGameState.fase;
            const myState = currentGameState.jugadores[myPlayerKey];
            const oroJugado = currentGameState.oroJugadoEnTurno?.[myPlayerKey];

            if (zoneType === 'hand') {
                // Carta en mano: se puede jugar según fase y tipo
                const costo = card.coste || 0;
                let canPlay = false;

                if (card.tipo === 'Oro') {
                    canPlay = faseActual === 'comienzo_vigilia' && !oroJugado;
                } else if (card.tipo === 'Talisman') {
                    canPlay = (faseActual === 'vigilia' || faseActual === 'batalla') && myState && myState.recursos >= costo;
                } else {
                    canPlay = faseActual === 'vigilia' && myState && myState.recursos >= costo;
                }

                if (canPlay) {
                    div.classList.add('playable');
                    div.onclick = () => playCard(card.id);
                }
            } else if (zoneType === 'defensa') {
                // Aliado en línea de defensa: se puede declarar ataque
                if (faseActual === 'batalla' && !card.girada) {
                    div.onclick = () => selectAttacker(card.id);
                }
            } else if (isOpponentDefense && zoneType === 'defensa') {
                // Aliado del oponente: se puede seleccionar como objetivo
                if (selectedAttacker) {
                    div.onclick = () => attackTarget(card.id);
                    div.classList.add('playable');
                }
            }
        }

        // Tooltip con información completa
        div.title = `${card.nombre}\nTipo: ${card.tipo}\n${card.fuerza ? 'Fuerza: ' + card.fuerza : ''}\n${card.coste !== undefined ? 'Coste: ' + card.coste : ''}`;

        return div;
    } catch (error) {
        console.error(`❌ Error creando elemento para carta ${card.id}:`, error);
        // Retornar un elemento básico en caso de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'game-card error';
        errorDiv.textContent = card.nombre || card.id;
        return errorDiv;
    }
}

/**
 * Obtiene los datos de una carta (con caché)
 */
async function getCardData(cardId) {
    if (allCardsCache[cardId]) {
        console.log(`📦 Carta ${cardId} encontrada en caché`);
        return allCardsCache[cardId];
    }

    try {
        console.log(`🌐 Cargando carta ${cardId} desde API...`);
        const response = await api.getCard(cardId);
        console.log(`📥 Respuesta de API para carta ${cardId}:`, response);
        if (response.success && response.data) {
            allCardsCache[cardId] = response.data;
            console.log(`✅ Carta ${cardId} cargada:`, response.data.nombre);
            return response.data;
        } else {
            console.error(`❌ Error en respuesta de API para carta ${cardId}:`, response);
        }
    } catch (error) {
        console.error(`❌ Error cargando carta ${cardId}:`, error);
    }

    return null;
}

/**
 * Realiza una acción en el juego
 */
async function performAction(accion, datos) {
    if (!currentGameId) {
        console.warn(`⚠️ performAction sin currentGameId para accion ${accion}`);
        showError('No hay partida activa (sin gameId)');
        return;
    }

    // Evitar acciones de juego si mulligan no está completo (seguridad en UI)
    if (accion !== 'mulligan' && accion !== 'confirmar_mano' && currentGameState && !currentGameState.mulliganCompletado) {
        showMessage('Aún no termina el mulligan de ambos jugadores', 'info');
        return;
    }

    console.log('➡️ performAction (solo WS)', { accion, datos, gameId: currentGameId, hasSocket: !!gameSocket, socketConnected: gameSocket?.connected, version: GAME_JS_VERSION });

    if (gameSocket && gameSocket.connected) {
        console.log('📤 Enviando acción por WS', { accion, datos, gameId: currentGameId });
        gameSocket.emit('action', {
            gameId: currentGameId,
            accion,
            datos
        });
        showActionFeedback('Acción enviada', 'info');
        return;
    }

    console.warn('⚠️ WS no conectado, no se envió la acción', { hasSocket: !!gameSocket, connected: gameSocket?.connected });
    showError('WS no conectado, recarga la partida. (Solo WS, sin HTTP)');
}

/**
 * Solicita un mulligan
 */
async function requestMulligan() {
    console.log('🌀 Solicitando mulligan...');
    showActionFeedback('Solicitando mulligan...', 'info');
    await performAction('mulligan', {});
}

/**
 * Confirma la mano inicial para cerrar el mulligan del jugador
 */
async function confirmHand() {
    console.log('✅ Confirmando mano...');
    showActionFeedback('Confirmando mano...', 'info');
    await performAction('confirmar_mano', {});
}

/**
 * Muestra feedback rápido si se intenta actuar antes de terminar mulligan
 */
function ensureMulliganReady() {
    if (currentGameState && !currentGameState.mulliganCompletado) {
        showMessage('Esperando a que ambos confirmen el mulligan', 'info');
        return false;
    }
    return true;
}

/**
 * Juega una carta hacia una zona específica (drag & drop)
 */
async function playCardToZone(cardId, zoneType) {
    if (!cardId) return;

    showActionFeedback('Jugando carta...', 'info');
    highlightCard(cardId, 800);

    // Animación rápida a la carta en mano
    const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
    if (cardEl) {
        cardEl.classList.add('card-played');
        setTimeout(() => cardEl.classList.remove('card-played'), 600);
    }

    await performAction('jugar_carta', {
        carta_id: cardId,
        objetivo_id: null,
        zona: zoneType
    });
}

/**
 * Juega una carta
 */
async function playCard(cardId) {
    await playCardToZone(cardId, null);
}

/**
 * Selecciona un atacante
 */
function selectAttacker(cardId) {
    selectedAttacker = cardId;
    
    // Mostrar modal de selección de objetivo
    const targetModal = document.getElementById('targetModal');
    const targetOptions = document.getElementById('targetOptions');
    targetOptions.innerHTML = '';

    const opponentState = currentGameState.jugadores[opponentPlayerKey];

    // Agregar opciones de aliados del oponente
    if (opponentState.lineaDefensa && opponentState.lineaDefensa.length > 0) {
        opponentState.lineaDefensa.forEach(cardId => {
            getCardData(cardId).then(card => {
                if (card) {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-sm';
                    btn.textContent = card.nombre;
                    btn.onclick = () => attackTarget(cardId);
                    targetOptions.appendChild(btn);
                }
            });
        });
    } else {
        targetOptions.innerHTML = '<p>No hay aliados para atacar</p>';
    }

    targetModal.style.display = 'block';
}

/**
 * Ataca a un objetivo
 */
async function attackTarget(targetCardId) {
    if (!selectedAttacker) return;

    showActionFeedback('Atacando...', 'info');
    highlightCard(selectedAttacker, 800);
    if (targetCardId) {
        highlightCard(targetCardId, 800);
    }

    await performAction('atacar', {
        atacante_id: selectedAttacker,
        objetivo_id: targetCardId
    });

    if (targetCardId) {
        shakeCard(targetCardId);
    }

    selectedAttacker = null;
    document.getElementById('targetModal').style.display = 'none';
}

/**
 * Muestra modal para descartar cartas
 */
function showDiscardModal(cardsToDiscardCount) {
    const discardModal = document.getElementById('discardModal');
    const discardOptions = document.getElementById('discardOptions');
    const confirmBtn = document.getElementById('confirmDiscardBtn');
    
    discardOptions.innerHTML = '';
    cardsToDiscard = [];
    confirmBtn.disabled = true;

    const myState = currentGameState.jugadores[myPlayerKey];
    if (!myState) {
        showError('No se pudo cargar tu mano para descartar');
        return;
    }
    
    myState.mano.forEach(cardId => {
        getCardData(cardId).then(card => {
            if (card) {
                const cardDiv = createCardElement(card, 'hand', true);
                cardDiv.onclick = () => {
                    if (cardsToDiscard.includes(cardId)) {
                        cardsToDiscard = cardsToDiscard.filter(id => id !== cardId);
                        cardDiv.classList.remove('selected');
                    } else if (cardsToDiscard.length < cardsToDiscardCount) {
                        cardsToDiscard.push(cardId);
                        cardDiv.classList.add('selected');
                    }
                    confirmBtn.disabled = cardsToDiscard.length !== cardsToDiscardCount;
                };
                discardOptions.appendChild(cardDiv);
            }
        });
    });

    discardModal.style.display = 'block';
}

/**
 * Confirma el descarte de cartas
 */
async function confirmDiscard() {
    // Por ahora, solo cerramos el modal
    // TODO: Implementar acción de descarte cuando esté disponible en el backend
    document.getElementById('discardModal').style.display = 'none';
    showMessage('Descarte implementado próximamente', 'info');
}

/**
 * Finaliza la partida actual
 */
async function endCurrentGame() {
    if (!confirm('¿Estás seguro de que quieres abandonar la partida?')) {
        return;
    }

    if (!currentGameId) return;

    try {
        await api.endGame(currentGameId);
        showMessage('Partida abandonada', 'info');
        
        // Volver al menú principal
        document.getElementById('gameContainer').style.display = 'none';
        document.getElementById('gameSetupModal').style.display = 'block';
        currentGameId = null;
        currentGameState = null;
    } catch (error) {
        showError('Error al finalizar partida: ' + error.message);
    }
}

/**
 * Muestra feedback visual de una acción
 */
function showActionFeedback(message, type = 'info') {
    const feedbackEl = document.createElement('div');
    feedbackEl.className = `action-feedback ${type}`;
    feedbackEl.textContent = message;

    const messagesContainer = document.getElementById('gameMessages');
    if (messagesContainer) {
        messagesContainer.appendChild(feedbackEl);

        setTimeout(() => {
            feedbackEl.style.opacity = '0';
            feedbackEl.style.transform = 'translateY(-20px)';
            setTimeout(() => feedbackEl.remove(), 300);
        }, 3000);
    }
}

/**
 * Resalta temporalmente una carta
 */
function highlightCard(cardId, duration = 1000) {
    const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
    if (!cardEl) return;

    cardEl.classList.add('highlighted');
    setTimeout(() => {
        cardEl.classList.remove('highlighted');
    }, duration);
}

/**
 * Anima una carta al recibir daño
 */
function shakeCard(cardId) {
    const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
    if (!cardEl) return;

    cardEl.classList.add('card-damaged');
    setTimeout(() => {
        cardEl.classList.remove('card-damaged');
    }, 500);
}

/**
 * Resalta una zona brevemente
 */
function glowZone(zoneId, color = '#4CAF50') {
    const zoneEl = document.getElementById(zoneId);
    if (!zoneEl) return;

    zoneEl.style.boxShadow = `0 0 20px ${color}`;
    setTimeout(() => {
        zoneEl.style.boxShadow = '';
    }, 1000);
}

/**
 * Inicializa UI y listeners del chat en partida
 */
function initChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');
    const toggleBtn = document.getElementById('toggleChatBtn');

    // Vincular listener de socket cada vez que se llame
    if (gameSocket) {
        gameSocket.off?.('chat_message');
        gameSocket.on('chat_message', (data) => displayChatMessage(data));
    }

    if (!chatInput || !sendBtn || !toggleBtn) {
        return;
    }

    if (chatInitialized) return;
    chatInitialized = true;

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    sendBtn.addEventListener('click', sendChatMessage);

    toggleBtn.addEventListener('click', () => {
        const chatContainer = document.getElementById('gameChat');
        const chatMessages = document.getElementById('chatMessages');
        const chatInputContainer = document.querySelector('.chat-input-container');

        if (!chatContainer || !chatMessages || !chatInputContainer) return;

        if (chatContainer.classList.contains('collapsed')) {
            chatContainer.classList.remove('collapsed');
            chatMessages.style.display = 'block';
            chatInputContainer.style.display = 'flex';
            toggleBtn.textContent = '−';
        } else {
            chatContainer.classList.add('collapsed');
            chatMessages.style.display = 'none';
            chatInputContainer.style.display = 'none';
            toggleBtn.textContent = '+';
        }
    });
}

/**
 * Envía un mensaje de chat al servidor
 */
function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;

    const message = chatInput.value.trim();

    if (!message || !currentGameId) return;

    if (gameSocket) {
        gameSocket.emit('chat_message', {
            gameId: currentGameId,
            message
        });
        chatInput.value = '';
    }
}

/**
 * Muestra un mensaje en el chat
 */
function displayChatMessage(data) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message';

    const isMyMessage = data.userId === currentUserId;
    if (isMyMessage) {
        messageEl.classList.add('my-message');
    }

    const time = new Date(data.timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });

    messageEl.innerHTML = `
        <div class="chat-message-header">
            <span class="chat-username">${escapeHtml(data.username || data.userId)}</span>
            <span class="chat-time">${time}</span>
        </div>
        <div class="chat-message-text">${escapeHtml(data.message)}</div>
    `;

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Muestra un mensaje
 */
function showMessage(text, type = 'info') {
    const messagesContainer = document.getElementById('gameMessages');
    if (!messagesContainer) {
        console.warn('⚠️ Contenedor de mensajes no encontrado');
        return;
    }
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    messagesContainer.appendChild(message);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        message.remove();
    }, 5000);
}

/**
 * Muestra un error
 */
function showError(message) {
    showMessage(message, 'error');
}

/**
 * Capitaliza la primera letra
 */
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Nombres amigables para las fases oficiales
 */
function formatPhaseName(phase) {
    const map = {
        reagrupar: 'Reagrupar',
        comienzo_vigilia: 'Comienzo de Vigilia',
        vigilia: 'Vigilia',
        batalla: 'Batalla Mitológica',
        final: 'Fase Final'
    };
    return map[phase] || capitalizeFirst(phase || '');
}







