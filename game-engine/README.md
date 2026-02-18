# 🎴 Sistema de Habilidades - Mitos y Leyendas

Sistema completo para manejar habilidades de cartas en formato JSON estructurado.

## 📁 Estructura

```
game-engine/
├── abilities/
│   ├── AbilityParser.js       # Parsea texto → JSON estructurado
│   ├── AbilityValidator.js    # Valida estructura de habilidades
│   ├── AbilityExecutor.js     # Ejecuta habilidades durante el juego
│   ├── AbilityManager.js      # Gestor unificado (parser + validator + executor)
│   └── EventSystem.js         # Sistema de eventos para triggers
├── schemas/
│   └── ability-schema.json    # JSON Schema para validación
├── examples/
│   ├── card-abilities.json    # Ejemplos de habilidades
│   └── usage-example.js       # Ejemplos de uso
├── index.js                   # Exportaciones principales
└── INTEGRATION.md             # Guía de integración
```

## 🚀 Inicio Rápido

### Instalación

```javascript
const { AbilityManager, EventSystem } = require('./game-engine');
```

### Uso Básico

```javascript
// 1. Crear manager
const manager = new AbilityManager();

// 2. Procesar una carta
const card = {
    nombre: 'Mago Arcano',
    textoHabilidad: 'Al entrar al campo, roba 1 carta'
};

const processed = manager.processCard(card);
console.log(processed.abilities); // Array de habilidades estructuradas

// 3. Validar
const validation = manager.validate(processed);
console.log(validation.valid); // true/false

// 4. Ejecutar (requiere gameState)
const gameState = new GameState();
manager.setGameState(gameState);

const result = manager.execute(processed.abilities[0], {
    card: card,
    player: 'jugador1'
});
```

## 📚 Documentación

- **[Guía de Integración](./INTEGRATION.md)**: Cómo integrar con tu aplicación
- **[Propuesta del Sistema](../docs/ABILITY_SYSTEM_PROPOSAL.md)**: Diseño y arquitectura
- **[JSON Schema](./schemas/ability-schema.json)**: Especificación completa
- **[Ejemplos](./examples/)**: Ejemplos de uso y habilidades

## 🎯 Características

✅ **Parser**: Convierte texto natural a JSON estructurado  
✅ **Validador**: Valida estructura según JSON Schema  
✅ **Ejecutor**: Ejecuta habilidades durante el juego  
✅ **Gestor Unificado**: Interfaz simple para todo el sistema  
✅ **Sistema de Eventos**: Para triggers y respuestas  
✅ **Integración**: Compatible con modelo Card existente  

## 📝 Formato de Habilidades

Las habilidades se representan en JSON estructurado:

```json
{
  "type": "triggered",
  "trigger": {
    "type": "enters_play",
    "target": "self"
  },
  "effect": {
    "type": "draw_cards",
    "amount": 1,
    "target": "controller"
  },
  "text": "Al entrar al campo, roba 1 carta"
}
```

## 🔧 Componentes

### AbilityParser
Convierte texto de habilidades a formato JSON estructurado.

### AbilityValidator
Valida que las habilidades cumplan con el JSON Schema.

### AbilityExecutor
Ejecuta habilidades durante el juego, respetando reglas y estado.

### AbilityManager
Gestor unificado que coordina parser, validator y executor.

### EventSystem
Sistema de eventos para manejar triggers de habilidades.

## 📖 Ejemplos

Ver `examples/usage-example.js` para ejemplos completos:

```bash
node examples/usage-example.js
```

## 🎮 Integración con el Juego

El sistema está integrado con el modelo `Card.js`. Ver [INTEGRATION.md](./INTEGRATION.md) para detalles.

## 📊 Estado del Proyecto

✅ **Completado**: Parser básico, Validador, Ejecutor básico, Gestor, Eventos, Integración  
⏳ **En progreso**: Parser avanzado, Ejecutor completo, Testing  

## 🤝 Contribuir

Para agregar nuevos tipos de efectos o triggers:

1. Actualizar `schemas/ability-schema.json`
2. Agregar handler en `AbilityExecutor.js`
3. Agregar patrón en `AbilityParser.js` (si aplica)
4. Agregar ejemplos en `examples/card-abilities.json`

## 📄 Licencia

ISC











