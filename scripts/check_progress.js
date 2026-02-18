const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'server', 'data', 'game.db');
const db = new Database(dbPath, { readonly: true });

const total = db.prepare(`
    SELECT COUNT(*) as count 
    FROM cartas 
    WHERE textoHabilidad IS NOT NULL 
      AND textoHabilidad != '' 
      AND textoHabilidad != 'Sin habilidades especiales'
      AND textoHabilidad != 'NaN'
      AND textoHabilidad != 'null'
`).get();

const procesadas = db.prepare(`
    SELECT COUNT(*) as count 
    FROM cartas 
    WHERE textoHabilidad IS NOT NULL 
      AND textoHabilidad != '' 
      AND textoHabilidad != 'Sin habilidades especiales'
      AND textoHabilidad != 'NaN'
      AND textoHabilidad != 'null'
      AND abilities_json IS NOT NULL 
      AND abilities_json != ''
`).get();

const faltantes = db.prepare(`
    SELECT COUNT(*) as count 
    FROM cartas 
    WHERE textoHabilidad IS NOT NULL 
      AND textoHabilidad != '' 
      AND textoHabilidad != 'Sin habilidades especiales'
      AND textoHabilidad != 'NaN'
      AND textoHabilidad != 'null'
      AND (abilities_json IS NULL OR abilities_json = '')
`).get();

console.log('\n📊 Estadísticas de Procesamiento:\n');
console.log(`Total cartas con habilidades: ${total.count}`);
console.log(`Cartas procesadas: ${procesadas.count}`);
console.log(`Cartas faltantes: ${faltantes.count}`);
console.log(`Progreso: ${((procesadas.count / total.count) * 100).toFixed(2)}%\n`);

db.close();








