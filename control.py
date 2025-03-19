import serial
import pygame
import socket
import struct

pygame.init()


# Standardized Names
Button = "Button"
Axis = "Axis"
Hat = "Hat"

LeftBumper = "LB"
RightBumper = "RB"
LeftTrigger = "LT"
RightTrigger = "RT"

AButton = "A"
BButton = "B"
XButton = "X"
YButton = "Y"
HomeButton = "HOME"

LeftJoyLeftRight = "LJ_LR"
LeftJoyUpDown = "LJ_UD"
LeftJoyIn = "LJ_IN"
RightJoyLeftRight = "RJ_LR"
RightJoyUpDown = "RJ_UD"
RightJoyIn = "RJ_IN"

DpadLeftRight = "D_LR"
DpadUpDown = "D_UD"

ControllerMappings = {
    "Nintendo Switch Pro Controller": {
        AButton: (Button, 1), BButton: (Button, 0),
        XButton: (Button, 2), YButton: (Button, 3),
        LeftBumper: (Button, 5),  RightBumper: (Button, 6),
        LeftTrigger: (Button, 7), RightTrigger: (Button, 8),
        LeftJoyIn: (Button, 12),  RightJoyIn: (Button, 13),
        HomeButton: (Button, 11),

        LeftJoyLeftRight: (Axis, 0, 1),  LeftJoyUpDown: (Axis, 1, -1),
        RightJoyLeftRight: (Axis, 2, 1), RightJoyUpDown: (Axis, 3, -1),

        DpadLeftRight: (Hat, 0, 0), DpadUpDown: (Hat, 0, 1),
    },
    "Xbox One S Controller": {
        AButton: (Button, 0), BButton: (Button, 1),
        XButton: (Button, 3), YButton: (Button, 4),
        LeftBumper: (Button, 6),  RightBumper: (Button, 7),
        LeftTrigger: (Axis, 4, 1), RightTrigger: (Axis, 5, 1),
        LeftJoyIn: (Button, 13),  RightJoyIn: (Button, 14),
        HomeButton: (Button, 12),

        LeftJoyLeftRight: (Axis, 0, 1),  LeftJoyUpDown: (Axis, 1, -1),
        RightJoyLeftRight: (Axis, 2, 1), RightJoyUpDown: (Axis, 3, -1),

        DpadLeftRight: (Hat, 0, 0), DpadUpDown: (Hat, 0, 1),
    },
    "Xbox 360 Controller": {
        LeftJoyLeftRight: (Axis, 0, 1),  LeftJoyUpDown: (Axis, 1, -1),
        RightJoyLeftRight: (Axis, 3, 1), RightJoyUpDown: (Axis, 4, -1),
    },
    "DualSense Wireless Controller": {
       LeftJoyLeftRight: (Axis, 0, 1), LeftJoyUpDown: (Axis, 1, -1),
       RightJoyLeftRight: (Axis, 3, 1), RightJoyUpDown: (Axis, 4, -1),     
    }
}


def pollJoy(joystick, input_source):
    try:
        name = joystick.get_name()
        controllerMap = ControllerMappings.get(name, False)
        source = controllerMap.get(input_source, False)
    except:
        return 0

    if source[0] == Button:
        return joystick.get_button(source[1])

    if source[0] == Axis:
        if (source[2] < 0):
            return joystick.get_axis(source[1]) * -1
        return joystick.get_axis(source[1])

    if source[0] == Hat:
        return joystick.get_hat(source[1])[source[2]]

    print(f"Unable to find source \"{source}\".")
    exit(1)


def calculateMecanumWheel(joystick, deadzone):
    speed  = pollJoy(joystick, LeftJoyUpDown)
    strafe = pollJoy(joystick, LeftJoyLeftRight)
    turn   = pollJoy(joystick, RightJoyLeftRight)

    deadzone = abs(deadzone)
    if speed > -deadzone and speed < deadzone:
        speed = 0

    if strafe > -deadzone and strafe < deadzone:
        strafe = 0

    if turn > -deadzone and turn < deadzone:
        turn = 0

    # Map joysticks onto mecanum wheels
    lFwd = speed + strafe + turn
    lBwd = speed - strafe + turn
    rFwd = speed - strafe - turn
    rBwd = speed + strafe - turn

    # Calculate if any values exceed 1
    peak = max(abs(lFwd), abs(lBwd), abs(rFwd), abs(rBwd), 1)

    # divide by that value so no value exceeds 1
    lFwd /= peak
    lBwd /= peak
    rFwd /= peak
    rBwd /= peak

    return (lFwd, lBwd, rFwd, rBwd)


def main():
    clock = pygame.time.Clock()
    joysticks = {}
    ser = serial.Serial('/dev/ttyACM0', 9600)

   #Initalizes socket to 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('172.20.10.12', 9999))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"{joy.get_name()}, id#{joy.get_instance_id()} connencted")
            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"{joy.get_name()}, id#{event.instance_id} disconnected")

        lf, lb, rf, rb = 0, 0, 0, 0
        for joystick in joysticks.values():
            lf, lb, rf, rb = calculateMecanumWheel(joystick, 0.08)
            if lf < 0 and lb < 0:
                lf = int(abs(abs(lf*64) - 63))
                lb = int(abs(abs(lb*192) - 63))
                if lf == 0 or lb == 129: 
                       lf = 1
                       lb = 128
                
            else: 
                 lf = int(abs(lf*64) + 64)
                 lb = int(abs(lb*192) + 64)
            if lf > 127 or lb > 255:
                        lf = 127
                        lb = 255
            if rf < 0 and rb < 0:
                 rf = int(abs(abs(rf*64) - 64))
                 rb = int(abs(abs(rb*192) - 64))
                 if rf == 0 or rb == 129:
                     rf = 1
                     rb = 128
            else: 
                rf = int(abs(rf*64) + 64)
                rb = int(abs(rb*192) + 64)
            if rf > 127 or rb > 255:
                     rf = 127
                     rb = 255
            print(lf)
            print(lb)
            print(rf)
            print(rb)
            
        try: 
            client.send(struct.pack('!bbbb',lf,lb,rf,rb))
        except:
            client.close()
            print("connection refused")
            client.connect('172.20.10.4', 9999)
            

       

        clock.tick(30)


if __name__ == "__main__":
    main()
    pygame.quit()
