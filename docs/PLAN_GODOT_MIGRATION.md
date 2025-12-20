# Plan de migración a Godot (Web + móvil, WebSocket, imágenes locales)

## Objetivo y criterios de éxito
- Migrar el cliente a Godot 4.x (Web y móvil) manteniendo reglas y flujo actuales.
- Reutilizar backend Node/Express con WS para estado en tiempo real.
- Imágenes de cartas servidas localmente con caché básica.
- Criterio de listo: partida completa entre 2 clientes (desktop + móvil) cumpliendo `GAME_RULES.md`, con reconexión básica y assets locales funcionando.

## Supuestos y responsables
- Godot 4.x LTS, Node/Express versión actual.
- Roles sugeridos: Backend (WS, assets), Front Godot (escenas/UI), QA (tests multi-cliente/móvil).
- Entornos: dev/local primero; luego build Web y prueba en navegador móvil.

## Fase 0 – Alineación y entorno
- [x] Confirmar versiones y dependencias (Godot 4.x LTS, Node/Express).
- [x] Verificar ruta imágenes locales `public/images/cards_new` y convención id→filename.
- [x] Definir base URL backend y endpoint WS (`/ws/games/:id`); documentar en `.env` o config Godot.
- [x] Asegurar JWT disponible para el cliente Godot (almacenado seguro en Web export).
- [x] Salida: documento de configuración + check de assets presentes.

### Estado actual (17 Dec 2025)
- Backend: Node recomendado ≥18.x; dependencias clave `express@4.18.2`, `socket.io@4.6.1`, `jsonwebtoken@9.0.3`, `better-sqlite3@12.5.0`, `bcrypt@6.0.0`.
- Godot: no hay proyecto en repo; usar Godot 4.x LTS (sugerido 4.3 LTS) y generar proyecto nuevo para la fase 3.
- Imágenes: la carpeta `public/images/cards_new` aún no existe. Seguir `docs/EJECUTAR_DESCARGA_IMAGENES.txt` (`python scripts/descargar_y_organizar_imagenes.py`) para poblarla; los faltantes se listan en `server/data/cards/imagenes_no_descargadas.txt`.
- Base URL backend: `http://localhost:3000` (por defecto `PORT` env). WS via socket.io en `ws://localhost:3000/ws` con token Bearer en header o `handshake.auth.token`.
- JWT cliente: el frontend web guarda el token en `localStorage` como `auth_token` (`public/js/api.js`). El cliente Godot debe aceptar/inyectar el mismo token y enviarlo como `Authorization: Bearer <token>` tanto en REST como en WS.

## Fase 1 – Backend WebSocket
- [x] Elegir librería (`ws` preferido por simplicidad; socket.io si se necesita fallback).
- [x] Implementar upgrade WS en Express y encapsular en módulo `wsServer`.
- [x] Autenticación en `connection`: validar token Bearer; cerrar si inválido.
- [x] Salas por partida: `gameId -> Set<socket>`.
- [x] Protocolo entrante `{type:"action", accion, datos}` → reutilizar GameController/servicio.
- [x] Broadcast exitoso: `{type:"state", gameState, finalizado, ganador}` a la sala.
- [x] Errores: `{type:"error", message}` solo al emisor.
- [x] Heartbeat/ping 20–30s y limpieza en `close`.
- [x] REST `createGame`/`listGames` devuelven `gameId` y URL WS.
- [x] Salida: tests manuales con dos sockets simulados mostrando broadcast (ejecutado `npm run ws:smoke` con token de `OLVIDADO` y gameId `game_1766002547610_1esbr87jf` contra `ws://localhost:3001/ws`).

## Fase 2 – Backend imágenes
- [x] Confirmar mapeo `card.id` → filename (usar campo `imagen`; fallback `${id}.webp/png`). Si no se encuentra, usa placeholder configurable `CARD_PLACEHOLDER` (default `/images/cards_new/placeholder.svg`).
- [x] Servir estático `public/images/cards_new` (Express static ya incluye la ruta).
- [x] Placeholder por defecto si falta asset; documentado (`public/images/cards_new/placeholder.svg`).
- [x] Salida: endpoint accesible `/images/cards_new/:file` validado (200 para `placeholder.svg` en `/images/cards_new/placeholder.svg`; API devuelve `imagenUrl` local/externa según datos, con placeholder si no hay asset).

## Fase 3 – Godot estructura
- [x] Crear proyecto Godot 4 (viewport 16:9) y escena base `Main`.
- [x] Escenas: `Login`, `Lobby`, `Game`, `Card`, `CardZoomOverlay`, `ModalObjetivo`, `ModalDescarte` (stubs creados en `godot/scenes/`).
- [x] Scripts núcleo: `ApiClient.gd` (REST), `WsClient.gd` (WS), `GameStateView.gd` (render zonas), `CardLoader.gd` (texturas locales + caché), `InputMapper.gd` (gestos mobile opcional) en `godot/scripts/`.
- [x] Ajustes PWA/mobile: UI escalable, gestos tap/long-press/drag, scroll/carrusel (stubs preparados; falta pulir en editor).
- [x] Salida: proyecto compilando en editor, escenas stub con nodos principales (proyecto en `godot/project.godot`, main `Main.tscn` apunta a `Lobby.tscn`).

