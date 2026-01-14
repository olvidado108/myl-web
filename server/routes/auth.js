const express = require('express');
const router = express.Router();
const authController = require('../controllers/AuthController');
const { authenticateToken } = require('../middleware/auth');

// POST /api/auth/register - Registro de nuevo usuario
router.post('/register', authController.register.bind(authController));

// POST /api/auth/login - Inicio de sesión
router.post('/login', authController.login.bind(authController));

// GET /api/auth/me - Obtener información del usuario actual (requiere autenticación)
router.get('/me', authenticateToken, authController.me.bind(authController));

module.exports = router;









