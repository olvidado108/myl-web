extends Control
class_name CardLoader

@export var title_path: NodePath = NodePath("VBox/Title")
@export var meta_path: NodePath = NodePath("VBox/Meta")
@export var texture_path: NodePath = NodePath("VBox/Texture")
@export var placeholder: Texture2D = preload("res://assets/placeholder.svg")
@export var image_base: String = "http://localhost:3000" # para rutas /images/...

var card_data: Dictionary = {}
var _cache: Dictionary = {}
@export var hover_scale: float = 3.0
@export var hover_tween_time: float = 0.08
@export var hover_escape_clip: bool = true
@export var hover_limit_to_original_area: bool = true
@export var hover_screen_margin: float = 8.0
var _hover_tween: Tween
var _scroll_container: ScrollContainer
var _orig_clip: bool = true
var _is_hovering: bool = false
var _hover_offset: Vector2 = Vector2.ZERO

func _ready():
	# En Web, usar el mismo origen para evitar CORS
	if OS.has_feature("JavaScript"):
		var origin = JavaScriptBridge.eval("location.origin")
		if typeof(origin) == TYPE_STRING and origin != "":
			image_base = origin
	mouse_filter = Control.MOUSE_FILTER_STOP
	# Centrar pivot para que el escalado de hover se vea natural
	_update_pivot()
	resized.connect(_update_pivot)
	_scroll_container = _find_scroll_container()
	if _scroll_container:
		_orig_clip = _scroll_container.clip_contents
	# Hover para zoom
	mouse_entered.connect(_on_mouse_entered)
	mouse_exited.connect(_on_mouse_exited)

func _gui_input(event: InputEvent) -> void:
	if not hover_limit_to_original_area:
		return
	if not _is_hovering:
		return
	if event is InputEventMouseMotion:
		var s := scale
		var safe_scale := Vector2(s.x if s.x != 0 else 1.0, s.y if s.y != 0 else 1.0)
		var local := get_local_mouse_position()
		var unscaled := Vector2(local.x / safe_scale.x, local.y / safe_scale.y)
		if not Rect2(Vector2.ZERO, size).has_point(unscaled):
			_on_mouse_exited()

func set_card(data: Dictionary) -> void:
	card_data = data
	_update_ui()
	_update_zoom_overlay(false)

func _update_ui() -> void:
	var title_node: Label = get_node_or_null(title_path) as Label
	var meta_node: Label = get_node_or_null(meta_path) as Label
	var tex_node: TextureRect = get_node_or_null(texture_path) as TextureRect
	print("CardLoader data: ", card_data)

	if title_node:
		title_node.text = card_data.get("nombre", "Sin nombre")
	if meta_node:
		var coste: int = int(card_data.get("coste", 0))
		var fuerza: int = int(card_data.get("fuerza", 0))
		meta_node.text = "Coste %s / Fuerza %s" % [coste, fuerza]

	if tex_node:
		var url: String = str(card_data.get("imagenUrl", ""))
		if url == "":
			tex_node.texture = placeholder
			_update_zoom_overlay(false, tex_node.texture)
			return
		if _cache.has(url):
			tex_node.texture = _cache[url]
			_update_zoom_overlay(false, tex_node.texture)
			return
		await _load_texture_async(url, tex_node)
		_update_zoom_overlay(false, tex_node.texture)

