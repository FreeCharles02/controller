import platform
import pygame
import socket
import time
import struct
import subprocess
import re
import MotorControl


def get_ip_from_mac(mac_address):
    os = platform.system()
    if os == "Windows":
        mac_address = mac_address.replace(":", "-")
    try:
        arp_output = subprocess.check_output(['arp', '-a'], text=True)
        arp_lines = arp_output.splitlines()
        for line in arp_lines:
            if mac_address in line:
                ip_address = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if ip_address:
                    return ip_address.group(0)
                return None
    except subprocess.CalledProcessError:
         return None

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
    "Pro Controller": {
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
        AButton: (Button, 0), BButton: (Button, 1),
        XButton: (Button, 3), YButton: (Button, 2),
        LeftJoyLeftRight: (Axis, 0, 1),  LeftJoyUpDown: (Axis, 1, -1),
        RightJoyLeftRight: (Axis, 3, 1), RightJoyUpDown: (Axis, 4, -1),
        LeftBumper: (Button, 4),  RightBumper: (Button, 5),
        LeftTrigger: (Axis, 4, 1), RightTrigger: (Axis, 5, 1),
    },
    "DualSense Wireless Controller": {
        AButton: (Button, 0), BButton: (Button, 1),
        XButton: (Button, 3), YButton: (Button, 2),
        LeftBumper: (Button, 4),  RightBumper: (Button, 5),
        LeftTrigger: (Axis, 2, 1), RightTrigger: (Axis, 5, 1),
        LeftJoyIn: (Button, 13),  RightJoyIn: (Button, 14),
        HomeButton: (Button, 12),

        LeftJoyLeftRight: (Axis, 0, 1),  LeftJoyUpDown: (Axis, 1, -1),
        RightJoyLeftRight: (Axis, 3, 1), RightJoyUpDown: (Axis, 4, -1),

        DpadLeftRight: (Hat, 0, 0), DpadUpDown: (Hat, 0, 1),
    }
}


def pollJoy(joystick, input_source):
    name = joystick.get_name()
    controllerMap = ControllerMappings.get(name, False)
    source = controllerMap.get(input_source, False)

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


def calculateMecanumWheel(joystick, deadzone, maxspeed):
    speed = pollJoy(joystick, LeftJoyUpDown)
    strafe = pollJoy(joystick, LeftJoyLeftRight)
    turn = pollJoy(joystick, RightJoyLeftRight)

    deadzone = abs(deadzone) 

    if turn > -deadzone and turn < deadzone:
        turn = 0

    # Map joysticks onto mecanum wheels
    lFwd = speed - strafe + turn
    lBwd = speed + strafe + turn
    rFwd = speed + strafe - turn
    rBwd = speed + strafe - turn

    # Calculate if any values exceed 1
    peak = max(abs(lFwd), abs(lBwd), abs(rFwd), abs(rBwd), 1)

    # divide by that value so no value exceeds 1
    lFwd /= peak
    lBwd /= peak
    rFwd /= peak
    rBwd /= peak

    lFwd *= maxspeed
    lBwd *= maxspeed
    rFwd *= maxspeed
    rBwd *= maxspeed

    return (lFwd, lBwd, rFwd, rBwd)


def remap(ch1, ch2):
    if (ch2 > 0):
        return (int(ch1*63+64), int(ch2*63+192))
    else:
        return (int(ch1*63+64), int(ch2*64+192))
    

connect = True


def main():
    clock = pygame.time.Clock()
    joysticks = {}

    ip_address = get_ip_from_mac("d8:3a:dd:d0:ac:cb")

    # Initalizes socket to
    if connect:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip_address, 9999))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"{joy.get_name()}, connencted") 
            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"{joy.get_name()}, disconnected")

        lf, lb, rf, rb = 0, 0, 0, 0
        lb_button, rb_button = 0, 0
        rt_trigger, lt_trigger = 0, 0
        dpad_value_1 = 0
        dpad_value_2 = 0
        a, b, x, y = 0, 0, 0, 0

        for joystick in joysticks.values():
            lf, lb, rf, rb = calculateMecanumWheel(joystick, 0.08, 0.8)

            lb_button = pollJoy(joystick, LeftBumper) 
            rb_button = pollJoy(joystick, RightBumper)

            dpad_value_1 = pollJoy(joystick, DpadUpDown) + 1
            dpad_value_2 = pollJoy(joystick, DpadLeftRight) + 1

            b = pollJoy(joystick, BButton)
            x = pollJoy(joystick, XButton)
            y = pollJoy(joystick, YButton)
            a = pollJoy(joystick, AButton)

            rt_trigger = pollJoy(joystick, RightTrigger) + 1 
            lt_trigger = pollJoy(joystick, LeftTrigger) + 1

            rt_trigger = int(rt_trigger)
            lt_trigger = int(lt_trigger)

        # Robot frame&motor power visualizer
        print("\\===\\-----/===/\n" +
              f"\\{lf*100:3.0f}\\     /{rf*100:3.0f}/\n" +
              "\\===\\     /===/\n" +
              ("   |       |\n" * 3) +
              "/===/     \\===\\\n" +
              f"/{lb*100:3.0f}/     \\{rb*100:3.0f}\\\n" +
              "/===/-----\\===\\\n")

        lb, lf = remap(lb*-1, lf*-1)
        rb, rf = remap(rf, rb)
        
        print(f"{lf:3d}\t{rf:3d}\n{lb:3d}\t{rb:3d}\t{dpad_value_1: 3d}\t{dpad_value_2: 3d}\t{a: 3d}\t{y: 3d}\t{rt_trigger: 3d}\t{lt_trigger: 3d}\t{lb_button: 3d}\t {rb_button: 3d}\t {a: 3d}\t{y: 3d} \n\n")
        print(ip_address)
        
        if connect:
            try:
                client.send(struct.pack('!' + 'B'*14,
                                        rb, rf, lb, lf,
                                        rb_button, lb_button,
                                        dpad_value_1, dpad_value_2, rt_trigger,lt_trigger, x, b, a, y))
            except (ConnectionResetError, BrokenPipeError):
                client.close()
                print("connection refused")
                while(True):
                    try:
                        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client.connect((ip_address, 9999))
                        break
                    except (ConnectionRefusedError, BrokenPipeError):
                        time.sleep(0.1)
                print("reconnected")

        clock.tick(30)


if __name__ == "__main__":
    main()
    pygame.quit()
