# Mitos y Leyendas - Clon Web

Juego de cartas coleccionable (TCG) para navegador web, inspirado en "Mitos y Leyendas".

## 📊 Estado del Proyecto

**Fase Actual:** Fase 0 ✅ Completada  
**Próxima Fase:** Fase 1 - Prototipo Jugable en Consola

👉 **Ver [PROGRESS.md](./PROGRESS.md) para el estado detallado del proyecto**

## Estructura del Proyecto

```
myl/
├── public/          # Cliente web (HTML, CSS, JS)
│   ├── index.html
│   └── client.js
├── server/          # Servidor Node.js
│   ├── server.js
│   ├── models/      # Modelos de datos
│   │   ├── Card.js
│   │   └── GameState.js
│   └── data/        # Datos del juego
│       └── deck.json
├── package.json
└── README.md
```

## Instalación

1. Instalar dependencias:
```bash
npm install
```

2. Iniciar el servidor:
```bash
npm start
```

3. Abrir en el navegador:
```
http://localhost:3000
```

## 📚 Documentación del Proyecto

- **[GAME_RULES.md](./GAME_RULES.md)** - ⭐ **Reglas oficiales del juego** (LEER PRIMERO)
- **[DECK_CONSTRUCTION_RULES.md](./DECK_CONSTRUCTION_RULES.md)** - ⭐ **Reglas de construcción de mazos** (OBLIGATORIO)
- **[PROGRESS.md](./PROGRESS.md)** - Estado actual, fases completadas y pendientes
- **[ROADMAP.md](./ROADMAP.md)** - Plan detallado de desarrollo por fases
- **[IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md)** - Notas sobre cómo implementar las reglas
- **[CHANGELOG.md](./CHANGELOG.md)** - Historial de cambios importantes
- **[BUGS.md](./BUGS.md)** - Registro de bugs conocidos y resueltos
- **[IMPROVEMENTS.md](./IMPROVEMENTS.md)** - Mejoras sugeridas e ideas futuras

## 🌿 Estrategia de Ramas Git

El proyecto usa un sistema de ramas por fase para mantener control sobre las implementaciones:

- **`main`** - Código estable y probado (producción)
- **`fase-1`** - Desarrollo de Fase 1 (Prototipo en Consola)
- **`fase-2`** - Desarrollo de Fase 2 (Interfaz Gráfica)
- **`fase-3`** - Desarrollo de Fase 3 (Funcionalidades Completas)

**Flujo de trabajo:**
1. Crear rama `fase-X` desde `main`
2. Trabajar en la fase correspondiente
3. Revisar y probar
4. Hacer merge a `main` cuando esté completa y estable

## ✅ Verificación del Proyecto

Antes de comenzar a trabajar, puedes verificar que todo está configurado correctamente:

```bash
npm test
```

Esto ejecutará verificaciones de:
- Modelos de datos (Card, GameState)
- Utilidades del juego
- Mazo de demostración
- Integración de componentes

También puedes ver un ejemplo de uso:
```bash
node server/test/example-usage.js
```

## 🚀 Próximos Pasos (Fase 1)

- Implementar lógica básica del juego en consola
- Sistema de barajar y repartir cartas ✅ Ya implementado
- Bucle de juego por turnos
- IA básica para oponente automático

Ver [ROADMAP.md](./ROADMAP.md) para el plan completo.

## ⚖️ Nota Legal

Este es un proyecto personal/educativo. Para uso comercial se requeriría licencia de Fenix Entertainment.

