const express = require('express');
const router = express.Router();
const userController = require('../controllers/UserController');
const { authenticateToken, optionalAuth, requireAdmin } = require('../middleware/auth');

// Rutas de administrador (deben ir antes de las rutas con parámetros)
// GET /api/users - Listar todos los usuarios (solo administradores)
router.get('/', authenticateToken, requireAdmin, userController.listAll.bind(userController));

// GET /api/users/:id - Obtener perfil de usuario
router.get('/:id', optionalAuth, userController.getProfile.bind(userController));

// PUT /api/users/:id - Actualizar perfil (requiere autenticación y ser el dueño)
router.put('/:id', authenticateToken, userController.updateProfile.bind(userController));

// PUT /api/users/:id/admin - Actualizar usuario como administrador (solo admins)
router.put('/:id/admin', authenticateToken, requireAdmin, userController.updateUser.bind(userController));

// GET /api/users/:id/stats - Obtener estadísticas de usuario
router.get('/:id/stats', optionalAuth, userController.getStats.bind(userController));

module.exports = router;











