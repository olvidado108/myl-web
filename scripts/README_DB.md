# Repositorio de Cartas - JSON Indexado

## ¿Por qué JSON Indexado?

Para este proyecto, **JSON con indexación en memoria** es la mejor opción porque:

✅ **Sin dependencias** - Solo usa Node.js nativo, no requiere compilación  
✅ **Rápido** - Indexación en memoria para búsquedas instantáneas  
✅ **Simple** - Fácil de entender y mantener  
✅ **Suficiente** - Perfecto para ~3000 cartas  
✅ **Fácil de versionar** - Los JSON se versionan en Git  

## Comparación

| Característica | JSON Simple | JSON Indexado | SQLite |
|---------------|------------|---------------|--------|
| Consultas complejas | ❌ | ✅ | ✅ |
| Búsquedas rápidas | ❌ | ✅ | ✅ |
| Indexación | ❌ | ✅ | ✅ |
| Sin dependencias | ✅ | ✅ | ❌* |
| Fácil de versionar | ✅ | ✅ | ✅ |
| Complejidad | ⭐ | ⭐⭐ | ⭐⭐⭐ |

*SQLite requiere compilación nativa en Windows

## Instalación

No requiere instalación adicional. Solo usa Node.js nativo.

## Uso

### En Node.js

```javascript
const CardRepository = require('./server/repository/CardRepository');

// Crear instancia
const repo = new CardRepository();

// Cargar cartas automáticamente desde todos los JSON disponibles
repo.cargarTodas();

// O cargar desde archivos específicos
repo.cargarDesdeJSON([
    'espada_sagrada.json',
    'helenica.json',
    'hijos_de_daana.json',
    'dominios_de_ra.json'
]);

// Búsquedas
const carta = repo.buscarPorId('es559');
const aliados = repo.buscarPorTipo('Aliado');
const caballeros = repo.buscarPorRaza('Caballero');

// Búsqueda avanzada
const resultados = repo.buscar({
    tipo: 'Aliado',
    raza: 'Caballero',
    edicion: 'espada sagrada',
    limite: 10
});

// Estadísticas
const stats = repo.obtenerEstadisticas();
console.log(stats);
```

## Estructura Interna

### Almacenamiento

- **Map principal**: `cartas` - ID → Carta (acceso O(1))
- **Índices en memoria**: Maps con Sets de IDs para búsquedas rápidas

### Índices

- `porTipo` - tipo → Set de IDs
- `porRaza` - raza → Set de IDs  
- `porEdicion` - edición → Set de IDs
- `porNombre` - nombre normalizado → Set de IDs
- `porRareza` - rareza → Set de IDs

Todas las búsquedas usan estos índices para ser instantáneas.

## Ventajas sobre JSON Simple

1. **Búsquedas rápidas**: Con índices en memoria, las búsquedas son instantáneas
2. **Consultas complejas**: Puedes combinar múltiples filtros fácilmente
3. **Sin dependencias**: Solo usa Node.js nativo
4. **Fácil de mantener**: Código simple y claro
5. **Versionable**: Los JSON se versionan en Git fácilmente

## Rendimiento

- **Carga inicial**: ~100-200ms para 3000 cartas
- **Búsqueda por ID**: O(1) - Instantánea
- **Búsqueda por tipo/raza/edición**: O(1) - Instantánea
- **Búsqueda por nombre parcial**: O(n) pero optimizada con índices

Para 3000 cartas, todas las operaciones son prácticamente instantáneas.

## Próximos Pasos

1. ✅ Implementar CardRepository con JSON indexado
2. ⏭️ Integrar con el juego
3. ⏭️ Agregar API REST para búsquedas
4. ⏭️ Si crece mucho (>10k cartas), considerar migrar a SQLite

## Migración Futura a SQLite

Si en el futuro necesitas SQLite (por ejemplo, si tienes >10k cartas o necesitas persistencia), puedes:
1. Usar `better-sqlite3` (requiere Visual Studio Build Tools en Windows)
2. O usar `sql.js` (SQLite en JavaScript, sin compilación pero más lento)

Por ahora, JSON indexado es perfecto para este proyecto.







