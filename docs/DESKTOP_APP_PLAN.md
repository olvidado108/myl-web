# 🖥️ Plan: Aplicación de Escritorio Windows

## 📋 Resumen Ejecutivo

Migrar la parte del juego a una aplicación de escritorio Windows que se conecte a los servicios web existentes (APIs REST + WebSocket). La página web se mantiene para gestión de mazos, perfil de usuario, administración y otras operaciones.

---

## 🎯 Objetivos

1. **Aplicación de escritorio nativa** para Windows que ejecute el juego
2. **Reutilizar infraestructura existente**: APIs REST, WebSocket, autenticación
3. **Mantener página web** para operaciones complementarias (mazos, perfil, admin)
4. **Experiencia de usuario mejorada** en escritorio (mejor rendimiento, notificaciones, etc.)

---

## 🏗️ Arquitectura Propuesta

### Opción Recomendada: **Electron**

#### ¿Por qué Electron?

✅ **Ventajas:**
- Reutiliza código JavaScript existente (`ApiClient`, lógica de juego)
- Mismo stack tecnológico (HTML/CSS/JS)
- Desarrollo rápido y familiar
- Acceso a APIs nativas de Windows (notificaciones, sistema de archivos)
- Fácil empaquetado y distribución
- Multiplataforma potencial (Windows, macOS, Linux)

⚠️ **Desventajas:**
- Tamaño de aplicación más grande (~100-150 MB)
- Consumo de memoria moderado

#### Alternativas Consideradas:

| Tecnología | Pros | Contras | Decisión |
|------------|------|---------|----------|
| **Electron** | Reutiliza JS, rápido desarrollo | Tamaño mayor | ✅ **RECOMENDADO** |
| **Tauri** | Más ligero, mejor rendimiento | Requiere Rust, más complejo | ❌ |
| **Godot** | Ya iniciado, buen rendimiento | Requiere reescribir en GDScript | ❌ |
| **.NET/WPF** | Nativo Windows | Requiere reescribir todo en C# | ❌ |

---

## 📐 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR WEB (Node.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  APIs REST   │  │  WebSocket   │  │  SQLite DB   │      │
│  │  (Express)   │  │ (Socket.IO)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         │                        │
         │                        │
    ┌────┴────┐              ┌────┴────┐
    │         │              │         │
