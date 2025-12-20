# 📊 Resumen Ejecutivo: Módulo de Usuarios

## 🎯 Visión General

Sistema completo de usuarios para el juego de cartas "Mitos y Leyendas" que incluye autenticación, gestión de mazos, partidas, estadísticas y funcionalidades sociales.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Public)                    │
├─────────────────────────────────────────────────────────┤
│  login.html  │  register.html  │  profile.html         │
│  decks.html  │  games.html     │  stats.html          │
│  leaderboard.html                                      │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                    BACKEND (Server)                      │
├─────────────────────────────────────────────────────────┤
│  Routes: auth.js │ users.js │ decks.js │ games.js       │
│  Controllers: Auth │ User │ Deck │ Game │ Stats         │
│  Repositories: User │ Deck │ Game │ Stats              │
│  Middleware: auth.js │ validateDeck.js                 │
└─────────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────────┐
│              BASE DE DATOS (SQLite)                      │
├─────────────────────────────────────────────────────────┤
│  usuarios │ mazos │ partidas │ estadisticas_usuario    │
│  sesiones │ favoritos                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Componentes Principales

### 1. 🔐 Autenticación
- **Registro**: Crear cuenta nueva
- **Login**: Iniciar sesión con username/email y password
- **JWT Tokens**: Autenticación stateless
- **Sesiones**: Gestión de sesiones activas
- **Cambio de contraseña**: Actualizar credenciales

### 2. 👤 Gestión de Usuarios
- **Perfil**: Ver y editar información personal
- **Avatar**: Imagen de perfil
- **Niveles**: Sistema de progresión
- **Experiencia**: Puntos de experiencia por partidas

### 3. 🃏 Sistema de Mazos
- **Crear**: Constructor visual de mazos
- **Editar**: Modificar mazos existentes
- **Eliminar**: Borrar mazos propios
- **Validar**: Verificar reglas de construcción
- **Duplicar**: Copiar mazos propios o públicos
- **Públicos/Privados**: Compartir o mantener privados

### 4. 🎮 Partidas
- **Crear**: Iniciar nueva partida
- **Jugar**: Realizar acciones en partida
- **Finalizar**: Terminar partida y actualizar estadísticas
- **Historial**: Ver partidas anteriores
- **Reanudar**: Continuar partidas guardadas

### 5. 📊 Estadísticas
- **Personales**: Partidas jugadas, ganadas, perdidas, empatadas
- **Puntuaciones**: Sistema de puntos
- **Rachas**: Racha actual y mejor racha
- **Mazos**: Estadísticas de uso de mazos
- **Rankings**: Posición en leaderboard global

### 6. ⭐ Favoritos
- **Agregar**: Marcar cartas como favoritas
- **Listar**: Ver cartas favoritas
- **Eliminar**: Quitar de favoritos

---

## 🗄️ Base de Datos - Tablas Principales

| Tabla | Propósito | Relaciones |
|-------|-----------|------------|
| `usuarios` | Datos de usuarios | - |
| `mazos` | Mazos de usuarios | → usuarios |
| `partidas` | Partidas jugadas | → usuarios, mazos |
| `estadisticas_usuario` | Estadísticas por usuario | → usuarios |
| `sesiones` | Tokens JWT activos | → usuarios |
| `favoritos` | Cartas favoritas | → usuarios, cartas |

---

## 🔌 APIs Principales

### Autenticación
```
POST   /api/auth/register      - Registro
POST   /api/auth/login         - Login
POST   /api/auth/logout        - Logout
GET    /api/auth/me            - Usuario actual
POST   /api/auth/refresh       - Renovar token
```

### Usuarios
```
GET    /api/users/:id          - Perfil de usuario
PUT    /api/users/:id          - Actualizar perfil
GET    /api/users/:id/stats    - Estadísticas
GET    /api/users/leaderboard  - Ranking
```

### Mazos
```
GET    /api/decks              - Listar mazos
POST   /api/decks              - Crear mazo
GET    /api/decks/:id          - Obtener mazo
PUT    /api/decks/:id          - Actualizar mazo
DELETE /api/decks/:id          - Eliminar mazo
POST   /api/decks/:id/validate - Validar mazo
```

