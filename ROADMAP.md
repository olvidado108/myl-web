# 🗺️ Roadmap del Proyecto - Mitos y Leyendas Clone

## Visión General
Crear un juego de cartas coleccionable (TCG) para navegador web, inspirado en "Mitos y Leyendas". Arquitectura cliente-servidor para soportar partidas online.

## Fases del Proyecto

### ✅ Fase 0: Preparación y Arquitectura (COMPLETADA)
**Duración estimada:** Semana 1  
**Estado:** ✅ Completada

**Objetivos:**
- Configurar entorno de desarrollo
- Definir estructuras de datos centrales
- Crear mazo de demostración

**Entregables:**
- ✅ Proyecto Node.js inicializado
- ✅ Estructura de carpetas creada
- ✅ Modelos de datos (Card, GameState)
- ✅ Mazo de 30 cartas de ejemplo
- ✅ Servidor básico funcionando

---

### 🚧 Fase 1: Prototipo Jugable en Consola
**Duración estimada:** Semanas 2-3  
**Estado:** Pendiente  
**Rama Git:** `fase-1`

**Objetivos:**
- Implementar lógica central del juego sin interfaz gráfica
- Sistema de comandos básico
- IA básica para oponente

**Tareas Detalladas:**

0. **Repositorio de Cartas**
   - [ ] Crear sistema de repositorio de cartas (CardRepository)
   - [ ] Implementar almacenamiento de cartas (JSON/Base de datos)
   - [ ] Funciones de búsqueda: por ID, tipo, raza, edición, nombre
   - [ ] Funciones de filtrado: por formato, por restricciones
   - [ ] Validación de cartas (estructura, campos requeridos)
   - [ ] Cargar cartas desde archivos/BD
   - [ ] Sistema de metadatos de cartas (edición, raza, rareza, etc.)

1. **Lógica Básica en Node.js**
   - [ ] Función para barajar mazo (Fisher-Yates) ✅ Ya existe
   - [ ] Función para repartir cartas iniciales ✅ Ya existe
   - [ ] Bucle de juego por turnos
   - [ ] Sistema de fases de turno (inicio, robo, preparación, batalla, final)
   - [ ] Gestión de recursos (Oros)
   - [ ] Sistema de robar cartas

2. **Sistema de Comandos**
   - [ ] Comando `jugar [indiceCarta]` - Jugar carta de la mano
   - [ ] Comando `atacar [indiceAliado] [indiceObjetivo]` - Atacar con aliado
   - [ ] Comando `pasar` - Pasar turno
   - [ ] Comando `estado` - Ver estado actual
   - [ ] Comando `mano` - Ver cartas en mano
   - [ ] Comando `campo` - Ver cartas en campo

3. **Lógica de Combate**
   - [ ] Sistema de ataque entre aliados
   - [ ] Sistema de ataque al jugador
   - [ ] Cálculo de daño
   - [ ] Eliminación de cartas (vida <= 0)
   - [ ] Movimiento de cartas al cementerio

4. **Condiciones de Victoria**
   - [ ] Verificar vida <= 0
   - [ ] Declarar ganador
   - [ ] Finalizar partida

5. **IA Básica**
   - [ ] Oponente que juega cartas al azar
   - [ ] Oponente que ataca al azar
   - [ ] Validación de maná disponible

**Hito:** Poder jugar una partida completa (1 jugador vs IA) escribiendo comandos en la terminal.

**Archivos a Crear/Modificar:**
- `server/repository/CardRepository.js` - Repositorio de cartas (búsqueda, filtrado, validación)
- `server/data/cards/` - Carpeta con archivos JSON de cartas por edición
- `server/game/GameEngine.js` - Motor del juego
- `server/game/CommandHandler.js` - Procesador de comandos
- `server/game/AI.js` - IA básica
- `server/game/CombatSystem.js` - Sistema de combate
- `server/cli.js` - Interfaz de línea de comandos

---

