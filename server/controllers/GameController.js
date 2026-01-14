const GameRepository = require('../repository/GameRepository');
const DeckRepository = require('../repository/DeckRepository');
const CardRepositorySQLite = require('../repository/CardRepositorySQLite');
const GameState = require('../models/GameState');
const Carta = require('../models/Card');
const { barajar, repartirCartasIniciales } = require('../utils/gameUtils');
const { AbilityManager, EventSystem } = require('../../game-engine');

// Config WS para informar al cliente cómo conectarse
const WS_PATH = process.env.WS_PATH || '/ws';
const defaultWsBase = () => `ws://localhost:${process.env.PORT || 3000}`;
const buildWsUrl = (gameId) => {
    const base = process.env.WS_BASE_URL || process.env.PUBLIC_WS_URL || defaultWsBase();
    return `${base}${WS_PATH}${gameId ? `?gameId=${gameId}` : ''}`;
};

class GameController {
    constructor() {
        this.gameRepo = new GameRepository();
        this.deckRepo = new DeckRepository();
        this.cardRepo = new CardRepositorySQLite();
        this.abilityManager = null; // Se inicializa con cada partida
    }

    /**
     * Crea una nueva partida
     */
    async createGame(req, res) {
        try {
            const userId = req.user?.userId;
            
            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Debes estar autenticado para crear partidas'
                });
            }

            const { mazo1_id, mazo2_id, jugador2_id } = req.body;

            if (!mazo1_id) {
                return res.status(400).json({
                    success: false,
                    error: 'Debes especificar un mazo para el jugador 1'
                });
            }

            // Cargar mazos
            const mazo1 = this.deckRepo.buscarPorId(mazo1_id);
            if (!mazo1) {
                return res.status(404).json({
                    success: false,
                    error: 'Mazo 1 no encontrado'
                });
            }

            // Verificar que el mazo pertenece al usuario (o es público)
            if (mazo1.usuario_id !== userId && !mazo1.es_publico) {
                console.warn(`⚠️ Usuario ${userId} intentó usar mazo ${mazo1.id} que pertenece a ${mazo1.usuario_id}`);
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para usar este mazo'
                });
            }

            console.log(`✅ Usuario ${userId} usando mazo ${mazo1.id} (${mazo1.nombre}) con ${Array.isArray(mazo1.cartas) ? mazo1.cartas.length : JSON.parse(mazo1.cartas || '[]').length} cartas`);

            let mazo2 = null;
            let jugador2Id = jugador2_id || userId; // Por ahora, permitir jugar contra uno mismo (modo práctica)

            if (mazo2_id) {
                mazo2 = this.deckRepo.buscarPorId(mazo2_id);
                if (!mazo2) {
                    return res.status(404).json({
                        success: false,
                        error: 'Mazo 2 no encontrado'
                    });
                }
                if (jugador2_id && mazo2.usuario_id !== jugador2_id) {
                    return res.status(403).json({
                        success: false,
                        error: 'El mazo 2 no pertenece al jugador 2'
                    });
                }
            } else {
                // Si no hay mazo2, usar el mismo mazo (modo práctica)
                mazo2 = mazo1;
                jugador2Id = userId;
            }

            // Inicializar GameState
            console.log(`🎮 Creando partida: Jugador1=${userId}, Jugador2=${jugador2Id}, Mazo1=${mazo1.id}, Mazo2=${mazo2?.id || 'mismo'}`);
            const gameState = this._inicializarPartida(mazo1, mazo2, userId, jugador2Id);
            const jugador1Key = gameState.getKeyPorId(userId) || Object.keys(gameState.jugadores)[0];
            console.log(`✅ Partida inicializada. Cartas en mano jugador1: ${gameState.jugadores[jugador1Key].mano.length}`);

            // Crear partida en BD
            const partida = this.gameRepo.crearPartida({
                jugador1_id: userId,
                jugador2_id: jugador2Id,
                mazo1_id: mazo1_id,
                mazo2_id: mazo2_id || mazo1_id,
                estado_juego: gameState.toJSON()
            });

            res.status(201).json({
                success: true,
                data: {
                    partida: {
                        id: partida.id,
                        jugador1_id: partida.jugador1_id,
                        jugador2_id: partida.jugador2_id,
                        estado: partida.estado,
                        turnoActual: gameState.turnoActual,
                        fase: gameState.fase
                    },
                    gameState: this._filtrarEstadoParaJugador(gameState, userId),
                    ws: {
                        url: buildWsUrl(partida.id),
                        path: WS_PATH,
                        gameId: partida.id
                    }
                }
            });
        } catch (error) {
            console.error('❌ Error creando partida:', error);
            console.error('Stack trace:', error.stack);
            res.status(500).json({
                success: false,
                error: error.message,
                stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
            });
        }
    }

    /**
     * Inicializa una partida con los mazos dados
     */
    _inicializarPartida(mazo1, mazo2, jugador1Id, jugador2Id) {
        const gameState = new GameState(jugador1Id, jugador2Id);

        // Inicializar AbilityManager para esta partida (opcional, puede fallar si no está completamente implementado)
        try {
            this.abilityManager = new AbilityManager(gameState);
            console.log('✅ AbilityManager inicializado');
        } catch (error) {
            console.warn('⚠️ No se pudo inicializar AbilityManager:', error.message);
            console.warn('Stack:', error.stack);
            this.abilityManager = null;
        }
        
        // EventSystem es opcional por ahora (no se usa aún)
        try {
            // const eventSystem = new EventSystem(); // No se usa aún
        } catch (error) {
            console.warn('⚠️ No se pudo inicializar EventSystem:', error.message);
        }

        // Cargar cartas de los mazos
        const cartas1 = this._cargarCartasDelMazo(mazo1);
        const cartas2 = this._cargarCartasDelMazo(mazo2);
        
        console.log(`🔍 cartas1 después de _cargarCartasDelMazo:`, {
            tipo: typeof cartas1,
            esArray: Array.isArray(cartas1),
            longitud: Array.isArray(cartas1) ? cartas1.length : 'N/A'
        });
        console.log(`🔍 cartas2 después de _cargarCartasDelMazo:`, {
            tipo: typeof cartas2,
            esArray: Array.isArray(cartas2),
            longitud: Array.isArray(cartas2) ? cartas2.length : 'N/A'
        });

        // Separar oro inicial de cada mazo
        const resultado1 = this._separarOroInicial(cartas1, mazo1.oro_inicial_id);
        const resultado2 = this._separarOroInicial(cartas2, mazo2.oro_inicial_id);
        
        console.log(`🔍 Resultado de _separarOroInicial 1:`, {
            oroInicial: resultado1.oroInicial ? resultado1.oroInicial.nombre : null,
            cartasRestantesTipo: typeof resultado1.cartasRestantes,
            cartasRestantesEsArray: Array.isArray(resultado1.cartasRestantes),
            cartasRestantesLength: Array.isArray(resultado1.cartasRestantes) ? resultado1.cartasRestantes.length : 'N/A',
            cartasRestantesValue: resultado1.cartasRestantes
        });
        console.log(`🔍 Resultado de _separarOroInicial 2:`, {
            oroInicial: resultado2.oroInicial ? resultado2.oroInicial.nombre : null,
            cartasRestantesTipo: typeof resultado2.cartasRestantes,
            cartasRestantesEsArray: Array.isArray(resultado2.cartasRestantes),
            cartasRestantesLength: Array.isArray(resultado2.cartasRestantes) ? resultado2.cartasRestantes.length : 'N/A'
        });
        console.log(`🔍 ¿Son el mismo objeto?`, resultado1 === resultado2);
        console.log(`🔍 ¿Son el mismo array?`, resultado1.cartasRestantes === resultado2.cartasRestantes);
        
        // Extraer valores directamente sin desestructuración para evitar problemas
        const oroInicial1 = resultado1.oroInicial;
        const cartasRestantes1 = resultado1.cartasRestantes;
        const oroInicial2 = resultado2.oroInicial;
        const cartasRestantes2 = resultado2.cartasRestantes;

        console.log(`🔍 Después de extracción directa:`);
        console.log(`   - resultado1.cartasRestantes:`, typeof resultado1.cartasRestantes, Array.isArray(resultado1.cartasRestantes), resultado1.cartasRestantes?.length);
        console.log(`   - cartasRestantes1:`, typeof cartasRestantes1, Array.isArray(cartasRestantes1), cartasRestantes1?.length);
        console.log(`   - resultado2.cartasRestantes:`, typeof resultado2.cartasRestantes, Array.isArray(resultado2.cartasRestantes), resultado2.cartasRestantes?.length);
        console.log(`   - cartasRestantes2:`, typeof cartasRestantes2, Array.isArray(cartasRestantes2), cartasRestantes2?.length);
        
        console.log(`🃏 Cartas restantes jugador 1: ${Array.isArray(cartasRestantes1) ? cartasRestantes1.length : 'NO ES ARRAY'}`);
        console.log(`🃏 Cartas restantes jugador 2: ${Array.isArray(cartasRestantes2) ? cartasRestantes2.length : 'NO ES ARRAY'}`);

        // Barajar los mazos (asegurar que son arrays)
        const mazo1Barajado = Array.isArray(cartasRestantes1) ? barajar([...cartasRestantes1]) : [];
        const mazo2Barajado = Array.isArray(cartasRestantes2) ? barajar([...cartasRestantes2]) : [];

        // Repartir cartas iniciales (8 cartas según reglas oficiales)
        const { mano: mano1, mazoRestante: mazo1Restante } = repartirCartasIniciales(mazo1Barajado, 8);
        const { mano: mano2, mazoRestante: mazo2Restante } = repartirCartasIniciales(mazo2Barajado, 8);

        // Obtener las claves internas de los jugadores (pueden ser diferentes si tienen el mismo ID)
        const jugadorKeys = Object.keys(gameState.jugadores);
        // Si ambos jugadores tienen el mismo ID, usar el índice para obtener la clave correcta
        const jugador1Key = gameState.getKeyPorId(jugador1Id, 0) || jugadorKeys[0];
        const jugador2Key = gameState.getKeyPorId(jugador2Id, jugador1Id === jugador2Id ? 1 : 0) || jugadorKeys[1];

        // Configurar estado inicial del jugador 1 (guardar solo IDs)
        gameState.jugadores[jugador1Key].mazo = mazo1Restante.map(c => c.id);
        gameState.jugadores[jugador1Key].mano = mano1.map(c => c.id);
        console.log(`📋 Jugador 1 (${jugador1Id}, key: ${jugador1Key}): ${mano1.length} cartas en mano, ${mazo1Restante.length} cartas en mazo`);
        console.log(`📋 IDs de cartas en mano jugador 1:`, gameState.jugadores[jugador1Key].mano);
        if (oroInicial1) {
            gameState.jugadores[jugador1Key].reservaOro = [oroInicial1.id];
            gameState.jugadores[jugador1Key].recursosTotales = 1;
            gameState.jugadores[jugador1Key].recursos = 1;
            console.log(`🟡 Oro inicial jugador 1: ${oroInicial1.nombre} (${oroInicial1.id})`);
        }

        // Configurar estado inicial del jugador 2 (guardar solo IDs)
        gameState.jugadores[jugador2Key].mazo = mazo2Restante.map(c => c.id);
        gameState.jugadores[jugador2Key].mano = mano2.map(c => c.id);
        console.log(`📋 Jugador 2 (${jugador2Id}, key: ${jugador2Key}): ${mano2.length} cartas en mano, ${mazo2Restante.length} cartas en mazo`);
        console.log(`📋 IDs de cartas en mano jugador 2:`, gameState.jugadores[jugador2Key].mano);
        if (oroInicial2) {
            gameState.jugadores[jugador2Key].reservaOro = [oroInicial2.id];
            gameState.jugadores[jugador2Key].recursosTotales = 1;
            gameState.jugadores[jugador2Key].recursos = 1;
            console.log(`🟡 Oro inicial jugador 2: ${oroInicial2.nombre} (${oroInicial2.id})`);
        }
        
        // Verificar estado final antes de retornar
        console.log(`✅ Estado final del GameState:`);
        console.log(`   - Jugador 1 mano:`, gameState.jugadores[jugador1Key].mano);
        console.log(`   - Jugador 2 mano:`, gameState.jugadores[jugador2Key].mano);
        const estadoJSON = gameState.toJSON();
        console.log(`   - toJSON() jugador 1 mano:`, estadoJSON.jugadores[jugador1Key]?.mano);
        console.log(`   - toJSON() jugador 2 mano:`, estadoJSON.jugadores[jugador2Key]?.mano);

        // Procesar habilidades de las cartas iniciales
        this._procesarHabilidadesCartas(mano1.concat(mano2).concat(oroInicial1 ? [oroInicial1] : []).concat(oroInicial2 ? [oroInicial2] : []));

        // Ajustar estado inicial: el primer jugador comienza en Reagrupar
        gameState.fase = 'reagrupar';
        this._aplicarFaseReagrupar(gameState);

        return gameState;
    }

    /**
     * Carga las cartas de un mazo desde la BD
     */
    _cargarCartasDelMazo(mazo) {
        const cartaIds = Array.isArray(mazo.cartas) ? mazo.cartas : JSON.parse(mazo.cartas || '[]');
        const cartas = [];
        
        console.log(`📦 Cargando mazo "${mazo.nombre}" con ${cartaIds.length} cartas`);

        let cartasEncontradas = 0;
        let cartasNoEncontradas = 0;

        for (const cartaId of cartaIds) {
            if (!cartaId) {
                console.warn(`⚠️ ID de carta vacío o inválido`);
                cartasNoEncontradas++;
                continue;
            }

            const cartaData = this.cardRepo.buscarPorId(cartaId);
            if (cartaData) {
                const carta = Carta.fromJSON(cartaData);
                cartas.push(carta);
                cartasEncontradas++;
            } else {
                console.warn(`⚠️ Carta no encontrada en BD: ${cartaId} (tipo: ${typeof cartaId})`);
                cartasNoEncontradas++;
            }
        }
        
        if (cartas.length === 0 && cartaIds.length > 0) {
            console.error(`❌ ERROR: No se encontró ninguna carta del mazo. Verificar configuración de BD.`);
            console.error(`   - BD de cartas: ${this.cardRepo.dbPath}`);
            console.error(`   - Primeros 5 IDs buscados: ${cartaIds.slice(0, 5).join(', ')}`);
        }

        console.log(`✅ Cartas cargadas: ${cartasEncontradas} encontradas, ${cartasNoEncontradas} no encontradas`);
        console.log(`🔍 _cargarCartasDelMazo retornando:`, {
            tipo: typeof cartas,
            esArray: Array.isArray(cartas),
            longitud: Array.isArray(cartas) ? cartas.length : 'N/A',
            primerElemento: cartas.length > 0 ? (cartas[0] ? cartas[0].id : 'undefined') : 'array vacío'
        });
        
        if (cartasNoEncontradas > 0) {
            console.warn(`⚠️ Atención: ${cartasNoEncontradas} cartas del mazo no se encontraron en la base de datos`);
        }

        // Asegurar que siempre retornamos un array
        return Array.isArray(cartas) ? cartas : [];
    }

    /**
     * Separa el oro inicial del resto de cartas
     */
    _separarOroInicial(cartas, oroInicialId) {
        // Asegurar que cartas es un array
        console.log(`🔍 _separarOroInicial recibió:`, {
            tipo: typeof cartas,
            esArray: Array.isArray(cartas),
            longitud: Array.isArray(cartas) ? cartas.length : 'N/A',
            oroInicialId: oroInicialId
        });
        
        if (!Array.isArray(cartas)) {
            console.error('❌ ERROR: _separarOroInicial recibió algo que no es un array:', typeof cartas, cartas);
            return { oroInicial: null, cartasRestantes: [] };
        }

        const oroInicialIndex = cartas.findIndex(c => c && c.id === oroInicialId);
        let oroInicial = null;
        let cartasRestantes = [...cartas]; // Crear copia del array

        console.log(`🔍 Índice del oro inicial: ${oroInicialIndex}, Total cartas: ${cartas.length}`);

        if (oroInicialIndex >= 0) {
            oroInicial = cartasRestantes.splice(oroInicialIndex, 1)[0];
            console.log(`🟡 Oro inicial separado: ${oroInicial ? oroInicial.nombre : 'NO ENCONTRADO'} (${oroInicialId})`);
            console.log(`🔍 Cartas restantes después de separar oro: ${cartasRestantes.length}`);
        } else {
            console.warn(`⚠️ Oro inicial no encontrado en el mazo: ${oroInicialId}`);
        }

        console.log(`🔍 Retornando:`, {
            oroInicial: oroInicial ? oroInicial.nombre : null,
            cartasRestantesLength: cartasRestantes.length,
            cartasRestantesEsArray: Array.isArray(cartasRestantes)
        });

        // Asegurar que retornamos un array nuevo (no una referencia)
        const cartasRestantesFinal = Array.isArray(cartasRestantes) ? [...cartasRestantes] : [];
        console.log(`🔍 Array final a retornar:`, {
            tipo: typeof cartasRestantesFinal,
            esArray: Array.isArray(cartasRestantesFinal),
            longitud: cartasRestantesFinal.length
        });

        return { oroInicial, cartasRestantes: cartasRestantesFinal };
    }

    /**
     * Procesa las habilidades de un conjunto de cartas
     */
    _procesarHabilidadesCartas(cartas) {
        if (!this.abilityManager) {
            console.warn('⚠️ AbilityManager no disponible, saltando procesamiento de habilidades');
            return;
        }

        try {
            cartas.forEach(carta => {
                if (carta && typeof carta.processAbilities === 'function') {
                    carta.processAbilities(this.abilityManager);
                }
            });
        } catch (error) {
            console.warn('⚠️ Error procesando habilidades de cartas:', error.message);
        }
    }

    /**
     * Obtiene el estado de una partida
     */
    async getGame(req, res) {
        try {
            const { id } = req.params;
            const userId = req.user?.userId;

            const partida = this.gameRepo.buscarPorId(id);
            if (!partida) {
                return res.status(404).json({
                    success: false,
                    error: 'Partida no encontrada'
                });
            }

            // Verificar que el usuario es parte de la partida
            if (partida.jugador1_id !== userId && partida.jugador2_id !== userId) {
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para ver esta partida'
                });
            }

            // Cargar GameState desde BD
            const gameState = this._cargarGameState(partida.estado_juego, partida.jugador1_id, partida.jugador2_id);

            res.json({
                success: true,
                data: {
                    partida: {
                        id: partida.id,
                        estado: partida.estado,
                        turnos: partida.turnos
                    },
                    gameState: this._filtrarEstadoParaJugador(gameState, userId),
                    ws: {
                        url: buildWsUrl(partida.id),
                        path: WS_PATH,
                        gameId: partida.id
                    }
                }
            });
        } catch (error) {
            console.error('Error obteniendo partida:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Carga un GameState desde JSON
     */
    _cargarGameState(estadoJson, jugador1Id, jugador2Id) {
        const gameState = new GameState(jugador1Id, jugador2Id);
        
        if (estadoJson) {
            // Copiar propiedades del estado guardado
            gameState.turnoActual = estadoJson.turnoActual || jugador1Id;
            gameState.fase = estadoJson.fase || 'reagrupar';
            gameState.turnoNumero = estadoJson.turnoNumero || 1;
            gameState.ganador = estadoJson.ganador || null;
            gameState.finalizado = estadoJson.finalizado || false;
            gameState.jugadorInicialKey = estadoJson.jugadorInicialKey || gameState.jugadorInicialKey;
            gameState.oroJugadoEnTurno = estadoJson.oroJugadoEnTurno || gameState.oroJugadoEnTurno;
            gameState.roboInicialSaltado = estadoJson.roboInicialSaltado || false;
            gameState.mulligans = estadoJson.mulligans || gameState.mulligans;
            gameState.mulliganListo = estadoJson.mulliganListo || gameState.mulliganListo;
            gameState.mulliganCompletado = estadoJson.mulliganCompletado || false;
            
            // Copiar estados de jugadores
            if (estadoJson.jugadores) {
                Object.keys(estadoJson.jugadores).forEach(jugadorId => {
                    if (gameState.jugadores[jugadorId]) {
                        Object.assign(gameState.jugadores[jugadorId], estadoJson.jugadores[jugadorId]);
                        if (!Array.isArray(gameState.jugadores[jugadorId].lineaAtaque)) {
                            gameState.jugadores[jugadorId].lineaAtaque = [];
                        }
                    }
                });
            }
        }

        // Asegurar que mulliganListo tenga claves para ambos jugadores
        const jugadorKeys = Object.keys(gameState.jugadores);
        gameState.mulliganListo = gameState.mulliganListo || {};
        jugadorKeys.forEach((key) => {
            if (typeof gameState.mulliganListo[key] !== 'boolean') {
                gameState.mulliganListo[key] = false;
            }
        });
        // Recalcular flag global
        gameState.estaMulliganCompletado();

        // Inicializar AbilityManager si no existe
        if (!this.abilityManager) {
            this.abilityManager = new AbilityManager(gameState);
        }

        return gameState;
    }

    /**
     * Realiza una acción en la partida
     */
    async performAction(req, res) {
        try {
            const { id } = req.params;
            const { accion, datos } = req.body;
            const userId = req.user?.userId;

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Debes estar autenticado'
                });
            }

            const response = await this._ejecutarAccionInterna(id, userId, accion, datos);

            if (!response.success) {
                return res.status(response.status || 400).json({
                    success: false,
                    error: response.error
                });
            }

            res.json({
                success: true,
                data: {
                    resultado: response.resultado,
                    gameState: response.gameStateFiltrado,
                    finalizado: response.finalizado,
                    ganador: response.ganador
                }
            });
        } catch (error) {
            console.error('Error realizando acción:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Roba una carta del mazo
     */
    _robarCarta(gameState) {
        if (gameState.fase !== 'final') {
            return { exito: false, error: 'Solo puedes robar al inicio de la Fase Final' };
        }

        return this._robarEnFaseFinal(gameState);
    }

    /**
     * Juega una carta
     */
    _jugarCarta(gameState, datos) {
        const { carta_id, objetivo_id, posicion } = datos;
        const { jugador, key: jugadorKey } = gameState.getJugadorEnTurno();
        if (!jugador) {
            return { exito: false, error: 'Jugador no encontrado' };
        }

        // Buscar carta en la mano
        const indiceCarta = jugador.mano.indexOf(carta_id);
        if (indiceCarta === -1) {
            return { exito: false, error: 'La carta no está en tu mano' };
        }

        // Cargar datos de la carta
        const cartaData = this.cardRepo.buscarPorId(carta_id);
        if (!cartaData) {
            return { exito: false, error: 'Carta no encontrada' };
        }

        const carta = Carta.fromJSON(cartaData);
        carta.processAbilities(this.abilityManager);

        const esOro = carta.esOro();
        const esTalisman = carta.tipo === 'Talisman';
        const fase = gameState.fase;

        // Validar fase según tipo de carta
        const faseValida = esOro
            ? fase === 'comienzo_vigilia'
            : esTalisman
                ? (fase === 'vigilia' || fase === 'batalla')
                : fase === 'vigilia';

        if (!faseValida) {
            return {
                exito: false,
                error: esOro
                    ? 'Solo puedes bajar un Oro en la Fase de Comienzo de Vigilia'
                    : 'Solo puedes jugar cartas en Vigilia (Talismanes también en Batalla)'
            };
        }

        // Reglas de oro inicial / oro por turno
        if (esOro && gameState.oroJugadoEnTurno[jugadorKey]) {
            return { exito: false, error: 'Solo puedes jugar un Oro por turno' };
        }

        // Verificar recursos (los oros no tienen coste)
        if (!esOro && jugador.recursos < carta.coste) {
            return { exito: false, error: 'No tienes suficientes recursos' };
        }

        // Pagar coste si aplica
        if (!esOro) {
            jugador.recursos -= carta.coste;
        }

        // Remover de la mano
        jugador.mano.splice(indiceCarta, 1);

        // Colocar carta según su tipo
        if (esOro) {
            jugador.reservaOro.push(carta_id);
            gameState.oroJugadoEnTurno[jugadorKey] = true;
            gameState.calcularRecursosTotales(jugadorKey);
        } else if (carta.tipo === 'Aliado') {
            jugador.lineaDefensa.push(carta_id);
        } else if (carta.tipo === 'Totem' || carta.tipo === 'Arma') {
            jugador.lineaApoyo.push(carta_id);
        } else if (carta.tipo === 'Talisman') {
            // Los talismanes se juegan y van al cementerio
            jugador.cementerio.push(carta_id);
        }

        // Activar habilidades "enters_play"
        const entersPlayAbilities = carta.getAbilitiesByTrigger('enters_play');
        entersPlayAbilities.forEach(ability => {
            if (this.abilityManager) {
                this.abilityManager.execute(ability, {
                    card: carta,
                    player: jugadorKey,
                    gameState: gameState
                });
            }
        });

        return {
            exito: true,
            mensaje: `Carta ${carta.nombre} jugada correctamente`,
            carta: carta_id,
            tipo: carta.tipo
        };
    }

    /**
     * Ataca con un aliado
     */
    _atacar(gameState, datos) {
        if (gameState.fase !== 'batalla') {
            return { exito: false, error: 'Solo puedes atacar en la fase de batalla' };
        }

        const { atacante_id, objetivo_id } = datos;
        const { jugador, key: jugadorKey } = gameState.getJugadorEnTurno();
        if (!jugador) {
            return { exito: false, error: 'Jugador no encontrado' };
        }
        const oponente = gameState.getOponente();

        const yaAtaco = jugador.lineaAtaque.includes(atacante_id);
        const enDefensa = jugador.lineaDefensa.includes(atacante_id);

        // Verificar que el atacante está disponible y no atacó antes
        if (!enDefensa && !yaAtaco) {
            return { exito: false, error: 'El aliado no está disponible para atacar' };
        }
        if (yaAtaco) {
            return { exito: false, error: 'Ese aliado ya atacó este turno' };
        }

        // Mover el aliado a la línea de ataque para dejar constancia
        const indexEnDefensa = jugador.lineaDefensa.indexOf(atacante_id);
        if (indexEnDefensa >= 0) {
            jugador.lineaDefensa.splice(indexEnDefensa, 1);
        }
        jugador.lineaAtaque.push(atacante_id);

        // Cargar carta atacante
        const atacanteData = this.cardRepo.buscarPorId(atacante_id);
        if (!atacanteData) {
            return { exito: false, error: 'Carta atacante no encontrada' };
        }

        const atacante = Carta.fromJSON(atacanteData);

        // Si el objetivo es otro aliado
        if (objetivo_id && oponente.lineaDefensa.includes(objetivo_id)) {
            const objetivoData = this.cardRepo.buscarPorId(objetivo_id);
            if (!objetivoData) {
                return { exito: false, error: 'Carta objetivo no encontrada' };
            }

            const objetivo = Carta.fromJSON(objetivoData);

            // Aplicar daño mutuo
            const atacanteDestruido = atacante.recibirDano(objetivo.fuerza);
            const objetivoDestruido = objetivo.recibirDano(atacante.fuerza);

            // Mover a cementerio si están destruidos
            if (atacanteDestruido) {
                const index = jugador.lineaAtaque.indexOf(atacante_id);
                if (index >= 0) {
                    jugador.lineaAtaque.splice(index, 1);
                }
                jugador.cementerio.push(atacante_id);
            }

            if (objetivoDestruido) {
                const index = oponente.lineaDefensa.indexOf(objetivo_id);
                oponente.lineaDefensa.splice(index, 1);
                oponente.cementerio.push(objetivo_id);
            }

            return {
                exito: true,
                mensaje: 'Combate resuelto',
                atacanteDestruido,
                objetivoDestruido
            };
        } else {
            // Ataque directo al Castillo
            const daño = atacante.fuerza;
            const cartasADescartar = Math.min(daño, oponente.mazo.length);
            
            for (let i = 0; i < cartasADescartar; i++) {
                oponente.cementerio.push(oponente.mazo.shift());
            }

            return {
                exito: true,
                mensaje: `Ataque directo al Castillo: ${cartasADescartar} cartas descartadas`,
                daño: cartasADescartar
            };
        }
    }

    /**
     * Aplica los efectos obligatorios de la fase de Reagrupar
     * - Recupera recursos según la cantidad de Oros
     * - Devuelve los aliados que atacaron a la Línea de Defensa
     * - Resetea el control de oro jugado en el turno
     */
    _aplicarFaseReagrupar(gameState) {
        const { jugador, key } = gameState.getJugadorEnTurno();
        if (!jugador) {
            return { exito: false, error: 'Jugador no encontrado en Reagrupar' };
        }

        // Devolver aliados de ataque a defensa
        if (!Array.isArray(jugador.lineaAtaque)) {
            jugador.lineaAtaque = [];
        }
        if (jugador.lineaAtaque.length > 0) {
            jugador.lineaDefensa.push(...jugador.lineaAtaque);
            jugador.lineaAtaque = [];
        }

        // Recuperar recursos
        gameState.calcularRecursosTotales(key);

        // Permitir jugar un oro nuevamente
        if (gameState.oroJugadoEnTurno) {
            gameState.oroJugadoEnTurno[key] = false;
        }

        return { exito: true, mensaje: 'Fase de Reagrupar aplicada' };
    }

    /**
     * Gestiona el robo en la Fase Final respetando la excepción del primer turno
     */
    _robarEnFaseFinal(gameState) {
        const { jugador, key } = gameState.getJugadorEnTurno();
        if (!jugador) {
            return { exito: false, error: 'Jugador no encontrado' };
        }

        const esPrimerTurnoDelInicial =
            !gameState.roboInicialSaltado &&
            gameState.turnoNumero === 1 &&
            gameState.turnoActual === gameState.getJugadorInicialKey();

        if (esPrimerTurnoDelInicial) {
            gameState.roboInicialSaltado = true;
            return {
                exito: true,
                mensaje: 'Primer turno del jugador inicial: no roba carta'
            };
        }

        if (jugador.mazo.length === 0) {
            const ganadorKey = Object.keys(gameState.jugadores).find(j => j !== key);
            gameState.ganador = ganadorKey ? (gameState.jugadores[ganadorKey]?.id || ganadorKey) : null;
            gameState.finalizado = true;
            return {
                exito: true,
                mensaje: 'No puedes robar: tu mazo está vacío. Pierdes la partida.',
                finPartida: true
            };
        }

        const carta = jugador.mazo.shift();
        jugador.mano.push(carta);

        return {
            exito: true,
            mensaje: 'Robas 1 carta al final del turno',
            requiereDescarte: jugador.mano.length > 8,
            cartasEnMano: jugador.mano.length
        };
    }

    /**
     * Ejecuta mulligan (solo al inicio de la partida).
     * Primer mulligan: 7 cartas, segundo: 6, tercero: 5 (límite 3).
     */
    _mulligan(gameState, userId) {
        const playerKey = gameState.getKeyPorId(userId);
        if (!playerKey) {
            return { exito: false, error: 'Jugador no encontrado' };
        }

        if (gameState.turnoNumero !== 1 || gameState.finalizado) {
            return { exito: false, error: 'El mulligan solo se puede realizar en el turno 1 antes de finalizar' };
        }

        const actual = gameState.mulligans?.[playerKey] || 0;
        if (gameState.mulliganListo?.[playerKey]) {
            return { exito: false, error: 'Ya confirmaste tu mano, no puedes hacer más mulligan' };
        }

        const jugador = gameState.jugadores[playerKey];
        if (!jugador) {
            return { exito: false, error: 'Estado de jugador no disponible' };
        }

        const mazoActual = Array.isArray(jugador.mazo) ? jugador.mazo : [];
        const manoActual = Array.isArray(jugador.mano) ? jugador.mano : [];

        // Regresar la mano al mazo y barajar
        const mazoConMano = barajar([...mazoActual, ...manoActual]);

        // Calcular nuevo tamaño de mano: 8 - mulliganIndex, mínimo 1
        const nuevoTamano = Math.max(1, 8 - (actual + 1));
        const nuevaMano = mazoConMano.slice(0, nuevoTamano);
        const mazoRestante = mazoConMano.slice(nuevoTamano);

        jugador.mano = nuevaMano;
        jugador.mazo = mazoRestante;

        gameState.mulligans[playerKey] = actual + 1;
        // Al hacer mulligan, ese jugador aún no ha confirmado y el proceso global sigue abierto
        if (!gameState.mulliganListo) gameState.mulliganListo = {};
        gameState.mulliganListo[playerKey] = false;
        gameState.mulliganCompletado = false;

        return {
            exito: true,
            mensaje: `Mulligan ${actual + 1}: nueva mano de ${nuevoTamano} cartas`
        };
    }

    /**
     * Confirma que el jugador mantiene su mano actual y cierra su mulligan
     */
    _confirmarMano(gameState, userId) {
        const playerKey = gameState.getKeyPorId(userId);
        if (!playerKey) {
            return { exito: false, error: 'Jugador no encontrado' };
        }

        if (gameState.turnoNumero !== 1 || gameState.finalizado) {
            return { exito: false, error: 'Solo puedes confirmar la mano al inicio de la partida' };
        }

        gameState.mulliganListo = gameState.mulliganListo || {};
        if (gameState.mulliganListo[playerKey]) {
            return { exito: true, mensaje: 'Ya confirmaste tu mano' };
        }

        gameState.mulliganListo[playerKey] = true;
        const completado = gameState.estaMulliganCompletado();

        return {
            exito: true,
            mensaje: completado
                ? 'Ambos jugadores confirmaron su mano. ¡Comienza la partida!'
                : 'Mano confirmada. Espera a que tu oponente termine su mulligan.',
            mulliganCompletado: completado
        };
    }

    /**
     * Pasa a la siguiente fase
     */
    _pasarFase(gameState) {
        const fases = ['reagrupar', 'comienzo_vigilia', 'vigilia', 'batalla', 'final'];
        const faseActual = gameState.fase;
        const indiceActual = fases.indexOf(faseActual);

        if (indiceActual === -1 || indiceActual === fases.length - 1) {
            return { exito: false, error: 'No se puede pasar de esta fase' };
        }

        // Aplicar acciones automáticas de la fase actual antes de avanzar
        if (faseActual === 'reagrupar') {
            this._aplicarFaseReagrupar(gameState);
        }

        const siguienteFase = fases[indiceActual + 1];
        gameState.fase = siguienteFase;

        // Acciones automáticas al entrar a ciertas fases
        if (siguienteFase === 'final') {
            return this._robarEnFaseFinal(gameState);
        }

        return { exito: true, mensaje: `Fase cambiada a ${siguienteFase}` };
    }

    /**
     * Pasa el turno
     */
    _pasarTurno(gameState) {
        if (gameState.fase !== 'final') {
            return { exito: false, error: 'Debes llegar a la fase final antes de pasar el turno' };
        }

        // Cambiar turno
        gameState.siguienteTurno();
        gameState.fase = 'reagrupar';

        // Aplicar Reagrupar automáticamente al inicio del turno del nuevo jugador
        this._aplicarFaseReagrupar(gameState);

        return { exito: true, mensaje: 'Turno pasado. Fase: Reagrupar' };
    }

    /**
     * Filtra el estado del juego para mostrar solo lo que el jugador puede ver
     */
    _filtrarEstadoParaJugador(gameState, jugadorId) {
        // Clonar profundamente para no mutar el estado original al filtrar
        const estadoCompleto = JSON.parse(JSON.stringify(gameState.toJSON()));
        
        // Obtener las claves internas de los jugadores
        const jugadorKeys = Object.keys(estadoCompleto.jugadores);
        
        // Si hay múltiples jugadores con el mismo ID, el jugador que creó la partida es siempre el primero (índice 0)
        // El jugador actual (quien hace la petición) siempre es el jugador 1
        const miKey = gameState.getKeyPorId(jugadorId, 0) || jugadorKeys.find(key => estadoCompleto.jugadores[key]?.id === jugadorId) || jugadorKeys[0];
        const oponenteKey = jugadorKeys.find(key => key !== miKey) || jugadorKeys[1];

        console.log(`🔍 Filtrando estado para jugador ${jugadorId} (key: ${miKey})`);
        console.log(`🔍 Claves disponibles:`, jugadorKeys);
        console.log(`🔍 Mi clave: ${miKey}, Clave oponente: ${oponenteKey}`);

        // Ocultar mano del oponente (solo mostrar cantidad)
        if (oponenteKey && estadoCompleto.jugadores[oponenteKey]) {
            const manoOponente = estadoCompleto.jugadores[oponenteKey].mano;
            estadoCompleto.jugadores[oponenteKey].mano = Array.isArray(manoOponente) ? manoOponente.length : manoOponente;
        }

        // Asegurar que la mano del jugador se mantiene como array
        if (miKey && estadoCompleto.jugadores[miKey]) {
            const miMano = estadoCompleto.jugadores[miKey].mano;
            console.log(`🔍 Mano del jugador ${jugadorId} (key: ${miKey}) antes de verificar:`, miMano, `Tipo:`, typeof miMano, `Es array:`, Array.isArray(miMano));
            if (!Array.isArray(miMano)) {
                console.warn(`⚠️ La mano del jugador no es un array:`, miMano);
                estadoCompleto.jugadores[miKey].mano = [];
            } else {
                console.log(`✅ Mano del jugador ${jugadorId} tiene ${miMano.length} cartas:`, miMano);
            }
        } else {
            console.error(`❌ No se encontró el jugador ${jugadorId} en el estado`);
        }

        return estadoCompleto;
    }

    /**
     * Finaliza una partida
     */
    async endGame(req, res) {
        try {
            const { id } = req.params;
            const userId = req.user?.userId;

            const partida = this.gameRepo.buscarPorId(id);
            if (!partida) {
                return res.status(404).json({
                    success: false,
                    error: 'Partida no encontrada'
                });
            }

            if (partida.estado === 'finalizada') {
                return res.status(400).json({
                    success: false,
                    error: 'La partida ya está finalizada'
                });
            }

            // Marcar como abandonada
            const partidaActualizada = this.gameRepo.actualizarPartida(id, {
                estado: 'abandonada',
                resultado: 'abandono',
                fecha_fin: new Date().toISOString()
            });

            res.json({
                success: true,
                data: partidaActualizada
            });
        } catch (error) {
            console.error('Error finalizando partida:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Lista las partidas de un usuario
     */
    async listGames(req, res) {
        try {
            const userId = req.user?.userId;

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Debes estar autenticado'
                });
            }

            const { estado, limite, offset } = req.query;
            const partidas = this.gameRepo.listarPorUsuario(userId, {
                estado,
                limite: limite ? parseInt(limite) : undefined,
                offset: offset ? parseInt(offset) : undefined
            });

            res.json({
                success: true,
                count: partidas.length,
                data: partidas.map((p) => ({
                    ...p,
                    ws: {
                        url: buildWsUrl(p.id),
                        path: WS_PATH,
                        gameId: p.id
                    }
                }))
            });
        } catch (error) {
            console.error('Error listando partidas:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

/**
 * Métodos de soporte para WebSocket y reutilización de lógica sin Express
 */
GameController.prototype._ejecutarAccionInterna = async function (gameId, userId, accion, datos) {
    const partida = this.gameRepo.buscarPorId(gameId);
    if (!partida) {
        return { success: false, status: 404, error: 'Partida no encontrada' };
    }

    if (partida.estado !== 'en_curso') {
        return { success: false, status: 400, error: 'La partida no está en curso' };
    }

    // Cargar estado
    const gameState = this._cargarGameState(partida.estado_juego, partida.jugador1_id, partida.jugador2_id);

    // Verificar turno
    const jugadorEnTurno = gameState.getJugadorEnTurno();
    const esTurnoDelUsuario = jugadorEnTurno.jugador && jugadorEnTurno.jugador.id === userId;
    const esAccionMulligan = accion === 'mulligan' || accion === 'confirmar_mano';
    // Mulligan y confirmación se permiten para ambos jugadores al inicio, aun si no es su turno
    if (!esTurnoDelUsuario && !esAccionMulligan) {
        return { success: false, status: 403, error: 'No es tu turno' };
    }

    // Bloquear cualquier acción distinta a mulligan/confirmar mientras el mulligan no esté cerrado para ambos
    if (!gameState.estaMulliganCompletado() && !esAccionMulligan) {
        return { success: false, status: 400, error: 'El mulligan no ha finalizado para ambos jugadores' };
    }

    // Ejecutar acción
    let resultado;
    switch (accion) {
        case 'robar_carta':
            resultado = this._robarCarta(gameState);
            break;
        case 'jugar_carta':
            resultado = this._jugarCarta(gameState, datos);
            break;
        case 'atacar':
            resultado = this._atacar(gameState, datos);
            break;
        case 'pasar_fase':
            resultado = this._pasarFase(gameState);
            break;
        case 'pasar_turno':
            resultado = this._pasarTurno(gameState);
            break;
        case 'mulligan':
            resultado = this._mulligan(gameState, userId);
            break;
        case 'confirmar_mano':
            resultado = this._confirmarMano(gameState, userId);
            break;
        default:
            return { success: false, status: 400, error: `Acción no reconocida: ${accion}` };
    }

    if (!resultado.exito) {
        return { success: false, status: 400, error: resultado.error };
    }

    // Verificar ganador
    const ganador = gameState.verificarGanador();
    if (ganador) {
        this.gameRepo.finalizarPartida(
            gameId,
            ganador,
            ganador === userId ? 'victoria' : 'derrota',
            gameState.turnoNumero
        );
        partida.estado = 'finalizada';
    }

    // Guardar estado
    this.gameRepo.actualizarPartida(gameId, {
        estado_juego: gameState.toJSON(),
        turnos: gameState.turnoNumero
    });

    return {
        success: true,
        resultado,
        gameStateFiltrado: this._filtrarEstadoParaJugador(gameState, userId),
        gameState, // estado completo para difusión controlada
        finalizado: !!ganador,
        ganador
    };
};

/**
 * Crea una partida desde el lobby (sin Express)
 */
GameController.prototype.createGameForLobby = async function (player1Id, player2Id, deck1Id, deck2Id) {
    try {
        if (!player1Id || !player2Id) {
            return { success: false, error: 'Jugadores requeridos' };
        }
        if (!deck1Id || !deck2Id) {
            return { success: false, error: 'Decks requeridos' };
        }

        const mazo1 = this.deckRepo.buscarPorId(deck1Id);
        const mazo2 = this.deckRepo.buscarPorId(deck2Id);

        if (!mazo1) {
            return { success: false, error: 'Mazo del jugador 1 no encontrado' };
        }
        if (!mazo2) {
            return { success: false, error: 'Mazo del jugador 2 no encontrado' };
        }

        if (mazo1.usuario_id && mazo1.usuario_id !== player1Id && !mazo1.es_publico) {
            return { success: false, error: 'El mazo del jugador 1 no pertenece al usuario' };
        }
        if (mazo2.usuario_id && mazo2.usuario_id !== player2Id && !mazo2.es_publico) {
            return { success: false, error: 'El mazo del jugador 2 no pertenece al usuario' };
        }

        const gameState = this._inicializarPartida(mazo1, mazo2, player1Id, player2Id);
        const partida = this.gameRepo.crearPartida({
            jugador1_id: player1Id,
            jugador2_id: player2Id,
            mazo1_id: deck1Id,
            mazo2_id: deck2Id,
            estado_juego: gameState.toJSON()
        });

        return {
            success: true,
            data: {
                partida,
                gameState,
                filteredStates: {
                    [player1Id]: this._filtrarEstadoParaJugador(gameState, player1Id),
                    [player2Id]: this._filtrarEstadoParaJugador(gameState, player2Id)
                }
            }
        };
    } catch (error) {
        console.error('Error creando partida desde lobby:', error);
        return { success: false, error: error.message };
    }
};

GameController.prototype.obtenerEstadoParaJugador = function (gameId, userId) {
    const partida = this.gameRepo.buscarPorId(gameId);
    if (!partida) {
        return { success: false, status: 404, error: 'Partida no encontrada' };
    }

    if (partida.jugador1_id !== userId && partida.jugador2_id !== userId) {
        return { success: false, status: 403, error: 'No tienes permiso para ver esta partida' };
    }

    const gameState = this._cargarGameState(partida.estado_juego, partida.jugador1_id, partida.jugador2_id);
    return {
        success: true,
        gameState,
        gameStateFiltrado: this._filtrarEstadoParaJugador(gameState, userId),
        partida
    };
};

module.exports = new GameController();
