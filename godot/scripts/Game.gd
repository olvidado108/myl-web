extends Control

@export var ws_url: String = "ws://localhost:3000/ws"
@export var token: String = ""
@export var game_id: String = ""
@export var ws_path: NodePath = NodePath("Ws")
@export var view_path: NodePath = NodePath("Root")
@export var api_path: NodePath = NodePath("Api")
@onready var phase_label: Label = $"Root/HUD/HudInfo/PhaseLabel"
@onready var turn_label: Label = $"Root/HUD/HudInfo/TurnLabel"
@onready var resources_label: Label = $"Root/HUD/HudInfo/ResourcesLabel"
@onready var pass_phase_btn: Button = $"Root/HUD/Buttons/PassPhase"
@onready var pass_turn_btn: Button = $"Root/HUD/Buttons/PassTurn"
var ws
var view: GameStateView = null
var api: ApiClient = null

func _ready() -> void:
	# Recuperar datos pasados desde Lobby vía metadata
	var session: Variant = {}
	if get_tree().has_meta("session"):
		session = get_tree().get_meta("session")
	if session is Dictionary:
		if session.has("token"):
			token = session["token"]
		if session.has("game_id"):
			game_id = session["game_id"]
	# Obtener nodos
	ws = get_node_or_null(ws_path)
	view = get_node_or_null(view_path) as GameStateView
	api = get_node_or_null(api_path) as ApiClient
	if api and token != "":
		api.set_token(token)
	if ws:
		ws.url = ws_url
		ws.token = token
		ws.game_id = game_id
		ws.state_received.connect(_on_state_received)
		ws.error_received.connect(_on_ws_error)
		ws.connected.connect(_on_ws_connected)
		ws.connect_ws()
	_connect_ui()
	# fallback: cargar estado por REST para mostrar algo aunque WS falle
	if api and game_id != "":
		_load_state_rest()

func _on_ws_connected() -> void:
	if ws and game_id != "":
		ws.join_game(game_id)

func _on_state_received(data: Dictionary) -> void:
	_update_hud(data.get("gameState", data))
	if view:
		await view.set_state(data.get("gameState", data))

func _on_ws_error(msg) -> void:
	print("WS error: ", msg)

func _connect_ui() -> void:
	if pass_phase_btn:
		pass_phase_btn.pressed.connect(_on_pass_phase)
	if pass_turn_btn:
		pass_turn_btn.pressed.connect(_on_pass_turn)

func _update_hud(state: Dictionary) -> void:
	if not state:
		return
	if phase_label and state.has("fase"):
		phase_label.text = "Fase: %s" % str(state["fase"])
	if turn_label:
		var turno: String = str(state.get("turnoNumero", ""))
		var jugador: String = str(state.get("turnoActual", ""))
		turn_label.text = "Turno: %s (%s)" % [str(turno), str(jugador)]
	if resources_label:
		var recursos := _extract_recursos(state)
		if recursos is Dictionary and recursos.size() > 0:
			var disp := int(recursos.get("disponibles", recursos.get("available", 0)))
			var total := int(recursos.get("totales", recursos.get("total", 0)))
			resources_label.text = "Oro: %s / %s" % [disp, total]
	if pass_phase_btn:
		pass_phase_btn.disabled = not bool(state.get("puedePasarFase", true))
	if pass_turn_btn:
		pass_turn_btn.disabled = not bool(state.get("puedePasarTurno", true))

func _on_pass_phase() -> void:
	if _is_ws_connected():
		ws.send_action("pasar_fase")
	elif api and game_id != "":
		var res := await api.perform_action(game_id, "pasar_fase", {})
		if res.has("data") and res["data"].has("gameState"):
			await _on_state_received({"gameState": res["data"]["gameState"]})

func _on_pass_turn() -> void:
	if _is_ws_connected():
		ws.send_action("pasar_turno")
	elif api and game_id != "":
		var res := await api.perform_action(game_id, "pasar_turno", {})
		if res.has("data") and res["data"].has("gameState"):
			await _on_state_received({"gameState": res["data"]["gameState"]})

func _is_ws_connected() -> bool:
	return ws != null and ws.has_method("is_ws_connected") and ws.is_ws_connected()

func _load_state_rest() -> void:
	var res: Dictionary = await api.get_game(game_id)
	if not res.has("data"):
		print("REST get_game sin data: ", res)
		return
	if res.has("data") and res["data"].has("gameState"):
		await _on_state_received({"gameState": res["data"]["gameState"]})
	else:
		print("REST get_game sin gameState: ", res)

func _extract_recursos(state: Dictionary) -> Dictionary:
	if state.has("recursos") and state["recursos"] is Dictionary:
		return state["recursos"]
	if state.has("jugadores") and state["jugadores"] is Dictionary:
		for k in state["jugadores"].keys():
			var jugador: Dictionary = state["jugadores"][k] if state["jugadores"][k] is Dictionary else {}
			if jugador.has("recursos") and jugador["recursos"] is Dictionary:
				return jugador["recursos"]
			# tolerar nombres alternos
			if jugador.has("oroDisponibles") or jugador.has("oroTotales"):
				return {
					"disponibles": jugador.get("oroDisponibles", 0),
					"totales": jugador.get("oroTotales", 0),
				}
	return {}






