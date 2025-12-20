/**
 * Script para listar usuarios
 */

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath);
db.pragma('journal_mode = WAL');

// Migración: agregar columna 'isAdmin' si no existe
try {
    const columns = db.prepare("PRAGMA table_info(usuarios)").all();
    const hasIsAdmin = columns.some(col => col.name === 'isAdmin');
    if (!hasIsAdmin) {
        console.log('Agregando columna "isAdmin" a la tabla usuarios...');
        db.exec(`ALTER TABLE usuarios ADD COLUMN isAdmin BOOLEAN DEFAULT 0`);
        console.log('✅ Columna "isAdmin" agregada exitosamente.\n');
    }
} catch (error) {
    console.warn('⚠️ Advertencia al verificar/agregar columna isAdmin:', error.message);
}

try {
    const users = db.prepare('SELECT id, username, email, isAdmin FROM usuarios').all();
    
    console.log('Usuarios encontrados:');
    console.log('===================');
    
    if (users.length === 0) {
        console.log('No hay usuarios en la base de datos.');
    } else {
        users.forEach((u, index) => {
            console.log(`${index + 1}. Username: ${u.username}`);
            console.log(`   Email: ${u.email}`);
            console.log(`   Es Admin: ${u.isAdmin ? 'Sí' : 'No'}`);
            console.log(`   ID: ${u.id}`);
            console.log('');
        });
    }
    
    db.close();
} catch (error) {
    console.error('Error:', error.message);
    db.close();
    process.exit(1);
}

