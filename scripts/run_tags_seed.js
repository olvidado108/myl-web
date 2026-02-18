/**
 * Ejecuta el seed de tags sobre server/data/game.db.
 * Uso: node scripts/run_tags_seed.js [ruta_db]
 */
const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const dbPath = process.argv[2] || path.join(process.cwd(), 'server', 'data', 'game.db');
const sqlPath = path.join(process.cwd(), 'scripts', 'tags_schema_seed.sql');

const sql = fs.readFileSync(sqlPath, 'utf8');
const db = new Database(dbPath);
db.exec(sql);

const tables = db
  .prepare("select count(*) as c from sqlite_master where type='table' and name in ('tags','carta_tags')")
  .get().c;
const tags = db.prepare('select count(*) as c from tags').get().c;

console.log({ dbPath, tables_created: tables, tags_count: tags });
db.close();









