/**
 * Script de migración: cambiar campo 'rol' por 'isAdmin' booleano
 */

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath);
db.pragma('journal_mode = WAL');

console.log('🔄 Iniciando migración: rol -> isAdmin\n');

try {
    // Verificar estructura actual
    const columns = db.prepare("PRAGMA table_info(usuarios)").all();
    const columnNames = columns.map(col => col.name);
    
    const hasRol = columnNames.includes('rol');
    const hasIsAdmin = columnNames.includes('isAdmin');

    if (hasIsAdmin && !hasRol) {
        console.log('✅ La migración ya está completa (isAdmin existe, rol no existe)');
        db.close();
        process.exit(0);
    }

    // Si tiene rol pero no isAdmin, hacer la migración
    if (hasRol && !hasIsAdmin) {
        console.log('📋 Paso 1: Agregando columna isAdmin...');
        db.exec(`ALTER TABLE usuarios ADD COLUMN isAdmin BOOLEAN DEFAULT 0`);
        
        console.log('📋 Paso 2: Migrando datos de rol a isAdmin...');
        db.exec(`UPDATE usuarios SET isAdmin = 1 WHERE rol = 'admin'`);
        db.exec(`UPDATE usuarios SET isAdmin = 0 WHERE rol IS NULL OR rol = 'user'`);
        
        console.log('📋 Paso 3: Eliminando columna rol...');
        // SQLite no soporta DROP COLUMN directamente, así que recreamos la tabla
        db.exec(`
            CREATE TABLE usuarios_new (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT,
                avatar_url TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso DATETIME,
                activo BOOLEAN DEFAULT 1,
                nivel INTEGER DEFAULT 1,
                experiencia INTEGER DEFAULT 0,
                isAdmin BOOLEAN DEFAULT 0
            )
        `);
        
        db.exec(`
            INSERT INTO usuarios_new 
            (id, username, email, password_hash, nombre_completo, avatar_url, 
             fecha_registro, ultimo_acceso, activo, nivel, experiencia, isAdmin)
            SELECT 
            id, username, email, password_hash, nombre_completo, avatar_url,
            fecha_registro, ultimo_acceso, activo, nivel, experiencia, isAdmin
            FROM usuarios
        `);
        
        db.exec(`DROP TABLE usuarios`);
        db.exec(`ALTER TABLE usuarios_new RENAME TO usuarios`);
        
        // Recrear índices
        db.exec(`CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username)`);
        db.exec(`CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)`);
        
        console.log('✅ Migración completada exitosamente\n');
    } else if (!hasRol && !hasIsAdmin) {
        // Si no tiene ninguno, simplemente agregamos isAdmin
        console.log('📋 Agregando columna isAdmin (primera vez)...');
        db.exec(`ALTER TABLE usuarios ADD COLUMN isAdmin BOOLEAN DEFAULT 0`);
        console.log('✅ Columna isAdmin agregada exitosamente\n');
    }

    // Mostrar estado final
    const users = db.prepare('SELECT username, email, isAdmin FROM usuarios').all();
    console.log('📊 Estado actual de usuarios:');
    users.forEach(u => {
        const role = u.isAdmin ? 'Admin' : 'Usuario';
        console.log(`   - ${u.username}: ${role}`);
    });

    db.close();
} catch (error) {
    console.error('❌ Error en la migración:', error.message);
    console.error(error);
    db.close();
    process.exit(1);
}








