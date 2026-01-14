const bcrypt = require('bcrypt');

const SALT_ROUNDS = 10;

/**
 * Genera un hash de contraseña usando bcrypt
 * @param {string} password - Contraseña en texto plano
 * @returns {Promise<string>} Hash de la contraseña
 */
async function hashPassword(password) {
    return await bcrypt.hash(password, SALT_ROUNDS);
}

/**
 * Compara una contraseña con su hash
 * @param {string} password - Contraseña en texto plano
 * @param {string} hash - Hash de la contraseña
 * @returns {Promise<boolean>} true si coinciden, false si no
 */
async function comparePassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

/**
 * Valida la fortaleza de una contraseña
 * @param {string} password - Contraseña a validar
 * @returns {Object} { valida: boolean, errores: string[] }
 */
function validarFortalezaPassword(password) {
    const errores = [];

    if (!password || password.length < 8) {
        errores.push('La contraseña debe tener al menos 8 caracteres');
    }

    if (password && password.length > 0 && !/[A-Z]/.test(password)) {
        errores.push('La contraseña debe contener al menos una letra mayúscula');
    }

    if (password && password.length > 0 && !/[a-z]/.test(password)) {
        errores.push('La contraseña debe contener al menos una letra minúscula');
    }

    if (password && password.length > 0 && !/[0-9]/.test(password)) {
        errores.push('La contraseña debe contener al menos un número');
    }

    return {
        valida: errores.length === 0,
        errores
    };
}

module.exports = {
    hashPassword,
    comparePassword,
    validarFortalezaPassword,
    SALT_ROUNDS
};









