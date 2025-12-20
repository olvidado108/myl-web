/**
 * Ejemplo de uso de los componentes del juego
 * Muestra cómo se usarían Card, GameState y las utilidades juntas
 */

const Carta = require('../models/Card');
const GameState = require('../models/GameState');
const { barajar, repartirCartasIniciales, calcularManaMaximo } = require('../utils/gameUtils');
const fs = require('fs');
const path = require('path');

console.log('🎮 Ejemplo de uso de los componentes del juego\n');

// 1. Cargar el mazo
console.log('1️⃣ Cargando mazo de demostración...');
const deckPath = path.join(__dirname, '../data/deck.json');
const deckData = JSON.parse(fs.readFileSync(deckPath, 'utf8'));
const mazo = deckData.map(cartaData => Carta.fromJSON(cartaData));
console.log(`   ✅ Mazo cargado: ${mazo.length} cartas\n`);

// 2. Crear un estado de juego
console.log('2️⃣ Creando estado de juego...');
const estado = new GameState('Jugador1', 'Jugador2');
console.log(`   ✅ Estado creado - Turno: ${estado.turnoActual}, Fase: ${estado.fase}\n`);

// 3. Preparar mazos para los jugadores (copias del mazo base)
console.log('3️⃣ Preparando mazos para los jugadores...');
const mazoJugador1 = barajar([...mazo]);
const mazoJugador2 = barajar([...mazo]);
estado.jugadores.Jugador1.mazo = mazoJugador1;
estado.jugadores.Jugador2.mazo = mazoJugador2;
console.log(`   ✅ Mazos preparados (${mazoJugador1.length} cartas cada uno)\n`);

// 4. Repartir cartas iniciales
console.log('4️⃣ Repartiendo cartas iniciales...');
const { mano: mano1, mazoRestante: mazo1Restante } = repartirCartasIniciales([...mazoJugador1], 5);
const { mano: mano2, mazoRestante: mazo2Restante } = repartirCartasIniciales([...mazoJugador2], 5);
estado.jugadores.Jugador1.mano = mano1;
estado.jugadores.Jugador1.mazo = mazo1Restante;
estado.jugadores.Jugador2.mano = mano2;
estado.jugadores.Jugador2.mazo = mazo2Restante;
console.log(`   ✅ Jugador1: ${mano1.length} cartas en mano`);
console.log(`   ✅ Jugador2: ${mano2.length} cartas en mano\n`);

// 5. Mostrar algunas cartas de la mano
console.log('5️⃣ Cartas en mano del Jugador1:');
mano1.slice(0, 3).forEach((carta, index) => {
    console.log(`   ${index + 1}. ${carta.nombre} (${carta.tipo}) - Coste: ${carta.coste}, Ataque: ${carta.ataque}, Defensa: ${carta.defensa}`);
});
console.log('');

// 6. Calcular maná para el turno
console.log('6️⃣ Calculando maná disponible:');
for (let turno = 1; turno <= 5; turno++) {
    const mana = calcularManaMaximo(turno);
    console.log(`   Turno ${turno}: ${mana} maná máximo`);
}
console.log('');

// 7. Simular inicio de turno
console.log('7️⃣ Simulando inicio de turno:');
const jugadorActual = estado.getJugadorActual();
estado.turnoNumero = 1;
jugadorActual.manaMaximo = calcularManaMaximo(estado.turnoNumero);
jugadorActual.mana = jugadorActual.manaMaximo;
console.log(`   Jugador: ${jugadorActual.id}`);
console.log(`   Maná disponible: ${jugadorActual.mana}/${jugadorActual.manaMaximo}`);
console.log(`   Cartas en mano: ${jugadorActual.mano.length}`);
console.log(`   Cartas en mazo: ${jugadorActual.mazo.length}`);
console.log('');

// 8. Verificar si una carta puede jugarse
console.log('8️⃣ Verificando cartas jugables:');
const cartaEjemplo = jugadorActual.mano[0];
if (cartaEjemplo) {
    const puedeJugarse = cartaEjemplo.puedeJugarse(jugadorActual.mana);
    console.log(`   Carta: ${cartaEjemplo.nombre}`);
    console.log(`   Coste: ${cartaEjemplo.coste}`);
    console.log(`   Maná disponible: ${jugadorActual.mana}`);
    console.log(`   ¿Puede jugarse? ${puedeJugarse ? '✅ Sí' : '❌ No'}`);
}
console.log('');

// 9. Cambiar de turno
console.log('9️⃣ Cambiando de turno...');
estado.siguienteTurno();
console.log(`   ✅ Turno actual: ${estado.turnoActual}`);
console.log(`   ✅ Número de turno: ${estado.turnoNumero}`);
console.log('');

console.log('✅ Ejemplo completado exitosamente!');
console.log('📝 Todos los componentes funcionan correctamente juntos.\n');









