def is_pressed(isbutton: bool, inp: number):
    if isbutton:
        return input.button_is_pressed(inp)
    else:
        return input.pin_is_pressed(inp)
gameOver = False
serial.redirect_to_usb()
shape = 0
timer = 0
shape_index = 0
shapes = [IconNames.DIAMOND,
    IconNames.HEART,
    IconNames.SQUARE,
    IconNames.TRIANGLE]
inputs = [Button.A, Button.B, TouchPin.P0, TouchPin.P2]
arebuttons = [True, True, False, False]

def on_forever():
    global shape_index, gameOver
    while True:
        if serial.read_until(serial.delimiters(Delimiters.NEW_LINE)) == "ready":
            break
    shape_index = randint(0, 3)
    gameOver = False
    basic.show_icon(shapes[shape_index])
    serial.write_line("start")
    while True:
        if is_pressed(arebuttons[shape_index], inputs[shape_index]):
            serial.write_line("stop")
            basic.show_string("GG!")
            break
    basic.pause(5000)
    basic.clear_screen()
basic.forever(on_forever)

