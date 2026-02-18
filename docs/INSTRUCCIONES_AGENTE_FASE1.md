# 🤖 Instrucciones para el Agente: Implementar Fase 1 - Sistema de Lobby

**Objetivo:** Implementar el sistema de lobby y emparejamiento de jugadores  
**Tiempo estimado:** 2-3 semanas  
**Prioridad:** 🔴 ALTA

---

## 📋 Resumen de la Tarea

Implementar un sistema completo de lobby que permita:
- ✅ Búsqueda rápida de partidas
- ✅ Emparejamiento automático de jugadores
- ✅ Creación de partidas privadas
- ✅ Lista de partidas disponibles
- ✅ Estadísticas del lobby en tiempo real

---

## 📚 Documentos de Referencia

**LEER PRIMERO estos documentos en orden:**

1. **`docs/ANALISIS_DUELING_NEXUS.md`**
   - Contexto general del análisis
   - Comparación con Dueling Nexus
   - Arquitectura propuesta

2. **`docs/IMPLEMENTACION_LOBBY_SISTEMA.md`** ⭐ **GUÍA PRINCIPAL**
   - Código completo listo para implementar
   - Todos los archivos necesarios
   - Ejemplos de frontend y backend

3. **`docs/ARCHITECTURE.md`**
   - Principios arquitectónicos del proyecto
   - Estructura de carpetas
   - Convenciones de código

4. **`docs/RESUMEN_DUELING_NEXUS.md`**
   - Resumen ejecutivo
   - Prioridades

---

## 🎯 Tareas Específicas a Implementar

### Tarea 1: Crear LobbyManager (Backend)

**Archivo a crear:** `server/ws/lobbyManager.js`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 1: Crear Módulo de Lobby Manager"

**Qué debe hacer:**
- Crear clase `LobbyManager` que gestione jugadores en lobby
- Implementar métodos para agregar/remover jugadores
- Implementar cola de emparejamiento
- Implementar lógica de emparejamiento automático
- Gestionar partidas disponibles

**Verificación:**
```javascript
// Probar que el módulo se puede importar
const lobbyManager = require('./server/ws/lobbyManager');
console.log('LobbyManager cargado correctamente');
```

---

### Tarea 2: Extender gameSocket.js (Backend)

**Archivo a modificar:** `server/ws/gameSocket.js`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 2: Extender gameSocket.js"

**Qué debe hacer:**
- Importar `lobbyManager`
- Agregar evento `join_lobby`
- Agregar evento `find_match` (búsqueda de partida)
- Agregar evento `cancel_matchmaking`
- Agregar evento `create_private_game`
- Agregar evento `join_private_game`
- Agregar evento `get_lobby_state`
- Manejar desconexiones (remover del lobby)

**IMPORTANTE:** 
- No eliminar código existente, solo agregar
- Mantener compatibilidad con funcionalidad actual
- Seguir el patrón de código existente

**Verificación:**
- El servidor debe iniciar sin errores
- Los eventos WebSocket existentes deben seguir funcionando

---

### Tarea 3: Crear Página de Lobby (Frontend)

**Archivo a crear:** `public/lobby.html`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 3: Crear Página de Lobby"

**Qué debe hacer:**
- Crear HTML completo de la página de lobby
- Incluir secciones:
  - Estadísticas del lobby (jugadores online, en cola, partidas activas)
  - Búsqueda rápida de partidas
  - Lista de partidas disponibles
  - Creación de partidas privadas
- Incluir scripts necesarios (api.js, auth.js, navbar.js, lobby.js)

**Verificación:**
- La página debe cargar en `/lobby`
- Debe mostrar la barra de navegación
- Debe tener todos los elementos visuales

---

### Tarea 4: Crear JavaScript del Lobby (Frontend)

**Archivo a crear:** `public/js/lobby.js`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 4: Crear JavaScript del Lobby"

**Qué debe hacer:**
- Conectar WebSocket al servidor
- Implementar función `initLobby()`
- Implementar función `connectWebSocket()`
- Implementar función `loadDecks()` (cargar mazos del usuario)
- Implementar función `findQuickMatch()` (buscar partida)
- Implementar función `cancelMatchmaking()` (cancelar búsqueda)
- Implementar función `createPrivateGame()` (crear partida privada)
- Manejar eventos del servidor:
  - `lobby_state` - Actualizar estadísticas
  - `match_found` - Redirigir a partida
  - `searching` - Mostrar estado de búsqueda
  - `error` - Mostrar errores

**IMPORTANTE:**
- Usar `api.js` para llamadas REST (ver `public/js/api.js` para referencia)
- Usar `auth.js` para autenticación (ver `public/js/auth.js` para referencia)
- Seguir el patrón de código de `public/js/game.js`

**Verificación:**
- Debe conectarse al WebSocket sin errores
- Debe cargar los mazos del usuario
- Debe mostrar estadísticas del lobby

---

### Tarea 5: Crear Estilos CSS del Lobby (Frontend)

**Archivo a crear:** `public/css/lobby.css`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 5: Crear Estilos CSS"

**Qué debe hacer:**
- Crear estilos para `.lobby-container`
- Crear estilos para `.lobby-stats` y `.stat-card`
- Crear estilos para `.lobby-section`
- Crear estilos para `.quick-match-form`
- Crear estilos para `.matchmaking-status` y animación de progreso
- Crear estilos para `.games-list` y `.game-item`
- Crear estilos para `.private-game-info`
- Agregar responsive design (media queries)

**IMPORTANTE:**
- Seguir el estilo visual del proyecto (ver `public/css/game.css` y `public/css/auth.css`)
- Usar colores consistentes con el tema del juego

**Verificación:**
- La página debe verse bien en desktop y móvil
- Las animaciones deben funcionar

