const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath, { readonly: true });

const cardIds = ['ra696', 'ra79', 'ra205', 'he152', 'he180', 'ra818', 'ra178', 'es306', 'he166', 'he156'];
const placeholders = cardIds.map(() => '?').join(',');

const cards = db.prepare(`
    SELECT id, nombre, 
           CASE WHEN abilities_json IS NOT NULL AND abilities_json != '' THEN 1 ELSE 0 END as processed
    FROM cartas 
    WHERE id IN (${placeholders})
`).all(...cardIds);

console.log('Estado de las cartas:');
cards.forEach(c => {
    console.log(`${c.id} (${c.nombre}): ${c.processed ? '✅ Procesada' : '❌ Sin procesar'}`);
});

db.close();