func _load_texture_async(url: String, tex_node: TextureRect) -> void:
	var final_url := url
	if url.begins_with("/"):
		final_url = "%s%s" % [image_base, url]

	var http := HTTPRequest.new()
	add_child(http)
	var err := http.request(final_url)
	if err != OK:
		print("HTTP request error ", err, " url=", final_url)
		tex_node.texture = placeholder
		http.queue_free()
		return
	var result = await http.request_completed
	http.queue_free()
	if result.size() < 4:
		print("HTTP result incompleto url=", final_url, " result=", result)
		tex_node.texture = placeholder
		return
	var status := int(result[1])
	var headers: PackedStringArray = result[2]
	var body: PackedByteArray = result[3]
	if status != 200 or body.size() == 0:
		print("HTTP status ", status, " body.size=", body.size(), " url=", final_url)
		tex_node.texture = placeholder
		return

	var img := Image.new()
	var ext := final_url.to_lower()
	var content_type := ""
	for h in headers:
		var hs := str(h).to_lower()
		if hs.begins_with("content-type"):
			content_type = hs
			break
	# Si el backend devuelve placeholder SVG u otra respuesta de texto, no intentes decodificarla como PNG
	if ext.ends_with(".svg") or content_type.find("svg") != -1:
		_cache[url] = placeholder
		tex_node.texture = placeholder
		return
	if content_type.find("json") != -1 or content_type.find("html") != -1 or content_type.begins_with("text/"):
		print("HTTP content-type no imagen ", content_type, " url=", final_url)
		_cache[url] = placeholder
		tex_node.texture = placeholder
		return
	# Sniff de cuerpo binario sin parsear texto para evitar errores de unicode
	var is_text_like := false
	if body.size() > 0:
		var b0 := body[0]
		if b0 == 0x3C or b0 == 0x7B or b0 == 0x5B: # '<' '{' '['
			is_text_like = true
	if is_text_like:
		print("HTTP body no imagen (sniff byte) url=", final_url, " first_byte=0x", String.num_int64(body[0], 16))
		_cache[url] = placeholder
		tex_node.texture = placeholder
		return

	# Detección por firmas mágicas para evitar tratar binario no imagen
	var is_png_sig := body.size() >= 8 and body[0] == 0x89 and body[1] == 0x50 and body[2] == 0x4E and body[3] == 0x47 and body[4] == 0x0D and body[5] == 0x0A and body[6] == 0x1A and body[7] == 0x0A
	var is_jpg_sig := body.size() >= 3 and body[0] == 0xFF and body[1] == 0xD8 and body[2] == 0xFF
	var is_webp_sig := false
	if body.size() >= 12:
		var riff := body.slice(0, 4).get_string_from_ascii()
		var webp := body.slice(8, 12).get_string_from_ascii()
		is_webp_sig = riff == "RIFF" and webp == "WEBP"
	var load_err := ERR_FILE_CORRUPT
	var tried := []
	var _try_load_png := func():
		tried.append("png")
		return img.load_png_from_buffer(body)
	var _try_load_jpg := func():
		tried.append("jpg")
		return img.load_jpg_from_buffer(body)
	var _try_load_webp := func():
		tried.append("webp")
		if img.has_method("load_webp_from_buffer"):
			return img.load_webp_from_buffer(body)
		return ERR_FILE_CORRUPT

	if content_type.find("jpeg") != -1 or content_type.find("jpg") != -1 or ext.ends_with(".jpg") or ext.ends_with(".jpeg") or is_jpg_sig:
		load_err = _try_load_jpg.call()
		if load_err != OK:
			load_err = _try_load_png.call()
	elif content_type.find("png") != -1 or ext.ends_with(".png") or is_png_sig:
		load_err = _try_load_png.call()
		if load_err != OK:
			load_err = _try_load_jpg.call()
	elif content_type.find("webp") != -1 or ext.ends_with(".webp") or is_webp_sig:
		load_err = _try_load_webp.call()
		if load_err != OK:
			load_err = _try_load_png.call()
	else:
		# Desconocido: probar en orden jpg -> png -> webp
		load_err = _try_load_jpg.call()
		if load_err != OK:
			load_err = _try_load_png.call()
		if load_err != OK:
			load_err = _try_load_webp.call()

	if load_err != OK:
		print("Imagen load error ", load_err, " url=", final_url, " ext=", ext, " ctype=", content_type, " size=", body.size(), " tried=", tried)
		tex_node.texture = placeholder
		return

	var tex := ImageTexture.create_from_image(img)
	_cache[url] = tex
	tex_node.texture = tex
	_update_zoom_overlay(false, tex_node.texture)

