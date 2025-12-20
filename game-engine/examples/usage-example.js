/**
 * Ejemplos de uso del Sistema de Habilidades
 * 
 * Este archivo muestra cómo usar el sistema de habilidades
 * para parsear, validar y ejecutar habilidades de cartas.
 */

const { AbilityManager, EventSystem } = require('../index');

// Ejemplo 1: Parsear y validar una habilidad simple
console.log('=== Ejemplo 1: Parsear y validar habilidad ===');
const manager = new AbilityManager();

const textoHabilidad = "Al entrar al campo, roba 1 carta";
const result = manager.parseAndValidate(textoHabilidad);

console.log('Texto:', textoHabilidad);
console.log('Válido:', result.valid);
console.log('Habilidades parseadas:', JSON.stringify(result.abilities, null, 2));

if (result.errors.length > 0) {
    console.log('Errores:', result.errors);
}

// Ejemplo 2: Procesar una carta completa
console.log('\n=== Ejemplo 2: Procesar carta completa ===');
const card = {
    id: 'carta_001',
    nombre: 'Mago Arcano',
    tipo: 'Aliado',
    coste: 3,
    fuerza: 2,
    textoHabilidad: 'Al entrar al campo, roba 1 carta',
    imagen: 'mago_arcano.jpg'
};

const processedCard = manager.processCard(card);
console.log('Carta procesada:');
console.log('- Nombre:', processedCard.nombre);
console.log('- Habilidades válidas:', processedCard.abilitiesValid);
console.log('- Número de habilidades:', processedCard.abilities.length);
console.log('- Habilidades:', JSON.stringify(processedCard.abilities, null, 2));

// Ejemplo 3: Obtener habilidades por tipo
console.log('\n=== Ejemplo 3: Filtrar habilidades por tipo ===');
const card2 = {
    id: 'carta_002',
    nombre: 'Rey Arturo',
    tipo: 'Aliado',
    coste: 5,
    fuerza: 4,
    textoHabilidad: 'Al entrar al campo, roba 1 carta. Mientras está en juego, todos los Caballeros ganan +1 a la fuerza.',
    imagen: 'rey_arturo.jpg'
};

const processedCard2 = manager.processCard(card2);
const triggeredAbilities = manager.getAbilitiesByType(processedCard2.abilities, 'triggered');
const staticAbilities = manager.getAbilitiesByType(processedCard2.abilities, 'static');

console.log('Carta:', processedCard2.nombre);
console.log('Habilidades triggered:', triggeredAbilities.length);
console.log('Habilidades static:', staticAbilities.length);

// Ejemplo 4: Sistema de eventos
console.log('\n=== Ejemplo 4: Sistema de eventos ===');
const eventSystem = new EventSystem();

// Registrar listener para evento 'enters_play'
eventSystem.on('enters_play', (data) => {
    console.log('Evento enters_play:', data);
});

// Emitir evento
eventSystem.emit('enters_play', {
    card: { id: 'carta_001', nombre: 'Mago Arcano' },
    player: 'jugador1'
});

// Ejemplo 5: Habilidad compleja
console.log('\n=== Ejemplo 5: Habilidad compleja ===');
const textoComplejo = "En respuesta a que un Aliado que controles salga del juego por un efecto oponente, busca un Aliado de igual o menor coste en tu Mazo Castillo y ponlo en tu Mano.";

const resultComplejo = manager.parseAndValidate(textoComplejo);
console.log('Texto complejo:', textoComplejo);
console.log('Válido:', resultComplejo.valid);
console.log('Habilidades:', JSON.stringify(resultComplejo.abilities, null, 2));

if (resultComplejo.errors.length > 0) {
    console.log('Errores:', resultComplejo.errors);
}

console.log('\n=== Ejemplos completados ===');




