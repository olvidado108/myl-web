const Database = require('better-sqlite3');
const db = new Database('./server/data/game.db', {readonly: true});
const mazos = db.prepare('SELECT id, nombre, usuario_id FROM mazos').all();
console.log('Mazos en game.db:');
mazos.forEach(m => console.log(`  - ${m.nombre} (ID: ${m.id}, Usuario: ${m.usuario_id})`));
db.close();

