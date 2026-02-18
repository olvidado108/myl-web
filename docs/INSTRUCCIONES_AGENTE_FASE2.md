# 🤖 Instrucciones para el Agente: Implementar Fase 2 - Experiencia de Usuario

**Objetivo:** Mejorar la experiencia de usuario con chat, mejoras visuales, feedback de acciones y animaciones  
**Tiempo estimado:** 2-3 semanas  
**Prioridad:** 🟡 MEDIA

---

## 📋 Resumen de la Tarea

Implementar mejoras en la experiencia de usuario que incluyen:
- ✅ Sistema de chat en partida
- ✅ Mejoras visuales (drag & drop mejorado)
- ✅ Feedback visual de acciones
- ✅ Animaciones fluidas
- ✅ Sonidos y efectos (opcional)

---

## 📚 Documentos de Referencia

**LEER PRIMERO estos documentos en orden:**

1. **`docs/ANALISIS_DUELING_NEXUS.md`**
   - Sección "2. Mejoras en la Interfaz de Juego"
   - Sección "4. Sistema de Chat en Partida"
   - Contexto general del análisis

2. **`docs/ARCHITECTURE.md`**
   - Principios arquitectónicos del proyecto
   - Estructura de carpetas
   - Convenciones de código

3. **Código existente:**
   - `public/js/game.js` - Ver cómo funciona el juego actual
   - `public/css/game.css` - Ver estilos actuales
   - `server/ws/gameSocket.js` - Ver cómo funcionan los WebSockets

---

## 🎯 Tareas Específicas a Implementar

### Tarea 1: Mejorar Drag & Drop de Cartas

**Archivo a modificar:** `public/js/game.js`

**Referencia:** Ver `docs/ANALISIS_DUELING_NEXUS.md` - Sección "2. Mejoras en la Interfaz de Juego" - "Drag & Drop Mejorado"

**Qué debe hacer:**
- Modificar función `createCardElement()` para agregar soporte drag & drop
- Agregar atributo `draggable="true"` a cartas en la mano (solo cuando es tu turno)
- Implementar eventos:
  - `dragstart` - Guardar datos de la carta
  - `dragend` - Limpiar estado visual
  - `dragover` - Permitir drop en zonas válidas
  - `dragleave` - Remover indicador visual
  - `drop` - Validar y ejecutar acción
- Agregar función `canPlayCardInZone(cardId, zoneType)` para validar
- Agregar función `playCardToZone(cardId, zoneType)` para ejecutar acción

**IMPORTANTE:**
- Solo permitir drag & drop cuando es el turno del jugador
- Validar que la carta se puede jugar en la zona objetivo
- Mantener funcionalidad de click existente como alternativa

**Código de referencia:**
```javascript
// En createCardElement, agregar:
if (isMyTurn && zoneType === 'hand') {
    div.draggable = true;
    
    div.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('cardId', card.id);
        e.dataTransfer.setData('zoneType', zoneType);
        div.classList.add('dragging');
    });
    
    div.addEventListener('dragend', () => {
        div.classList.remove('dragging');
        // Remover indicadores de drop de todas las zonas
        document.querySelectorAll('.zone').forEach(z => {
            z.classList.remove('drop-target');
        });
    });
}

// Agregar listeners a las zonas de drop
function setupDropZones() {
    const dropZones = document.querySelectorAll('.zone');
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            const cardId = e.dataTransfer.getData('cardId');
            if (canPlayCardInZone(cardId, zone.dataset.zoneType)) {
                zone.classList.add('drop-target');
            }
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drop-target');
        });
        
        zone.addEventListener('drop', async (e) => {
            e.preventDefault();
            zone.classList.remove('drop-target');
            
            const cardId = e.dataTransfer.getData('cardId');
            const sourceZone = e.dataTransfer.getData('zoneType');
            
            if (canPlayCardInZone(cardId, zone.dataset.zoneType)) {
                await playCardToZone(cardId, zone.dataset.zoneType);
            }
        });
    });
}
```

