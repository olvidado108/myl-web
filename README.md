# Mitos y Leyendas - Clon Web

Juego de cartas coleccionable (TCG) para navegador web, inspirado en "Mitos y Leyendas".

## 📊 Estado del Proyecto

**Fase actual:** Fase 1 - Prototipo Jugable en Consola 🚧 En progreso  
**Rama activa:** `fase-1`  
**Próxima fase:** Fase 2 - Interfaz Gráfica Web con Phaser

👉 **Ver [docs/PROGRESS.md](./docs/PROGRESS.md) para el estado detallado del proyecto**

## 🚀 Puesta en marcha rápida

1. Instalar dependencias:
```bash
npm install
```

2. Iniciar API y cliente estático:
```bash
npm start
```

3. Abrir en el navegador: `http://localhost:3000`

4. Verificación rápida (smoke test):
```bash
npm test
```

Ejemplo de uso mínimo:
```bash
node server/test/example-usage.js
```

## 📁 Estructura del Proyecto

```
myl/
├── docs/              # Toda la documentación (ver DOCUMENTATION.md)
├── server/            # API REST + Socket.IO + SQLite
│   ├── controllers/   # Rutas Express
│   ├── repository/    # Acceso a datos (Cartas, Mazos, Usuarios)
│   ├── ws/            # Eventos de juego por WebSocket
│   └── data/          # Bases SQLite y JSON de cartas
├── public/            # Cliente web (HTML, CSS, JS)
│   ├── js/, css/, images/...
│   └── cards.html, game.html, etc.
├── game-engine/       # Motor de reglas aislado (WIP)
├── godot/             # Prototipo de interfaz en Godot
├── scripts/           # Scripts utilitarios (tests, descargas, tooling)
├── DOCUMENTATION.md   # Índice completo de docs
└── README.md
```

## 📚 Documentación del Proyecto

**📁 Toda la documentación está en la carpeta [`docs/`](./docs/)** o en el índice raíz [`DOCUMENTATION.md`](./DOCUMENTATION.md)

### Documentos Principales:
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - ⭐ Arquitectura y principios (LEER PRIMERO)
- **[docs/GAME_RULES.md](./docs/GAME_RULES.md)** - ⭐ Reglas oficiales del juego (LEER PRIMERO)
- **[docs/DECK_CONSTRUCTION_RULES.md](./docs/DECK_CONSTRUCTION_RULES.md)** - ⭐ Reglas de construcción de mazos (OBLIGATORIO)
- **[docs/PROGRESS.md](./docs/PROGRESS.md)** - Estado actual, fases completadas y pendientes
- **[docs/ROADMAP.md](./docs/ROADMAP.md)** - Plan detallado de desarrollo por fases
- **Módulo de usuarios:** Índice maestro en [docs/USER_MODULE_INDEX.md](./docs/USER_MODULE_INDEX.md)

## 🌿 Estrategia de Ramas Git

El proyecto usa un sistema de ramas por fase:

- **`main`** - Código estable y probado (producción)
- **`fase-1`** - Desarrollo de Fase 1 (prototipo en consola)
- **`fase-2`** - Desarrollo de Fase 2 (interfaz gráfica web)
- **`fase-3`** - Desarrollo de Fase 3 (funcionalidades completas)

**Flujo de trabajo:**
1. Crear rama `fase-X` desde `main`
2. Trabajar en la fase correspondiente
3. Revisar y probar
4. Hacer merge a `main` cuando esté completa y estable

## ✅ Verificación del Proyecto

`npm test` ejecuta el smoke test de modelos, utilidades y mazos de demo.  
`node server/test/example-usage.js` muestra un flujo mínimo de uso.

## 🚀 Próximos Pasos (Fase 1)

- [ ] CardRepository y carga de cartas desde SQLite
- [ ] Lógica básica en Node.js y bucle de turnos
- [ ] Comandos de consola: `jugar`, `atacar`, `pasar`
- [ ] Condiciones de victoria
- [ ] IA básica para oponente automático
- [x] Barajar y repartir cartas (`server/utils/gameUtils.js`)

Ver [docs/ROADMAP.md](./docs/ROADMAP.md) para el plan completo.

## ⚖️ Nota Legal

Este es un proyecto personal/educativo. Para uso comercial se requeriría licencia de Fenix Entertainment.