func _on_mouse_entered() -> void:
	_is_hovering = true
	_animate_hover(true)
	_update_zoom_overlay(true)

func _on_mouse_exited() -> void:
	if not _is_hovering:
		return
	_is_hovering = false
	_animate_hover(false)
	_update_zoom_overlay(false)

func _update_zoom_overlay(show_overlay: bool, tex: Texture2D = null) -> void:
	var overlay = get_tree().get_first_node_in_group("card_zoom_overlay")
	if overlay == null or not overlay is Control:
		return
	overlay.visible = show_overlay
	if not show_overlay:
		return
	var tex_node: TextureRect = overlay.get_node_or_null("Texture") as TextureRect
	var title_node: Label = overlay.get_node_or_null("Title") as Label
	var stats_node: Label = overlay.get_node_or_null("Stats") as Label
	var body_node: RichTextLabel = overlay.get_node_or_null("Body") as RichTextLabel
	if title_node:
		title_node.text = card_data.get("nombre", "Sin nombre")
	if stats_node:
		var coste: int = int(card_data.get("coste", 0))
		var fuerza: int = int(card_data.get("fuerza", 0))
		stats_node.text = "Coste %s / Fuerza %s" % [coste, fuerza]
	if tex_node:
		if tex != null:
			tex_node.texture = tex
		elif texture_path != NodePath() and has_node(texture_path):
			var small_tex: TextureRect = get_node(texture_path)
			tex_node.texture = small_tex.texture
		else:
			tex_node.texture = placeholder
	if body_node:
		var texto: String = str(card_data.get("textoHabilidad", ""))
		body_node.text = texto

func _animate_hover(hovering: bool) -> void:
	if _hover_tween:
		_hover_tween.kill()
	if hover_escape_clip and _scroll_container:
		_scroll_container.clip_contents = not hovering and _orig_clip or false
	if not hovering and _hover_offset != Vector2.ZERO:
		position -= _hover_offset
		_hover_offset = Vector2.ZERO
	_hover_tween = create_tween()
	var target_scale_value := hover_scale if hovering else 1.0
	if hovering:
		_hover_offset = _compute_hover_offset(target_scale_value)
		if _hover_offset != Vector2.ZERO:
			position += _hover_offset
	var target_scale := Vector2.ONE * target_scale_value
	_hover_tween.tween_property(self, "scale", target_scale, hover_tween_time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT if hovering else Tween.EASE_IN)
	z_index = 20 if hovering else 0

func _update_pivot() -> void:
	pivot_offset = Vector2(size.x * 0.5, size.y)

func _find_scroll_container() -> ScrollContainer:
	var node := get_parent()
	while node:
		if node is ScrollContainer:
			return node
		node = node.get_parent()
	return null

func _compute_hover_offset(scale_val: float) -> Vector2:
	var vp := get_viewport()
	if vp == null:
		return Vector2.ZERO
	if size.x <= 0.0 or size.y <= 0.0:
		return Vector2.ZERO
	var margin := hover_screen_margin
	var pivot_global := global_position + pivot_offset
	var scaled_top_left := pivot_global - pivot_offset * scale_val
	var scaled_bottom_right := scaled_top_left + size * scale_val
	var vp_size := vp.get_visible_rect().size
	var delta := Vector2.ZERO
	if scaled_top_left.x < margin:
		delta.x = margin - scaled_top_left.x
	elif scaled_bottom_right.x > vp_size.x - margin:
		delta.x = (vp_size.x - margin) - scaled_bottom_right.x
	if scaled_top_left.y < margin:
		delta.y = margin - scaled_top_left.y
	elif scaled_bottom_right.y > vp_size.y - margin:
		delta.y = (vp_size.y - margin) - scaled_bottom_right.y
	return delta
