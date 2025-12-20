# WebSocket para partidas (socket.io)

## Endpoint
- URL base: mismo host/puerto que Express.
- Path: `/ws`
- Transporte: socket.io (usa WebSocket cuando está disponible).

## Autenticación
- En el handshake:
  - Header: `Authorization: Bearer <token>`
  - o `auth: { token: "<token>" }` en la conexión.
- Requisito: el token debe ser válido (JWT existente en el backend).

## Smoke test rápido (dev)
- Script: `npm run ws:smoke -- --gameId=ID --token=JWT [--url=ws://localhost:3000/ws] [--action=pasar_fase] [--datos='{}']`
- Variables de entorno alternativas: `WS_URL`, `AUTH_TOKEN`, `GAME_ID`, `ACTION`, `DATOS`.
- Requisitos: servidor arriba, gameId existente, token del jugador de esa partida.

### Credenciales y ejemplo local (solo entorno de pruebas)
- Login para obtener token:
  ```bash
  curl -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"OLVIDADO","password":"Olvidado108$"}'
  ```
  La respuesta incluye `data.token` (JWT).
- Crear partida con mazo de prueba:
  ```bash
  curl -X POST http://localhost:3000/api/games \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <TOKEN>" \
    -d '{"mazo1_id":"deck_1765951885065_v5vzfoxks"}'
  ```
  La respuesta devuelve `data.partida.id` (úsalo como `gameId`) y `ws.url`.
- Probar WS:
  ```bash
  npm run ws:smoke -- --gameId=<ID> --token=<TOKEN> --url=ws://localhost:3000/ws
  ```

## Flujo
1) Conectar con token.
2) Emitir `join_game` con `{ gameId }`.
   - Respuesta: evento `state` con estado filtrado para el jugador.
3) Emitir acciones con `action`:
   - Payload: `{ gameId?, accion, datos }`
   - `gameId` opcional si ya se hizo `join_game` (se usa el que quedó en `socket.data`).
4) Recibir actualizaciones:
   - Evento `state` tras cada acción válida:
     - `{ gameState, finalizado, ganador, resultado? }`
   - Evento `error` en caso de fallo:
     - `{ message }`

## Acciones soportadas (`accion`)
- `jugar_carta` → datos `{ carta_id, objetivo_id?, posicion? }`
- `atacar` → datos `{ atacante_id, objetivo_id }` (`objetivo_id` puede ser null para Castillo)
- `pasar_fase`
- `pasar_turno`
- `robar_carta` (solo válido si la fase lo permite; el backend valida)

### Ejemplos de payload de acción
- Pasar fase:
  ```json
  { "accion": "pasar_fase" }
  ```
- Jugar carta (aliado/tótem/arma):
  ```json
  { "accion": "jugar_carta", "datos": { "carta_id": "ID_CARTA" } }
  ```
- Jugar oro:
  ```json
  { "accion": "jugar_carta", "datos": { "carta_id": "ID_ORO" } }
  ```
- Atacar a un aliado defensor:
  ```json
  { "accion": "atacar", "datos": { "atacante_id": "ID_ATACANTE", "objetivo_id": "ID_DEFENSOR" } }
  ```
- Atacar Castillo (sin objetivo):
  ```json
  { "accion": "atacar", "datos": { "atacante_id": "ID_ATACANTE", "objetivo_id": null } }
  ```
- Pasar turno:
  ```json
  { "accion": "pasar_turno" }
  ```
- Robar carta (si fase lo permite):
  ```json
  { "accion": "robar_carta" }
  ```

## Ejemplo (socket.io client)
```js
import { io } from "socket.io-client";

const socket = io("http://localhost:3000", {
  path: "/ws",
  auth: { token: "<JWT>" }
});

socket.on("connect", () => {
  socket.emit("join_game", { gameId: "<id-de-partida>" });
});

socket.on("state", (payload) => {
  console.log("estado", payload);
});

socket.on("error", (err) => {
  console.error("ws error", err);
});

// Ejemplo de acción:
socket.emit("action", { accion: "pasar_fase" });
```

## Notas de seguridad y CORS
- Actualmente `origin: '*'` en socket.io (ajustar en producción).
- Mantener el token fresco: si expira, reconectar con token nuevo.

## Consideraciones de cliente (Godot)
- Conectar tras crear/cargar partida (REST).
- Guardar `gameId` y token; emitir `join_game`.
- Reaccionar a `state` actualizando UI; mostrar mano del oponente solo como conteo (ya viene filtrado).
- Manejar reconexión y re-emisión de `join_game` tras reconnect.

## Ejemplo rápido de conexión en Godot 4 (GDScript)
```gdscript
extends Node

var client := SocketIOClient.new()
var ws_url := "http://localhost:3000" # Ajustar host/puerto
var jwt := "<JWT>"
var game_id := "<id-de-partida>"

func _ready():
    client.connect("connected", Callable(self, "_on_connected"))
    client.connect("connection_error", Callable(self, "_on_error"))
    client.connect("error", Callable(self, "_on_error"))
    client.connect("disconnected", Callable(self, "_on_disconnected"))
    client.connect("state", Callable(self, "_on_state"))

    var opts = {
        "path": "/ws",
        "auth": { "token": jwt }
    }
    client.connect_to_url(ws_url, opts)

func _on_connected(_args = null):
    client.emit("join_game", { "gameId": game_id })

func _on_state(payload):
    print("state: ", payload)

func _on_error(err):
    print("ws error: ", err)

func _on_disconnected(_args = null):
    print("ws disconnected")
```
