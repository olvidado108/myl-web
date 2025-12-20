# 📊 Información sobre Base de Datos

## ✅ Sistema Migrado a SQLite

El sistema ahora usa **SQLite** como base de datos principal. La migración se completó exitosamente.

### Estado Actual

- ✅ Base de datos SQLite creada: `server/data/cards/cards.db`
- ✅ 3003 cartas migradas desde JSON
- ✅ Servidor actualizado para usar SQLite
- ✅ Todas las operaciones CRUD funcionan con la base de datos

### Ventajas de SQLite (Actual)

1. **Persistencia real** - Los cambios se guardan inmediatamente en la BD
2. **Transacciones** - Operaciones atómicas y seguras
3. **Mejor rendimiento** - Consultas optimizadas con índices
4. **Escalable** - Puede manejar millones de registros
5. **Concurrencia** - Múltiples lecturas simultáneas (WAL mode)

## 📝 Información Histórica

### ¿Por qué se usaba JSON antes?

### ✅ Ventajas de JSON (Actual)

1. **Sin dependencias adicionales** - Solo usa Node.js nativo
2. **Fácil de versionar** - Los archivos JSON se pueden versionar en Git
3. **Rápido para ~3000 cartas** - Con indexación en memoria, las búsquedas son instantáneas
4. **Simple de mantener** - No requiere configuración de base de datos
5. **Portable** - Los datos están en archivos de texto plano

### ⚠️ Desventajas de JSON

1. **Persistencia en memoria** - Los cambios se guardan en archivo, pero se cargan en memoria
2. **No es ideal para múltiples usuarios simultáneos** - Sin transacciones
3. **Escalabilidad limitada** - Para >10k cartas podría ser más lento

## 🔄 Cómo Funciona Ahora

### Estructura de la Base de Datos

La base de datos SQLite tiene una tabla `cartas` con todos los campos necesarios:
- Información básica (id, nombre, tipo, coste)
- Estadísticas de combate (ataque, defensa)
- Metadatos (edición, raza, rareza)
- Imágenes y enlaces

### Operaciones Disponibles

Todas las operaciones CRUD funcionan directamente con SQLite:
- ✅ **Crear** cartas → INSERT en la BD
- ✅ **Leer** cartas → SELECT con índices optimizados
- ✅ **Actualizar** cartas → UPDATE en la BD
- ✅ **Eliminar** cartas → DELETE en la BD
- ✅ **Búsquedas** → Consultas SQL optimizadas

### Índices Creados

Para mejorar el rendimiento, se crearon índices en:
- `tipo` - Búsquedas por tipo de carta
- `raza` - Búsquedas por raza
- `edicion` - Búsquedas por edición
- `rareza` - Búsquedas por rareza
- `nombreNormalizado` - Búsquedas por nombre (case-insensitive)

## 🖼️ Sobre las Imágenes

Las imágenes ahora se cargan automáticamente desde `public/images/cards_organized/` basándose en:
- **Edición** (ej: `espada_sagrada`, `helenica`)
- **Raza** (ej: `caballero`, `dragon`, `sin_raza`)
- **Tipo** (ej: `aliado`, `talisman`, `oro`)

La estructura es: `cards_organized/{edicion}/{raza}/{tipo}/*.png`

El sistema busca automáticamente las imágenes y las asocia a las cartas.

## 🛠️ Mantenimiento

### Backup de la Base de Datos

Para hacer backup de tus cartas:
```bash
# Copiar el archivo de la base de datos
cp server/data/cards/cards.db server/data/cards/cards.db.backup
```

### Restaurar desde Backup

```bash
# Restaurar desde backup
cp server/data/cards/cards.db.backup server/data/cards/cards.db
```

### Ver Contenido de la BD

Puedes usar cualquier cliente SQLite:
- **DB Browser for SQLite** (GUI)
- **sqlite3** (línea de comandos)
- Extensiones de VS Code

## 📊 Estadísticas

- **Total de cartas:** 3003
- **Ediciones:** 5 (dominios_de_ra, es, espada_sagrada, helenica, hijos_de_daana)
- **Tamaño de BD:** ~2-3 MB (depende de los datos)

## ✅ Estado: Sistema Completamente Migrado

El sistema ahora usa SQLite como base de datos principal. Todas las operaciones son persistentes y optimizadas.

