/**
 * Utilidades para el juego
 */

/**
 * Algoritmo Fisher-Yates para barajar un array
 * @param {Array} array - Array a barajar
 * @returns {Array} - Nuevo array barajado
 */
function barajar(array) {
    const arrayBarajado = [...array]; // Copia para no mutar el original
    for (let i = arrayBarajado.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arrayBarajado[i], arrayBarajado[j]] = [arrayBarajado[j], arrayBarajado[i]];
    }
    return arrayBarajado;
}

/**
 * Reparte cartas iniciales a un jugador
 * @param {Array} mazo - Mazo del jugador
 * @param {number} cantidad - Cantidad de cartas a repartir
 * @returns {Object} - Objeto con {mano: [], mazoRestante: []}
 */
function repartirCartasIniciales(mazo, cantidad = 5) {
    const mazoBarajado = barajar(mazo);
    const mano = mazoBarajado.slice(0, cantidad);
    const mazoRestante = mazoBarajado.slice(cantidad);
    return { mano, mazoRestante };
}

/**
 * Roba una carta del mazo
 * @param {Array} mazo - Mazo del jugador
 * @returns {Object|null} - Carta robada o null si el mazo está vacío
 */
function robarCarta(mazo) {
    if (mazo.length === 0) return null;
    return mazo.shift();
}

/**
 * Calcula el maná máximo para un turno
 * @param {number} turnoNumero - Número del turno actual
 * @param {number} maximo - Maná máximo permitido (por defecto 10)
 * @returns {number} - Maná máximo para este turno
 */
function calcularManaMaximo(turnoNumero, maximo = 10) {
    return Math.min(turnoNumero, maximo);
}

module.exports = {
    barajar,
    repartirCartasIniciales,
    robarCarta,
    calcularManaMaximo
};

