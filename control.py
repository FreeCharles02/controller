from inputs import get_gamepad

while True: 
    events = get_gamepad()
    for event in events: 
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_X':
                    print(f'Left joystick x: {event.state}')
                elif event.code == 'ABS_Y':
                    print(f'Left joystick y: {event.state}')
                elif event.code == 'ABS_RX': 
                    print(f'Right joystick x: {event.state}')
                elif event.code == 'ABS_RY': 
                    print(f'Right joystick y: {event.state}')
                else:
                    print(event.code)