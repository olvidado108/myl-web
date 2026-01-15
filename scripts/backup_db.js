/**
 * Script para crear backup de la base de datos game.db
 * Uso: node scripts/backup_db.js
 */

const fs = require('fs');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const backupDir = path.join(__dirname, '..', 'server', 'data', 'backups');

// Crear directorio de backups si no existe
if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
}

// Generar nombre de backup con timestamp
const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
const backupPath = path.join(backupDir, `game.db.backup_${timestamp}`);

try {
    // Copiar archivos de la BD
    if (fs.existsSync(dbPath)) {
        fs.copyFileSync(dbPath, backupPath);
        console.log(`✅ Backup principal creado: ${path.basename(backupPath)}`);
        
        // Copiar archivos WAL/SHM si existen
        const shmPath = `${dbPath}-shm`;
        const walPath = `${dbPath}-wal`;
        
        if (fs.existsSync(shmPath)) {
            fs.copyFileSync(shmPath, `${backupPath}-shm`);
            console.log(`✅ Backup SHM creado`);
        }
        
        if (fs.existsSync(walPath)) {
            fs.copyFileSync(walPath, `${backupPath}-wal`);
            console.log(`✅ Backup WAL creado`);
        }
        
        const size = fs.statSync(backupPath).size;
        console.log(`📦 Tamaño del backup: ${(size / 1024 / 1024).toFixed(2)} MB`);
        console.log(`📁 Ubicación: ${backupPath}`);
        
        // Limpiar backups antiguos (mantener solo los últimos 10)
        const backups = fs.readdirSync(backupDir)
            .filter(f => f.startsWith('game.db.backup_'))
            .map(f => ({
                name: f,
                path: path.join(backupDir, f),
                time: fs.statSync(path.join(backupDir, f)).mtime
            }))
            .sort((a, b) => b.time - a.time);
        
        if (backups.length > 10) {
            const toDelete = backups.slice(10);
            toDelete.forEach(b => {
                // Eliminar archivos relacionados
                [b.path, `${b.path}-shm`, `${b.path}-wal`].forEach(p => {
                    if (fs.existsSync(p)) {
                        fs.unlinkSync(p);
                    }
                });
                console.log(`🗑️  Eliminado backup antiguo: ${b.name}`);
            });
        }
        
        console.log(`\n✅ Backup completado exitosamente!`);
    } else {
        console.error(`❌ Error: No se encontró ${dbPath}`);
        process.exit(1);
    }
} catch (error) {
    console.error(`❌ Error creando backup: ${error.message}`);
    process.exit(1);
}

