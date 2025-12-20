/**
 * Script para verificar que la migración se completó correctamente
 */

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');

console.log('📊 Verificación de game.db:\n');

try {
    const db = new Database(dbPath, { readonly: true });
    
    console.log('Cartas:', db.prepare('SELECT COUNT(*) as count FROM cartas').get().count);
    console.log('Usuarios:', db.prepare('SELECT COUNT(*) as count FROM usuarios').get().count);
    console.log('Mazos:', db.prepare('SELECT COUNT(*) as count FROM mazos').get().count);
    console.log('Estadísticas:', db.prepare('SELECT COUNT(*) as count FROM estadisticas_usuario').get().count);
    console.log('Sesiones:', db.prepare('SELECT COUNT(*) as count FROM sesiones').get().count);
    console.log('Favoritos:', db.prepare('SELECT COUNT(*) as count FROM favoritos').get().count);
    
    console.log('\n✅ Tablas en la BD:');
    const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").all();
    tables.forEach(t => console.log('  -', t.name));
    
    console.log('\n✅ Índices en la BD:');
    const indices = db.prepare("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name").all();
    indices.forEach(idx => console.log('  -', idx.name));
    
    db.close();
    console.log('\n✨ Verificación completada!');
} catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
}

