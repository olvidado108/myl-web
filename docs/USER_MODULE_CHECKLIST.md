# ✅ Checklist de Implementación: Módulo de Usuarios

Este documento es una guía paso a paso para implementar el módulo de usuarios.

---

## 📋 Pre-requisitos

- [ ] Node.js instalado
- [ ] Proyecto actual funcionando
- [ ] Base de datos de cartas funcionando
- [ ] Entender la estructura actual del proyecto

---

## 🔧 Fase 1: Configuración Inicial

### 1.1 Instalar Dependencias
```bash
npm install bcrypt jsonwebtoken cookie-parser
```

- [ ] Ejecutar comando de instalación
- [ ] Verificar que se instalaron correctamente
- [ ] Actualizar `package.json` si es necesario

### 1.2 Crear Estructura de Carpetas
```
server/
├── data/
│   └── users/          (nueva)
├── models/
│   ├── User.js         (nuevo)
│   ├── Deck.js         (nuevo)
│   └── Game.js         (nuevo)
├── repository/
│   ├── UserRepository.js      (nuevo)
│   ├── DeckRepository.js      (nuevo)
│   ├── GameRepository.js      (nuevo)
│   └── StatsRepository.js     (nuevo)
├── controllers/
│   ├── AuthController.js      (nuevo)
│   ├── UserController.js      (nuevo)
│   ├── DeckController.js      (nuevo)
│   ├── GameController.js      (nuevo)
│   └── StatsController.js     (nuevo)
├── middleware/
│   ├── auth.js         (nuevo)
│   └── validateDeck.js  (nuevo)
├── routes/
│   ├── auth.js         (nuevo)
│   ├── users.js       (nuevo)
│   ├── decks.js        (nuevo)
│   ├── games.js        (nuevo)
│   └── stats.js        (nuevo)
└── utils/
    ├── passwordUtils.js (nuevo)
    ├── jwtUtils.js      (nuevo)
    └── deckValidator.js (nuevo)
```

- [ ] Crear carpeta `server/data/users/`
- [ ] Crear todas las carpetas necesarias
- [ ] Verificar estructura

### 1.3 Variables de Entorno
- [ ] Crear archivo `.env` (o agregar a existente)
- [ ] Agregar `JWT_SECRET` (generar uno seguro)
- [ ] Documentar variables de entorno

---

## 🗄️ Fase 2: Base de Datos

### 2.1 UserRepository
- [ ] Crear `server/repository/UserRepository.js`
- [ ] Implementar método `_crearTablas()`
- [ ] Crear tabla `usuarios`
- [ ] Crear tabla `estadisticas_usuario`
- [ ] Crear índices necesarios
- [ ] Implementar `crearUsuario()`
- [ ] Implementar `buscarPorId()`
- [ ] Implementar `buscarPorUsername()`
- [ ] Implementar `verificarPassword()`
- [ ] Implementar `actualizarUsuario()`
- [ ] Probar con datos de prueba

### 2.2 DeckRepository
- [ ] Crear `server/repository/DeckRepository.js`
- [ ] Crear tabla `mazos`
- [ ] Implementar `crearMazo()`
- [ ] Implementar `buscarPorId()`
- [ ] Implementar `listarPorUsuario()`
- [ ] Implementar `actualizarMazo()`
- [ ] Implementar `eliminarMazo()`
- [ ] Probar con datos de prueba

### 2.3 GameRepository
- [ ] Crear `server/repository/GameRepository.js`
- [ ] Crear tabla `partidas`
- [ ] Implementar métodos básicos
- [ ] Integrar con GameState existente

### 2.4 StatsRepository
- [ ] Crear `server/repository/StatsRepository.js`
- [ ] Implementar `obtenerEstadisticas()`
- [ ] Implementar `actualizarEstadisticas()`
- [ ] Implementar `obtenerLeaderboard()`

### 2.5 Verificación
- [ ] Probar creación de tablas
- [ ] Verificar relaciones (foreign keys)
- [ ] Verificar índices
- [ ] Probar inserción de datos de prueba
- [ ] Probar consultas básicas

---

## 🔐 Fase 3: Autenticación

### 3.1 Utilidades
- [ ] Crear `server/utils/passwordUtils.js`
- [ ] Implementar hash de contraseñas
- [ ] Crear `server/utils/jwtUtils.js`
- [ ] Implementar generación de tokens
- [ ] Implementar verificación de tokens

