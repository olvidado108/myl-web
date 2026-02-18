# 📑 Índice de Instrucciones para Agentes

**Documento maestro que lista todas las fases de implementación**

---

## 🎯 Resumen de Fases

Este proyecto se divide en **3 fases principales** de implementación, cada una con sus propias instrucciones detalladas.

---

## 📋 Fase 1: Sistema de Lobby y Emparejamiento

**Prioridad:** 🔴 ALTA  
**Tiempo estimado:** 2-3 semanas  
**Estado:** ⏳ Pendiente

### Objetivo
Implementar un sistema completo de lobby que permita a los jugadores buscar partidas, emparejarse automáticamente y crear partidas privadas.

### Documento de Instrucciones
👉 **`docs/INSTRUCCIONES_AGENTE_FASE1.md`**

### Tareas Principales
- [ ] Crear LobbyManager (Backend)
- [ ] Extender gameSocket.js con eventos de lobby
- [ ] Crear página de lobby (Frontend)
- [ ] Implementar búsqueda de partidas
- [ ] Implementar emparejamiento automático
- [ ] Crear partidas privadas

### Documentos de Referencia
- `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Código completo
- `docs/ANALISIS_DUELING_NEXUS.md` - Contexto y análisis

### Prompt para el Agente
```
Implementa la Fase 1 del sistema de lobby según las instrucciones 
en docs/INSTRUCCIONES_AGENTE_FASE1.md

Usa como referencia:
- docs/IMPLEMENTACION_LOBBY_SISTEMA.md para el código completo
- docs/ARCHITECTURE.md para entender la arquitectura
- El código existente en server/ws/gameSocket.js como referencia
```

---

## 📋 Fase 2: Experiencia de Usuario

**Prioridad:** 🟡 MEDIA  
**Tiempo estimado:** 2-3 semanas  
**Estado:** ⏳ Pendiente

### Objetivo
Mejorar la experiencia de usuario con chat, mejoras visuales, feedback de acciones y animaciones fluidas.

### Documento de Instrucciones
👉 **`docs/INSTRUCCIONES_AGENTE_FASE2.md`**

### Tareas Principales
- [ ] Mejorar drag & drop de cartas
- [ ] Agregar animaciones CSS
- [ ] Implementar feedback visual de acciones
- [ ] Agregar sistema de chat en partida
- [ ] Mejorar UI/UX general

### Documentos de Referencia
- `docs/ANALISIS_DUELING_NEXUS.md` - Secciones sobre UI/UX
- `public/js/game.js` - Código existente del juego
- `public/css/game.css` - Estilos existentes

### Prompt para el Agente
```
Implementa la Fase 2 de mejoras de experiencia de usuario según 
las instrucciones en docs/INSTRUCCIONES_AGENTE_FASE2.md

Asegúrate de:
- No romper funcionalidad existente
- Seguir las convenciones del proyecto
- Probar cada componente antes de continuar
```

---

## 📋 Fase 3: Funcionalidades Avanzadas

**Prioridad:** 🟢 BAJA (pero importante)  
**Tiempo estimado:** 3-4 semanas  
**Estado:** ⏳ Pendiente

### Objetivo
Implementar funcionalidades avanzadas: rankings, replay de partidas, modo práctica vs IA y estadísticas de jugador.

### Documento de Instrucciones
👉 **`docs/INSTRUCCIONES_AGENTE_FASE3.md`**

### Tareas Principales
- [ ] Sistema de rankings y estadísticas
- [ ] Sistema de replay de partidas
- [ ] Modo de práctica vs IA (opcional)
- [ ] Perfil de jugador mejorado

### Documentos de Referencia
- `docs/ANALISIS_DUELING_NEXUS.md` - Plan de implementación
- `server/controllers/GameController.js` - Lógica de partidas
- `server/repository/UserRepository.js` - Gestión de usuarios

### Prompt para el Agente
```
Implementa la Fase 3 de funcionalidades avanzadas según 
las instrucciones en docs/INSTRUCCIONES_AGENTE_FASE3.md

Nota: La implementación de IA es opcional y puede simplificarse.
Enfócate primero en rankings y replays.
```

---

## 📊 Orden Recomendado de Implementación

1. **Fase 1** (Primero) - Sistema de Lobby
   - Es la base para que los jugadores encuentren partidas
   - Sin esto, el juego no es jugable online

2. **Fase 2** (Segundo) - Experiencia de Usuario
   - Mejora significativamente la jugabilidad
   - Hace el juego más atractivo y profesional

3. **Fase 3** (Tercero) - Funcionalidades Avanzadas
   - Agrega valor adicional
   - Puede implementarse parcialmente (rankings primero, IA después)

---

## 🔗 Documentos Relacionados

### Análisis y Planificación
- `docs/ANALISIS_DUELING_NEXUS.md` - Análisis completo de Dueling Nexus
- `docs/RESUMEN_DUELING_NEXUS.md` - Resumen ejecutivo
- `docs/IMPLEMENTACION_LOBBY_SISTEMA.md` - Código de referencia para Fase 1

### Arquitectura y Referencia
- `docs/ARCHITECTURE.md` - Arquitectura del proyecto
- `docs/GAME_RULES.md` - Reglas del juego
- `docs/PROGRESS.md` - Estado actual del proyecto

---

## ✅ Checklist General de Proyecto

### Fase 1: Lobby
- [ ] Sistema de lobby implementado
- [ ] Búsqueda de partidas funciona
- [ ] Emparejamiento automático funciona
- [ ] Partidas privadas funcionan

### Fase 2: UX
- [ ] Drag & drop mejorado
- [ ] Animaciones implementadas
- [ ] Chat en partida funciona
- [ ] Feedback visual implementado

### Fase 3: Avanzado
- [ ] Rankings implementados
- [ ] Replays funcionan
- [ ] Estadísticas de jugador
- [ ] IA básica (opcional)

---

## 🚀 Cómo Usar Estas Instrucciones

1. **Para implementar una fase:**
   - Abre el documento de instrucciones correspondiente
   - Lee la sección "Documentos de Referencia" primero
   - Sigue las tareas en orden
   - Usa el checklist para verificar progreso

2. **Si encuentras problemas:**
   - Revisa la sección "Solución de Problemas Comunes"
   - Consulta los documentos de referencia
   - Revisa el código existente para ver patrones

3. **Al completar una fase:**
   - Verifica el checklist completo
   - Prueba todas las funcionalidades
   - Documenta cualquier cambio o decisión importante

---

## 📝 Notas Importantes

1. **No romper funcionalidad existente:**
   - Cada fase debe mantener compatibilidad con lo anterior
   - Probar exhaustivamente antes de continuar

2. **Seguir convenciones:**
   - Usar el mismo estilo de código
   - Seguir la arquitectura API-First
   - Mantener consistencia en nombres y estructura

3. **Testing:**
   - Probar cada componente individualmente
   - Probar integración completa
   - Probar en diferentes navegadores

---

## 🎯 Criterios de Éxito del Proyecto Completo

El proyecto se considera completo cuando:

✅ Los jugadores pueden buscar y encontrar partidas fácilmente  
✅ La interfaz es intuitiva y agradable de usar  
✅ Las partidas se pueden reproducir y analizar  
✅ Los jugadores tienen estadísticas y rankings  
✅ El juego es estable y funcional  

---

**Última actualización:** 2025-01-27




