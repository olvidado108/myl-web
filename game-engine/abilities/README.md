# 🎴 Sistema de Habilidades - Mitos y Leyendas

Este directorio contiene el sistema de manejo de habilidades para el motor del juego de cartas.

## 📁 Estructura

```
abilities/
├── AbilityParser.js       # Parsea texto de habilidades a JSON estructurado
├── AbilityExecutor.js     # Ejecuta habilidades durante el juego
├── AbilityValidator.js    # Valida estructura de habilidades (TODO)
├── triggers/              # Tipos de triggers (TODO)
├── effects/               # Tipos de efectos (TODO)
└── conditions/            # Condiciones (TODO)
```

## 🚀 Uso Básico

### Validar Habilidades

```javascript
const { AbilityValidator } = require('../index');
const validator = new AbilityValidator();

const abilitiesData = {
  version: "1.0",
  abilities: [
    {
      type: "triggered",
      trigger: { type: "enters_play", target: "self" },
      effect: { type: "draw_cards", amount: 1, target: "controller" }
    }
  ]
};

const validation = validator.validate(abilitiesData);
console.log(validation.valid); // true/false
console.log(validation.errors); // Array de errores
```

### Ejecutar una Habilidad

```javascript
const AbilityExecutor = require('./AbilityExecutor');
const executor = new AbilityExecutor(gameState);

const ability = {
  type: "triggered",
  trigger: { type: "enters_play", target: "self" },
  effect: { type: "draw_cards", amount: 1, target: "controller" }
};

const context = {
  card: cardInstance,
  player: playerId,
  triggeredBy: null
};

const result = executor.execute(ability, context);
console.log(result);
// { success: true, result: { success: true, cardsDrawn: 1 } }
```

## 📝 Formato de Habilidades

Las habilidades se representan en formato JSON estructurado. Ver `../schemas/ability-schema.json` para la especificación completa.

### Tipos de Habilidades

1. **triggered**: Se activan cuando ocurre un evento
2. **static**: Efectos continuos mientras la carta está en juego
3. **activated**: Se activan pagando un costo
4. **response**: Se activan en respuesta a un evento

### Ejemplos

Ver `../examples/card-abilities.json` para ejemplos completos de diferentes tipos de habilidades.

## 🔧 Estado Actual

### ✅ Implementado

- [x] Validador de habilidades (AbilityValidator)
- [x] Ejecutor básico de efectos simples
- [x] Estructura de carpetas
- [x] JSON Schema para validación
- [x] Ejemplos de habilidades
- [x] AbilityManager (gestor unificado)
- [x] EventSystem para triggers
- [x] Integración con modelo Card
- [x] Ejemplos de uso

### ⚠️ Cambios Importantes

- **Parser automático removido**: Las habilidades deben crearse manualmente
- Ver [INSTRUCCIONES_PROCESAMIENTO_MANUAL_HABILIDADES.md](../../docs/INSTRUCCIONES_PROCESAMIENTO_MANUAL_HABILIDADES.md) para el proceso manual

### ⏳ Pendiente

- [ ] Procesamiento manual de todas las cartas
- [ ] Ejecutor completo (todos los efectos avanzados)
- [ ] Sistema de condiciones completo
- [ ] Testing completo con casos reales
- [ ] Optimización de performance

## 📚 Documentación

- [Propuesta del Sistema](../docs/ABILITY_SYSTEM_PROPOSAL.md)
- [JSON Schema](../schemas/ability-schema.json)
- [Ejemplos](../examples/card-abilities.json)

## 🎯 Próximos Pasos

1. Mejorar el parser para casos más complejos
2. Implementar todos los tipos de efectos
3. Crear sistema de eventos para triggers
4. Agregar tests unitarios
5. Integrar con el motor del juego principal

