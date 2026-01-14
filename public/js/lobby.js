/**
 * Lógica del Lobby
 */

let socket = null;
let isSearching = false;
let searchStartTime = null;
let currentGameId = null;
let currentOpponent = null;
let currentOpponentName = null;
let currentUserId = null;

/**
 * Inicializa el lobby
 */
async function initLobby() {
    try {
        console.log('🎮 Inicializando lobby...');

        await loadDecks();
        // obtener usuario para usar en RPS
        const me = await api.getCurrentUser();
        if (me?.success && me.data?.id) {
            currentUserId = me.data.id;
        }
        await connectWebSocket();
        setupEventListeners();

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
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');

    // Conectar al namespace raíz, usando path /ws configurado en el servidor
    socket = io({
        auth: { token },
        path: '/ws',
        transports: ['websocket'], // evitar polling 400
        forceNew: true,
        reconnectionAttempts: 3,
        timeout: 10000
    });

    socket.on('connect', () => {
        console.log('✅ Conectado al servidor');
        socket.emit('join_lobby');
    });

    // Responder al heartbeat del servidor para evitar desconexiones
    socket.on('heartbeat', () => {
        socket.emit('heartbeat');
    });

    socket.on('disconnect', () => {
        console.log('❌ Desconectado del servidor');
        showError('Desconectado del servidor. Intentando reconectar...');
    });

    socket.on('connect_error', (err) => {
        console.error('❌ Error de conexión WS:', err?.message || err);
        showError('No se pudo conectar al lobby: ' + (err?.message || 'WS error'));
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

    socket.on('joined_private_game', (data) => {
        handleMatchFound(data);
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
            const joinPrivateDeck = document.getElementById('joinPrivateDeck');

            quickMatchDeck.innerHTML = '<option value="">Selecciona un mazo...</option>';
            privateGameDeck.innerHTML = '<option value="">Selecciona un mazo...</option>';
            if (joinPrivateDeck) {
                joinPrivateDeck.innerHTML = '<option value="">Selecciona un mazo...</option>';
            }

            response.data.forEach(deck => {
                const cantidadCartas = Array.isArray(deck.cartas)
                    ? deck.cartas.length
                    : (typeof deck.cartas === 'string' ? JSON.parse(deck.cartas).length : 0);

                const option = document.createElement('option');
                option.value = deck.id;
                option.textContent = `${deck.nombre} (${cantidadCartas} cartas)`;

                quickMatchDeck.appendChild(option.cloneNode(true));
                privateGameDeck.appendChild(option.cloneNode(true));
                if (joinPrivateDeck) {
                    joinPrivateDeck.appendChild(option);
                }
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
    document.getElementById('joinPrivateGameBtn').onclick = joinPrivateGame;
    const genBtn = document.getElementById('generateInviteCodeBtn');
    if (genBtn) {
        genBtn.onclick = () => {
            const code = 'PRV_' + Math.random().toString(36).substring(2, 8).toUpperCase();
            const input = document.getElementById('customInviteCode');
            if (input) input.value = code;
        };
    }
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

    document.getElementById('findMatchBtn').disabled = true;
    document.getElementById('cancelMatchBtn').style.display = 'inline-block';
    document.getElementById('matchmakingStatus').style.display = 'block';
    document.getElementById('findMatchText').textContent = 'Buscando...';
    document.getElementById('findMatchSpinner').style.display = 'inline-block';

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
    currentGameId = data.gameId;
    currentOpponent = data.opponent;
    currentOpponentName = data.opponentName || data.opponent || 'Oponente';
    showRpsModal(data.gameId, currentOpponentName);
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
    const inviteCode = (document.getElementById('customInviteCode')?.value || '').trim();

    if (!deckId) {
        showError('Por favor selecciona un mazo');
        return;
    }

    socket.emit('create_private_game', { deckId, inviteCode });
}

/**
 * Unirse a una partida privada con código
 */
function joinPrivateGame() {
    const inviteCodeInput = document.getElementById('joinInviteCode');
    const deckId = document.getElementById('joinPrivateDeck').value;
    const inviteCode = inviteCodeInput.value.trim();

    if (!inviteCode) {
        showError('Ingresa el código de invitación');
        return;
    }

    if (!deckId) {
        showError('Por favor selecciona un mazo');
        return;
    }

    socket.emit('join_private_game', { inviteCode, deckId });
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
                <p>Host: ${game.host || 'N/A'}</p>
                <p>Jugadores: ${game.players?.length || 0}/${game.maxPlayers || 2}</p>
                <p>Modo: ${game.isPrivate ? 'Privada' : 'Pública'}</p>
            </div>
            <button class="btn btn-sm" onclick="joinGame('${game.gameId}', ${game.isPrivate ? 'true' : 'false'})">
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
function joinGame(gameId, isPrivate = false) {
    if (isPrivate) {
        const deckId = document.getElementById('joinPrivateDeck').value;
        let inviteCode = document.getElementById('joinInviteCode').value.trim();
        if (!inviteCode) {
            inviteCode = prompt('Ingresa el código de invitación');
        }
        if (!inviteCode) {
            showError('Código de invitación requerido');
            return;
        }
        if (!deckId) {
            showError('Por favor selecciona un mazo');
            return;
        }
        socket.emit('join_private_game', { gameId, inviteCode, deckId });
        return;
    }

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

/**
 * ===================== RPS (Piedra/Papel/Tijera) =====================
 */
function showRpsModal(gameId, opponentDisplay) {
    const modal = document.createElement('div');
    modal.id = 'rps-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.background = 'rgba(0,0,0,0.7)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '9999';

    modal.innerHTML = `
      <div style="background:#111827;padding:20px;border-radius:10px;width:320px;color:#e6e9ef;font-family:sans-serif;">
        <h3>Elige quién empieza</h3>
        <p>Contra: ${opponentDisplay}</p>
        <div id="rps-status" style="margin:8px 0;">Elige: </div>
        <div style="display:flex;gap:8px;margin-bottom:12px;justify-content:center;">
          <button class="btn btn-primary" data-choice="rock">Piedra</button>
          <button class="btn btn-primary" data-choice="paper">Papel</button>
          <button class="btn btn-primary" data-choice="scissors">Tijera</button>
        </div>
        <div id="rps-decision" style="display:none;">
          <p>Ganaste el RPS. ¿Quién empieza?</p>
          <button class="btn btn-secondary" id="start-me">Yo empiezo</button>
          <button class="btn btn-secondary" id="start-op">Oponente empieza</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelectorAll('button[data-choice]').forEach(btn => {
        btn.onclick = () => {
            const choice = btn.dataset.choice;
            socket.emit('rps_choice', { gameId, choice });
            modal.querySelector('#rps-status').textContent = 'Esperando al oponente...';
        };
    });

    socket.off('rps_result');
    socket.on('rps_result', (payload) => {
        if (payload.tie) {
            modal.querySelector('#rps-status').textContent = 'Empate. Elige de nuevo.';
            return;
        }
        const iWon = currentUserId && payload.winner === currentUserId;
        modal.querySelector('#rps-status').textContent = iWon
            ? 'Ganaste el RPS.'
            : 'El oponente ganó el RPS. Espera decisión...';
        modal.querySelector('#rps-decision').style.display = iWon ? 'block' : 'none';
    });

    socket.off('rps_final');
    socket.on('rps_final', (payload) => {
        modal.remove();
        // Redirigir pasando starter en la URL
        window.location.href = `/game?gameId=${gameId}&starter=${payload.starter}`;
    });

    modal.querySelector('#start-me').onclick = () => {
        const starter = socket.data?.userId || 'me';
        socket.emit('rps_decide_first', { gameId, starter });
    };
    modal.querySelector('#start-op').onclick = () => {
        socket.emit('rps_decide_first', { gameId, starter: currentOpponent });
    };
}

