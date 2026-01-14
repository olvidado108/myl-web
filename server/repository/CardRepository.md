# 📚 Repositorio de Cartas - Especificación

## Objetivo

Crear un sistema centralizado para gestionar todas las cartas del juego, permitiendo búsqueda, filtrado, validación y acceso eficiente.

## Estructura Propuesta

### Clase CardRepository

```javascript
class CardRepository {
    constructor() {
        this.cartas = new Map(); // ID -> Carta
        this.indices = {
            porTipo: new Map(),
            porRaza: new Map(),
            porEdicion: new Map(),
            porNombre: new Map()
        };
    }
    
    // Cargar cartas desde archivos/BD
    async cargarCartas(rutaArchivos) { }
    
    // Búsquedas
    buscarPorId(id) { }
    buscarPorNombre(nombre, exacto = false) { }
    buscarPorTipo(tipo) { }
    buscarPorRaza(raza) { }
    buscarPorEdicion(edicion) { }
    buscarPorFormato(formato) { }
    
    // Validaciones
    validarCarta(carta) { }
    esCartaValida(carta, formato) { }
    
    // Utilidades
    obtenerTodas() { }
    contarCartas() { }
    obtenerCartasDisponibles(formato) { }
}
```

## Estructura de Datos de Cartas

Cada carta debe tener:

```javascript
{
    id: "carta_001",                    // ID único
    nombre: "Guerrero Valiente",
    tipo: "Aliado",                     // Aliado, Talisman, Oro, Totem, Arma
    subtipo: "Oro Inicial",             // Opcional: para Oros Iniciales
    coste: 2,
    ataque: 3,                          // Solo para Aliados
    defensa: 2,                         // Solo para Aliados
    defensaMaxima: 2,                   // Solo para Aliados
    textoHabilidad: "Sin habilidades",
    imagen: "guerrero_valiente.jpg",
    
    // Metadatos
    edicion: "Helénica",                // Edición de origen
    raza: "Olímpico",                   // Raza (para Aliados)
    rareza: "Común",                    // Común, Rara, Épica, Legendaria
    formato: ["Primer Bloque"],         // Formatos donde está permitida
    restriccion: null,                  // null, "Prohibida", "Limitada"
    
    // Validación
    esUnica: false,                     // Si es carta única (máx 1 copia)
    esOroInicial: false                 // Si es Oro Inicial obligatorio
}
```

## Organización de Archivos

```
server/
├── repository/
│   ├── CardRepository.js          # Clase principal
│   └── CardRepository.md          # Esta especificación
├── data/
│   ├── cards/                     # Cartas por edición
│   │   ├── helenica.json
│   │   ├── nordica.json
│   │   ├── egipcia.json
│   │   └── ...
│   └── deck.json                  # Mazo de demostración (actual)
```

## Funcionalidades Clave

### 1. Carga de Cartas
- Cargar desde archivos JSON
- Validar estructura de cada carta
- Indexar por diferentes criterios para búsqueda rápida

### 2. Búsqueda y Filtrado
- Búsqueda por múltiples criterios
- Combinación de filtros (ej: Aliados Olímpicos de edición Helénica)
- Búsqueda por formato (solo cartas permitidas)

### 3. Validación
- Validar estructura de carta
- Validar si carta es válida para un formato específico
- Verificar restricciones (prohibidas, limitadas)

### 4. Construcción de Mazos
- Obtener cartas disponibles para un formato
- Filtrar por raza y edición según formato
- Validar mazo completo

## Integración con el Juego

El CardRepository será usado por:
- **Constructor de Mazos**: Para buscar y validar cartas
- **GameEngine**: Para crear instancias de cartas durante el juego
- **Validación de Formatos**: Para verificar restricciones
- **Sistema de Búsqueda**: Para que los jugadores encuentren cartas

## Próximos Pasos

1. Crear estructura de archivos
2. Implementar CardRepository básico
3. Migrar cartas actuales a nuevo formato
4. Añadir metadatos (edición, raza, etc.)
5. Implementar búsquedas y filtros
6. Integrar con sistema de construcción de mazos

---

**Última actualización:** 2025-01-27