### 3.2 Middleware
- [ ] Crear `server/middleware/auth.js`
- [ ] Implementar `authenticateToken()`
- [ ] Implementar `optionalAuth()`
- [ ] Probar middleware

### 3.3 AuthController
- [ ] Crear `server/controllers/AuthController.js`
- [ ] Implementar `register()`
- [ ] Validar datos de registro
- [ ] Hash de contraseñas
- [ ] Generar tokens
- [ ] Implementar `login()`
- [ ] Verificar credenciales
- [ ] Implementar `me()`
- [ ] Manejo de errores

### 3.4 Rutas de Autenticación
- [ ] Crear `server/routes/auth.js`
- [ ] Ruta `POST /api/auth/register`
- [ ] Ruta `POST /api/auth/login`
- [ ] Ruta `GET /api/auth/me`
- [ ] Ruta `POST /api/auth/logout` (opcional)
- [ ] Registrar rutas en `server.js`

### 3.5 Pruebas
- [ ] Probar registro de usuario
- [ ] Probar login
- [ ] Probar token inválido
- [ ] Probar usuario no encontrado
- [ ] Verificar que tokens funcionan

---

## 👤 Fase 4: Gestión de Usuarios

### 4.1 UserController
- [ ] Crear `server/controllers/UserController.js`
- [ ] Implementar `getProfile()`
- [ ] Implementar `updateProfile()`
- [ ] Implementar `getStats()`
- [ ] Validaciones

### 4.2 Rutas de Usuario
- [ ] Crear `server/routes/users.js`
- [ ] Ruta `GET /api/users/:id`
- [ ] Ruta `PUT /api/users/:id`
- [ ] Ruta `GET /api/users/:id/stats`
- [ ] Proteger rutas con middleware
- [ ] Registrar rutas en `server.js`

### 4.3 Pruebas
- [ ] Probar obtener perfil
- [ ] Probar actualizar perfil
- [ ] Probar obtener estadísticas
- [ ] Verificar permisos (solo propio perfil)

---

## 🃏 Fase 5: Sistema de Mazos

### 5.1 Validador de Mazos
- [ ] Crear `server/utils/deckValidator.js`
- [ ] Implementar `validarTamañoMazo()`
- [ ] Implementar `validarOroInicial()`
- [ ] Implementar `validarCopias()`
- [ ] Implementar `validarMinimoAliados()`
- [ ] Implementar `validarRaza()`
- [ ] Implementar `validarMazoCompleto()`
- [ ] Probar validaciones

### 5.2 DeckController
- [ ] Crear `server/controllers/DeckController.js`
- [ ] Implementar `listDecks()`
- [ ] Implementar `getDeck()`
- [ ] Implementar `createDeck()`
- [ ] Validar mazo antes de crear
- [ ] Implementar `updateDeck()`
- [ ] Implementar `deleteDeck()`
- [ ] Implementar `validateDeck()`
- [ ] Verificar permisos (solo propios mazos)

### 5.3 Rutas de Mazos
- [ ] Crear `server/routes/decks.js`
- [ ] Ruta `GET /api/decks`
- [ ] Ruta `POST /api/decks`
- [ ] Ruta `GET /api/decks/:id`
- [ ] Ruta `PUT /api/decks/:id`
- [ ] Ruta `DELETE /api/decks/:id`
- [ ] Ruta `POST /api/decks/validate`
- [ ] Proteger rutas con middleware
- [ ] Registrar rutas en `server.js`

### 5.4 Pruebas
- [ ] Probar crear mazo válido
- [ ] Probar crear mazo inválido (debe fallar)
- [ ] Probar listar mazos
- [ ] Probar actualizar mazo
- [ ] Probar eliminar mazo
- [ ] Probar validación sin guardar

---

## 🎮 Fase 6: Partidas

### 6.1 GameController
- [ ] Crear `server/controllers/GameController.js`
- [ ] Implementar `createGame()`
- [ ] Validar mazos
- [ ] Inicializar GameState
- [ ] Implementar `getGame()`
- [ ] Implementar `performAction()`
- [ ] Implementar `endGame()`
- [ ] Actualizar estadísticas al finalizar

### 6.2 Rutas de Partidas
- [ ] Crear `server/routes/games.js`
- [ ] Ruta `POST /api/games`
- [ ] Ruta `GET /api/games/:id`
- [ ] Ruta `POST /api/games/:id/actions`
- [ ] Ruta `POST /api/games/:id/end`
- [ ] Ruta `GET /api/games`
- [ ] Proteger rutas
- [ ] Registrar rutas en `server.js`

