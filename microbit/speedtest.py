def is_pressed(isbutton: bool, inp: number):
    return input.pin_is_pressed(inp)

serial.redirect_to_usb()
shape_index = 0
shapes = [IconNames.DIAMOND,
    IconNames.SQUARE,
    IconNames.TRIANGLE]
inputs = [TouchPin.P1, TouchPin.P0, TouchPin.P2]
two_players = False


def on_finish(winner):
    serial.write_line("stop")
    serial.write_line("winner:"+winner-1)

def on_p1():
    basic.show_leds("""
                    # # . . .
                    # # . . .
                    # # . . .
                    # # . . .
                    # # . . .
            """)
    on_finish(2)

def on_p2():
    basic.show_leds("""
                    . . . # #
                    . . . # #
                    . . . # # 
                    . . . # #
                    . . . # #
            """)
    on_finish(1)


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
        basic.pause(5000)
        basic.clear_screen()
    else:
        for i in range(5):
            # multi-player mode
            basic.show_number(3)
            basic.show_number(2)
            basic.show_number(1)
            basic.clear_screen()
            running = True
            while running:
                pass



                


basic.forever(on_forever)

