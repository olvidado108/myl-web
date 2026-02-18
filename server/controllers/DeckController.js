const DeckRepository = require('../repository/DeckRepository');
const DeckValidator = require('../utils/deckValidator');
const CardRepositorySQLite = require('../repository/CardRepositorySQLite');

class DeckController {
    constructor() {
        this.deckRepo = new DeckRepository();
        this.cardRepo = new CardRepositorySQLite();
        this.validator = new DeckValidator(this.cardRepo);
    }

    /**
     * Lista los mazos del usuario actual con estadísticas
     */
    async listDecks(req, res) {
        try {
            const userId = req.user?.userId;
            
            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Debes estar autenticado para ver tus mazos'
                });
            }

            const mazos = this.deckRepo.listarPorUsuarioConEstadisticas(userId);
            res.json({
                success: true,
                count: mazos.length,
                data: mazos
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Obtiene un mazo específico
     */
    async getDeck(req, res) {
        try {
            const { id } = req.params;
            const mazo = this.deckRepo.buscarPorId(id);

            if (!mazo) {
                return res.status(404).json({
                    success: false,
                    error: 'Mazo no encontrado'
                });
            }

            // Verificar permisos (solo el dueño o mazos públicos)
            const userId = req.user?.userId;
            if (mazo.usuario_id !== userId && !mazo.es_publico) {
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para ver este mazo'
                });
            }

            res.json({
                success: true,
                data: mazo
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Crea un nuevo mazo
     */
    async createDeck(req, res) {
        try {
            const userId = req.user?.userId;
            
            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Debes estar autenticado para crear mazos'
                });
            }

            const {
                nombre,
                descripcion,
                formato,
                raza,
                edicion_original,
                cartas,
                oro_inicial_id,
                es_publico = false
            } = req.body;

            if (!nombre) {
                return res.status(400).json({
                    success: false,
                    error: 'El nombre del mazo es requerido'
                });
            }

            const mazoData = {
                usuario_id: userId,
                nombre,
                descripcion,
                formato,
                raza,
                edicion_original,
                cartas: cartas || [],
                oro_inicial_id,
                es_publico
            };

            // Validar mazo si tiene cartas
            if (mazoData.cartas.length > 0) {
                const validacion = this.validator.validarMazoCompleto(mazoData, formato);
                if (!validacion.valido) {
                    return res.status(400).json({
                        success: false,
                        error: 'El mazo no es válido',
                        detalles: validacion.errores
                    });
                }
            }

            const mazo = this.deckRepo.crearMazo(mazoData);

            res.status(201).json({
                success: true,
                data: mazo
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Actualiza un mazo
     */
    async updateDeck(req, res) {
        try {
            const { id } = req.params;
            const userId = req.user?.userId;

            const mazo = this.deckRepo.buscarPorId(id);
            if (!mazo) {
                return res.status(404).json({
                    success: false,
                    error: 'Mazo no encontrado'
                });
            }

            // Verificar permisos
            if (mazo.usuario_id !== userId) {
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para actualizar este mazo'
                });
            }

            const datosActualizacion = req.body;

            // Si se actualizan las cartas, validar el mazo completo
            if (datosActualizacion.cartas !== undefined) {
                const mazoActualizado = {
                    ...mazo,
                    ...datosActualizacion
                };
                const validacion = this.validator.validarMazoCompleto(
                    mazoActualizado,
                    datosActualizacion.formato || mazo.formato
                );
                if (!validacion.valido) {
                    return res.status(400).json({
                        success: false,
                        error: 'El mazo no es válido',
                        detalles: validacion.errores
                    });
                }
            }

            const mazoActualizado = this.deckRepo.actualizarMazo(id, datosActualizacion);

            res.json({
                success: true,
                data: mazoActualizado
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Elimina un mazo
     */
    async deleteDeck(req, res) {
        try {
            const { id } = req.params;
            const userId = req.user?.userId;

            const mazo = this.deckRepo.buscarPorId(id);
            if (!mazo) {
                return res.status(404).json({
                    success: false,
                    error: 'Mazo no encontrado'
                });
            }

            // Verificar permisos
            if (mazo.usuario_id !== userId) {
                return res.status(403).json({
                    success: false,
                    error: 'No tienes permiso para eliminar este mazo'
                });
            }

            const eliminado = this.deckRepo.eliminarMazo(id);
            if (!eliminado) {
                return res.status(500).json({
                    success: false,
                    error: 'Error al eliminar el mazo'
                });
            }

            res.json({
                success: true,
                message: 'Mazo eliminado correctamente'
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Valida un mazo sin guardarlo
     */
    async validateDeck(req, res) {
        try {
            const mazo = req.body;
            const formato = mazo.formato || 'Racial Edición';

            const validacion = this.validator.validarMazoCompleto(mazo, formato);

            res.json({
                success: true,
                valido: validacion.valido,
                errores: validacion.errores || []
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new DeckController();











