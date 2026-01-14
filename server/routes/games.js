const express = require('express');
const GameController = require('../controllers/GameController');
const { authenticateToken } = require('../middleware/auth');
const router = express.Router();

// Todas las rutas de juegos requieren autenticación
router.use(authenticateToken);

// Crear partida
router.post('/', (req, res) => GameController.createGame(req, res));

// Obtener partida por ID
router.get('/:id', (req, res) => GameController.getGame(req, res));

// Listar partidas del usuario autenticado
router.get('/', (req, res) => GameController.listGames(req, res));

// Ejecutar acción en partida
router.post('/:id/action', (req, res) => GameController.playAction(req, res));

// Finalizar partida
router.post('/:id/end', (req, res) => GameController.endGame(req, res));

module.exports = router;
