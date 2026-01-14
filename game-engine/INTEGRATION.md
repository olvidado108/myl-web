# 🔌 Guía de Integración del Sistema de Habilidades

Esta guía explica cómo integrar el Sistema de Habilidades con tu aplicación existente.

## 📦 Instalación

El sistema está en `game-engine/`. Para usarlo:

```javascript
const { AbilityManager, EventSystem } = require('./game-engine');
```

## 🚀 Uso Básico

### 1. Inicializar el AbilityManager

```javascript
const { AbilityManager } = require('./game-engine');
const manager = new AbilityManager(gameState); // gameState es opcional inicialmente
```

### 2. Procesar una Carta

```javascript
// Desde la base de datos o API
const cardData = {
    id: 'carta_001',
    nombre: 'Mago Arcano',
    tipo: 'Aliado',
    coste: 3,
    fuerza: 2,
    textoHabilidad: 'Al entrar al campo, roba 1 carta',
    imagen: 'mago_arcano.jpg'
};

// Procesar la carta para obtener habilidades estructuradas
const processedCard = manager.processCard(cardData);

// La carta ahora tiene:
// - processedCard.abilities: Array de habilidades en formato JSON
// - processedCard.abilitiesValid: Boolean indicando si son válidas
```

### 3. Integrar con el Modelo Card

El modelo `Card.js` ya está actualizado para soportar habilidades:

```javascript
const Carta = require('./server/models/Card');
const { AbilityManager } = require('./game-engine');

// Crear una carta
const carta = Carta.fromJSON(cardData);

// Procesar sus habilidades
const manager = new AbilityManager();
carta.processAbilities(manager);

// Ahora puedes usar:
// - carta.abilities: Array de habilidades
// - carta.getAbilitiesByType('triggered')
// - carta.getAbilitiesByTrigger('enters_play')
```

## 🎮 Integración con el Motor del Juego

### Durante el Juego

```javascript
const { AbilityManager, EventSystem } = require('./game-engine');
const GameState = require('./server/models/GameState');

// Inicializar
const gameState = new GameState('jugador1', 'jugador2');
const manager = new AbilityManager(gameState);
const eventSystem = new EventSystem();

// Cuando una carta entra en juego
function onCardEntersPlay(card, player) {
    // Obtener habilidades triggered con trigger 'enters_play'
    const entersPlayAbilities = card.getAbilitiesByTrigger('enters_play');
    
    // Ejecutar cada habilidad
    entersPlayAbilities.forEach(ability => {
        const context = {
            card: card,
            player: player,
            triggeredBy: null
        };
        
        const result = manager.execute(ability, context);
        if (result.success) {
            console.log(`Habilidad ejecutada: ${ability.text}`);
        }
    });
    
    // Emitir evento para otros sistemas
    eventSystem.emit('enters_play', { card, player });
}
```

### Sistema de Eventos

```javascript
const eventSystem = new EventSystem();

// Registrar listeners para triggers
eventSystem.on('enters_play', (data) => {
    const { card, player } = data;
    const abilities = card.getAbilitiesByTrigger('enters_play');
    // Procesar habilidades...
});

eventSystem.on('attacks', (data) => {
    const { attacker, target } = data;
    // Procesar habilidades de ataque...
});

// Emitir eventos cuando ocurren
eventSystem.emit('enters_play', { card, player });
eventSystem.emit('attacks', { attacker, target });
```

## 🔄 Flujo Completo

### 1. Al Cargar Cartas desde la Base de Datos

```javascript
const CardRepository = require('./server/repository/CardRepositorySQLite');
const { AbilityManager } = require('./game-engine');

const repo = new CardRepository();
const manager = new AbilityManager();

// Obtener carta
const cardData = await repo.buscarPorId('carta_001');

// Procesar habilidades
const card = Carta.fromJSON(cardData);
card.processAbilities(manager);

// Guardar habilidades procesadas (opcional, para caché)
// Puedes guardar card.abilities en la BD o en memoria
```

### 2. Durante el Juego

```javascript
// Cuando se juega una carta
function playCard(card, player) {
    // 1. Verificar si se puede jugar
    if (!canPlayCard(card, player)) {
        return false;
    }
    
    // 2. Pagar coste
    gameState.spendResources(player, card.coste);
    
    // 3. Poner carta en juego
    gameState.putCardInPlay(card, player);
    
    // 4. Activar habilidades "enters_play"
    const entersPlayAbilities = card.getAbilitiesByTrigger('enters_play');
    entersPlayAbilities.forEach(ability => {
        manager.execute(ability, {
            card: card,
            player: player
        });
    });
    
    // 5. Emitir evento
    eventSystem.emit('enters_play', { card, player });
    
    return true;
}
```

## 📊 Almacenamiento de Habilidades

### Opción 1: Procesar al Vuelo (Recomendado para empezar)

```javascript
// Procesar habilidades cuando se necesiten
const card = await repo.buscarPorId('carta_001');
card.processAbilities(manager);
// Usar card.abilities
```

### Opción 2: Pre-procesar y Guardar

```javascript
// Procesar todas las cartas y guardar habilidades en BD
const allCards = await repo.buscarTodas();
const manager = new AbilityManager();

for (const card of allCards) {
    card.processAbilities(manager);
    
    // Guardar habilidades procesadas
    await repo.updateCardAbilities(card.id, card.abilities);
}
```

### Opción 3: Caché en Memoria

```javascript
// Caché de habilidades procesadas
const abilitiesCache = new Map();

function getCardAbilities(cardId) {
    if (abilitiesCache.has(cardId)) {
        return abilitiesCache.get(cardId);
    }
    
    const card = await repo.buscarPorId(cardId);
    card.processAbilities(manager);
    abilitiesCache.set(cardId, card.abilities);
    
    return card.abilities;
}
```

## 🎯 Mejores Prácticas

1. **Inicializar AbilityManager una vez**: Crear una instancia al inicio y reutilizarla
2. **Validar habilidades**: Usar `validate()` antes de ejecutar habilidades críticas
3. **Manejar errores**: Siempre verificar `result.success` después de ejecutar
4. **Usar eventos**: El EventSystem permite desacoplar la lógica de habilidades
5. **Caché cuando sea posible**: Procesar habilidades una vez y reutilizar

## 🔧 Extensión del Sistema

### Agregar Nuevos Tipos de Efectos

1. Agregar al JSON Schema (`schemas/ability-schema.json`)
2. Agregar handler en `AbilityExecutor.js`
3. Agregar patrón en `AbilityParser.js` (si aplica)

### Agregar Nuevos Triggers

1. Agregar al JSON Schema
2. Agregar patrón en `AbilityParser.js`
3. Emitir evento correspondiente en el motor del juego

## 📝 Ejemplo Completo

Ver `examples/usage-example.js` para ejemplos completos de uso.









