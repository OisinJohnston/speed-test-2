def is_pressed(isbutton: bool, inp: number):
    return input.pin_is_pressed(inp)
shape_index = 0
serial.redirect_to_usb()
shapes = [IconNames.DIAMOND, IconNames.SQUARE, IconNames.TRIANGLE]
inputs = [TouchPin.P1, TouchPin.P0, TouchPin.P2]

def on_forever():
    global shape_index
    while True:
        if serial.read_until(serial.delimiters(Delimiters.NEW_LINE)) == "ready":
            mode = int(serial.read_until(serial.delimiters(Delimiters.NEW_LINE)))
            break
    if mode == 0:
        # single-player mode
        shape_index = randint(0, 2)
        basic.show_icon(shapes[shape_index])
        serial.write_line("start")
        while True:
            if input.pin_is_pressed(inputs[shape_index]):
                serial.write_line("stop")
                basic.show_string("GG!")
                break
    else:
        winnerscore = 0
        serial.write_line("start")
        # player one and two points
        p1 = 0
        p2 = 0
        for index in range(5):
            # multi-player mode
            basic.show_number(3)
            basic.show_number(2)
            basic.show_number(1)
            basic.clear_screen()
            while 1:
                if input.pin_is_pressed(TouchPin.P1):
                    basic.show_leds("""
                        # # . . .
                                                # # . . .
                                                # # . . .
                                                # # . . .
                                                # # . . .
                    """)
                    p1 += 1
                    break
                if input.pin_is_pressed(TouchPin.P2):
                    basic.show_leds("""
                        . . . # #
                                                . . . # #
                                                . . . # #
                                                . . . # #
                                                . . . # #
                    """)
                    p2 += 1
                    break
        winner = 0 if p1 > p2 else 1
        winnerscore = p1 if p1 > p2 else p2
        serial.write_line("stop")
        serial.write_line("" + str(winner))
        serial.write_line("" + str(winnerscore))
    basic.pause(5000)
    basic.clear_screen()
basic.forever(on_forever)

