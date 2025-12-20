/**
 * Script para convertir un usuario en administrador
 * Uso: node scripts/make_user_admin.js [username]
 */

const path = require('path');
const Database = require('better-sqlite3');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath);
db.pragma('journal_mode = WAL');

// Migración: agregar columna 'isAdmin' si no existe
try {
    const columns = db.prepare("PRAGMA table_info(usuarios)").all();
    const hasIsAdmin = columns.some(col => col.name === 'isAdmin');
    if (!hasIsAdmin) {
        db.exec(`ALTER TABLE usuarios ADD COLUMN isAdmin BOOLEAN DEFAULT 0`);
    }
} catch (error) {
    // Ignorar error si ya existe
}

// Obtener el username del argumento de línea de comandos
const username = process.argv[2];

if (!username) {
    console.log('Uso: node scripts/make_user_admin.js <username>');
    console.log('\nEjemplo: node scripts/make_user_admin.js miusuario');
    process.exit(1);
}

try {
    // Verificar que el usuario existe
    const usuario = db.prepare('SELECT id, username, email, isAdmin FROM usuarios WHERE username = ?').get(username);
    
    if (!usuario) {
        console.error(`❌ Error: No se encontró un usuario con el nombre "${username}"`);
        process.exit(1);
    }

    console.log(`📋 Usuario encontrado:`);
    console.log(`   ID: ${usuario.id}`);
    console.log(`   Username: ${usuario.username}`);
    console.log(`   Email: ${usuario.email}`);
    console.log(`   Es Admin: ${usuario.isAdmin ? 'Sí' : 'No'}`);

    // Verificar si ya es admin
    if (usuario.isAdmin) {
        console.log(`\n✅ El usuario "${username}" ya es administrador.`);
        db.close();
        process.exit(0);
    }

    // Actualizar isAdmin a true
    const update = db.prepare('UPDATE usuarios SET isAdmin = ? WHERE username = ?');
    const result = update.run(1, username);

    if (result.changes > 0) {
        console.log(`\n✅ Usuario "${username}" actualizado exitosamente a administrador.`);
    } else {
        console.error(`\n❌ Error: No se pudo actualizar el usuario.`);
        process.exit(1);
    }

    db.close();
} catch (error) {
    console.error(`❌ Error: ${error.message}`);
    db.close();
    process.exit(1);
}