┌───▼───┐ ┌──▼────┐    ┌────▼────┐ ┌──▼────┐
│  WEB  │ │ DESKTOP│    │  WEB   │ │DESKTOP│
│ CLIENT│ │  APP   │    │ CLIENT │ │  APP  │
│       │ │        │    │        │ │       │
│ - Mazos│ │ - Juego│    │ - Perfil│ │ - Juego│
│ - Admin│ │ - Partidas│ │ - Stats │ │ - Partidas│
└───────┘ └────────┘    └────────┘ └────────┘
```

### Separación de Responsabilidades

**Página Web (`public/`):**
- ✅ Gestión de mazos (crear, editar, eliminar)
- ✅ Perfil de usuario
- ✅ Estadísticas y leaderboard
- ✅ Administración de usuarios
- ✅ Revisión de cartas y tags
- ✅ Catálogo de cartas

**Aplicación de Escritorio (`desktop-app/`):**
- ✅ Jugar partidas
- ✅ Lobby de partidas
- ✅ Ver estado de partidas en curso
- ✅ Historial de partidas
- ✅ Notificaciones de turnos
- ✅ Chat en partida (opcional)

---

## 📁 Estructura del Proyecto

```
myl/
├── server/              # Servidor (sin cambios)
│   ├── routes/         # APIs REST
│   ├── ws/             # WebSocket
│   └── ...
├── public/             # Página web (mantener)
│   ├── deck-builder.html
│   ├── profile.html
│   └── ...
├── desktop-app/        # 🆕 NUEVA: Aplicación Electron
│   ├── package.json
│   ├── main.js         # Proceso principal (Node.js)
│   ├── preload.js      # Script de precarga (seguridad)
│   ├── renderer/       # Proceso de renderizado (HTML/JS)
│   │   ├── index.html
│   │   ├── css/
│   │   ├── js/
│   │   │   ├── api.js      # Reutilizar ApiClient
│   │   │   ├── game.js      # Lógica de juego
│   │   │   └── ws-client.js # Cliente WebSocket
│   │   └── assets/
│   ├── assets/         # Iconos, imágenes
│   └── build/          # Scripts de build
│       └── build.js    # Electron Builder config
└── ...
```

---

## 🔧 Implementación Técnica

### 1. Configuración de Electron

**`desktop-app/package.json`:**
```json
{
  "name": "myl-desktop",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win"
  },
  "dependencies": {
    "electron": "^latest",
    "socket.io-client": "^4.7.5"
  },
  "devDependencies": {
    "electron-builder": "^latest"
  }
}
```

### 2. Proceso Principal (`main.js`)

- Crear ventana de aplicación
- Manejar autenticación (guardar token en almacenamiento seguro)
- Configurar menú de aplicación
- Manejar notificaciones del sistema
- Gestionar actualizaciones automáticas (opcional)

### 3. Proceso de Renderizado (`renderer/`)

**Reutilizar código existente:**
- ✅ `ApiClient` de `public/js/api.js` (con mínimas modificaciones)
- ✅ Lógica de juego de `public/js/game.js`
- ✅ Estilos CSS adaptados

**Modificaciones necesarias:**
- Cambiar `localStorage` por `electron-store` para persistencia
- Adaptar URLs de API (configuración de servidor)
- Integrar notificaciones nativas de Windows

### 4. Comunicación con Servidor

**APIs REST:**
```javascript
// En desktop-app/renderer/js/api.js
const ApiClient = require('../../shared/api-client');

const api = new ApiClient('http://localhost:3000'); // o URL de producción
// Reutiliza toda la lógica existente
```

**WebSocket:**
```javascript
// En desktop-app/renderer/js/ws-client.js
const io = require('socket.io-client');

const socket = io('http://localhost:3000', {
  auth: {
    token: api.getToken()
  }
});
// Misma lógica que en web
```

---

## 🔐 Autenticación

### Flujo Propuesto:

1. **Primera vez:**
   - Usuario abre aplicación
   - Se muestra pantalla de login
   - Usuario ingresa credenciales
   - Token JWT se guarda en `electron-store` (almacenamiento seguro)

2. **Sesiones siguientes:**
   - Aplicación verifica token guardado
   - Si es válido, inicia sesión automáticamente
   - Si expiró, solicita login nuevamente

3. **Logout:**
   - Elimina token del almacenamiento
   - Vuelve a pantalla de login

### Almacenamiento Seguro:

```javascript
// Usar electron-store en lugar de localStorage
const Store = require('electron-store');
const store = new Store();

// Guardar token
store.set('auth_token', token);

