extends Node
class_name WsClient

@export var url: String = "ws://localhost:3000/ws"
@export var token: String = ""
@export var game_id: String = ""

var _connected: bool = false
var _use_js: bool = OS.has_feature("JavaScript") # socket.io handshake solo en export Web

signal state_received(data)
signal error_received(message)
signal connected()
signal disconnected()

func is_ws_connected() -> bool:
	return _connected

func connect_ws() -> void:
	if _use_js:
		_connect_socket_io_js()
	else:
		push_warning("El backend usa socket.io; este cliente WS plano no es compatible en desktop. Usa export Web o REST como respaldo.")
		_connected = false

func _connect_socket_io_js() -> void:
	var js_template := """
(() => {
  if (!window._godotSocketQueue) window._godotSocketQueue = [];
  const enqueue = (ev) => window._godotSocketQueue.push(ev);
  function start() {
    try {
      if (window._godotSocket) { window._godotSocket.disconnect(); }
      const opts = { path: "/ws", auth: {}, query: {} };
      const token = __TOKEN__;
      const gameId = __GAMEID__;
      if (token) opts.auth.token = token;
      if (token) opts.query.token = token; // compat con middleware actual
      if (gameId) opts.query.gameId = gameId;
      const socket = window.io(__URL__, opts);
      window._godotSocket = socket;
      socket.on("connect", () => enqueue({ type: "connected" }));
      socket.on("disconnect", (reason) => enqueue({ type: "disconnected", reason }));
      socket.on("state", (data) => enqueue({ type: "state", data }));
      socket.on("error", (err) => enqueue({ type: "error", message: (err && err.message) || String(err) }));
      socket.on("connect_error", (err) => enqueue({ type: "error", message: (err && err.message) || String(err) }));
    } catch (e) {
      enqueue({ type: "error", message: e.message });
    }
  }
  if (window.io) { start(); }
  else {
    const s = document.createElement("script");
    s.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";
    s.onload = start;
    s.onerror = () => enqueue({ type: "error", message: "No se pudo cargar socket.io client" });
    document.head.appendChild(s);
  }
})();
"""
	var js_filled := js_template
	js_filled = js_filled.replace("__TOKEN__", JSON.stringify(token))
	js_filled = js_filled.replace("__GAMEID__", JSON.stringify(game_id))
	js_filled = js_filled.replace("__URL__", JSON.stringify(url))
	JavaScriptBridge.eval(js_filled)

func _process(_delta: float) -> void:
	if _use_js:
		while true:
			var ev = JavaScriptBridge.eval("(() => { const q = window._godotSocketQueue || []; return q.length ? q.shift() : null; })()")
			if ev == null:
				break
			if typeof(ev) != TYPE_DICTIONARY:
				continue
			var ev_type: String = str(ev.get("type", ""))
			match ev_type:
				"connected":
					_connected = true
					emit_signal("connected")
					if game_id != "":
						join_game(game_id)
				"disconnected":
					_connected = false
					emit_signal("disconnected")
				"state":
					emit_signal("state_received", ev.get("data", {}))
				"error":
					emit_signal("error_received", ev.get("message", "error"))
		return
	# No-op en desktop: no WS compatible disponible

func join_game(game_id_override := "") -> void:
	if game_id_override != "":
		game_id = game_id_override
	if not _connected or game_id == "":
		return
	if _use_js:
		var payload := JSON.stringify({"gameId": game_id})
		JavaScriptBridge.eval("(() => { const s = window._godotSocket; if (s) s.emit('join_game', " + payload + "); })()")

func send_action(accion: String, datos := {}):
	if not _connected or accion == "":
		return
	if _use_js:
		var payload := JSON.stringify({"gameId": game_id, "accion": accion, "datos": datos})
		JavaScriptBridge.eval("(() => { const s = window._godotSocket; if (s) s.emit('action', " + payload + "); })()")