**Verificación:**
- Las cartas en la mano deben ser arrastrables
- Al arrastrar sobre una zona válida, debe mostrar indicador visual
- Al soltar en zona válida, debe jugar la carta
- Al soltar en zona inválida, debe cancelar sin hacer nada

---

### Tarea 2: Agregar Animaciones CSS

**Archivo a modificar:** `public/css/game.css`

**Referencia:** Ver `docs/ANALISIS_DUELING_NEXUS.md` - Sección "2. Mejoras en la Interfaz de Juego" - "Animaciones CSS"

**Qué debe hacer:**
- Agregar transiciones suaves a `.game-card`
- Agregar efecto hover (elevación y escala)
- Agregar animación para cartas siendo arrastradas
- Agregar indicador visual para zonas de drop válidas
- Agregar animación al jugar carta
- Agregar animación al recibir daño
- Agregar animación al ganar/perder

**Código de referencia:**
```css
/* Transiciones básicas */
.game-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

/* Hover effect */
.game-card:hover:not(.dragging) {
    transform: translateY(-10px) scale(1.05);
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    z-index: 10;
    cursor: pointer;
}

/* Carta siendo arrastrada */
.game-card.dragging {
    opacity: 0.5;
    transform: rotate(5deg) scale(0.9);
    cursor: grabbing;
}

/* Zona de drop válida */
.zone.drop-target {
    border: 2px dashed #4CAF50;
    background-color: rgba(76, 175, 80, 0.1);
    animation: pulse-border 1s infinite;
}

@keyframes pulse-border {
    0%, 100% { border-color: #4CAF50; }
    50% { border-color: #81C784; }
}

/* Animación al jugar carta */
@keyframes cardPlay {
    0% { 
        transform: scale(1) rotate(0deg);
        opacity: 1;
    }
    50% { 
        transform: scale(1.2) rotate(5deg);
        opacity: 0.8;
    }
    100% { 
        transform: scale(1) rotate(0deg);
        opacity: 1;
    }
}

.card-played {
    animation: cardPlay 0.5s ease;
}

/* Animación de daño */
@keyframes takeDamage {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(255, 0, 0, 0.3); }
}

.card-damaged {
    animation: takeDamage 0.5s ease;
}

/* Animación de victoria/derrota */
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

.game-over-message {
    animation: fadeIn 0.5s ease;
}
```

**Verificación:**
- Las cartas deben tener efecto hover suave
- Las cartas arrastradas deben verse diferentes
- Las zonas de drop deben mostrar indicador visual
- Las animaciones deben ser fluidas (60fps)

---

### Tarea 3: Agregar Feedback Visual de Acciones

**Archivo a modificar:** `public/js/game.js`

**Qué debe hacer:**
- Agregar función `showActionFeedback(message, type)` para mostrar mensajes
- Agregar función `highlightCard(cardId, duration)` para resaltar cartas
- Agregar función `shakeCard(cardId)` para animar carta al recibir daño
- Agregar función `glowZone(zoneId, color)` para resaltar zonas
- Integrar feedback en acciones existentes:
  - Al jugar carta: mostrar mensaje + animar carta
  - Al atacar: resaltar atacante y objetivo
  - Al recibir daño: animar carta + mostrar número de daño
  - Al cambiar fase: mostrar mensaje de fase

