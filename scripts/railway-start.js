const fs = require('fs');
const path = require('path');

const VOLUME_DB_PATH = process.env.DATABASE_PATH || null;
const BUNDLED_DB_PATH = path.join(__dirname, '..', 'server', 'data', 'game.db');

if (VOLUME_DB_PATH) {
    const dir = path.dirname(VOLUME_DB_PATH);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`📁 Directorio creado: ${dir}`);
    }

    if (!fs.existsSync(VOLUME_DB_PATH)) {
        if (fs.existsSync(BUNDLED_DB_PATH)) {
            fs.copyFileSync(BUNDLED_DB_PATH, VOLUME_DB_PATH);
            console.log(`📦 Base de datos inicial copiada a volumen: ${VOLUME_DB_PATH}`);
        } else {
            console.log('⚠️  No se encontró DB inicial, se creará una vacía al arrancar');
        }
    } else {
        console.log(`✅ Base de datos existente en volumen: ${VOLUME_DB_PATH}`);
    }
}

require('../server/server.js');