### 6.3 Integración con GameState
- [ ] Verificar que GameState existente funciona
- [ ] Adaptar GameState para guardar en BD
- [ ] Implementar guardado de estado
- [ ] Implementar carga de estado

### 6.4 Pruebas
- [ ] Probar crear partida
- [ ] Probar realizar acciones
- [ ] Probar finalizar partida
- [ ] Verificar que estadísticas se actualizan

---

## 📊 Fase 7: Estadísticas

### 7.1 StatsController
- [ ] Crear `server/controllers/StatsController.js`
- [ ] Implementar `getUserStats()`
- [ ] Implementar `getLeaderboard()`
- [ ] Implementar `getGameHistory()`

### 7.2 Rutas de Estadísticas
- [ ] Crear `server/routes/stats.js`
- [ ] Ruta `GET /api/stats/user/:userId`
- [ ] Ruta `GET /api/stats/leaderboard`
- [ ] Ruta `GET /api/stats/user/:userId/games`
- [ ] Registrar rutas en `server.js`

### 7.3 Actualización Automática
- [ ] Verificar que estadísticas se actualizan al finalizar partida
- [ ] Probar diferentes resultados (victoria, derrota, empate)
- [ ] Verificar rachas de victorias
- [ ] Verificar puntos

### 7.4 Pruebas
- [ ] Probar obtener estadísticas
- [ ] Probar leaderboard
- [ ] Verificar cálculos correctos

---

## 🎨 Fase 8: Frontend - Autenticación

### 8.1 Cliente API
- [ ] Crear `public/js/api.js`
- [ ] Implementar clase `ApiClient`
- [ ] Implementar manejo de tokens
- [ ] Implementar métodos de autenticación
- [ ] Implementar métodos de mazos
- [ ] Implementar métodos de estadísticas

### 8.2 Página de Login
- [ ] Crear `public/login.html`
- [ ] Diseño del formulario
- [ ] Crear `public/js/auth.js`
- [ ] Implementar función de login
- [ ] Manejo de errores
- [ ] Redirección después de login

### 8.3 Página de Registro
- [ ] Crear `public/register.html`
- [ ] Diseño del formulario
- [ ] Validación de campos
- [ ] Implementar función de registro
- [ ] Manejo de errores
- [ ] Redirección después de registro

### 8.4 CSS
- [ ] Crear `public/css/auth.css`
- [ ] Estilos para login
- [ ] Estilos para registro
- [ ] Responsive design

### 8.5 Pruebas
- [ ] Probar registro desde frontend
- [ ] Probar login desde frontend
- [ ] Verificar que token se guarda
- [ ] Verificar redirecciones

---

## 🎨 Fase 9: Frontend - Perfil

### 9.1 Página de Perfil
- [ ] Crear `public/profile.html`
- [ ] Mostrar información del usuario
- [ ] Formulario de edición
- [ ] Cambio de contraseña
- [ ] Subir avatar (opcional)

### 9.2 JavaScript
- [ ] Crear `public/js/user.js`
- [ ] Cargar datos del usuario
- [ ] Implementar actualización
- [ ] Manejo de errores

### 9.3 CSS
- [ ] Crear `public/css/profile.css`
- [ ] Estilos para perfil

### 9.4 Pruebas
- [ ] Probar ver perfil
- [ ] Probar actualizar perfil
- [ ] Verificar permisos

---

## 🎨 Fase 10: Frontend - Mazos

### 10.1 Página de Mazos
- [ ] Crear `public/decks.html`
- [ ] Lista de mazos
- [ ] Botón crear nuevo
- [ ] Botones editar/eliminar
- [ ] Filtros y búsqueda

### 10.2 Constructor de Mazos
- [ ] Crear `public/deck-builder.html`
- [ ] Interfaz visual
- [ ] Agregar/quitar cartas
- [ ] Validación en tiempo real
- [ ] Vista previa del mazo
- [ ] Contador de cartas

### 10.3 JavaScript
- [ ] Crear `public/js/decks.js`
- [ ] Cargar mazos
- [ ] Crear mazo
- [ ] Editar mazo
- [ ] Eliminar mazo
- [ ] Validar mazo
- [ ] Integrar con constructor

### 10.4 CSS
- [ ] Crear `public/css/decks.css`
- [ ] Estilos para lista de mazos
- [ ] Estilos para constructor
- [ ] Responsive design

### 10.5 Pruebas
- [ ] Probar crear mazo desde frontend
- [ ] Probar validación en tiempo real
- [ ] Probar editar mazo
- [ ] Probar eliminar mazo

