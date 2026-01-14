const UserRepository = require('../repository/UserRepository');

class UserController {
    constructor() {
        this.userRepo = new UserRepository();
    }

    /**
     * Obtiene el perfil de un usuario
     */
    async getProfile(req, res) {
        try {
            const { id } = req.params;
            const currentUserId = req.user?.userId;

            // Solo puedes ver tu propio perfil completo, o perfiles públicos de otros
            const usuario = this.userRepo.buscarPorId(id);
            
            if (!usuario) {
                return res.status(404).json({
                    success: false,
                    error: 'Usuario no encontrado'
                });
            }

            // Si es el propio perfil, incluir email y más detalles
            if (id === currentUserId) {
                const stats = this.userRepo.obtenerEstadisticas(id);
                return res.json({
                    success: true,
                    data: {
                        ...usuario,
                        estadisticas: stats
                    }
                });
            }

            // Perfil público (sin email)
            const { email, ...perfilPublico } = usuario;
            res.json({
                success: true,
                data: perfilPublico
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Actualiza el perfil del usuario
     */
    async updateProfile(req, res) {
        try {
            const { id } = req.params;
            const currentUserId = req.user?.userId;

            // Solo puedes actualizar tu propio perfil
            if (id !== currentUserId) {
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para actualizar este perfil'
                });
            }

            const { nombre_completo, avatar_url } = req.body;
            const datosActualizacion = {};

            if (nombre_completo !== undefined) {
                datosActualizacion.nombre_completo = nombre_completo;
            }
            if (avatar_url !== undefined) {
                datosActualizacion.avatar_url = avatar_url;
            }

            const usuarioActualizado = this.userRepo.actualizarUsuario(id, datosActualizacion);

            res.json({
                success: true,
                data: usuarioActualizado
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Obtiene las estadísticas de un usuario
     */
    async getStats(req, res) {
        try {
            const { id } = req.params;
            const stats = this.userRepo.obtenerEstadisticas(id);

            if (!stats) {
                return res.status(404).json({
                    success: false,
                    error: 'Estadísticas no encontradas'
                });
            }

            res.json({
                success: true,
                data: stats
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Lista todos los usuarios (solo administradores)
     */
    async listAll(req, res) {
        try {
            const usuarios = this.userRepo.listarTodos();
            res.json({
                success: true,
                data: usuarios
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Actualiza un usuario (solo administradores pueden actualizar roles y estado)
     */
    async updateUser(req, res) {
        try {
            const { id } = req.params;
            const { nombre_completo, avatar_url, nivel, experiencia, activo, isAdmin } = req.body;
            const datosActualizacion = {};

            if (nombre_completo !== undefined) {
                datosActualizacion.nombre_completo = nombre_completo;
            }
            if (avatar_url !== undefined) {
                datosActualizacion.avatar_url = avatar_url;
            }
            if (nivel !== undefined) {
                datosActualizacion.nivel = nivel;
            }
            if (experiencia !== undefined) {
                datosActualizacion.experiencia = experiencia;
            }
            if (isAdmin !== undefined) {
                datosActualizacion.isAdmin = isAdmin;
            }

            if (activo !== undefined) {
                datosActualizacion.activo = activo;
            }

            const usuarioActualizado = this.userRepo.actualizarUsuario(id, datosActualizacion);

            if (!usuarioActualizado) {
                return res.status(404).json({
                    success: false,
                    error: 'Usuario no encontrado'
                });
            }

            res.json({
                success: true,
                data: usuarioActualizado
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new UserController();









