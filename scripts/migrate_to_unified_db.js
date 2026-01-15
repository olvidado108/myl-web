/**
 * Script de migración para consolidar cards_new.db y users.db en game.db
 * Este script:
 * 1. Crea una nueva base de datos game.db en server/data/
 * 2. Copia todas las tablas de cards_new.db (tabla cartas)
 * 3. Copia todas las tablas de users.db (usuarios, estadisticas_usuario, sesiones, favoritos, mazos)
 * 4. Mantiene todos los índices y estructura
 */

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const BASE_DIR = path.join(__dirname, '..');
const CARDS_DB_PATH = path.join(BASE_DIR, 'server', 'data', 'cards', 'cards_new.db');
const USERS_DB_PATH = path.join(BASE_DIR, 'server', 'data', 'users', 'users.db');
const NEW_DB_PATH = path.join(BASE_DIR, 'server', 'data', 'game.db');

console.log('🔄 Iniciando migración a base de datos unificada...\n');

// Verificar que las bases de datos existan
if (!fs.existsSync(CARDS_DB_PATH)) {
    console.error(`❌ Error: No se encontró ${CARDS_DB_PATH}`);
    process.exit(1);
}

if (!fs.existsSync(USERS_DB_PATH)) {
    console.error(`❌ Error: No se encontró ${USERS_DB_PATH}`);
    process.exit(1);
}

// Si game.db ya existe, hacer backup y eliminar
if (fs.existsSync(NEW_DB_PATH)) {
    const backupPath = `${NEW_DB_PATH}.backup.${Date.now()}`;
    console.log(`⚠️  game.db ya existe. Creando backup: ${backupPath}`);
    fs.copyFileSync(NEW_DB_PATH, backupPath);
    console.log(`✅ Backup creado`);
    // Eliminar BD y archivos relacionados para recrear desde cero
    try {
        fs.unlinkSync(NEW_DB_PATH);
        fs.unlinkSync(`${NEW_DB_PATH}-shm`);
        fs.unlinkSync(`${NEW_DB_PATH}-wal`);
    } catch (e) {
        // Ignorar errores si no existen
    }
    console.log(`🗑️  BD anterior eliminada para recrear desde cero\n`);
}

