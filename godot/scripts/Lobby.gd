extends Control

@export var token: String = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzE3NjU1ODU3NDc0MTRfYXg2MmhoZXJtIiwidXNlcm5hbWUiOiJPTFZJREFETyIsImlzQWRtaW4iOjEsImlhdCI6MTc2NjA5ODQwNiwiZXhwIjoxNzY2NzAzMjA2fQ.nb0XXdj3vz565vCDtaOruiFzD_k6XJlvmLx6kzzDcyA" # JWT de prueba local (7d)
@export var default_mazo_id: String = "deck_1765951885065_v5vzfoxks"
@export var api_path: NodePath = NodePath("Api")
@onready var _create_btn: Button = $"Root/CreateButton"
@onready var _join_btn: Button = $"Root/JoinButton"
@onready var _game_input: LineEdit = $"Root/GameIdInput"

var api: ApiClient

func _ready() -> void:
	api = get_node_or_null(api_path)
	if api:
		api.set_token(token)
	_connect_ui()

func _connect_ui() -> void:
	if _create_btn:
		_create_btn.pressed.connect(_on_create_pressed)
	if _join_btn:
		_join_btn.pressed.connect(_on_join_pressed)

func _on_create_pressed() -> void:
	if api == null:
		print("ApiClient no asignado")
		return
	if token == "":
		print("Token vacío, no se puede crear partida")
		return
	print("Creando partida con mazo ", default_mazo_id)
	var res = await api.create_game(default_mazo_id)
	print(res)
	if res.has("data") and res["data"].has("partida"):
		var game_id = res["data"]["partida"]["id"]
		_game_input.text = str(game_id)
		print("Partida creada: ", game_id)

func _on_join_pressed() -> void:
	var game_id = _game_input.text.strip_edges()
	if game_id == "":
		print("Ingresa un gameId para unirse")
		return
	print("Unirse a partida: ", game_id)
	# Guardar en metadata y cambiar a Game
	var session := {"token": token, "game_id": game_id}
	get_tree().set_meta("session", session)
	get_tree().change_scene_to_file("res://scenes/Game.tscn")