---

### Tarea 6: Agregar Ruta al Servidor

**Archivo a modificar:** `server/server.js`

**Referencia:** Ver `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Sección "Paso 6: Agregar Ruta al Servidor"

**Qué debe hacer:**
- Agregar ruta `app.get('/lobby', ...)` que sirva `public/lobby.html`
- Colocarla junto a las otras rutas de páginas (después de `/game`)

**Verificación:**
- Debe poder acceder a `http://localhost:3000/lobby`
- Debe servir el HTML correctamente

---

## ✅ Checklist de Implementación

Usa este checklist para verificar que todo está implementado:

### Backend
- [ ] `server/ws/lobbyManager.js` creado y funciona
- [ ] `server/ws/gameSocket.js` extendido con eventos de lobby
- [ ] Servidor inicia sin errores
- [ ] WebSocket acepta conexiones de lobby

### Frontend
- [ ] `public/lobby.html` creado
- [ ] `public/js/lobby.js` creado y funciona
- [ ] `public/css/lobby.css` creado
- [ ] Ruta `/lobby` agregada en `server/server.js`
- [ ] Página carga correctamente

### Funcionalidad
- [ ] Jugadores pueden unirse al lobby
- [ ] Estadísticas del lobby se actualizan
- [ ] Búsqueda de partidas funciona
- [ ] Emparejamiento automático funciona
- [ ] Creación de partidas privadas funciona
- [ ] Redirección a partida funciona

---

## 🧪 Pruebas a Realizar

### Prueba 1: Conexión Básica
1. Abrir `/lobby` en el navegador
2. Verificar que se conecta al WebSocket
3. Verificar que se muestran estadísticas (aunque sean 0)

### Prueba 2: Búsqueda de Partida
1. Abrir `/lobby` en dos navegadores diferentes (o dos pestañas con usuarios diferentes)
2. Seleccionar mazo en ambos
3. Hacer clic en "Buscar Partida" en ambos
4. Verificar que se crea la partida automáticamente
5. Verificar que ambos son redirigidos a `/game`

### Prueba 3: Partida Privada
1. Crear partida privada
2. Copiar código de invitación
3. Unirse con otro usuario usando el código
4. Verificar que ambos están en la misma partida

### Prueba 4: Cancelación
1. Iniciar búsqueda de partida
2. Cancelar la búsqueda
3. Verificar que se cancela correctamente

---

## 🐛 Solución de Problemas Comunes

### Error: "LobbyManager is not defined"
- Verificar que `lobbyManager.js` está en `server/ws/`
- Verificar que se importa correctamente: `const lobbyManager = require('./lobbyManager');`

### Error: "socket.emit is not a function"
- Verificar que `socket` está definido
- Verificar que se está dentro del callback `io.on('connection', ...)`

### Error: "Cannot read property 'getDecks' of undefined"
- Verificar que `api.js` está cargado antes de `lobby.js`
- Verificar que `api` está definido globalmente

### La página no carga
- Verificar que la ruta `/lobby` está en `server/server.js`
- Verificar que `lobby.html` está en `public/`
- Verificar la consola del navegador para errores

### WebSocket no se conecta
- Verificar que el servidor está corriendo
- Verificar que Socket.IO está instalado: `npm list socket.io`
- Verificar la consola del navegador para errores de conexión

---

## 📝 Notas Importantes

1. **No romper funcionalidad existente:**
   - El sistema de juego actual debe seguir funcionando
   - Solo agregar, no modificar código existente a menos que sea necesario

2. **Seguir convenciones del proyecto:**
   - Usar `async/await` para funciones asíncronas
   - Usar `console.log` para debugging
   - Seguir el formato de código existente

3. **Manejo de errores:**
   - Siempre usar try/catch en funciones async
   - Mostrar mensajes de error al usuario
   - Loggear errores en consola para debugging

4. **Testing:**
   - Probar con al menos 2 usuarios diferentes
   - Probar en diferentes navegadores
   - Verificar que funciona en móvil (responsive)

---

## 🎯 Criterios de Éxito

La implementación se considera exitosa cuando:

✅ El servidor inicia sin errores  
✅ Los jugadores pueden acceder a `/lobby`  
✅ Los jugadores pueden buscar partidas  
✅ El emparejamiento automático funciona  
✅ Los jugadores son redirigidos a la partida correctamente  
✅ Las partidas privadas se pueden crear y unirse  
✅ No se rompe funcionalidad existente  

---

## 📞 Si Necesitas Ayuda

Si encuentras problemas o necesitas clarificaciones:

1. **Revisar documentación:**
   - `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Código completo
   - `docs/ARCHITECTURE.md` - Arquitectura del proyecto
   - `docs/GAME_RULES.md` - Reglas del juego (contexto)

2. **Revisar código existente:**
   - `server/ws/gameSocket.js` - Ver cómo se manejan WebSockets
   - `public/js/game.js` - Ver cómo se conecta el frontend
   - `public/js/api.js` - Ver cómo se hacen llamadas API

3. **Verificar logs:**
   - Consola del servidor (Node.js)
   - Consola del navegador (F12)
   - Logs de WebSocket

---

## 🚀 Comenzar Implementación

**Orden recomendado de implementación:**

1. **Backend primero:**
   - Crear `lobbyManager.js`
   - Extender `gameSocket.js`
   - Probar que el servidor inicia

2. **Frontend después:**
   - Crear `lobby.html`
   - Crear `lobby.js`
   - Crear `lobby.css`
   - Agregar ruta en `server.js`

3. **Testing:**
   - Probar cada funcionalidad individualmente
   - Probar integración completa
   - Verificar que no se rompe nada existente

---

**¡Buena suerte con la implementación! 🎮**

---

**Última actualización:** 2025-01-27




