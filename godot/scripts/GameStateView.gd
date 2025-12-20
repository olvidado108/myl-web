extends Control
class_name GameStateView

@export var hand_path: NodePath = NodePath("HandContainer/HandScroll/Hand")
@export var hand_count_path: NodePath = NodePath("HandContainer/HandHeader/HandCount")
@export var opponent_row: NodePath = NodePath("OpponentRow")
@export var player_row: NodePath = NodePath("PlayerRow")
@export var hud_path: NodePath = NodePath("HUD")
@export var api_path: NodePath = NodePath("../Api")
@export var message_path: NodePath = NodePath("Message")
@export var use_mock_on_empty: bool = true

var card_scene: PackedScene = preload("res://scenes/Card.tscn")
var state := {}
var api: ApiClient
var _card_cache: Dictionary = {}

@onready var _opp_zone_nodes := {
	"oro": $"Root/Board/OpponentBoard/OppRight/OppOroPanel/OppOroScroll/Cards",
	"apoyo": $"Root/Board/OpponentBoard/OppCenter/OppApoyoPanel/OppApoyoScroll/Cards",
	"defensa": $"Root/Board/OpponentBoard/OppCenter/OppDefensaPanel/OppDefensaScroll/Cards",
	"ataque": $"Root/Board/OpponentBoard/OppCenter/OppAtaquePanel/OppAtaqueScroll/Cards",
	"mazo": $"Root/Board/OpponentBoard/OppLeft/OppDeckPanel/OppDeckCards",
	"cementerio": $"Root/Board/OpponentBoard/OppLeft/OppCementerioPanel/OppCementerioCards",
	"destierro": $"Root/Board/OpponentBoard/OppLeft/OppDestierroPanel/OppDestierroCards",
	"reserva": $"Root/Board/OpponentBoard/OppRight/OppReservaPanel/OppReservaScroll/Cards",
}

@onready var _player_zone_nodes := {
	"oro": $"Root/Board/PlayerBoard/PlayerRight/PlayerOroPanel/PlayerOroScroll/Cards",
	"apoyo": $"Root/Board/PlayerBoard/PlayerCenter/PlayerApoyoPanel/PlayerApoyoScroll/Cards",
	"defensa": $"Root/Board/PlayerBoard/PlayerCenter/PlayerDefensaPanel/PlayerDefensaScroll/Cards",
	"ataque": $"Root/Board/PlayerBoard/PlayerCenter/PlayerAtaquePanel/PlayerAtaqueScroll/Cards",
	"mazo": $"Root/Board/PlayerBoard/PlayerLeft/PlayerDeckPanel/PlayerDeckCards",
	"cementerio": $"Root/Board/PlayerBoard/PlayerLeft/PlayerCementerioPanel/PlayerCementerioCards",
	"destierro": $"Root/Board/PlayerBoard/PlayerLeft/PlayerDestierroPanel/PlayerDestierroCards",
	"reserva": $"Root/Board/PlayerBoard/PlayerRight/PlayerReservaPanel/PlayerReservaScroll/Cards",
}

func _ready() -> void:
	if state.is_empty() and use_mock_on_empty:
		state = _build_mock_state()
		await _render()

func set_state(new_state: Dictionary) -> void:
	state = new_state
	await _render()

func _render() -> void:
	if api == null:
		api = get_node_or_null(api_path) as ApiClient
	var players: Dictionary = state.get("jugadores", {})
	var me_key: String = _current_player_key(players)
	var opp_key: String = _opponent_key(players, me_key)
	var me: Dictionary = players.get(me_key, {})
	var opp: Dictionary = players.get(opp_key, {})

	await _render_hand(me)
	await _render_zone_group(_player_zone_nodes, me)
	await _render_zone_group(_opp_zone_nodes, opp)
	_render_message()

func _render_hand(me: Dictionary) -> void:
	var hand: HBoxContainer = get_node_or_null(hand_path) as HBoxContainer
	var hand_count_label: Label = get_node_or_null(hand_count_path) as Label
	if hand == null:
		return
	for c in hand.get_children():
		c.queue_free()
	var mano_val = me.get("mano", [])
	if typeof(mano_val) != TYPE_ARRAY:
		mano_val = []
	var mano: Array = mano_val
	if hand_count_label:
		hand_count_label.text = "%s cartas" % str(mano.size())
	for card_id in mano:
		var card := card_scene.instantiate()
		card.scale = Vector2.ONE * 0.9
		hand.add_child(card)
		var loader := card as CardLoader
		if loader:
			var data := await _get_card_data(card_id)
			if is_instance_valid(loader):
				loader.set_card(data)
		else:
			card.get_node("Title").text = str(card_id)

