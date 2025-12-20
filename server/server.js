const express = require('express');
const http = require('http');
const path = require('path');
// Usar SQLite en lugar de JSON
const CardRepositorySQLite = require('./repository/CardRepositorySQLite');
const { buscarImagenesCartas } = require('./utils/imageUtils');
const { initGameSocket } = require('./ws/gameSocket');
// Rutas de autenticación
const authRoutes = require('./routes/auth');

const app = express();
const server = http.createServer(app);
const PORT = process.env.PORT || 3000;

// Middleware para parsear JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos desde la carpeta public
app.use(express.static(path.join(__dirname, '../public')));

// Inicializar repositorio de cartas (SQLite)
const cardRepository = new CardRepositorySQLite();
console.log(`📚 Base de datos SQLite cargada: ${cardRepository.contarCartas()} cartas`);

// Limpiar y normalizar habilidades al iniciar (solo una vez, se puede desactivar después)
// Ejecutar la limpieza automáticamente al iniciar el servidor
try {
    const resultado = cardRepository.limpiarYNormalizarHabilidades();
    console.log(`📊 Resultado de limpieza: ${resultado.limpiados} limpiados, ${resultado.sincronizadas} sincronizadas`);
} catch (error) {
    console.warn('⚠️  Advertencia al limpiar habilidades:', error.message);
}

/**
 * Sincroniza las habilidades entre cartas con el mismo nombre
 * Si una carta tiene textoHabilidad válido, se aplica a todas las demás con el mismo nombre
 */
function sincronizarHabilidades(cartas) {
    // Normalizar textoHabilidad: convertir "NaN", null, undefined, o strings vacíos a null
    const normalizarHabilidad = (texto) => {
        if (!texto || texto === 'NaN' || texto === 'null' || texto.trim() === '') {
            return null;
        }
        return texto.trim();
    };

    // Agrupar cartas por nombre (case-insensitive, manejar variantes)
    const cartasPorNombre = {};
    cartas.forEach(carta => {
        // Normalizar nombre: remover "(Variante)" y espacios extra
        let nombreNormalizado = (carta.nombre || '').toLowerCase().trim();
        // Remover "(variante)" o "(Variante)" del nombre para agrupar correctamente
        nombreNormalizado = nombreNormalizado.replace(/\s*\(variante\)\s*$/i, '').trim();
        
        if (!cartasPorNombre[nombreNormalizado]) {
            cartasPorNombre[nombreNormalizado] = [];
        }
        cartasPorNombre[nombreNormalizado].push(carta);
    });

    // Para cada grupo de cartas con el mismo nombre, sincronizar habilidades
    Object.values(cartasPorNombre).forEach(grupo => {
        if (grupo.length <= 1) return; // No hay nada que sincronizar si solo hay una carta

        // Encontrar la habilidad más completa (no vacía, no NaN)
        let habilidadComun = null;
        for (const carta of grupo) {
            const habilidad = normalizarHabilidad(carta.textoHabilidad);
            if (habilidad) {
                habilidadComun = habilidad;
                break; // Usar la primera habilidad válida encontrada
            }
        }

        // Si encontramos una habilidad común, aplicarla a todas las cartas del grupo
        if (habilidadComun) {
            grupo.forEach(carta => {
                const habilidadActual = normalizarHabilidad(carta.textoHabilidad);
                if (!habilidadActual) {
                    carta.textoHabilidad = habilidadComun;
                }
            });
        }
    });

    return cartas;
}

// ==================== API ENDPOINTS ====================

// Rutas de autenticación
app.use('/api/auth', authRoutes);

// Rutas de usuarios
const userRoutes = require('./routes/users');
app.use('/api/users', userRoutes);

// Rutas de mazos
const deckRoutes = require('./routes/decks');
app.use('/api/decks', deckRoutes);

// Rutas de partidas
const gameRoutes = require('./routes/games');
app.use('/api/games', gameRoutes);