// Leer token
const token = store.get('auth_token');
```

---

## 🎨 Interfaz de Usuario

### Pantallas Principales:

1. **Login/Registro**
   - Formulario de autenticación
   - Opción de "Recordar sesión"

2. **Lobby**
   - Lista de partidas disponibles
   - Crear nueva partida
   - Unirse a partida existente
   - Historial de partidas

3. **Partida**
   - Tablero de juego
   - Mano de cartas
   - Campo de batalla
   - Información del oponente
   - Chat (opcional)

4. **Configuración**
   - URL del servidor
   - Preferencias de notificaciones
   - Configuración gráfica

### Diseño:

- Reutilizar estilos CSS existentes de `public/css/game.css`
- Adaptar para ventana de escritorio (no navegador)
- Aprovechar espacio de pantalla completa

---

## 📦 Distribución

### Electron Builder

**Configuración (`build/electron-builder.config.js`):**
```javascript
module.exports = {
  appId: 'com.myl.desktop',
  productName: 'Mitos y Leyendas',
  directories: {
    output: 'dist'
  },
  win: {
    target: 'nsis',
    icon: 'assets/icon.ico'
  },
  nsis: {
    oneClick: false,
    allowToChangeInstallationDirectory: true
  }
};
```

**Resultado:**
- Instalador `.exe` para Windows
- Actualizaciones automáticas (opcional con `electron-updater`)

---

## 🚀 Plan de Implementación

### Fase 1: Setup Inicial (1-2 días)
- [ ] Crear estructura de proyecto `desktop-app/`
- [ ] Configurar Electron básico
- [ ] Crear ventana principal
- [ ] Configurar build system

### Fase 2: Autenticación (1 día)
- [ ] Implementar pantalla de login
- [ ] Integrar `ApiClient` con almacenamiento seguro
- [ ] Manejar sesiones persistentes

### Fase 3: Integración de APIs (2-3 días)
- [ ] Adaptar `ApiClient` para Electron
- [ ] Implementar cliente WebSocket
- [ ] Probar conexión con servidor

### Fase 4: Interfaz de Juego (3-5 días)
- [ ] Crear lobby de partidas
- [ ] Implementar pantalla de partida
- [ ] Integrar lógica de juego existente
- [ ] Adaptar estilos CSS

### Fase 5: Funcionalidades Adicionales (2-3 días)
- [ ] Notificaciones del sistema
- [ ] Configuración de aplicación
- [ ] Manejo de errores y reconexión

### Fase 6: Build y Distribución (1-2 días)
- [ ] Configurar Electron Builder
- [ ] Crear instalador Windows
- [ ] Testing en diferentes versiones de Windows

**Total estimado: 10-16 días de desarrollo**

---

## 🔄 Migración desde Web

### Código Reutilizable (sin cambios):

✅ `server/` - Todo el backend
✅ `public/js/api.js` - Cliente API (con mínimas modificaciones)
✅ `public/js/game.js` - Lógica de juego
✅ `public/css/game.css` - Estilos del juego

### Código a Adaptar:

⚠️ `public/js/game.js` - Cambiar `localStorage` por `electron-store`
⚠️ URLs de API - Hacer configurables
⚠️ WebSocket - Mismo código, solo cambiar inicialización

### Código Específico de Web (mantener):

✅ `public/deck-builder.html` - Constructor de mazos
✅ `public/profile.html` - Perfil de usuario
✅ `public/admin-users.html` - Administración

---

## 🎯 Ventajas de esta Arquitectura

1. **Reutilización máxima**: ~70-80% del código existente
2. **Mantenimiento simple**: Cambios en servidor benefician ambos clientes
3. **Experiencia mejorada**: Notificaciones, mejor rendimiento en escritorio
4. **Flexibilidad**: Usuarios pueden elegir web o desktop
5. **Escalabilidad**: Fácil agregar más clientes (mobile, etc.)

---

## ❓ Preguntas para Decidir

1. **¿URL del servidor será configurable o fija?**
   - Recomendación: Configurable (permite desarrollo y producción)

2. **¿Actualizaciones automáticas?**
   - Recomendación: Sí, con `electron-updater`

3. **¿Soporte offline?**
   - Inicialmente: No (requiere conexión al servidor)
   - Futuro: Cache de cartas, modo offline limitado

4. **¿Multiplataforma (macOS, Linux)?**
   - Inicialmente: Solo Windows
   - Futuro: Fácil extender con Electron

---

## 📝 Próximos Pasos

1. **Revisar y aprobar este plan**
2. **Decidir sobre preguntas pendientes**
3. **Crear rama Git**: `desktop-app`
4. **Iniciar Fase 1**: Setup inicial de Electron

---

## 📚 Recursos

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [electron-store](https://github.com/sindresorhus/electron-store)
- [Socket.IO Client](https://socket.io/docs/v4/client-api/)

---

**¿Estás de acuerdo con este plan? ¿Alguna modificación o pregunta antes de comenzar?**