func _render_zone_group(zones: Dictionary, player: Dictionary) -> void:
	for zone_name in zones.keys():
		var container_node = zones[zone_name]
		if container_node == null:
			continue
		var is_deck_like: bool = zone_name in ["mazo", "cementerio", "destierro", "reserva"]
		var container: HBoxContainer = container_node as HBoxContainer
		if container == null:
			continue
		for c in container.get_children():
			c.queue_free()
		var cards_val = player.get(zone_name, [])
		if typeof(cards_val) != TYPE_ARRAY:
			cards_val = []
		var cards: Array = cards_val
		if cards.is_empty():
			var placeholder := Label.new()
			placeholder.text = "Vacío / pila" if is_deck_like else "Vacío"
			placeholder.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			container.add_child(placeholder)
			continue
		for card_id in cards:
			var card := card_scene.instantiate()
			card.scale = Vector2.ONE * (0.75 if is_deck_like else 0.8)
			container.add_child(card)
			var loader := card as CardLoader
			if loader:
				var data := await _get_card_data(card_id)
				if is_instance_valid(loader):
					loader.set_card(data)
			else:
				card.get_node("Title").text = str(card_id)

func _render_message() -> void:
	var message_node := get_node_or_null(message_path)
	if message_node == null:
		return
	var text_val: String = str(state.get("mensaje", "Escena mock: coloca cartas respetando línea y fase."))
	if message_node is RichTextLabel:
		message_node.bbcode_enabled = true
		message_node.text = text_val
	elif message_node is Label:
		message_node.text = text_val

func _current_player_key(players: Dictionary) -> String:
	for k in players.keys():
		var mano_val = players[k].get("mano", null)
		if typeof(mano_val) == TYPE_ARRAY:
			return k
	for k in players.keys():
		return k
	return ""

func _opponent_key(players: Dictionary, me_key: String) -> String:
	for k in players.keys():
		if k != me_key:
			return k
	return ""

func _get_card_data(card_id: String) -> Dictionary:
	if _card_cache.has(card_id):
		return _card_cache[card_id]
	if api == null:
		return {"id": card_id, "nombre": str(card_id), "coste": 0, "fuerza": 0, "tipo": "", "imagenUrl": ""}
	var res := await api.get_card(card_id)
	var data := {}
	if res.has("data"):
		print("get_card ok ", card_id, " -> ", res["data"].get("nombre", ""))
		data = res["data"]
	else:
		print("No data para carta ", card_id, " resp: ", res)
		data = {"id": card_id, "nombre": str(card_id), "coste": 0, "fuerza": 0, "tipo": "", "imagenUrl": ""}
	_card_cache[card_id] = data
	return data

func _build_mock_state() -> Dictionary:
	return {
		"fase": "Batalla Mitológica",
		"turnoNumero": 3,
		"turnoActual": "jugador_1",
		"puedePasarFase": true,
		"puedePasarTurno": false,
		"recursos": {"disponibles": 2, "totales": 3},
		"mensaje": "[center]Mock: coloca cartas en sus líneas; mazo/cementerio visibles a la izquierda; oro pagado y reserva a la derecha.[/center]",
		"jugadores": {
			"jugador_1": {
				"nombre": "Tú",
				"mano": ["ALIADO_DEF_01", "ARMA_01", "TALISMAN_01", "ALIADO_ATK_01", "TOTEM_01", "CARTA_EXTRA_01", "CARTA_EXTRA_02", "CARTA_EXTRA_03"],
				"oro": ["ORO_INICIAL", "ORO_BOSQUE"],
				"apoyo": ["TOTEM_01", "ARMA_01"],
				"defensa": ["ALIADO_DEF_01", "ALIADO_DEF_02"],
				"ataque": ["ALIADO_ATK_01"],
				"mazo": ["MAZO_TAPA"],
				"cementerio": ["CEM_01"],
				"destierro": [],
				"reserva": ["ORO_INICIAL"],
				"recursos": {"disponibles": 2, "totales": 3},
			},
			"jugador_2": {
				"nombre": "Oponente",
				"mano": [],
				"manoConteo": 4,
				"oro": ["ORO_RIO"],
				"apoyo": ["TOTEM_OP_01"],
				"defensa": ["ALIADO_OP_DEF"],
				"ataque": ["ALIADO_OP_ATK"],
				"mazo": ["MAZO_OP"],
				"cementerio": ["CEM_OP_01"],
				"destierro": [],
				"reserva": ["ORO_RIO"],
				"recursos": {"disponibles": 1, "totales": 2},
			},
		},
	}
