# 📋 Plan Completo: Módulo de Usuarios

## 🎯 Objetivo

Implementar un sistema completo de usuarios que permita:
- Autenticación (login/registro)
- Gestión de perfil de usuario
- Crear, editar, ver y eliminar mazos personalizados
- Ver cartas (con sesión de usuario)
- Estadísticas de juegos (jugados, ganados, perdidos, empatados)
- Puntuaciones y rankings
- Historial de partidas
- Y más funcionalidades relacionadas con usuarios

---

## 🗄️ 1. Base de Datos

### 1.1 Estructura de Tablas SQLite

#### Tabla: `usuarios`
```sql
CREATE TABLE usuarios (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre_completo TEXT,
    avatar_url TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME,
    activo BOOLEAN DEFAULT 1,
    nivel INTEGER DEFAULT 1,
    experiencia INTEGER DEFAULT 0
);
```

#### Tabla: `mazos` (Decks)
```sql
CREATE TABLE mazos (
    id TEXT PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    formato TEXT, -- 'Racial Edición', 'Racial Soporte Libre', etc.
    raza TEXT,
    edicion_original TEXT,
    cartas TEXT NOT NULL, -- JSON array de IDs de cartas
    oro_inicial_id TEXT, -- ID de la carta de oro inicial
    es_publico BOOLEAN DEFAULT 0,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    veces_usado INTEGER DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

#### Tabla: `partidas` (Games)
```sql
CREATE TABLE partidas (
    id TEXT PRIMARY KEY,
    jugador1_id TEXT NOT NULL,
    jugador2_id TEXT,
    mazo1_id TEXT,
    mazo2_id TEXT,
    estado TEXT NOT NULL, -- 'en_curso', 'finalizada', 'abandonada'
    ganador_id TEXT,
    resultado TEXT, -- 'victoria', 'derrota', 'empate', 'abandono'
    turnos INTEGER DEFAULT 0,
    duracion_segundos INTEGER,
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME,
    estado_juego TEXT, -- JSON del GameState completo
    FOREIGN KEY (jugador1_id) REFERENCES usuarios(id),
    FOREIGN KEY (jugador2_id) REFERENCES usuarios(id),
    FOREIGN KEY (mazo1_id) REFERENCES mazos(id),
    FOREIGN KEY (mazo2_id) REFERENCES mazos(id)
);
```

#### Tabla: `estadisticas_usuario`
```sql
CREATE TABLE estadisticas_usuario (
    usuario_id TEXT PRIMARY KEY,
    partidas_jugadas INTEGER DEFAULT 0,
    partidas_ganadas INTEGER DEFAULT 0,
    partidas_perdidas INTEGER DEFAULT 0,
    partidas_empatadas INTEGER DEFAULT 0,
    partidas_abandonadas INTEGER DEFAULT 0,
    puntos_totales INTEGER DEFAULT 0,
    racha_victorias INTEGER DEFAULT 0,
    mejor_racha_victorias INTEGER DEFAULT 0,
    cartas_jugadas_totales INTEGER DEFAULT 0,
    turnos_jugados_totales INTEGER DEFAULT 0,
    tiempo_jugado_segundos INTEGER DEFAULT 0,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

#### Tabla: `sesiones` (Para JWT tokens)
```sql
CREATE TABLE sesiones (
    id TEXT PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    activa BOOLEAN DEFAULT 1,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

#### Tabla: `favoritos` (Cartas favoritas del usuario)
```sql
CREATE TABLE favoritos (
    usuario_id TEXT NOT NULL,
    carta_id TEXT NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, carta_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

#### Índices para optimización:
```sql
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_mazos_usuario ON mazos(usuario_id);
CREATE INDEX idx_partidas_jugador1 ON partidas(jugador1_id);
CREATE INDEX idx_partidas_jugador2 ON partidas(jugador2_id);
CREATE INDEX idx_partidas_estado ON partidas(estado);
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX idx_sesiones_token ON sesiones(token_hash);
CREATE INDEX idx_favoritos_usuario ON favoritos(usuario_id);
```

---

## 🔐 2. Autenticación y Seguridad

### 2.1 Dependencias Necesarias

```json
{
  "bcrypt": "^5.1.1",  // Para hash de contraseñas
  "jsonwebtoken": "^9.0.2",  // Para JWT tokens
  "express-session": "^1.17.3",  // Opcional: sesiones
  "cookie-parser": "^1.4.6"  // Para cookies
}
```

### 2.2 Middleware de Autenticación

**Archivo: `server/middleware/auth.js`**
- Verificar JWT token
- Extraer usuario del token
- Proteger rutas que requieren autenticación

### 2.3 Endpoints de Autenticación

- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/refresh` - Renovar token
- `POST /api/auth/change-password` - Cambiar contraseña

---

## 📡 3. APIs REST - Usuarios

### 3.1 Endpoints de Usuario

#### `GET /api/users/:id`
Obtener perfil de usuario (público)

#### `GET /api/users/:id/stats`
Obtener estadísticas de un usuario

#### `PUT /api/users/:id`
Actualizar perfil (solo propio)

#### `GET /api/users/leaderboard`
Ranking de usuarios (top jugadores)

---

## 🃏 4. APIs REST - Mazos

### 4.1 Endpoints de Mazos

#### `GET /api/decks`
Listar mazos del usuario actual (o públicos si no hay sesión)

#### `GET /api/decks/:id`
Obtener un mazo específico

#### `POST /api/decks`
Crear nuevo mazo
- Validar reglas de construcción (50 cartas, oro inicial, etc.)
- Validar límites de copias

#### `PUT /api/decks/:id`
Actualizar mazo (solo propio)

#### `DELETE /api/decks/:id`
Eliminar mazo (solo propio)

#### `POST /api/decks/:id/validate`
Validar un mazo sin guardarlo

#### `GET /api/decks/:id/stats`
Estadísticas de uso de un mazo

#### `POST /api/decks/:id/duplicate`
Duplicar un mazo (propio o público)

---

## 🎮 5. APIs REST - Partidas y Estadísticas

### 5.1 Endpoints de Partidas

#### `POST /api/games`
Crear nueva partida
- Validar mazos
- Inicializar GameState

#### `GET /api/games/:id`
Obtener estado de partida

#### `POST /api/games/:id/actions`
Realizar acción en partida (jugar carta, atacar, etc.)

#### `POST /api/games/:id/end`
Finalizar partida
- Actualizar estadísticas de usuarios
- Guardar resultado

#### `GET /api/games`
Listar partidas del usuario
- Filtros: estado, fecha, oponente

#### `GET /api/games/:id/history`
Historial completo de una partida

### 5.2 Endpoints de Estadísticas

#### `GET /api/stats/user/:userId`
Estadísticas completas de un usuario

#### `GET /api/stats/user/:userId/games`
Historial de partidas de un usuario

#### `GET /api/stats/user/:userId/decks`
Estadísticas de mazos de un usuario

#### `GET /api/stats/leaderboard`
Ranking global

#### `GET /api/stats/leaderboard/:category`
Ranking por categoría (victorias, puntos, racha, etc.)

---

## ⭐ 6. APIs REST - Favoritos

### 6.1 Endpoints de Favoritos

#### `GET /api/favorites`
Listar cartas favoritas del usuario

#### `POST /api/favorites/:cartaId`
Agregar carta a favoritos

#### `DELETE /api/favorites/:cartaId`
Eliminar carta de favoritos

---

## 🏗️ 7. Estructura de Archivos

```
server/
├── data/
│   └── users/
│       └── users.db  (Nueva base de datos SQLite)
├── models/
│   ├── User.js
│   ├── Deck.js
│   ├── Game.js
│   └── UserStats.js
├── repository/
│   ├── UserRepository.js
│   ├── DeckRepository.js
│   ├── GameRepository.js
│   └── StatsRepository.js
├── controllers/
│   ├── AuthController.js
│   ├── UserController.js
│   ├── DeckController.js
│   ├── GameController.js
│   └── StatsController.js
├── middleware/
│   ├── auth.js
│   ├── validateDeck.js
│   └── errorHandler.js
├── routes/
│   ├── auth.js
│   ├── users.js
│   ├── decks.js
│   ├── games.js
│   └── stats.js
└── utils/
    ├── passwordUtils.js
    ├── jwtUtils.js
    └── deckValidator.js
```

---

## 🎨 8. Frontend - Páginas y Componentes

### 8.1 Páginas HTML

#### `public/login.html`
- Formulario de login
- Link a registro
- Recuperar contraseña (futuro)

#### `public/register.html`
- Formulario de registro
- Validación de campos
- Link a login

#### `public/profile.html`
- Perfil del usuario
- Editar información
- Cambiar contraseña
- Avatar

#### `public/decks.html`
- Lista de mazos del usuario
- Crear nuevo mazo
- Editar mazo
- Eliminar mazo
- Duplicar mazo
- Validar mazo

#### `public/deck-builder.html`
- Constructor visual de mazos
- Drag & drop de cartas
- Validación en tiempo real
- Vista previa del mazo

#### `public/stats.html`
- Estadísticas del usuario
- Gráficos de rendimiento
- Historial de partidas
- Rankings

#### `public/games.html`
- Lista de partidas
- Crear nueva partida
- Ver partida en curso
- Historial de partidas

#### `public/leaderboard.html`
- Ranking global
- Filtros por categoría
- Búsqueda de usuarios

### 8.2 JavaScript Frontend

#### `public/js/auth.js`
- Funciones de login/registro
- Manejo de tokens JWT
- Redirección según autenticación

#### `public/js/user.js`
- Gestión de perfil
- Actualizar información

#### `public/js/decks.js`
- CRUD de mazos
- Validación de mazos
- Constructor de mazos

#### `public/js/games.js`
- Crear partidas
- Ver estado de partidas
- Historial

#### `public/js/stats.js`
- Visualizar estadísticas
- Gráficos (usar Chart.js o similar)

#### `public/js/api.js`
- Cliente API centralizado
- Manejo de tokens
- Interceptores de requests

### 8.3 CSS

#### `public/css/auth.css`
- Estilos para login/registro

#### `public/css/profile.css`
- Estilos para perfil

#### `public/css/decks.css`
- Estilos para mazos y constructor

#### `public/css/stats.css`
- Estilos para estadísticas y gráficos

---

## 🔄 9. Flujo de Autenticación

### 9.1 Registro
1. Usuario completa formulario
2. Frontend envía `POST /api/auth/register`
3. Servidor valida datos
4. Hash de contraseña con bcrypt
5. Crear usuario en BD
6. Crear registro en `estadisticas_usuario`
7. Generar JWT token
8. Retornar token al cliente
9. Guardar token en localStorage
10. Redirigir a perfil o página principal

### 9.2 Login
1. Usuario ingresa credenciales
2. Frontend envía `POST /api/auth/login`
3. Servidor verifica credenciales
4. Generar JWT token
5. Guardar sesión en BD (opcional)
6. Retornar token y datos de usuario
7. Guardar token en localStorage
8. Redirigir según estado

### 9.3 Requests Autenticados
1. Cliente incluye token en header: `Authorization: Bearer <token>`
2. Middleware `auth.js` verifica token
3. Extrae `usuario_id` del token
4. Agrega `req.user` con datos del usuario
5. Continúa con el request

---

## ✅ 10. Validación de Mazos

### 10.1 Reglas a Validar

1. **Tamaño**: Exactamente 50 cartas
2. **Oro Inicial**: Exactamente 1 carta de "Oro Inicial"
3. **Mínimo de Aliados**: Según formato (15-20)
4. **Límite de Copias**:
   - Cartas normales: máximo 3 copias
   - Cartas únicas: máximo 1 copia
5. **Formato Racial Edición**:
   - Todos los Aliados de la misma raza
   - Cartas de soporte de la edición original
6. **Formato Racial Soporte Libre**:
   - Todos los Aliados de la misma raza
   - Cartas de soporte de ediciones permitidas

### 10.2 Archivo: `server/utils/deckValidator.js`

Funciones:
- `validarTamañoMazo(mazo)`
- `validarOroInicial(mazo)`
- `validarMinimoAliados(mazo, formato)`
- `validarCopias(mazo)`
- `validarRaza(mazo, formato, raza)`
- `validarEdiciones(mazo, formato, raza)`
- `validarMazoCompleto(mazo, formato)`

---

## 📊 11. Sistema de Estadísticas

### 11.1 Actualización de Estadísticas

Cuando una partida termina:
1. Determinar ganador/perdedor/empate
2. Actualizar `estadisticas_usuario`:
   - Incrementar `partidas_jugadas`
   - Incrementar `partidas_ganadas`/`perdidas`/`empatadas`
   - Actualizar `puntos_totales` (sistema de puntos)
   - Actualizar `racha_victorias`
   - Actualizar `mejor_racha_victorias`
   - Sumar `cartas_jugadas_totales`
   - Sumar `turnos_jugados_totales`
   - Sumar `tiempo_jugado_segundos`
3. Actualizar `mazos.veces_usado` para mazos usados

### 11.2 Sistema de Puntos

- Victoria: +10 puntos
- Derrota: +1 punto (participación)
- Empate: +5 puntos
- Victoria con racha: +2 puntos extra por racha

---

## 🎯 12. Funcionalidades Adicionales

### 12.1 Sistema de Niveles y Experiencia
- Ganar partidas otorga experiencia
- Subir de nivel desbloquea avatares, títulos, etc.

### 12.2 Logros (Achievements)
- Tabla `logros` y `logros_usuario`
- Logros: "Primera victoria", "10 victorias", "Racha de 5", etc.

### 12.3 Amigos y Social
- Tabla `amistades`
- Enviar solicitudes de amistad
- Ver amigos online
- Desafiar amigos

### 12.4 Notificaciones
- Tabla `notificaciones`
- Notificaciones: nueva solicitud de amistad, desafío, logro desbloqueado

### 12.5 Historial Detallado
- Guardar cada acción de partida
- Tabla `acciones_partida`
- Permite "replay" de partidas

---

## 🚀 13. Plan de Implementación (Fases)

### Fase 1: Base y Autenticación (Prioridad Alta)
- [ ] Crear base de datos de usuarios
- [ ] Implementar UserRepository
- [ ] Implementar autenticación (register/login)
- [ ] Middleware de autenticación
- [ ] Frontend: login.html y register.html
- [ ] Frontend: auth.js

### Fase 2: Perfil y Mazos Básicos (Prioridad Alta)
- [ ] API de usuarios (GET/PUT)
- [ ] API de mazos (CRUD básico)
- [ ] Validación básica de mazos
- [ ] Frontend: profile.html
- [ ] Frontend: decks.html
- [ ] Frontend: deck-builder.html

### Fase 3: Partidas y Estadísticas (Prioridad Media)
- [ ] API de partidas
- [ ] Integración con GameState existente
- [ ] Actualización de estadísticas
- [ ] Frontend: games.html
- [ ] Frontend: stats.html

### Fase 4: Funcionalidades Avanzadas (Prioridad Baja)
- [ ] Sistema de favoritos
- [ ] Rankings y leaderboard
- [ ] Sistema de niveles
- [ ] Logros
- [ ] Frontend: leaderboard.html

### Fase 5: Social y Mejoras (Futuro)
- [ ] Sistema de amigos
- [ ] Notificaciones
- [ ] Historial detallado de partidas
- [ ] Replay de partidas

---

## 🔒 14. Seguridad

### 14.1 Contraseñas
- Hash con bcrypt (salt rounds: 10)
- Nunca almacenar contraseñas en texto plano
- Validar fortaleza de contraseña (mínimo 8 caracteres, mayúsculas, números)

### 14.2 JWT Tokens
- Expiración: 24 horas
- Refresh tokens para renovar
- Invalidar tokens al logout
- Verificar firma en cada request

### 14.3 Validación de Input
- Sanitizar todos los inputs
- Validar tipos de datos
- Prevenir SQL injection (usar prepared statements)
- Prevenir XSS (escapar HTML)

### 14.4 Rate Limiting
- Limitar requests de login (5 intentos por minuto)
- Limitar requests de registro (3 por hora por IP)

---

## 📝 15. Ejemplos de Uso

### 15.1 Registro de Usuario
```javascript
// Frontend
const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'jugador1',
        email: 'jugador@example.com',
        password: 'Password123!',
        nombre_completo: 'Juan Pérez'
    })
});
const data = await response.json();
localStorage.setItem('token', data.token);
```

### 15.2 Crear Mazo
```javascript
// Frontend
const response = await fetch('/api/decks', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
        nombre: 'Mazo Olímpico',
        formato: 'Racial Edición',
        raza: 'Olímpico',
        edicion_original: 'Helénica',
        cartas: ['carta1', 'carta2', ...], // 50 IDs
        oro_inicial_id: 'oro_inicial_1'
    })
});
```

### 15.3 Obtener Estadísticas
```javascript
// Frontend
const response = await fetch('/api/stats/user/me', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});
const stats = await response.json();
```

---

## 🧪 16. Testing

### 16.1 Tests Unitarios
- Validación de mazos
- Hash de contraseñas
- Generación de tokens

### 16.2 Tests de Integración
- Flujo completo de registro/login
- Crear y validar mazo
- Iniciar y finalizar partida
- Actualización de estadísticas

---

## 📚 17. Documentación

### 17.1 Documentación de APIs
- Crear `API_DOCUMENTATION.md` con todos los endpoints
- Ejemplos de requests/responses
- Códigos de error

### 17.2 Guía de Usuario
- Cómo registrarse
- Cómo crear un mazo
- Cómo jugar una partida
- Cómo ver estadísticas

---

## 🎨 18. UI/UX Considerations

### 18.1 Diseño Consistente
- Mantener estilo visual del proyecto actual
- Usar mismo sistema de colores
- Componentes reutilizables

### 18.2 Responsive
- Diseño mobile-first
- Adaptable a tablets y desktop

### 18.3 Feedback Visual
- Loading states
- Mensajes de éxito/error
- Confirmaciones para acciones destructivas

---

## 🔄 19. Integración con Sistema Existente

### 19.1 Cartas
- Las APIs de cartas existentes siguen funcionando
- Agregar favoritos como funcionalidad adicional
- Mantener compatibilidad con código existente

### 19.2 GameState
- Integrar con GameState existente
- Guardar estado de partidas en BD
- Permitir reanudar partidas

---

## 📋 20. Checklist Final

Antes de considerar completo el módulo:

- [ ] Base de datos creada y migrada
- [ ] Autenticación funcionando
- [ ] CRUD de usuarios
- [ ] CRUD de mazos con validación
- [ ] Sistema de partidas integrado
- [ ] Estadísticas actualizándose correctamente
- [ ] Frontend completo y funcional
- [ ] Seguridad implementada
- [ ] Documentación completa
- [ ] Tests básicos pasando

---

**Última actualización:** 2025-01-XX

Este plan es extenso y completo. Se puede implementar por fases según las prioridades del proyecto.

