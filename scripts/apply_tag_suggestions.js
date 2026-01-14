/**
 * Inserta sugerencias de tags desde scripts/tags_sugeridos.tsv en carta_tags
 * marcándolas como suggested=1.
 * Uso:
 *   node scripts/apply_tag_suggestions.js [ruta_db] [ruta_tsv]
 * Por defecto usa server/data/game.db y scripts/tags_sugeridos.tsv.
 */

const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const dbPath = process.argv[2] || path.join(process.cwd(), 'server', 'data', 'game.db');
const tsvPath = process.argv[3] || path.join(process.cwd(), 'scripts', 'tags_sugeridos.tsv');

const db = new Database(dbPath);

const ensureSuggestedColumn = () => {
  const cols = db.prepare("PRAGMA table_info('carta_tags')").all();
  const hasSuggested = cols.some((c) => c.name === 'suggested');
  if (!hasSuggested) {
    db.exec("ALTER TABLE carta_tags ADD COLUMN suggested INTEGER DEFAULT 0");
  }
};

const loadTagsMap = () => {
  const map = new Map();
  const rows = db.prepare('SELECT id, slug FROM tags').all();
  rows.forEach((r) => map.set(r.slug, r.id));
  return map;
};

const parseLine = (line) => {
  // Expecting: id \t nombre \t tags_comma_list
  const parts = line.split('\t');
  if (parts.length < 3) return null;
  const cartaId = parts[0].trim();
  const tagsStr = parts[2].trim();
  if (!cartaId || !tagsStr) return null;
  const tags = tagsStr.split(',').map((t) => t.trim()).filter(Boolean);
  return { cartaId, tags };
};

const main = () => {
  ensureSuggestedColumn();
  const upsert = db.prepare(`
    INSERT INTO carta_tags (carta_id, tag_id, suggested)
    VALUES (?, ?, 1)
    ON CONFLICT(carta_id, tag_id) DO UPDATE SET suggested=1
  `);
  const tagMap = loadTagsMap();

  const buf = fs.readFileSync(tsvPath);
  const encoding = buf.includes(0x00) ? 'utf16le' : 'utf8';
  const lines = buf.toString(encoding).split(/\r?\n/);
  let inserted = 0;
  let updated = 0;
  let skipped = 0;
  let missingTags = new Set();

  const isSummary = (line) => line.startsWith('--- Frecuencia');

  for (const line of lines) {
    if (!line.trim() || isSummary(line)) continue;
    const parsed = parseLine(line);
    if (!parsed) continue;
    for (const slug of parsed.tags) {
      const tagId = tagMap.get(slug);
      if (!tagId) {
        missingTags.add(slug);
        continue;
      }
      const res = upsert.run(parsed.cartaId, tagId);
      if (res.changes === 1 && res.lastInsertRowid !== undefined) {
        inserted += 1;
      } else {
        updated += 1;
      }
    }
  }

  console.log({
    dbPath,
    tsvPath,
    inserted,
    updated,
    missingTags: Array.from(missingTags),
  });
};

main();