// GET /api/cards - Obtener todas las cartas (con filtros opcionales)
app.get('/api/cards', (req, res) => {
    try {
        const { tipo, raza, edicion, nombre, limite } = req.query;
        
        let cartas;
        if (tipo || raza || edicion || nombre) {
            const filtros = {};
            if (tipo) filtros.tipo = tipo;
            if (raza) filtros.raza = raza;
            if (edicion) filtros.edicion = edicion;
            if (nombre) filtros.nombre = nombre;
            if (limite) filtros.limite = parseInt(limite);
            
            cartas = cardRepository.buscar(filtros);
        } else {
            cartas = cardRepository.obtenerTodas();
        }
        
        // Agregar URLs de imágenes a las cartas
        const cartasConImagenes = buscarImagenesCartas(cartas);
        
        // Sincronizar habilidades entre cartas con el mismo nombre
        const cartasSincronizadas = sincronizarHabilidades(cartasConImagenes);
        
        res.json({
            success: true,
            count: cartasSincronizadas.length,
            data: cartasSincronizadas
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET /api/cards/missing-abilities - Obtener cartas sin habilidad
// IMPORTANTE: Esta ruta debe estar ANTES de /api/cards/:id para evitar conflictos
app.get('/api/cards/missing-abilities', (req, res) => {
    try {
        const { limite } = req.query;
        // No limitar por defecto, o usar un límite muy alto para obtener todas las cartas sin habilidad
        const filtros = limite ? { limite: parseInt(limite) } : {};
        
        // Usar el método específico que busca directamente en SQL por cartas sin habilidad
        const cartas = cardRepository.buscarSinHabilidad(filtros);
        
        // Agregar URLs de imágenes
        const cartasConImagenes = buscarImagenesCartas(cartas);
        
        res.json({
            success: true,
            count: cartasConImagenes.length,
            data: cartasConImagenes
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET /api/tag-suggestions - Cartas con tags sugeridos (suggested=1)
app.get('/api/tag-suggestions', (req, res) => {
    try {
        const limite = req.query.limite ? parseInt(req.query.limite) : 50;
        const offset = req.query.offset ? parseInt(req.query.offset) : 0;
        const search = req.query.search || null;
        const data = cardRepository.obtenerCartasConTagsSugeridos({ limite, offset, search });
        res.json({ success: true, count: data.length, data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// POST /api/cards/:id/verify - Marca carta verificada
app.post('/api/cards/:id/verify', (req, res) => {
    try {
        const ok = cardRepository.marcarVerificada(req.params.id, true);
        res.json({ success: ok });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// POST /api/cards/:id/unverify - Desmarca carta verificada
app.post('/api/cards/:id/unverify', (req, res) => {
    try {
        const ok = cardRepository.marcarVerificada(req.params.id, false);
        res.json({ success: ok });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// GET /api/tags - Listar catálogo de tags
app.get('/api/tags', (req, res) => {
    try {
        const tags = cardRepository.listarTags();
        res.json({ success: true, count: tags.length, data: tags });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// POST /api/tags - Crear/actualizar tag
app.post('/api/tags', (req, res) => {
    try {
        const { slug, nombre, categoria = null, descripcion = null } = req.body;
        if (!slug || !nombre) {
            return res.status(400).json({ success: false, error: 'slug y nombre son obligatorios' });
        }
        const tag = cardRepository.crearOActualizarTag({ slug, nombre, categoria, descripcion });
        res.json({ success: true, data: tag });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// POST /api/cards/:id/tags - Asignar tag a carta
app.post('/api/cards/:id/tags', (req, res) => {
    try {
        const { tag, suggested = 0 } = req.body;
        if (!tag) {
            return res.status(400).json({ success: false, error: 'tag (slug o id) es requerido' });
        }
        cardRepository.asignarTagACarta(tag, req.params.id, suggested ? 1 : 0);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// POST /api/cards/:id/tags/confirm - Confirmar todos los tags (quitar suggested)
app.post('/api/cards/:id/tags/confirm', (req, res) => {
    try {
        const changes = cardRepository.confirmarTagsDeCarta(req.params.id);
        res.json({ success: true, updated: changes });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// GET /api/cards/:id - Obtener una carta por ID
app.get('/api/cards/:id', (req, res) => {
    try {
        const carta = cardRepository.buscarPorId(req.params.id);
        
        if (!carta) {
            return res.status(404).json({
                success: false,
                error: 'Carta no encontrada'
            });
        }
        
        // Agregar URL de imagen
        const { buscarImagenCarta } = require('./utils/imageUtils');
        const imagenUrl = buscarImagenCarta(carta);
        
        // Si encontramos una imagen local, usarla
        if (imagenUrl) {
            const cartaConImagen = {
                ...carta,
                imagenUrl: imagenUrl
            };
            
            // Sincronizar habilidad con otras cartas del mismo nombre
            const todasLasCartas = cardRepository.obtenerTodas();
            const cartasSincronizadas = sincronizarHabilidades([...todasLasCartas, cartaConImagen]);
            const cartaSincronizada = cartasSincronizadas.find(c => c.id === carta.id) || cartaConImagen;
            
            return res.json({
                success: true,
                data: cartaSincronizada
            });
        }
        
        // Si no hay imagen local, verificar si imagenUrl de la BD es local
        const imagenUrlBD = carta.imagenUrl;
        let imagenUrlFinal = null;
        
        if (imagenUrlBD) {
            // Solo usar si es una ruta local (empieza con /images/ o images/)
            // NO usar URLs externas (http:// o https://)
            const esUrlLocal = imagenUrlBD.startsWith('/images/') || 
                              imagenUrlBD.startsWith('images/') ||
                              (!imagenUrlBD.startsWith('http://') && !imagenUrlBD.startsWith('https://'));
            
            if (esUrlLocal) {
                imagenUrlFinal = imagenUrlBD.startsWith('/') ? imagenUrlBD : `/images/${imagenUrlBD}`;
            }
        }
        
        const cartaConImagen = {
            ...carta,
            imagenUrl: imagenUrlFinal
        };
        
        // Sincronizar habilidad con otras cartas del mismo nombre
        const todasLasCartas = cardRepository.obtenerTodas();
        const cartasSincronizadas = sincronizarHabilidades([...todasLasCartas, cartaConImagen]);
        const cartaSincronizada = cartasSincronizadas.find(c => c.id === carta.id) || cartaConImagen;
        
        res.json({
            success: true,
            data: cartaSincronizada
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /api/cards - Crear una nueva carta
app.post('/api/cards', (req, res) => {
    try {
        const carta = req.body;
        
        // Validaciones básicas
        if (!carta.id || !carta.nombre || !carta.tipo) {
            return res.status(400).json({
                success: false,
                error: 'La carta debe tener id, nombre y tipo'
            });
        }
        
        // Verificar si ya existe
        if (cardRepository.buscarPorId(carta.id)) {
            return res.status(409).json({
                success: false,
                error: 'Ya existe una carta con ese ID'
            });
        }
        
        // Guardar la carta (SQLite guarda automáticamente)
        const cartaGuardada = cardRepository.guardarCarta(carta);
        
        res.status(201).json({
            success: true,
            data: cartaGuardada
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// PUT /api/cards/:id - Actualizar una carta
app.put('/api/cards/:id', (req, res) => {
    try {
        const id = req.params.id;
        const cartaActualizada = req.body;
        
        // Verificar que existe
        if (!cardRepository.buscarPorId(id)) {
            return res.status(404).json({
                success: false,
                error: 'Carta no encontrada'
            });
        }
        
        // Asegurar que el ID coincida
        cartaActualizada.id = id;
        
        // Actualizar la carta (SQLite guarda automáticamente)
        const carta = cardRepository.guardarCarta(cartaActualizada);
        
        res.json({
            success: true,
            data: carta
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// DELETE /api/cards/:id - Eliminar una carta
app.delete('/api/cards/:id', (req, res) => {
    try {
        const id = req.params.id;
        
        if (!cardRepository.eliminarCarta(id)) {
            return res.status(404).json({
                success: false,
                error: 'Carta no encontrada'
            });
        }
        
        res.json({
            success: true,
            message: 'Carta eliminada correctamente'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET /api/stats - Obtener estadísticas
app.get('/api/stats', (req, res) => {
    try {
        const stats = cardRepository.obtenerEstadisticas();
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
});

// POST /api/cards/clean-abilities - Limpiar y normalizar habilidades en la base de datos
app.post('/api/cards/clean-abilities', (req, res) => {
    try {
        const resultado = cardRepository.limpiarYNormalizarHabilidades();
        res.json({
            success: true,
            message: 'Habilidades limpiadas y sincronizadas correctamente',
            data: resultado
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Ruta principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Ruta para el CRUD de cartas
app.get('/cards', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/cards.html'));
});

// Ruta para cartas sin habilidad
app.get('/missing-abilities', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/missing-abilities.html'));
});

// Rutas de autenticación
app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/login.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/register.html'));
});

// Rutas de usuarios
app.get('/profile', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/profile.html'));
});

app.get('/decks', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/decks.html'));
});

app.get('/deck-builder', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/deck-builder.html'));
});

app.get('/deck-view', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/deck-view.html'));
});

app.get('/game', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/game.html'));
});

// Cerrar base de datos al terminar el proceso
process.on('SIGINT', () => {
    console.log('\n🛑 Cerrando servidor...');
    if (cardRepository) {
        cardRepository.cerrar();
    }
    process.exit(0);
});

// Iniciar servidor
server.listen(PORT, () => {
    console.log(`🚀 Servidor iniciado en http://localhost:${PORT}`);
    console.log(`📁 Sirviendo archivos desde: ${path.join(__dirname, '../public')}`);
    console.log(`🃏 Gestión de cartas: http://localhost:${PORT}/cards`);
    console.log(`💾 Usando base de datos SQLite: ${cardRepository.dbPath}`);
});

// Inicializar WebSocket para partidas
initGameSocket(server);

