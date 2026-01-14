/**
 * Script para migrar mazos de users.db a game.db
 * Verifica si hay mazos en users.db y los migra a game.db
 */

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const BASE_DIR = path.join(__dirname, '..');
const USERS_DB_PATH = path.join(BASE_DIR, 'server', 'data', 'users', 'users.db');
const GAME_DB_PATH = path.join(BASE_DIR, 'server', 'data', 'game.db');

console.log('🔄 Verificando y migrando mazos de users.db a game.db...\n');

// Verificar que las bases de datos existan
if (!fs.existsSync(USERS_DB_PATH)) {
    console.error(`❌ Error: No se encontró ${USERS_DB_PATH}`);
    process.exit(1);
}

if (!fs.existsSync(GAME_DB_PATH)) {
    console.error(`❌ Error: No se encontró ${GAME_DB_PATH}`);
    process.exit(1);
}

try {
    // Abrir bases de datos
    const usersDb = new Database(USERS_DB_PATH, { readonly: true });
    const gameDb = new Database(GAME_DB_PATH);
    gameDb.pragma('journal_mode = WAL');

    // Verificar si existe la tabla mazos en users.db
    let mazosEnUsers = 0;
    let mazosEnGame = 0;
    
    try {
        const result = usersDb.prepare('SELECT COUNT(*) as count FROM mazos').get();
        mazosEnUsers = result.count;
        console.log(`📊 Mazos en users.db: ${mazosEnUsers}`);
    } catch (error) {
        console.log(`⚠️  No se encontró tabla mazos en users.db: ${error.message}`);
    }

    try {
        const result = gameDb.prepare('SELECT COUNT(*) as count FROM mazos').get();
        mazosEnGame = result.count;
        console.log(`📊 Mazos en game.db: ${mazosEnGame}`);
    } catch (error) {
        console.log(`⚠️  No se encontró tabla mazos en game.db: ${error.message}`);
        console.log('   Creando tabla mazos en game.db...');
        
        // Crear tabla mazos si no existe
        gameDb.exec(`
            CREATE TABLE IF NOT EXISTS mazos (
                id TEXT PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                formato TEXT,
                raza TEXT,
                edicion_original TEXT,
                cartas TEXT NOT NULL,
                oro_inicial_id TEXT,
                es_publico BOOLEAN DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                veces_usado INTEGER DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);
        
        gameDb.exec(`
            CREATE INDEX IF NOT EXISTS idx_mazos_usuario ON mazos(usuario_id);
        `);
        
        console.log('   ✅ Tabla mazos creada en game.db');
    }

    // Si hay mazos en users.db, migrarlos
    if (mazosEnUsers > 0) {
        console.log(`\n🔄 Migrando ${mazosEnUsers} mazos de users.db a game.db...`);
        
        // Obtener todos los mazos de users.db
        const mazos = usersDb.prepare('SELECT * FROM mazos').all();
        
        if (mazos.length > 0) {
            // Obtener nombres de columnas
            const firstMazo = mazos[0];
            const columns = Object.keys(firstMazo);
            const placeholders = columns.map(() => '?').join(', ');
            
            // Preparar inserción con manejo de duplicados (INSERT OR IGNORE)
            const insertSql = `INSERT OR IGNORE INTO mazos (${columns.join(', ')}) VALUES (${placeholders})`;
            const insert = gameDb.prepare(insertSql);
            
            let migrados = 0;
            let duplicados = 0;
            
            const transaction = gameDb.transaction((mazos) => {
                for (const mazo of mazos) {
                    try {
                        const result = insert.run(...columns.map(col => mazo[col]));
                        if (result.changes > 0) {
                            migrados++;
                        } else {
                            duplicados++;
                        }
                    } catch (error) {
                        console.warn(`   ⚠️  Error migrando mazo ${mazo.id}: ${error.message}`);
                    }
                }
            });
            
            transaction(mazos);
            
            console.log(`   ✅ ${migrados} mazos migrados exitosamente`);
            if (duplicados > 0) {
                console.log(`   ℹ️  ${duplicados} mazos ya existían en game.db (omitidos)`);
            }
        }
    } else {
        console.log('\n✅ No hay mazos en users.db para migrar');
    }

    // Verificar resultado final
    const mazosFinales = gameDb.prepare('SELECT COUNT(*) as count FROM mazos').get().count;
    console.log(`\n📊 Total de mazos en game.db después de la migración: ${mazosFinales}`);

    // Cerrar conexiones
    usersDb.close();
    gameDb.close();

    console.log('\n✅ Migración completada exitosamente!');
    console.log(`📁 Base de datos unificada: ${GAME_DB_PATH}`);
    console.log('\n⚠️  IMPORTANTE: Asegúrate de que DeckRepository.js esté usando game.db');
    console.log('   (Ya debería estar configurado para usar game.db por defecto)');

} catch (error) {
    console.error('\n❌ Error durante la migración:', error.message);
    console.error(error.stack);
    process.exit(1);
}






