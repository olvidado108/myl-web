const express = require('express');
const http = require('http');
const path = require('path');
const CardRepositorySQLite = require('./repository/CardRepositorySQLite');
const { buscarImagenesCartas } = require('./utils/imageUtils');
const { initGameSocket } = require('./ws/gameSocket');
const authRoutes = require('./routes/auth');

const app = express();
const server = http.createServer(app);
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos
app.use(express.static(path.join(__dirname, '../public')));

// Inicializar repositorio de cartas
const cardRepository = new CardRepositorySQLite();
console.log(`📚 Base de datos SQLite cargada: ${cardRepository.contarCartas()} cartas`);

// Limpieza inicial de habilidades
try {
    const resultado = cardRepository.limpiarYNormalizarHabilidades();
    console.log(`📊 Resultado de limpieza: ${resultado.limpiados} limpiados, ${resultado.sincronizadas} sincronizadas`);
} catch (error) {
    console.warn('⚠️  Advertencia al limpiar habilidades:', error.message);
}

// Sincronizar habilidades entre cartas homónimas
function sincronizarHabilidades(cartas) {
    const normalizarHabilidad = (texto) => {
        if (!texto || texto === 'NaN' || texto === 'null' || texto.trim() === '') {
            return null;
        }
        return texto.trim();
    };

    const cartasPorNombre = {};
    cartas.forEach(carta => {
        let nombreNormalizado = (carta.nombre || '').toLowerCase().trim();
        nombreNormalizado = nombreNormalizado.replace(/\s*\(variante\)\s*$/i, '').trim();
        if (!cartasPorNombre[nombreNormalizado]) cartasPorNombre[nombreNormalizado] = [];
        cartasPorNombre[nombreNormalizado].push(carta);
    });

    Object.values(cartasPorNombre).forEach(grupo => {
        if (grupo.length <= 1) return;
        let habilidadComun = null;
        for (const carta of grupo) {
            const habilidad = normalizarHabilidad(carta.textoHabilidad);
            if (habilidad) { habilidadComun = habilidad; break; }
        }
        if (habilidadComun) {
            grupo.forEach(carta => {
                const hab = normalizarHabilidad(carta.textoHabilidad);
                if (!hab) carta.textoHabilidad = habilidadComun;
            });
        }
    });
    return cartas;
}

// ==================== API ENDPOINTS ====================
app.use('/api/auth', authRoutes);
app.use('/api/users', require('./routes/users'));
app.use('/api/decks', require('./routes/decks'));
app.use('/api/games', require('./routes/games'));

