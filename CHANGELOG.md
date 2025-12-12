# 📝 Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.1.0] - 2025-01-27

### ✅ Completado - Fase 0

#### Añadido
- Estructura inicial del proyecto
- Servidor Express básico (`server/server.js`)
- Cliente web básico (`public/index.html`, `public/client.js`)
- Modelo de datos `Card` (`server/models/Card.js`)
- Modelo de datos `GameState` (`server/models/GameState.js`)
- Mazo de demostración con 30 cartas (`server/data/deck.json`)
- Utilidades del juego (`server/utils/gameUtils.js`):
  - Función `barajar()` - Algoritmo Fisher-Yates
  - Función `repartirCartasIniciales()` - Reparte cartas al inicio
  - Función `robarCarta()` - Roba una carta del mazo
  - Función `calcularManaMaximo()` - Calcula maná por turno
- Configuración de Git y repositorio remoto
- Documentación inicial (README.md, PROGRESS.md, ROADMAP.md)

#### Configuración
- `package.json` con dependencias: Express, Socket.IO
- `.gitignore` configurado
- Repositorio Git inicializado y conectado a GitHub

---

## [Unreleased]

### Próximas características (Fase 1)
- Sistema de comandos básico
- Bucle de juego por turnos
- Sistema de combate
- IA básica para oponente

---

## Tipos de Cambios

- **Añadido** para nuevas características
- **Modificado** para cambios en funcionalidades existentes
- **Deprecado** para características que pronto serán eliminadas
- **Eliminado** para características eliminadas
- **Corregido** para corrección de bugs
- **Seguridad** para vulnerabilidades