**Código de referencia:**
```javascript
/**
 * Muestra feedback visual de una acción
 */
function showActionFeedback(message, type = 'info') {
    const feedbackEl = document.createElement('div');
    feedbackEl.className = `action-feedback ${type}`;
    feedbackEl.textContent = message;
    
    // Agregar al contenedor de mensajes
    const messagesContainer = document.getElementById('gameMessages');
    if (messagesContainer) {
        messagesContainer.appendChild(feedbackEl);
        
        // Auto-remover después de 3 segundos
        setTimeout(() => {
            feedbackEl.style.opacity = '0';
            feedbackEl.style.transform = 'translateY(-20px)';
            setTimeout(() => feedbackEl.remove(), 300);
        }, 3000);
    }
}

/**
 * Resalta una carta temporalmente
 */
function highlightCard(cardId, duration = 1000) {
    const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
    if (!cardEl) return;
    
    cardEl.classList.add('highlighted');
    setTimeout(() => {
        cardEl.classList.remove('highlighted');
    }, duration);
}

/**
 * Anima una carta al recibir daño
 */
function shakeCard(cardId) {
    const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
    if (!cardEl) return;
    
    cardEl.classList.add('card-damaged');
    setTimeout(() => {
        cardEl.classList.remove('card-damaged');
    }, 500);
}

/**
 * Resalta una zona temporalmente
 */
function glowZone(zoneId, color = '#4CAF50') {
    const zoneEl = document.getElementById(zoneId);
    if (!zoneEl) return;
    
    zoneEl.style.boxShadow = `0 0 20px ${color}`;
    setTimeout(() => {
        zoneEl.style.boxShadow = '';
    }, 1000);
}

// Integrar en funciones existentes
async function playCard(cardId) {
    // Mostrar feedback
    showActionFeedback('Jugando carta...', 'info');
    
    // Resaltar carta
    highlightCard(cardId);
    
    // Ejecutar acción
    await performAction('jugar_carta', {
        carta_id: cardId,
        objetivo_id: null
    });
    
    // Mostrar confirmación
    showActionFeedback('Carta jugada', 'success');
}
```

**Agregar estilos CSS:**
```css
.action-feedback {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px 20px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    z-index: 1000;
    transition: opacity 0.3s, transform 0.3s;
}

.action-feedback.info {
    background-color: #2196F3;
}

.action-feedback.success {
    background-color: #4CAF50;
}

.action-feedback.error {
    background-color: #f44336;
}

.game-card.highlighted {
    box-shadow: 0 0 20px #FFD700;
    transform: scale(1.1);
}
```

**Verificación:**
- Debe mostrar mensajes de feedback al realizar acciones
- Debe resaltar cartas relevantes
- Debe animar cartas al recibir daño
- Los mensajes deben desaparecer automáticamente

---

### Tarea 4: Implementar Sistema de Chat en Partida

**Archivo a modificar (Backend):** `server/ws/gameSocket.js`

**Referencia:** Ver `docs/ANALISIS_DUELING_NEXUS.md` - Sección "4. Sistema de Chat en Partida"

**Qué debe hacer:**
- Agregar evento `chat_message` en el servidor
- Validar que el usuario está en la partida
- Enviar mensaje a todos los jugadores en la sala
- Incluir información del remitente y timestamp

**Código:**
```javascript
socket.on('chat_message', (payload) => {
    const { gameId, message } = payload;
    const userId = socket.data.userId;
    
    // Validar que el usuario está en la partida
    const room = io.sockets.adapter.rooms.get(roomName(gameId));
    if (!room || !room.has(socket.id)) {
        socket.emit('error', { message: 'No estás en esta partida' });
        return;
    }
    
    // Validar mensaje
    if (!message || message.trim().length === 0) {
        socket.emit('error', { message: 'El mensaje no puede estar vacío' });
        return;
    }
    
    if (message.length > 200) {
        socket.emit('error', { message: 'El mensaje es demasiado largo (máx 200 caracteres)' });
        return;
    }
    
    // Obtener información del usuario (opcional, si tienes UserRepository)
    // const user = UserRepository.getById(userId);
    
    // Enviar mensaje a todos en la sala
    io.to(roomName(gameId)).emit('chat_message', {
        userId,
        username: userId, // O usar user.username si tienes la info
        message: message.trim(),
        timestamp: Date.now()
    });
});
```

**Verificación:**
- El servidor debe aceptar mensajes de chat
- Debe validar que el usuario está en la partida
- Debe enviar mensajes a todos los jugadores

---

### Tarea 5: Agregar UI de Chat (Frontend)