### Partidas
```
POST   /api/games              - Crear partida
GET    /api/games/:id          - Estado de partida
POST   /api/games/:id/actions  - Acción en partida
POST   /api/games/:id/end      - Finalizar partida
GET    /api/games              - Listar partidas
```

### Estadísticas
```
GET    /api/stats/user/:id     - Estadísticas usuario
GET    /api/stats/leaderboard  - Ranking global
```

---

## 🎨 Frontend - Páginas

| Página | Funcionalidad |
|--------|---------------|
| `login.html` | Iniciar sesión |
| `register.html` | Crear cuenta |
| `profile.html` | Perfil y configuración |
| `decks.html` | Lista de mazos |
| `deck-builder.html` | Constructor de mazos |
| `games.html` | Partidas |
| `stats.html` | Estadísticas personales |
| `leaderboard.html` | Rankings globales |

---

## 🔄 Flujos Principales

### Flujo de Registro
```
Usuario → Formulario → POST /api/auth/register
  → Validar datos → Hash password → Crear usuario
  → Generar JWT → Retornar token → Guardar en localStorage
  → Redirigir a perfil
```

### Flujo de Crear Mazo
```
Usuario → Constructor → Agregar cartas → POST /api/decks
  → Validar mazo (50 cartas, oro inicial, etc.)
  → Guardar en BD → Retornar mazo creado
  → Mostrar en lista de mazos
```

### Flujo de Partida
```
Usuario → Seleccionar mazo → POST /api/games
  → Crear GameState → Inicializar partida
  → Jugar turnos → POST /api/games/:id/actions
  → Finalizar → POST /api/games/:id/end
  → Actualizar estadísticas → Mostrar resultado
```

---

## ✅ Validación de Mazos

### Reglas Obligatorias
1. ✅ **50 cartas exactas** en el mazo
2. ✅ **1 Oro Inicial** obligatorio
3. ✅ **Mínimo 15-20 Aliados** (según formato)
4. ✅ **Máximo 3 copias** de cartas normales
5. ✅ **Máximo 1 copia** de cartas únicas
6. ✅ **Raza consistente** (si formato racial)
7. ✅ **Ediciones permitidas** (según formato)

---

## 📊 Sistema de Estadísticas

### Métricas Rastreadas
- Partidas jugadas/ganadas/perdidas/empatadas
- Puntos totales
- Racha de victorias
- Mejor racha de victorias
- Cartas jugadas totales
- Turnos jugados totales
- Tiempo jugado

### Sistema de Puntos
- Victoria: **+10 puntos**
- Derrota: **+1 punto** (participación)
- Empate: **+5 puntos**
- Bonus por racha: **+2 puntos** por racha

---

## 🔒 Seguridad

### Implementado
- ✅ Hash de contraseñas (bcrypt)
- ✅ JWT tokens con expiración
- ✅ Validación de inputs
- ✅ Prepared statements (SQL injection)
- ✅ Sanitización de datos
- ✅ Rate limiting (login/registro)

---

## 🚀 Fases de Implementación

### Fase 1: Base (Semana 1-2)
- Base de datos
- Autenticación básica
- Perfil de usuario

### Fase 2: Mazos (Semana 3-4)
- CRUD de mazos
- Validación de mazos
- Constructor visual

### Fase 3: Partidas (Semana 5-6)
- Sistema de partidas
- Integración con GameState
- Estadísticas básicas

### Fase 4: Avanzado (Semana 7-8)
- Rankings
- Favoritos
- Mejoras UI/UX

---

## 📈 Métricas de Éxito

- ✅ Usuarios pueden registrarse e iniciar sesión
- ✅ Usuarios pueden crear y gestionar mazos
- ✅ Mazos se validan correctamente
- ✅ Partidas se guardan y actualizan estadísticas
- ✅ Estadísticas se muestran correctamente
- ✅ Sistema es seguro y escalable

---

## 🎯 Próximos Pasos

1. **Revisar plan completo** (`USER_MODULE_PLAN.md`)
2. **Decidir prioridades** de implementación
3. **Instalar dependencias** necesarias
4. **Comenzar con Fase 1**: Base de datos y autenticación
5. **Iterar** según feedback

---

**Documento relacionado:** Ver `USER_MODULE_PLAN.md` para detalles completos de implementación.

