/**
 * Lógica del juego - Frontend
 */

let currentGameId = null;
let currentGameState = null;
let currentUserId = null;
let allCardsCache = {};
let selectedCard = null;
let selectedAttacker = null;
let cardsToDiscard = [];
let myPlayerKey = null;
let opponentPlayerKey = null;

/**
 * Inicializa el juego
 */
async function initGame() {
    try {
        console.log('🎮 Inicializando juego...');
        
        const user = await api.getCurrentUser();
        if (user.success) {
            currentUserId = user.data.id;
            console.log('👤 Usuario identificado:', currentUserId);
        } else {
            console.error('❌ No se pudo obtener el usuario');
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
    document.getElementById('passPhaseBtn').onclick = () => performAction('pasar_fase', {});
    document.getElementById('passTurnBtn').onclick = () => performAction('pasar_turno', {});
    document.getElementById('endGameBtn').onclick = endCurrentGame;

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
    document.getElementById('currentPhase').textContent = `Fase: ${formatPhaseName(currentGameState.fase)}`;
    document.getElementById('turnNumber').textContent = `Turno ${currentGameState.turnoNumero}`;
    
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

    const myState = currentGameState.jugadores[myPlayerKey];
    const opponentState = currentGameState.jugadores[opponentPlayerKey];
    if (!myState || !opponentState) {
        showError('No se pudo obtener el estado de los jugadores');
        return;
    }
    const isMyTurn = currentGameState.turnoActual === myPlayerKey;
    document.getElementById('currentPlayer').textContent = isMyTurn ? 'Es tu turno' : 'Turno del oponente';

    console.log('🔍 Estado del jugador (myState):', myState);
    console.log('🔍 Mano del jugador:', myState?.mano);
    console.log('🔍 Tipo de mano:', typeof myState?.mano, Array.isArray(myState?.mano));

    // Renderizar estado del jugador
    await renderPlayerState(myState, 'player', isMyTurn);
    
    // Renderizar estado del oponente
    await renderOpponentState(opponentState, 'opponent', isMyTurn);

    // Actualizar contadores
    document.getElementById('playerDeckCount').textContent = myState.mazo.length;
    document.getElementById('playerResources').textContent = myState.recursos;
    document.getElementById('playerResourcesTotal').textContent = myState.recursosTotales;
    document.getElementById('playerCementerioCount').textContent = myState.cementerio.length;
    document.getElementById('playerMazoCount').textContent = myState.mazo.length;

    document.getElementById('opponentDeckCount').textContent = opponentState.mazo.length;
    document.getElementById('opponentResources').textContent = `${opponentState.recursos}/${opponentState.recursosTotales}`;

    document.getElementById('handCount').textContent = Array.isArray(myState.mano) ? myState.mano.length : myState.mano;

    // Habilitar/deshabilitar botones según el turno
    const actionsEnabled = isMyTurn && !currentGameState.finalizado;
    document.getElementById('passPhaseBtn').disabled = !actionsEnabled;
    document.getElementById('passTurnBtn').disabled = !actionsEnabled || currentGameState.fase !== 'final';

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
 * Renderiza el estado de un jugador
 */
async function renderPlayerState(playerState, prefix, isMyTurn) {
    // Mano
    await renderZone(playerState.mano, `${prefix}HandZone`, 'hand', isMyTurn);
    
    // Línea de Defensa
    await renderZone(playerState.lineaDefensa, `${prefix}DefensaZone`, 'defensa', isMyTurn);
    
    // Línea de Ataque
    await renderZone(playerState.lineaAtaque, `${prefix}AtaqueZone`, 'ataque', isMyTurn);
    
    // Línea de Apoyo
    await renderZone(playerState.lineaApoyo, `${prefix}ApoyoZone`, 'apoyo', isMyTurn);
    
    // Reserva de Oro
    await renderZone(playerState.reservaOro, `${prefix}OroZone`, 'oro', isMyTurn);
}

/**
 * Renderiza el estado del oponente (sin mostrar mano)
 */
async function renderOpponentState(opponentState, prefix, isMyTurn) {
    // Línea de Defensa
    await renderZone(opponentState.lineaDefensa, `${prefix}DefensaZone`, 'defensa', isMyTurn, true);
    
    // Línea de Ataque
    await renderZone(opponentState.lineaAtaque, `${prefix}AtaqueZone`, 'ataque', isMyTurn, true);
    
    // Línea de Apoyo
    await renderZone(opponentState.lineaApoyo, `${prefix}ApoyoZone`, 'apoyo', isMyTurn);
    
    // Reserva de Oro
    await renderZone(opponentState.reservaOro, `${prefix}OroZone`, 'oro', isMyTurn);
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
 * Crea un elemento HTML para una carta
 */
function createCardElement(card, zoneType, isMyTurn, isOpponentDefense = false) {
    try {
        const div = document.createElement('div');
        div.className = 'game-card';
        div.dataset.cardId = card.id;
        div.dataset.zoneType = zoneType;

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
    if (!currentGameId) return;

    try {
        const response = await api.performGameAction(currentGameId, accion, datos);
        
        if (response.success) {
            currentGameState = response.data.gameState;
            
            // Renderizar nuevo estado
            await renderGameState();
            
            // Manejar acciones especiales
            if (response.data.resultado && response.data.resultado.requiereDescarte) {
                showDiscardModal(response.data.resultado.cartasEnMano - 8);
            }

            if (response.data.finalizado) {
                showMessage(`¡Partida finalizada! Ganador: ${response.data.ganador === currentUserId ? 'Tú' : 'Oponente'}`, 
                    response.data.ganador === currentUserId ? 'success' : 'error');
            } else {
                showMessage(response.data.resultado?.mensaje || 'Acción realizada', 'success');
            }
        }
    } catch (error) {
        showError('Error al realizar acción: ' + error.message);
    }
}

/**
 * Juega una carta
 */
async function playCard(cardId) {
    await performAction('jugar_carta', {
        carta_id: cardId,
        objetivo_id: null
    });
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

    await performAction('atacar', {
        atacante_id: selectedAttacker,
        objetivo_id: targetCardId
    });

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
 * Muestra un mensaje
 */
function showMessage(text, type = 'info') {
    const messagesContainer = document.getElementById('gameMessages');
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

