/**
 * Script de verificación rápida
 * Verifica que todos los componentes básicos funcionan correctamente
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verificando configuración del proyecto...\n');

let errores = 0;
let exitosas = 0;

// Función para verificar
function verificar(nombre, test) {
    try {
        const resultado = test();
        if (resultado) {
            console.log(`✅ ${nombre}`);
            exitosas++;
        } else {
            console.log(`❌ ${nombre} - Falló`);
            errores++;
        }
    } catch (error) {
        console.log(`❌ ${nombre} - Error: ${error.message}`);
        errores++;
    }
}

// 1. Verificar que Card se puede importar y usar
verificar('Modelo Card se puede importar', () => {
    const Carta = require('../models/Card');
    const carta = new Carta('test_001', 'Carta Test', 'Aliado', 2, 3, 2, 'Test', 'test.jpg');
    return carta.nombre === 'Carta Test' && carta.coste === 2;
});

// 2. Verificar métodos de Card
verificar('Métodos de Card funcionan', () => {
    const Carta = require('../models/Card');
    const carta = new Carta('test_001', 'Carta Test', 'Aliado', 3, 3, 2, 'Test', 'test.jpg');
    const json = carta.toJSON();
    const carta2 = Carta.fromJSON(json);
    return carta2.nombre === carta.nombre && carta2.coste === carta.coste;
});

// 3. Verificar que GameState se puede importar y usar
verificar('Modelo GameState se puede importar', () => {
    const GameState = require('../models/GameState');
    const estado = new GameState();
    return estado.turnoActual === 'jugador1' && estado.fase === 'inicio';
});

// 4. Verificar métodos de GameState
verificar('Métodos de GameState funcionan', () => {
    const GameState = require('../models/GameState');
    const estado = new GameState();
    const jugador = estado.getJugadorActual();
    estado.siguienteTurno();
    return jugador.id === 'jugador1' && estado.turnoActual === 'jugador2';
});

// 5. Verificar que las utilidades se pueden importar
verificar('Utilidades del juego se pueden importar', () => {
    const utils = require('../utils/gameUtils');
    return typeof utils.barajar === 'function' && 
           typeof utils.repartirCartasIniciales === 'function';
});

// 6. Verificar función barajar
verificar('Función barajar funciona correctamente', () => {
    const { barajar } = require('../utils/gameUtils');
    const array = [1, 2, 3, 4, 5];
    const barajado = barajar(array);
    // Verificar que tiene los mismos elementos
    return barajado.length === array.length && 
           array.every(item => barajado.includes(item));
});

// 7. Verificar función repartirCartasIniciales
verificar('Función repartirCartasIniciales funciona', () => {
    const { repartirCartasIniciales } = require('../utils/gameUtils');
    const mazo = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const { mano, mazoRestante } = repartirCartasIniciales(mazo, 5);
    return mano.length === 5 && mazoRestante.length === 5;
});

// 8. Verificar que el mazo existe y se puede cargar
verificar('Mazo de demostración existe y es válido', () => {
    const deckPath = path.join(__dirname, '../data/deck.json');
    if (!fs.existsSync(deckPath)) {
        return false;
    }
    const deckData = JSON.parse(fs.readFileSync(deckPath, 'utf8'));
    return Array.isArray(deckData) && deckData.length > 0;
});

// 9. Verificar que las cartas del mazo son válidas
verificar('Cartas del mazo tienen estructura válida', () => {
    const deckPath = path.join(__dirname, '../data/deck.json');
    const deckData = JSON.parse(fs.readFileSync(deckPath, 'utf8'));
    const Carta = require('../models/Card');
    
    // Probar crear algunas cartas desde el mazo
    const cartasValidas = deckData.slice(0, 5).every(cartaData => {
        try {
            const carta = Carta.fromJSON(cartaData);
            return carta.id && carta.nombre && carta.tipo && typeof carta.coste === 'number';
        } catch {
            return false;
        }
    });
    
    return cartasValidas && deckData.length >= 20;
});

// 10. Verificar cálculo de maná
verificar('Función calcularManaMaximo funciona', () => {
    const { calcularManaMaximo } = require('../utils/gameUtils');
    return calcularManaMaximo(1) === 1 &&
           calcularManaMaximo(5) === 5 &&
           calcularManaMaximo(15) === 10; // Máximo 10
});

// Resumen
console.log('\n' + '='.repeat(50));
console.log(`📊 Resumen: ${exitosas} exitosas, ${errores} errores`);

if (errores === 0) {
    console.log('✅ ¡Todo está funcionando correctamente!');
    console.log('🚀 Listo para comenzar la Fase 1');
    process.exit(0);
} else {
    console.log('❌ Hay errores que deben corregirse antes de continuar');
    process.exit(1);
}

