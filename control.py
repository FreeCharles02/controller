from inputs import get_gamepad

while True: 
    events = get_gamepad()
    for event in events: 
                if event.code == 'ABS_X':
                    print(f'Left joystick x: {event.state}')
                elif event.code == 'ABS_Y':
                    print(f'Left joystick y: {event.state}')
                elif event.code == 'ABS_RX': 
                    print(f'Right joystick x: {event.state}')
                elif event.code == 'ABS_RY': 
                    print(f'Right joystick y: {event.state}')
                elif event.code == 'ABS_HAT0Y' and event.state == 1: 
                    print("D-pad: Down")
                elif event.code == 'ABS_HAT0Y' and event.state == -1: 
                    print("D-pad: Up")
                elif event.code == 'ABS_HAT0X' and event.state == -1: 
                    print("D-pad: Left")
                elif event.code == 'ABS_HAT0X' and event.state ==  1: 
                    print("D-pad: Right")
                elif event.code == 'BTN_SOUTH' and event.state == 1:
                    print("A button pressed!")
                elif event.code == 'BTN_EAST' and event.state == 1:
                    print("B button pressed!")
                elif event.code == 'BTN_WEST'and event.state == 1:
                    print("X button pressed!")
                elif event.code == 'BTN_NORTH' and event.state == 1:
                    print("Y button pressed!")
                elif event.code == 'BTN_TR' and event.state == 1: 
                    print("Right trigger")
                elif event.code == 'BTN_TL' and event.state == 1:
                    print("Left trigger")
                elif event.code == 'ABS_RZ' and event.state == 1:
                    print("Right bumper")
                elif event.code == 'ABS_Z' and event.state == 1:
                    print("Left bumper")
               # else:
                #    print(event.code)