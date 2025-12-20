# 🏷️ Plan de Tags para Cartas

Objetivo: etiquetar cartas con un catálogo controlado de tags (ej. `imbloqueable`, `roba_cartas`, `destruye_objetivo`) para búsquedas, UI y analytics, sin reemplazar la lógica en `abilities_json`.

## Diseño de datos
- Tabla `tags`
  - `id` INTEGER PK
  - `slug` TEXT UNIQUE (minúsculas, snake_case)
  - `nombre` TEXT (legible)
  - `categoria` TEXT (opcional: `ofensivo`, `defensivo`, `recursos`, `control`, `soporte`, `triggers`)
  - `descripcion` TEXT (opcional)
- Tabla `carta_tags`
  - `carta_id` INTEGER FK -> `cartas.id`
  - `tag_id` INTEGER FK -> `tags.id`
  - PK compuesta (`carta_id`, `tag_id`)
  - Índices: `tag_id`, (`carta_id`, `tag_id`)
- Columna adicional `suggested` (INTEGER, default 0) en `carta_tags` para marcar sugerencias automáticas.
- Fuente de verdad sigue siendo `cartas` + `abilities_json`; los tags son metadatos derivados/curados.

## Catálogo inicial (propuesto)
slug → nombre
- `imbloqueable` → Imbloqueable
- `indesterrable` → Indesterrable / Inmune a destierro (ajustar término)
- `indestructible` → Indestructible
- `inmunidad` → Inmunidad a efectos (especificar en descripción)
- `roba_cartas` → Roba cartas
- `bota_cartas` → Muele mazo oponente
- `descarta_mano` → Descarta de mano
- `destruye_objetivo` → Destruye objetivo
- `destierra_objetivo` → Destierra objetivo
- `busca_mazo` → Busca en mazo (tutor)
- `regresa_cementerio` → Recupera del cementerio/baraja
- `previene_dano` → Previene daño
- `genera_recursos` → Genera/añade recursos
- `baraja` → Baraja cartas
- `mira_mazo` → Mira/reordena mazo
- `mira_mano_oponente` → Mira mano oponente
- `anula` → Anula efectos/talismanes
- `copia_habilidad` → Copia habilidad/efecto
- `gana_habilidad` → Confiere habilidad
- `pierde_habilidad` → Quita habilidad
- `modifica_fuerza` → Modifica fuerza
- `modifica_coste` → Modifica costes
- `mueve_zona` → Mueve zona (exilia, cementerio, juego)
- `salta_fase` → Salta fases
- `tap` → Gira/inhabilita
- `trigger_al_entrar` → Trigger al entrar en juego
- `trigger_al_salir` → Trigger al salir
- `trigger_al_atacar` → Trigger al atacar
- `trigger_al_bloquear` → Trigger al bloquear
- `una_vez_por_turno` → Limitado por turno
- `opcional` → Efecto opcional (“puedes”)

## Estrategia de llenado
1) Sembrar catálogo en `tags`.
2) Auto-sugerencias desde `abilities_json`:
   - `trigger.type=enters_play` → `trigger_al_entrar`
   - `trigger.type=leaves_play` → `trigger_al_salir`
   - `trigger.type=attacks`/`declared_attacker` → `trigger_al_atacar`
   - `trigger.type=blocks`/`declared_blocker` → `trigger_al_bloquear`
   - `effect.type=draw_cards` → `roba_cartas`
   - `effect.type=destroy` → `destruye_objetivo`
   - `effect.type=exile` → `destierra_objetivo`
   - `effect.type=search` → `busca_mazo`
   - `effect.type=discard` → `descarta_mano` (si target es mano) o `bota_cartas` (si es mazo)
   - `effect.type=immunity` → `inmunidad`
   - `effect.type=modify_force` → `modifica_fuerza`
   - `effect.type=modify_cost` → `modifica_coste`
   - `effect.type=generate_resources` → `genera_recursos`
   - `effect.type=prevent_damage` → `previene_dano`
   - `effect.type=move_zone`/`put_in_play`/`reorder_deck` → `mueve_zona`/`mira_mazo`/`baraja`
   - `optional=true` → `opcional`
   - `oncePerTurn=true` → `una_vez_por_turno`
3) Curado manual: validar/ajustar sugerencias y añadir tags que dependan de texto específico.
4) Iterar cuando aparezcan nuevos `effect.type` o triggers.

## Integración con repos y motor
- `CardRepositorySQLite`:
  - Métodos sugeridos: `listarTags()`, `tagsPorCarta(id)`, `asignarTags(id, tagIds)`, `buscarPorTags(slugs, matchAll=true/false)`.
  - Flag `includeTags` opcional en `obtenerCarta` para no romper APIs actuales.
- Motor/juego:
  - Tags son metadatos para filtros/UI, no reemplazan reglas; la lógica sigue en `abilities_json`.
- Scripts:
  - `scripts/seed_tags.js` o SQL para crear tablas y sembrar catálogo.
  - `scripts/sugerir_tags_desde_abilities.js` para auto-sugerencias.
  - Exportador opcional para UI/analytics.

## Consultas útiles
- Cartas con un tag:
  `SELECT c.* FROM cartas c JOIN carta_tags ct ON ct.carta_id=c.id JOIN tags t ON t.id=ct.tag_id WHERE t.slug='imbloqueable';`
- Cartas con varios tags (match all): agrupar por carta y filtrar por COUNT = N tags.
- Ver tags de una carta: join simple `carta_tags -> tags`.

## Pasos siguientes
1) Acordar catálogo definitivo (slugs/nombres) y semilla.
2) Crear tablas `tags` y `carta_tags` en `server/data/game.db`. → SQL listo en `scripts/tags_schema_seed.sql`.
3) Sembrar catálogo base. → Incluido en el SQL (INSERT OR IGNORE).
4) Generar auto-sugerencias desde `abilities_json` y revisarlas. → Script listo: `node scripts/sugerir_tags_desde_abilities.js [ruta_db]` (solo lectura).
5) Exponer lectura/búsqueda por tags en el repositorio/API/UI.


