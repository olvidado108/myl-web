# 🤖 Guía para Agentes de IA

Este documento ayuda a los agentes de IA a entender rápidamente el estado del proyecto y qué hacer a continuación.

## 📖 Archivos Clave a Revisar

Cuando un nuevo agente se une al proyecto, debe leer estos archivos en orden:

1. **ARCHITECTURE.md** - ⭐ **ARQUITECTURA Y PRINCIPIOS** (LEER PRIMERO)
2. **PROGRESS.md** - Estado actual del proyecto, qué está completado y qué falta
3. **ROADMAP.md** - Plan detallado de lo que se debe hacer en cada fase
4. **BUGS.md** - Bugs conocidos que necesitan atención
5. **IMPROVEMENTS.md** - Mejoras sugeridas
6. **CHANGELOG.md** - Historial de cambios recientes

## 🎯 Estado Actual del Proyecto

**Última actualización:** Ver PROGRESS.md

**Fase Actual:** Fase 0 ✅ Completada  
**Próxima Fase:** Fase 1 - Prototipo Jugable en Consola

## 🌿 Sistema de Ramas

- **Rama actual:** `fase-1` (para trabajar en Fase 1)
- **Rama principal:** `main` (código estable)

**IMPORTANTE:** Siempre trabajar en la rama de la fase correspondiente, NO directamente en `main`.

## 🔄 Flujo de Trabajo Recomendado

1. **Leer PROGRESS.md** para entender el estado actual
2. **Leer ROADMAP.md** para ver las tareas de la fase actual
3. **Revisar BUGS.md** para ver si hay bugs que resolver
4. **Trabajar en la rama correspondiente** (ej: `fase-1`)
5. **Actualizar PROGRESS.md** cuando completes tareas
6. **Actualizar CHANGELOG.md** cuando hagas cambios importantes
7. **Hacer commits descriptivos** con mensajes claros

## 📝 Cómo Actualizar la Documentación

### Al Completar una Tarea:
1. Marca la tarea como completada en `PROGRESS.md` o `ROADMAP.md`
2. Si es un cambio importante, añádelo a `CHANGELOG.md`

### Al Encontrar un Bug:
1. Añádelo a `BUGS.md` con el formato especificado
2. Si es crítico, trabaja en resolverlo primero

### Al Tener una Idea de Mejora:
1. Añádela a `IMPROVEMENTS.md`
2. Discute con el usuario si es prioritaria

### Al Completar una Fase:
1. Actualiza `PROGRESS.md` marcando la fase como completada
2. Añade un resumen a `CHANGELOG.md`
3. Haz merge de la rama `fase-X` a `main`
4. Crea la siguiente rama `fase-Y` para la próxima fase

## 🚨 Reglas Importantes

1. **⭐ API-FIRST**: TODAS las funcionalidades deben ser APIs REST (ver ARCHITECTURE.md)
2. **NUNCA** trabajar directamente en `main` (excepto para merges)
3. **SIEMPRE** actualizar la documentación cuando hagas cambios
4. **SIEMPRE** hacer commits descriptivos
5. **SIEMPRE** revisar `PROGRESS.md` antes de empezar a trabajar
6. **SIEMPRE** preguntar al usuario si algo no está claro

## 📋 Checklist para Nuevos Agentes

- [ ] Leer `ARCHITECTURE.md` completamente ⭐ (CRÍTICO)
- [ ] Leer `PROGRESS.md` completamente
- [ ] Leer `ROADMAP.md` para la fase actual
- [ ] Revisar `BUGS.md` para bugs pendientes
- [ ] Verificar en qué rama estamos (`git branch`)
- [ ] Entender qué tareas están pendientes
- [ ] Confirmar con el usuario antes de hacer cambios grandes
- [ ] Recordar: API-First para todas las funcionalidades

## 🎯 Preguntas Frecuentes

**P: ¿En qué rama debo trabajar?**  
R: Verifica con `git branch`. Deberías estar en `fase-X` donde X es el número de la fase actual.

**P: ¿Cómo sé qué hacer a continuación?**  
R: Lee `PROGRESS.md` y `ROADMAP.md`. Las tareas pendientes están marcadas con `[ ]`.

**P: ¿Debo actualizar la documentación?**  
R: Sí, siempre. Especialmente `PROGRESS.md` cuando completes tareas.

**P: ¿Qué hago si encuentro un bug?**  
R: Añádelo a `BUGS.md` y pregunta al usuario si debe resolverse inmediatamente.

**P: ¿Puedo hacer merge a main?**  
R: Solo cuando una fase esté completamente terminada y probada. Pregunta al usuario primero.

## 🔗 Enlaces Útiles

- Repositorio: https://github.com/OLVIDADO108/myl-web.git
- Servidor local: http://localhost:3000
- Email del desarrollador: hucarrz@gmail.com

---

**Última actualización de esta guía:** 2025-01-27