try {
    // Crear nueva base de datos
    console.log('📦 Creando nueva base de datos game.db...');
    const newDb = new Database(NEW_DB_PATH);
    newDb.pragma('journal_mode = WAL');
    
    // Abrir bases de datos existentes
    console.log('📂 Abriendo bases de datos existentes...');
    const cardsDb = new Database(CARDS_DB_PATH, { readonly: true });
    const usersDb = new Database(USERS_DB_PATH, { readonly: true });
    
    // ========== MIGRAR TABLA CARTAS ==========
    console.log('\n🃏 Migrando tabla cartas...');
    
    // Obtener estructura de la tabla cartas
    const cartasSchema = cardsDb.prepare(`
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='cartas'
    `).get();
    
    if (cartasSchema) {
        // Eliminar tabla si existe (para permitir re-migración)
        try {
            newDb.exec('DROP TABLE IF EXISTS cartas');
            console.log('   🗑️  Tabla cartas eliminada (si existía)');
        } catch (e) {
            console.warn(`   ⚠️  Error eliminando tabla: ${e.message}`);
        }
        // Modificar el SQL para asegurar que no tenga IF NOT EXISTS
        let createSql = cartasSchema.sql;
        createSql = createSql.replace(/IF NOT EXISTS/gi, '');
        // Crear tabla cartas en la nueva BD
        newDb.exec(createSql);
        console.log('   ✅ Tabla cartas creada');
        
        // Copiar datos
        const cartas = cardsDb.prepare('SELECT * FROM cartas').all();
        if (cartas.length > 0) {
            // Obtener nombres de columnas
            const firstCarta = cartas[0];
            const columns = Object.keys(firstCarta);
            const placeholders = columns.map(() => '?').join(', ');
            const insertSql = `INSERT INTO cartas (${columns.join(', ')}) VALUES (${placeholders})`;
            const insert = newDb.prepare(insertSql);
            
            const transaction = newDb.transaction((cartas) => {
                for (const carta of cartas) {
                    insert.run(...columns.map(col => carta[col]));
                }
            });
            
            transaction(cartas);
            console.log(`   ✅ ${cartas.length} cartas migradas`);
        }
        
        // Copiar índices de cartas
        const cartasIndices = cardsDb.prepare(`
            SELECT sql FROM sqlite_master 
            WHERE type='index' AND tbl_name='cartas' AND sql IS NOT NULL
        `).all();
        
        for (const idx of cartasIndices) {
            try {
                newDb.exec(idx.sql);
                console.log(`   ✅ Índice migrado: ${idx.sql.substring(0, 50)}...`);
            } catch (error) {
                console.warn(`   ⚠️  No se pudo crear índice (puede que ya exista): ${error.message}`);
            }
        }
    }
    
    // ========== MIGRAR TABLAS DE USUARIOS ==========
    console.log('\n👥 Migrando tablas de usuarios...');
    
    const userTables = ['usuarios', 'estadisticas_usuario', 'sesiones', 'favoritos', 'mazos'];
    
    for (const tableName of userTables) {
        const tableSchema = usersDb.prepare(`
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name=?
        `).get(tableName);
        
        if (tableSchema) {
            // Crear tabla en la nueva BD
            newDb.exec(tableSchema.sql);
            console.log(`   ✅ Tabla ${tableName} creada`);
            
            // Copiar datos
            const rows = usersDb.prepare(`SELECT * FROM ${tableName}`).all();
            if (rows.length > 0) {
                const firstRow = rows[0];
                const columns = Object.keys(firstRow);
                const placeholders = columns.map(() => '?').join(', ');
                const insertSql = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${placeholders})`;
                const insert = newDb.prepare(insertSql);
                
                const transaction = newDb.transaction((rows) => {
                    for (const row of rows) {
                        insert.run(...columns.map(col => row[col]));
                    }
                });
                
                transaction(rows);
                console.log(`   ✅ ${rows.length} registros migrados de ${tableName}`);
            }
        }
    }
    
    // Copiar índices de usuarios
    console.log('\n📑 Migrando índices de usuarios...');
    const userIndices = usersDb.prepare(`
        SELECT sql FROM sqlite_master 
        WHERE type='index' AND sql IS NOT NULL
    `).all();
    
    for (const idx of userIndices) {
        try {
            newDb.exec(idx.sql);
            console.log(`   ✅ Índice migrado`);
        } catch (error) {
            console.warn(`   ⚠️  No se pudo crear índice (puede que ya exista): ${error.message}`);
        }
    }
    
    // Verificar migración
    console.log('\n🔍 Verificando migración...');
    const cartasCount = newDb.prepare('SELECT COUNT(*) as count FROM cartas').get().count;
    const usuariosCount = newDb.prepare('SELECT COUNT(*) as count FROM usuarios').get().count;
    const mazosCount = newDb.prepare('SELECT COUNT(*) as count FROM mazos').get().count;
    
    console.log(`   📊 Cartas: ${cartasCount}`);
    console.log(`   👥 Usuarios: ${usuariosCount}`);
    console.log(`   🎴 Mazos: ${mazosCount}`);
    
    // Cerrar conexiones
    cardsDb.close();
    usersDb.close();
    newDb.close();
    
    console.log('\n✅ Migración completada exitosamente!');
    console.log(`📁 Nueva base de datos: ${NEW_DB_PATH}`);
    console.log('\n⚠️  IMPORTANTE: Ahora debes actualizar los repositorios para usar game.db');
    console.log('   Ejecuta los siguientes pasos:');
    console.log('   1. Actualizar CardRepositorySQLite.js');
    console.log('   2. Actualizar UserRepository.js');
    console.log('   3. Actualizar DeckRepository.js');
    console.log('   4. Actualizar todos los scripts que referencian las bases de datos antiguas');
    
} catch (error) {
    console.error('\n❌ Error durante la migración:', error.message);
    console.error(error.stack);
    process.exit(1);
}