**Archivo a modificar:** `public/game.html`

**Qué debe hacer:**
- Agregar sección de chat en el HTML
- Incluir contenedor de mensajes
- Incluir input de texto
- Incluir botón de enviar

**Código HTML:**
```html
<!-- Agregar dentro de #gameContainer, después de .game-board -->
<div class="game-chat-container">
    <div class="chat-header">
        <h4>Chat</h4>
        <button id="toggleChatBtn" class="btn-icon">−</button>
    </div>
    <div class="chat-messages" id="chatMessages">
        <!-- Los mensajes se agregarán aquí -->
    </div>
    <div class="chat-input-container">
        <input 
            type="text" 
            id="chatInput" 
            placeholder="Escribe un mensaje..." 
            maxlength="200"
        >
        <button id="sendChatBtn" class="btn btn-sm">Enviar</button>
    </div>
</div>
```

**Archivo a modificar:** `public/js/game.js`

**Qué debe hacer:**
- Agregar función `initChat()` para inicializar chat
- Agregar función `sendChatMessage()` para enviar mensajes
- Agregar listener para evento `chat_message` del servidor
- Agregar función `displayChatMessage()` para mostrar mensajes
- Agregar función para alternar visibilidad del chat

**Código:**
```javascript
/**
 * Inicializa el sistema de chat
 */
function initChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');
    const toggleBtn = document.getElementById('toggleChatBtn');
    
    // Enviar mensaje al presionar Enter o botón
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    sendBtn.addEventListener('click', sendChatMessage);
    
    // Toggle chat
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const chatContainer = document.querySelector('.game-chat-container');
            const chatMessages = document.getElementById('chatMessages');
            const chatInputContainer = document.querySelector('.chat-input-container');
            
            if (chatContainer.classList.contains('collapsed')) {
                chatContainer.classList.remove('collapsed');
                chatMessages.style.display = 'block';
                chatInputContainer.style.display = 'flex';
                toggleBtn.textContent = '−';
            } else {
                chatContainer.classList.add('collapsed');
                chatMessages.style.display = 'none';
                chatInputContainer.style.display = 'none';
                toggleBtn.textContent = '+';
            }
        });
    }
    
    // Escuchar mensajes del servidor
    if (socket) {
        socket.on('chat_message', (data) => {
            displayChatMessage(data);
        });
    }
}

/**
 * Envía un mensaje de chat
 */
function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message || !currentGameId) return;
    
    if (socket) {
        socket.emit('chat_message', {
            gameId: currentGameId,
            message: message
        });
        
        chatInput.value = '';
    }
}

/**
 * Muestra un mensaje de chat
 */
function displayChatMessage(data) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message';
    
    // Determinar si es mi mensaje
    const isMyMessage = data.userId === currentUserId;
    if (isMyMessage) {
        messageEl.classList.add('my-message');
    }
    
    const time = new Date(data.timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    messageEl.innerHTML = `
        <div class="chat-message-header">
            <span class="chat-username">${data.username || data.userId}</span>
            <span class="chat-time">${time}</span>
        </div>
        <div class="chat-message-text">${escapeHtml(data.message)}</div>
    `;
    
    chatMessages.appendChild(messageEl);
    
    // Auto-scroll al final
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Llamar initChat() en initGame()
async function initGame() {
    // ... código existente ...
    initChat();
}
```

**Agregar estilos CSS:**
```css
.game-chat-container {
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 300px;
    max-height: 400px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    z-index: 100;
}

.game-chat-container.collapsed {
    max-height: 40px;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background: #667eea;
    color: white;
    border-radius: 10px 10px 0 0;
}

.chat-header h4 {
    margin: 0;
    font-size: 1em;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    max-height: 300px;
}

.chat-message {
    margin-bottom: 10px;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 5px;
}

.chat-message.my-message {
    background: #e3f2fd;
    margin-left: 20px;
}

.chat-message-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.8em;
    color: #666;
    margin-bottom: 5px;
}

.chat-username {
    font-weight: bold;
}

.chat-message-text {
    color: #333;
}

.chat-input-container {
    display: flex;
    gap: 5px;
    padding: 10px;
    border-top: 1px solid #e0e0e0;
}

.chat-input-container input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

@media (max-width: 768px) {
    .game-chat-container {
        width: 250px;
        max-height: 300px;
    }
}
```

