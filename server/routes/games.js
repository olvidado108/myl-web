const express = require('express');
const router = express.Router();
const GameController = require('../controllers/GameController');
const { authenticateToken } = require('../middleware/auth');

/**
 * POST /api/games
 * Crea una nueva partida
 */
router.post('/', authenticateToken, GameController.createGame.bind(GameController));

/**
 * GET /api/games/:id
 * Obtiene el estado de una partida
 */
router.get('/:id', authenticateToken, GameController.getGame.bind(GameController));

/**
 * POST /api/games/:id/actions
 * Realiza una acción en la partida
 */
router.post('/:id/actions', authenticateToken, GameController.performAction.bind(GameController));

/**
 * POST /api/games/:id/end
 * Finaliza una partida
 */
router.post('/:id/end', authenticateToken, GameController.endGame.bind(GameController));

/**
 * GET /api/games
 * Lista las partidas del usuario
 */
router.get('/', authenticateToken, GameController.listGames.bind(GameController));

module.exports = router;