// Cartas
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
        const cartasConImagenes = buscarImagenesCartas(cartas);
        const cartasSincronizadas = sincronizarHabilidades(cartasConImagenes);
        res.json({ success: true, count: cartasSincronizadas.length, data: cartasSincronizadas });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/cards/missing-abilities', (req, res) => {
    try {
        const { limite } = req.query;
        const filtros = limite ? { limite: parseInt(limite) } : {};
        const cartas = cardRepository.buscarSinHabilidad(filtros);
        const cartasConImagenes = buscarImagenesCartas(cartas);
        res.json({ success: true, count: cartasConImagenes.length, data: cartasConImagenes });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

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

app.post('/api/cards/:id/verify', (req, res) => {
    try {
        const ok = cardRepository.marcarVerificada(req.params.id, true);
        res.json({ success: ok });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.post('/api/cards/:id/unverify', (req, res) => {
    try {
        const ok = cardRepository.marcarVerificada(req.params.id, false);
        res.json({ success: ok });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/tags', (req, res) => {
    try {
        const tags = cardRepository.listarTags();
        res.json({ success: true, count: tags.length, data: tags });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

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

app.post('/api/cards/:id/tags/confirm', (req, res) => {
    try {
        const changes = cardRepository.confirmarTagsDeCarta(req.params.id);
        res.json({ success: true, updated: changes });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/cards/:id', (req, res) => {
    try {
        const carta = cardRepository.buscarPorId(req.params.id);
        if (!carta) {
            return res.status(404).json({ success: false, error: 'Carta no encontrada' });
        }
        const { buscarImagenCarta } = require('./utils/imageUtils');
        const imagenUrl = buscarImagenCarta(carta);
        if (imagenUrl) {
            const cartaConImagen = { ...carta, imagenUrl };
            const todasLasCartas = cardRepository.obtenerTodas();
            const cartasSincronizadas = sincronizarHabilidades([...todasLasCartas, cartaConImagen]);
            const cartaSincronizada = cartasSincronizadas.find(c => c.id === carta.id) || cartaConImagen;
            return res.json({ success: true, data: cartaSincronizada });
        }
        const imagenUrlBD = carta.imagenUrl;
        let imagenUrlFinal = null;
        if (imagenUrlBD) {
            const esUrlLocal = imagenUrlBD.startsWith('/images/') ||
                imagenUrlBD.startsWith('images/') ||
                (!imagenUrlBD.startsWith('http://') && !imagenUrlBD.startsWith('https://'));
            if (esUrlLocal) {
                imagenUrlFinal = imagenUrlBD.startsWith('/') ? imagenUrlBD : `/images/${imagenUrlBD}`;
            }
        }
        const cartaConImagen = { ...carta, imagenUrl: imagenUrlFinal };
        const todasLasCartas = cardRepository.obtenerTodas();
        const cartasSincronizadas = sincronizarHabilidades([...todasLasCartas, cartaConImagen]);
        const cartaSincronizada = cartasSincronizadas.find(c => c.id === carta.id) || cartaConImagen;
        res.json({ success: true, data: cartaSincronizada });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.post('/api/cards', (req, res) => {
    try {
        const carta = req.body;
        if (!carta.id || !carta.nombre || !carta.tipo) {
            return res.status(400).json({ success: false, error: 'La carta debe tener id, nombre y tipo' });
        }
        if (cardRepository.buscarPorId(carta.id)) {
            return res.status(409).json({ success: false, error: 'Ya existe una carta con ese ID' });
        }
        const cartaGuardada = cardRepository.guardarCarta(carta);
        res.status(201).json({ success: true, data: cartaGuardada });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.put('/api/cards/:id', (req, res) => {
    try {
        const id = req.params.id;
        const cartaActualizada = req.body;
        if (!cardRepository.buscarPorId(id)) {
            return res.status(404).json({ success: false, error: 'Carta no encontrada' });
        }
        cartaActualizada.id = id;
        const carta = cardRepository.guardarCarta(cartaActualizada);
        res.json({ success: true, data: carta });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.delete('/api/cards/:id', (req, res) => {
    try {
        const id = req.params.id;
        if (!cardRepository.eliminarCarta(id)) {
            return res.status(404).json({ success: false, error: 'Carta no encontrada' });
        }
        res.json({ success: true, message: 'Carta eliminada correctamente' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/stats', (req, res) => {
    try {
        const stats = cardRepository.obtenerEstadisticas();
        res.json({ success: true, data: stats });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.post('/api/cards/clean-abilities', (req, res) => {
    try {
        const resultado = cardRepository.limpiarYNormalizarHabilidades();
        res.json({
            success: true,
            message: 'Habilidades limpiadas y sincronizadas correctamente',
            data: resultado
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ==================== RUTAS DE PÁGINA ====================
app.get('/', (req, res) => res.sendFile(path.join(__dirname, '../public/index.html')));
app.get('/cards', (req, res) => res.sendFile(path.join(__dirname, '../public/cards.html')));
app.get('/missing-abilities', (req, res) => res.sendFile(path.join(__dirname, '../public/missing-abilities.html')));
app.get('/login', (req, res) => res.sendFile(path.join(__dirname, '../public/login.html')));
app.get('/register', (req, res) => res.sendFile(path.join(__dirname, '../public/register.html')));
app.get('/profile', (req, res) => res.sendFile(path.join(__dirname, '../public/profile.html')));
app.get('/decks', (req, res) => res.sendFile(path.join(__dirname, '../public/decks.html')));
app.get('/deck-builder', (req, res) => res.sendFile(path.join(__dirname, '../public/deck-builder.html')));
app.get('/deck-view', (req, res) => res.sendFile(path.join(__dirname, '../public/deck-view.html')));
app.get('/game', (req, res) => res.sendFile(path.join(__dirname, '../public/game.html')));
app.get('/lobby', (req, res) => res.sendFile(path.join(__dirname, '../public/lobby.html')));

// Cerrar base de datos al terminar
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

// WebSocket
initGameSocket(server);



