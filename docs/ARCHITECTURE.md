# 🏗️ Arquitectura del Proyecto

## Principios Arquitectónicos

### 1. API-First Architecture ⭐ **CRÍTICO**

**TODAS las funcionalidades del servidor deben exponerse como APIs REST.**

#### ¿Por qué?
- ✅ **Multiplataforma**: La misma API sirve para web, Android, iOS, y futuros clientes
- ✅ **Separación de responsabilidades**: Lógica de negocio en el servidor, UI en el cliente
- ✅ **Escalabilidad**: Fácil escalar el backend sin afectar clientes
- ✅ **Mantenibilidad**: Cambios en un solo lugar
- ✅ **Testing**: Probar APIs independientemente de la UI

#### Regla de Oro:
> **NUNCA** implementar lógica directamente en el cliente web.  
> **SIEMPRE** crear endpoints REST en el servidor.  
> El cliente web es solo un consumidor más de la API.

#### Ejemplos:

❌ **INCORRECTO:**
```javascript
// En el cliente (public/client.js)
const cartas = JSON.parse(fs.readFileSync('cards.json')); // ❌ No funciona en navegador
const carta = cartas.find(c => c.id === id); // ❌ Lógica en cliente
```

✅ **CORRECTO:**
```javascript
// En el servidor (server/routes/cards.js)
app.get('/api/cards/:id', (req, res) => {
    const carta = cardRepository.buscarPorId(req.params.id);
    res.json(carta);
});

// En el cliente (public/client.js)
fetch('/api/cards/es559')
    .then(res => res.json())
    .then(carta => console.log(carta));
```

### 2. Estructura de APIs

Todas las APIs deben seguir este patrón:

```
/api/[recurso]/[accion]
```

**Ejemplos:**
- `GET /api/cards` - Listar cartas
- `GET /api/cards/:id` - Obtener carta por ID
- `GET /api/cards/search?tipo=Aliado&raza=Caballero` - Búsqueda
- `POST /api/game/start` - Iniciar partida
- `POST /api/game/:id/play-card` - Jugar carta
- `GET /api/game/:id/state` - Estado de partida

### 3. Formato de Respuestas

Todas las respuestas deben seguir este formato:

```json
{
    "success": true,
    "data": { ... },
    "error": null,
    "message": "Operación exitosa"
}
```

En caso de error:
```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "CARD_NOT_FOUND",
        "message": "Carta no encontrada"
    }
}
```

### 4. Códigos HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado
- `400 Bad Request` - Error de validación
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## Estructura de Carpetas

```
server/
├── routes/           # Rutas de API (REST endpoints)
│   ├── cards.js      # API de cartas
│   ├── game.js       # API de juego
│   └── decks.js      # API de mazos
├── controllers/      # Lógica de negocio
│   ├── CardController.js
│   └── GameController.js
├── repository/       # Acceso a datos
│   └── CardRepository.js
├── models/          # Modelos de datos
│   ├── Card.js
│   └── GameState.js
└── middleware/      # Middleware (auth, validación, etc.)
    └── errorHandler.js
```

## Flujo de Datos

```
Cliente (Web/Android/iOS)
    ↓ HTTP Request
API Endpoint (routes/)
    ↓
Controller (controllers/)
    ↓
Repository (repository/)
    ↓
Datos (JSON/DB)
```

## Ejemplo Completo

### 1. Definir Endpoint (routes/cards.js)
```javascript
const express = require('express');
const router = express.Router();
const CardController = require('../controllers/CardController');

router.get('/:id', CardController.getById);
router.get('/search', CardController.search);

module.exports = router;
```

### 2. Implementar Lógica (controllers/CardController.js)
```javascript
const CardRepository = require('../repository/CardRepository');

class CardController {
    static getById(req, res) {
        const carta = CardRepository.buscarPorId(req.params.id);
        if (carta) {
            res.json({ success: true, data: carta });
        } else {
            res.status(404).json({ 
                success: false, 
                error: { code: 'CARD_NOT_FOUND' } 
            });
        }
    }
}
```

### 3. Registrar en Servidor (server.js)
```javascript
app.use('/api/cards', require('./routes/cards'));
```

### 4. Consumir desde Cliente
```javascript
// Web
fetch('/api/cards/es559').then(res => res.json());

// Android (Kotlin)
val response = client.get("/api/cards/es559")
```

## Checklist para Nuevas Funcionalidades

Antes de implementar cualquier funcionalidad, verificar:

- [ ] ¿Existe un endpoint REST para esto?
- [ ] ¿La lógica está en el servidor, no en el cliente?
- [ ] ¿El formato de respuesta es consistente?
- [ ] ¿Los códigos HTTP son correctos?
- [ ] ¿Hay manejo de errores?
- [ ] ¿Está documentado?

## Documentación de APIs

Todas las APIs deben estar documentadas. Usar:
- Comentarios JSDoc en el código
- Archivo `API_DOCUMENTATION.md` con ejemplos
- Considerar Swagger/OpenAPI en el futuro

## Futuras Consideraciones

- **Autenticación**: Cuando se implemente, usar JWT tokens
- **Rate Limiting**: Limitar requests por IP/usuario
- **Caching**: Cachear respuestas frecuentes (Redis)
- **WebSockets**: Para tiempo real (ya tenemos Socket.IO)
- **Versionado**: `/api/v1/cards` para futuras versiones

---

**Última actualización:** 2025-12-12




