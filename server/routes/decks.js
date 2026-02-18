const express = require('express');
const router = express.Router();
const deckController = require('../controllers/DeckController');
const { authenticateToken } = require('../middleware/auth');

// GET /api/decks - Listar mazos del usuario actual
router.get('/', authenticateToken, deckController.listDecks.bind(deckController));

// POST /api/decks - Crear nuevo mazo
router.post('/', authenticateToken, deckController.createDeck.bind(deckController));

// POST /api/decks/validate - Validar mazo sin guardarlo
router.post('/validate', authenticateToken, deckController.validateDeck.bind(deckController));

// GET /api/decks/:id - Obtener un mazo específico
router.get('/:id', authenticateToken, deckController.getDeck.bind(deckController));

// PUT /api/decks/:id - Actualizar un mazo
router.put('/:id', authenticateToken, deckController.updateDeck.bind(deckController));

// DELETE /api/decks/:id - Eliminar un mazo
router.delete('/:id', authenticateToken, deckController.deleteDeck.bind(deckController));

module.exports = router;











