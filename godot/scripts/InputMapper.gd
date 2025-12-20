extends Node

class_name InputMapper

signal tap(card_id)
signal long_press(card_id)
signal drag_start(card_id)
signal drag_end(card_id)

@export var long_press_time := 0.4
var _press_timer := 0.0
var _pressed := false
var _pressed_card := ""

func _unhandled_input(event):
	if event is InputEventMouseButton and event.pressed:
		_pressed = true
		_press_timer = 0.0
		_pressed_card = "" # set from caller
	elif event is InputEventMouseButton and not event.pressed and _pressed:
		if _press_timer < long_press_time:
			emit_signal("tap", _pressed_card)
		else:
			emit_signal("long_press", _pressed_card)
		_pressed = false
		_pressed_card = ""

func _process(delta):
	if _pressed:
		_press_timer += delta