---

## 🎨 Fase 11: Frontend - Partidas y Estadísticas

### 11.1 Página de Partidas
- [ ] Crear `public/games.html`
- [ ] Lista de partidas
- [ ] Crear nueva partida
- [ ] Ver partida en curso
- [ ] Historial

### 11.2 Página de Estadísticas
- [ ] Crear `public/stats.html`
- [ ] Mostrar estadísticas personales
- [ ] Gráficos (usar Chart.js)
- [ ] Historial de partidas

### 11.3 Página de Leaderboard
- [ ] Crear `public/leaderboard.html`
- [ ] Tabla de rankings
- [ ] Filtros por categoría
- [ ] Búsqueda de usuarios

### 11.4 JavaScript
- [ ] Crear `public/js/games.js`
- [ ] Crear `public/js/stats.js`
- [ ] Implementar funcionalidades

### 11.5 CSS
- [ ] Crear `public/css/games.css`
- [ ] Crear `public/css/stats.css`
- [ ] Estilos para gráficos

### 11.6 Pruebas
- [ ] Probar crear partida
- [ ] Probar ver estadísticas
- [ ] Probar leaderboard

---

## 🔒 Fase 12: Seguridad y Validación

### 12.1 Validación de Inputs
- [ ] Sanitizar todos los inputs
- [ ] Validar tipos de datos
- [ ] Validar longitudes
- [ ] Prevenir SQL injection
- [ ] Prevenir XSS

### 12.2 Rate Limiting
- [ ] Implementar rate limiting para login
- [ ] Implementar rate limiting para registro
- [ ] Configurar límites apropiados

### 12.3 Seguridad de Tokens
- [ ] Verificar expiración de tokens
- [ ] Invalidar tokens al logout
- [ ] Refresh tokens (opcional)

### 12.4 Pruebas de Seguridad
- [ ] Probar SQL injection
- [ ] Probar XSS
- [ ] Probar tokens expirados
- [ ] Probar acceso no autorizado

---

## 🧪 Fase 13: Testing

### 13.1 Tests Unitarios
- [ ] Tests de validación de mazos
- [ ] Tests de hash de contraseñas
- [ ] Tests de generación de tokens
- [ ] Tests de repositorios

### 13.2 Tests de Integración
- [ ] Test flujo completo de registro/login
- [ ] Test crear y validar mazo
- [ ] Test iniciar y finalizar partida
- [ ] Test actualización de estadísticas

### 13.3 Tests Manuales
- [ ] Probar todos los flujos de usuario
- [ ] Probar casos edge
- [ ] Probar errores

---

## 📚 Fase 14: Documentación

### 14.1 Documentación de APIs
- [ ] Documentar todos los endpoints
- [ ] Ejemplos de requests/responses
- [ ] Códigos de error
- [ ] Crear `API_DOCUMENTATION.md`

### 14.2 Documentación de Usuario
- [ ] Guía de registro
- [ ] Guía de creación de mazos
- [ ] Guía de partidas
- [ ] FAQ

### 14.3 Comentarios en Código
- [ ] Agregar JSDoc a funciones importantes
- [ ] Comentar código complejo
- [ ] Documentar decisiones de diseño

---

## 🚀 Fase 15: Deployment y Optimización

### 15.1 Optimización
- [ ] Optimizar consultas SQL
- [ ] Agregar índices faltantes
- [ ] Optimizar carga de datos
- [ ] Cachear datos frecuentes (opcional)

### 15.2 Deployment
- [ ] Configurar variables de entorno en producción
- [ ] Cambiar JWT_SECRET en producción
- [ ] Configurar HTTPS
- [ ] Backup de base de datos

### 15.3 Monitoreo
- [ ] Logs de errores
- [ ] Monitoreo de performance
- [ ] Alertas (opcional)

---

## ✅ Checklist Final

Antes de considerar completo:

- [ ] Todas las fases anteriores completadas
- [ ] No hay errores en consola
- [ ] Todas las funcionalidades probadas
- [ ] Documentación completa
- [ ] Código comentado
- [ ] Seguridad implementada
- [ ] Performance aceptable
- [ ] UI/UX pulida

---

## 📝 Notas

- Marcar cada ítem como completado cuando se termine
- Priorizar fases según necesidades del proyecto
- No todas las fases son obligatorias para MVP
- Iterar y mejorar continuamente

---

**Última actualización:** 2025-01-XX

