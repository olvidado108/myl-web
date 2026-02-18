const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'tu_secreto_super_seguro_cambiar_en_produccion';
const JWT_EXPIRATION = '24h';

/**
 * Genera un token JWT para un usuario
 * @param {Object} payload - Datos del usuario (userId, username, etc.)
 * @returns {string} Token JWT
 */
function generarToken(payload) {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRATION });
}

/**
 * Verifica y decodifica un token JWT
 * @param {string} token - Token JWT a verificar
 * @returns {Object|null} Payload decodificado o null si es inválido
 */
function verificarToken(token) {
    try {
        return jwt.verify(token, JWT_SECRET);
    } catch (error) {
        return null;
    }
}

/**
 * Extrae el token del header Authorization
 * @param {Object} req - Request object de Express
 * @returns {string|null} Token o null si no existe
 */
function extraerToken(req) {
    const authHeader = req.headers['authorization'];
    if (authHeader && authHeader.startsWith('Bearer ')) {
        return authHeader.substring(7);
    }
    return null;
}

module.exports = {
    generarToken,
    verificarToken,
    extraerToken,
    JWT_SECRET,
    JWT_EXPIRATION
};