## Fase 4 – Godot layout y render
- [ ] Mesa: fila oponente (Oro, Apoyo, Defensa, Ataque), centro HUD/mensajes, fila jugador (Oro, Apoyo, Defensa, Ataque, Mano carrusel).
- [ ] Mano: carrusel horizontal con zoom al tap/hover.
- [ ] Zonas con scroll horizontal y placeholder “Vacío”.
- [ ] HUD: fase (Reagrupar, Comienzo de Vigilia, Vigilia, Batalla Mitológica, Final), turno, recursos disponibles/total; botones Pasar Fase/Pasar Turno habilitados según estado.
- [ ] CardZoomOverlay: nombre, tipo, fuerza, coste, texto/abilities.
- [ ] Salida: escena `Game` renderiza estado mock con al menos 1 carta en cada zona.

### Plan de trabajo Fase 4 (detallado)
1) Estado mock
   - Crear JSON/Dictionary en `Game.tscn` o script `GameStateView.gd` con todas las zonas pobladas (al menos 1 carta/placeholder).
   - Incluir mano jugador (5–7 cartas) y conteo mano oponente (solo número).
2) Layout base
   - Usar `VBoxContainer` raíz: fila oponente, HUD centro, fila jugador.
   - Cada fila: `HBoxContainer` con columnas Oro, Apoyo, Defensa, Ataque; mano sólo en fila jugador.
   - Cada zona: `ScrollContainer` + `HBoxContainer` con placeholder “Vacío” cuando no haya cartas.
3) Cartas y carrusel
   - Reutilizar escena `Card.tscn` para zonas y `HandCard` variante con tamaño reducido.
   - Carrusel mano: `ScrollContainer` horizontal con botones de flecha opcionales y `CardZoomOverlay` al hover/tap.
4) HUD y controles
   - Panel superior con textos: fase, turno actual, recursos disponibles/total.
   - Botones `Pasar Fase` y `Pasar Turno` con estados disabled según mock (`puedePasarFase`, `puedePasarTurno`).
   - Área de mensajes breves/toasts para errores o info.
5) Overlay y zoom
   - `CardZoomOverlay` centrado modal con datos: nombre, tipo, fuerza, coste, texto.
   - Cierre con tap/click fuera o botón X.
6) Responsivo y estilo
   - Ajustar tamaños: desktop carta 180px alto aprox., mobile 150px; margen/espaciado uniforme.
   - Probar en viewport 16:9 y en vertical estrecho simulando mobile; evitar overflow.
7) Validación de salida
   - Escena `Game` debe cargar y mostrar todas las zonas con datos mock sin errores en Godot editor.
   - Captura rápida (screenshot) para anexar en fase 7.

## Fase 5 – Interacción alineada a GAME_RULES.md
- [ ] Validar habilitación UI: Oro solo en Comienzo de Vigilia y si no jugó oro.
- [ ] Aliados/Tótems/Armas solo en Vigilia; Talismanes en Vigilia y Batalla.
- [ ] Ataque: solo en Batalla; un aliado no ataca dos veces; vuelve a Defensa en Reagrupar.
- [ ] Mano del oponente: mostrar conteo, no cartas.
- [ ] Modal de objetivos: defensores o Castillo; modal de descarte si >8 cartas tras robo.
- [ ] Mostrar fin de partida y ganador.
- [ ] Salida: lista de acciones UI vs regla validada con QA/`GAME_RULES.md`.

## Fase 6 – WS en Godot
- [ ] Tras create/load (REST), conectar WS con token y `gameId`.
- [ ] Enviar acciones `{type:"action", accion, datos}`.
- [ ] Recibir `{type:"state"}` → actualizar estado y re-render.
- [ ] Manejar `{type:"error"}` → toast/mensaje.
- [ ] Reconexión: N reintentos; si falla, ofrecer volver al lobby.
- [ ] Salida: partida completa entre 2 clientes Godot (desktop + incognito) sin desync.

## Fase 7 – Pruebas
- [ ] Dos clientes en misma partida: turnos, fases, jugar carta, atacar, descarte, derrota por mazo vacío.
- [ ] Mobile (Chrome Android/Safari iOS): gestos y tamaño de carta.
- [ ] Verificar carga de imágenes locales y fallback a placeholder.
- [ ] Salida: checklist de prueba con capturas o gifs cortos.

## Fase 8 – Optimización/UI
- [ ] Cache de texturas (no recargar cada frame).
- [ ] Animaciones ligeras (fade/slide) sin penalizar Web export.
- [ ] Ajustar tamaño carta (desktop 160–200px alto; mobile 140–160px) y espaciado.
- [ ] Salida: medición simple (FPS estable en escena de partida).

## Fase 9 – Entregables/handoff
- [ ] README cliente Godot: correr, exportar Web, configurar endpoint/token.
- [ ] Ejemplos payload WS y flujo de reconexión.
- [ ] Lista de pendientes/bugs si quedan abiertos.
- [ ] Confirmar cumplimiento de `GAME_RULES.md` (UI habilita según fase; backend valida).
- [ ] Salida: carpeta `docs/` con README + ejemplos + pendientes.