### 📋 Fase 2: Interfaz Gráfica Web con Phaser
**Duración estimada:** Semanas 4-6  
**Estado:** Pendiente  
**Rama Git:** `fase-2`

**Objetivos:**
- Migrar el juego a motor gráfico para navegador
- Implementar interfaz visual
- Establecer comunicación cliente-servidor

**Tareas Detalladas:**

1. **Integración de Phaser 3**
   - [ ] Incluir Phaser via CDN o npm
   - [ ] Configurar escena básica
   - [ ] Configurar canvas y dimensiones

2. **Assets y Gráficos**
   - [ ] Cargar imágenes de fondo
   - [ ] Crear placeholders para cartas
   - [ ] Diseñar UI básica (vida, maná, etc.)

3. **Objetos Gráficos**
   - [ ] Clase para representar cartas visualmente
   - [ ] Zona de mano del jugador
   - [ ] Campo de batalla
   - [ ] Marcadores de vida y maná
   - [ ] Botones de acción

4. **Interactividad**
   - [ ] Implementar drag & drop para cartas
   - [ ] Detectar clics en cartas
   - [ ] Selección de objetivos
   - [ ] Animaciones básicas

5. **Comunicación Cliente-Servidor**
   - [ ] Configurar Socket.IO en servidor
   - [ ] Configurar Socket.IO en cliente
   - [ ] Eventos: `jugarCarta`, `atacar`, `pasar`
   - [ ] Sincronización de estado
   - [ ] Actualización de UI en tiempo real

**Hito:** Interfaz gráfica funcional donde se pueden arrastrar cartas y ver actualizaciones en tiempo real.

---

### 📋 Fase 3: Funcionalidades Completas y Publicación
**Duración estimada:** Semanas 7-8+  
**Estado:** Pendiente  
**Rama Git:** `fase-3`

**Objetivos:**
- Añadir características avanzadas
- Pulir experiencia de usuario
- Preparar para despliegue

**Tareas Detalladas:**

1. **Sistema de Mazos**
   - [ ] Interfaz para construir mazos
   - [ ] Guardar mazos en localStorage
   - [ ] Cargar mazos guardados
   - [ ] Validación de mazos (mínimo/máximo cartas)

2. **Habilidades Especiales**
   - [ ] Sistema de procesamiento de habilidades
   - [ ] Implementar habilidades básicas
   - [ ] Sistema de efectos (daño, curación, robo, etc.)

3. **Pulido del Juego**
   - [ ] Animaciones fluidas
   - [ ] Efectos de sonido
   - [ ] Feedback visual claro
   - [ ] Fases de turno bien definidas
   - [ ] Mensajes informativos

4. **Preparación para Despliegue**
   - [ ] Obtener assets gráficos (éticamente)
   - [ ] Optimizar assets
   - [ ] Configurar variables de entorno
   - [ ] Elegir plataforma de hosting
   - [ ] Configurar dominio y HTTPS

**Hito:** Juego completo y desplegado en producción.

---

## 🎯 Criterios de Éxito por Fase

### Fase 1
- ✅ Partida jugable desde consola
- ✅ IA funcional
- ✅ Sistema de combate básico

### Fase 2
- ✅ Interfaz gráfica funcional
- ✅ Drag & drop de cartas
- ✅ Comunicación en tiempo real

### Fase 3
- ✅ Sistema de mazos completo
- ✅ Habilidades especiales funcionando
- ✅ Juego desplegado y accesible

---

## 📚 Recursos y Referencias

- **Phaser 3:** Tutorial "How to Build a Solitaire Game"
- **Socket.IO:** Tutorial de chat básico
- **Datos de Cartas:** Scraper de mitos y leyendas (uso personal/educativo)

---

## ⚠️ Notas Importantes

- Este es un proyecto **personal/educativo**
- Para uso comercial se requeriría licencia de Fenix Entertainment
- Usar assets de manera ética y respetando términos de uso