**Verificación:**
- El chat debe aparecer en la esquina inferior derecha
- Debe poder enviar y recibir mensajes
- Los mensajes propios deben verse diferentes
- Debe poder colapsar/expandir el chat
- Debe hacer scroll automático a nuevos mensajes

---

## ✅ Checklist de Implementación

### Drag & Drop
- [ ] Cartas en mano son arrastrables
- [ ] Zonas de drop muestran indicador visual
- [ ] Validación de zonas válidas funciona
- [ ] Acción se ejecuta al soltar en zona válida

### Animaciones
- [ ] Efecto hover en cartas
- [ ] Animación al arrastrar
- [ ] Animación al jugar carta
- [ ] Animación al recibir daño
- [ ] Animaciones son fluidas (60fps)

### Feedback Visual
- [ ] Mensajes de feedback aparecen
- [ ] Cartas se resaltan al interactuar
- [ ] Zonas se resaltan cuando es relevante
- [ ] Feedback desaparece automáticamente

### Chat
- [ ] Chat aparece en la interfaz
- [ ] Se pueden enviar mensajes
- [ ] Se pueden recibir mensajes
- [ ] Mensajes propios se distinguen
- [ ] Chat se puede colapsar/expandir
- [ ] Validación de mensajes funciona

---

## 🧪 Pruebas a Realizar

### Prueba 1: Drag & Drop
1. Abrir partida
2. Arrastrar carta de la mano
3. Verificar que muestra indicador en zonas válidas
4. Soltar en zona válida
5. Verificar que se juega la carta

### Prueba 2: Animaciones
1. Hacer hover sobre cartas
2. Arrastrar cartas
3. Jugar cartas
4. Verificar que todas las animaciones son fluidas

### Prueba 3: Chat
1. Abrir partida en dos navegadores
2. Enviar mensaje desde uno
3. Verificar que aparece en el otro
4. Verificar que los mensajes propios se distinguen

---

## 🐛 Solución de Problemas Comunes

### Drag & Drop no funciona
- Verificar que `draggable="true"` está en el elemento
- Verificar que los event listeners están agregados
- Verificar consola del navegador para errores

### Animaciones no son fluidas
- Verificar que se usan `transform` y `opacity` (GPU-accelerated)
- Evitar animar `width`, `height`, `top`, `left`
- Usar `will-change` si es necesario

### Chat no envía mensajes
- Verificar que `socket` está definido
- Verificar que `currentGameId` está definido
- Verificar consola del navegador para errores
- Verificar que el servidor acepta el evento `chat_message`

---

## 📝 Notas Importantes

1. **Performance:**
   - Las animaciones deben usar GPU (transform, opacity)
   - Limitar número de mensajes de chat visibles (scroll)
   - No animar demasiados elementos a la vez

2. **Accesibilidad:**
   - Mantener funcionalidad de click como alternativa a drag & drop
   - Agregar `aria-label` a elementos interactivos
   - Asegurar contraste suficiente en textos

3. **UX:**
   - Feedback debe ser claro pero no intrusivo
   - Chat debe ser opcional (colapsable)
   - Animaciones deben ser sutiles

---

## 🎯 Criterios de Éxito

La implementación se considera exitosa cuando:

✅ Drag & drop funciona correctamente  
✅ Animaciones son fluidas y mejoran la UX  
✅ Feedback visual es claro y útil  
✅ Chat funciona entre jugadores  
✅ No se rompe funcionalidad existente  
✅ Código sigue convenciones del proyecto  

---

**Última actualización:** 2025-01-27




