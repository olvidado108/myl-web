extends Node

class_name ApiClient

@export var base_url: String = "http://localhost:3000"
var token: String = ""

func _ready() -> void:
	# En export Web, usar el mismo origen para evitar CORS
	if OS.has_feature("JavaScript"):
		var origin = JavaScriptBridge.eval("location.origin")
		if typeof(origin) == TYPE_STRING and origin != "":
			base_url = origin

func set_token(new_token: String) -> void:
	token = new_token

func _headers() -> PackedStringArray:
	var h := PackedStringArray()
	h.append("Content-Type: application/json")
	if token != "":
		h.append("Authorization: Bearer %s" % token)
	return h

func login(username: String, password: String) -> Dictionary:
	var body := {
		"username": username,
		"password": password
	}
	return await post_json("/api/auth/login", body)

func create_game(mazo1_id: String, mazo2_id: String = "", jugador2_id: String = "") -> Dictionary:
	var body := {"mazo1_id": mazo1_id}
	if mazo2_id != "":
		body["mazo2_id"] = mazo2_id
	if jugador2_id != "":
		body["jugador2_id"] = jugador2_id
	return await post_json("/api/games", body)

func list_games() -> Dictionary:
	return await get_json("/api/games")

func get_json(endpoint: String) -> Dictionary:
	return await _request(endpoint, HTTPClient.METHOD_GET, "")

func get_card(card_id: String) -> Dictionary:
	return await get_json("/api/cards/%s" % card_id)

func get_game(game_id: String) -> Dictionary:
	return await get_json("/api/games/%s" % game_id)

func perform_action(game_id: String, accion: String, datos: Dictionary = {}) -> Dictionary:
	return await post_json("/api/games/%s/actions" % game_id, {
		"accion": accion,
		"datos": datos
	})

func post_json(endpoint: String, body: Dictionary) -> Dictionary:
	return await _request(endpoint, HTTPClient.METHOD_POST, JSON.stringify(body))

func _request(endpoint: String, method: int, body_str: String) -> Dictionary:
	var http := HTTPRequest.new()
	add_child(http)
	var err := http.request("%s%s" % [base_url, endpoint], _headers(), method, body_str)
	if err != OK:
		return {"success": false, "error": "HTTP error %s" % err}
	var result = await http.request_completed
	http.queue_free()
	if result.size() < 4:
		return {"success": false, "error": "Respuesta incompleta"}
	var _response_code: int = int(result[1])
	var payload := {}
	var body_bytes: PackedByteArray = result[3]
	if body_bytes.size() > 0:
		var json := JSON.new()
		var parse_res := json.parse(body_bytes.get_string_from_utf8())
		if parse_res == OK:
			payload = json.data
		else:
			payload = {"success": false, "error": "JSON parse error"}
	if _response_code != 200:
		print("HTTP ", _response_code, " en ", endpoint, " body: ", payload)
	return payload
