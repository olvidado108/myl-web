const UserRepository = require('../repository/UserRepository');
const { generarToken } = require('../utils/jwtUtils');
const { validarFortalezaPassword } = require('../utils/passwordUtils');

class AuthController {
    constructor() {
        this.userRepo = new UserRepository();
    }

    async register(req, res) {
        try {
            const { username, email, password, nombre_completo } = req.body;

            // Validaciones básicas
            if (!username || !email || !password) {
                return res.status(400).json({
                    success: false,
                    error: 'Username, email y password son requeridos'
                });
            }

            // Validar formato de email básico
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                return res.status(400).json({
                    success: false,
                    error: 'Email inválido'
                });
            }

            // Validar fortaleza de contraseña
            const validacionPassword = validarFortalezaPassword(password);
            if (!validacionPassword.valida) {
                return res.status(400).json({
                    success: false,
                    error: validacionPassword.errores.join(', ')
                });
            }

            // Validar username (al menos 3 caracteres, solo alfanuméricos y guiones bajos)
            if (username.length < 3) {
                return res.status(400).json({
                    success: false,
                    error: 'El username debe tener al menos 3 caracteres'
                });
            }

            if (!/^[a-zA-Z0-9_]+$/.test(username)) {
                return res.status(400).json({
                    success: false,
                    error: 'El username solo puede contener letras, números y guiones bajos'
                });
            }

            // Crear usuario
            const usuario = await this.userRepo.crearUsuario({
                username,
                email,
                password,
                nombre_completo
            });

            // Generar token
            const token = generarToken({
                userId: usuario.id,
                username: usuario.username,
                isAdmin: usuario.isAdmin || false
            });

            res.status(201).json({
                success: true,
                data: {
                    user: {
                        id: usuario.id,
                        username: usuario.username,
                        email: usuario.email,
                        nombre_completo: usuario.nombre_completo,
                        nivel: usuario.nivel,
                        experiencia: usuario.experiencia,
                        isAdmin: usuario.isAdmin || false
                    },
                    token
                }
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }

    async login(req, res) {
        try {
            const { username, password } = req.body;

            if (!username || !password) {
                return res.status(400).json({
                    success: false,
                    error: 'Username y password son requeridos'
                });
            }

            const usuario = await this.userRepo.verificarPassword(username, password);
            if (!usuario) {
                return res.status(401).json({
                    success: false,
                    error: 'Credenciales inválidas'
                });
            }

            // Verificar que el usuario esté activo
            if (!usuario.activo) {
                return res.status(403).json({
                    success: false,
                    error: 'Usuario inactivo'
                });
            }

            // Generar token
            const token = generarToken({
                userId: usuario.id,
                username: usuario.username,
                isAdmin: usuario.isAdmin || false
            });

            res.json({
                success: true,
                data: {
                    user: {
                        id: usuario.id,
                        username: usuario.username,
                        email: usuario.email,
                        nombre_completo: usuario.nombre_completo,
                        nivel: usuario.nivel,
                        experiencia: usuario.experiencia,
                        isAdmin: usuario.isAdmin || false
                    },
                    token
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    async me(req, res) {
        try {
            const usuario = this.userRepo.buscarPorId(req.user.userId);
            if (!usuario) {
                return res.status(404).json({
                    success: false,
                    error: 'Usuario no encontrado'
                });
            }

            res.json({
                success: true,
                data: usuario
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new AuthController();




