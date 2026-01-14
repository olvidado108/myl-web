/**
 * Script para agregar la columna abilities_json a la tabla cartas
 * Ejecutar una vez para migrar la base de datos
 */

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');

console.log('🔧 Agregando columna abilities_json a la tabla cartas...');
console.log('📁 Base de datos:', dbPath);

try {
    const db = new Database(dbPath);
    
    // Verificar si la columna ya existe
    const tableInfo = db.prepare("PRAGMA table_info(cartas)").all();
    const tieneAbilitiesJson = tableInfo.some(col => col.name === 'abilities_json');
    
    if (tieneAbilitiesJson) {
        console.log('✅ La columna abilities_json ya existe');
        db.close();
        process.exit(0);
    }
    
    // Agregar columna abilities_json
    console.log('➕ Agregando columna abilities_json...');
    db.exec('ALTER TABLE cartas ADD COLUMN abilities_json TEXT');
    
    // Agregar columna abilities_version para versionado futuro
    console.log('➕ Agregando columna abilities_version...');
    db.exec('ALTER TABLE cartas ADD COLUMN abilities_version TEXT DEFAULT "1.0"');
    
    // Agregar columna abilities_processed_at para tracking
    console.log('➕ Agregando columna abilities_processed_at...');
    db.exec('ALTER TABLE cartas ADD COLUMN abilities_processed_at DATETIME');
    
    console.log('✅ Columnas agregadas exitosamente');
    console.log('\n📊 Columnas en la tabla cartas:');
    const newTableInfo = db.prepare("PRAGMA table_info(cartas)").all();
    newTableInfo.forEach(col => {
        console.log(`   - ${col.name} (${col.type})`);
    });
    
    db.close();
    console.log('\n✨ Migración completada');
    
} catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
}









