const { verificarToken, extraerToken } = require('../utils/jwtUtils');

/**
 * Middleware para autenticar requests usando JWT
 * Requiere que el request tenga un token válido
 */
function authenticateToken(req, res, next) {
    const token = extraerToken(req);

    if (!token) {
        return res.status(401).json({
            success: false,
            error: 'Token de autenticación requerido'
        });
    }

    const decoded = verificarToken(token);
    if (!decoded) {
        return res.status(403).json({
            success: false,
            error: 'Token inválido o expirado'
        });
    }

    req.user = decoded;
    next();
}

/**
 * Middleware opcional de autenticación
 * Si hay token, lo verifica y agrega req.user, pero no falla si no hay token
 */
function optionalAuth(req, res, next) {
    const token = extraerToken(req);

    if (token) {
        const decoded = verificarToken(token);
        if (decoded) {
            req.user = decoded;
        }
    }

    next();
}

/**
 * Middleware para verificar que el usuario sea administrador
 * Debe usarse después de authenticateToken
 */
function requireAdmin(req, res, next) {
    if (!req.user) {
        return res.status(401).json({
            success: false,
            error: 'Autenticación requerida'
        });
    }

    if (!req.user.isAdmin) {
        return res.status(403).json({
            success: false,
            error: 'Acceso denegado: se requieren permisos de administrador'
        });
    }

    next();
}

module.exports = {
    authenticateToken,
    optionalAuth,
    requireAdmin
};











