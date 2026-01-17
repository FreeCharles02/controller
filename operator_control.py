import platform
import pygame
import socket
import time
import struct
import subprocess
import re
from MotorControlWatcher import MotorControlWatcher

# Helper to find an IP address in the local ARP table by MAC address.
def get_ip_from_mac(mac_address):
    os = platform.system()
    if os == "Windows":
        mac_address = mac_address.replace(":", "-")  # Windows arp output uses dashes
    try:
        # run `arp -a` and search lines for the MAC address
        arp_output = subprocess.check_output(['arp', '-a'], text=True)
        arp_lines = arp_output.splitlines()
        for line in arp_lines:
            if mac_address in line:
                # extract the first IPv4-looking substring
                ip_address = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if ip_address:
                    return ip_address.group(0)
                return None
    except subprocess.CalledProcessError:
         return None


# Standardized input type names used in mapping table
Button = "Button"
Axis = "Axis"
Hat = "Hat"

# Logical names for buttons/axes used by the rest of the program
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

# Controller mappings: maps controller name to how its inputs map to our logical names.
# Each mapping entry is a tuple: (type, index, optional_sign_or_hat_index)
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


# Read a logical input (input_source) from a pygame joystick using the mapping table.
def pollJoy(joystick, input_source):
    name = joystick.get_name()
    controllerMap = ControllerMappings.get(name, False)  # get mapping for this controller
    source = controllerMap.get(input_source, False)  # get how this logical input is implemented

    if source[0] == Button:
        # read a digital button
        return joystick.get_button(source[1])

    if source[0] == Axis:
        # read an analog axis (sign handling already baked into mapping tuples)
        if (source[2] < 0):
            return joystick.get_axis(source[1])
        return joystick.get_axis(source[1])

    if source[0] == Hat:
        # read a hat (D-pad) value, return specified axis of the hat tuple
        return joystick.get_hat(source[1])[source[2]]

    # If mapping is invalid, print and exit
    print(f"Unable to find source \"{source}\".")
    exit(1)


# Convert joystick axes into four mecanum wheel values.
# deadzone: small joystick noise threshold
# maxspeed: scale factor for motor outputs
def calculateMecanumWheel(joystick, deadzone, maxspeed):
    speed = pollJoy(joystick, LeftJoyUpDown)       # forward/back
    strafe = pollJoy(joystick, LeftJoyLeftRight)   # left/right
    turn = pollJoy(joystick, RightJoyLeftRight)    # rotation

    deadzone = abs(deadzone)  # ensure positive

    # apply deadzone to ignore small joystick noise
    if turn > -deadzone and turn < deadzone:
        turn = 0
    if speed > -deadzone and speed < deadzone:
        speed = 0
    if strafe > -deadzone and speed < deadzone:
        strafe = 0

    # debug prints for joystick raw values
    print("Deadzone: ", f"{deadzone}")
    print("Turn: ", f"{turn}")
    print("Strafe: ", f"{strafe}")
    print("Speed: ", f"{speed}")

    # Map joysticks onto mecanum wheel contributions
    lFwd = speed + strafe + turn
    rFwd = speed - strafe - turn
    lBwd = speed - strafe + turn
    rBwd = speed + strafe - turn

    # Normalize so none exceed magnitude 1
    peak = max(abs(lFwd), abs(lBwd), abs(rFwd), abs(rBwd), 1)
    lFwd /= peak
    lBwd /= peak
    rFwd /= peak
    rBwd /= peak

    # Scale to desired max speed
    lFwd *= maxspeed
    lBwd *= maxspeed
    rFwd *= maxspeed
    rBwd *= maxspeed

    # return wheel powers: left front, left back, right front, right back
    return (lFwd, lBwd, rFwd, rBwd)


# Simple remapping function converting two channels into bytes for sending.
def remap(ch1, ch2):
    if (ch2 > 0):
        return (int(ch1*63+64), int(ch2*63+192))
    else:
        return (int(ch1*63+64), int(ch2*63+192))
    
    
connect = True  # whether to connect to the remote robot server
MotorControlChange = False  # unused flag in this file


def main():
    pygame.init()  # initialize pygame modules (needed for joystick events)

    # Create a MotorControlWatcher to observe motor value changes
    MotorControlWatcher1 = MotorControlWatcher()
 #   MotorControlWatcher1.add_observer(MotorControlChange)  # commented out in original

    clock = pygame.time.Clock()
    joysticks = {}  # active joysticks tracked by instance id

    # Choose IP address to connect to (placeholder or use ARP lookup)
    ip_address =  '127.0.0.1' # get_ip_from_mac("d8:3a:dd:d0:ac:cb")

    # Initialize TCP connection to robot (if enabled)
    if connect:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip_address, 9999))

    # Main loop: process events, read joystick inputs, compute motors, and send updates.
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Handle joystick hotplug events
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"{joy.get_name()}, connencted") 
            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"{joy.get_name()}, disconnected")

        # default values for this update
        lf, lb, rf, rb = 0.0, 0.0, 0.0, 0.0
        lb_button, rb_button = 0, 0
        rt_trigger, lt_trigger = 0, 0
        dpad_value_1 = 0
        dpad_value_2 = 0
        a, b, x, y = 0, 0, 0, 0

        # Read inputs from all connected joysticks (currently uses last joystick read)
        for joystick in joysticks.values():
            lf, lb, rf, rb = calculateMecanumWheel(joystick, 0.08, 0.8)

            # notify watcher about motor values (observer pattern)
            MotorControlWatcher1.notify(lf,lb,rf,rb)

            # read button/hat/trigger values
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

        # Convert wheel float values into bytes for visualizer / sending
        lb, lf = remap(lb * -1, lf *-1)
        rb, rf = remap(rf * -1, rb * -1)

        # Print a simple ASCII robot frame and values for debugging
        print("\\===\\-----/===/\n" +
              f"\\{lf}\\     /{rf}/\n" +
              "\\===\\     /===/\n" +
              ("   |       |\n" * 3) +
              "/===/     \\===\\\n" +
              f"/{lb}/     \\{rb}\\\n" +
              "/===/-----\\===\\\n")
        
        # Print numeric values; formatting may assume integers
        print(f"{lf:3d}\t{rf:3d}\n{lb:3d}\t{rb:3d}\t{dpad_value_1: 3d}\t{dpad_value_2: 3d}\t{a: 3d}\t{y: 3d}\t{rt_trigger: 3d}\t{lt_trigger: 3d}\t{lb_button: 3d}\t {rb_button: 3d}\t {a: 3d}\t{y: 3d} \n\n")
        print(ip_address)
        
        # show watcher state for debugging
        print("Motor Control boolean: ", MotorControlWatcher1.observer)
    
        # Send 4 bytes (rb, rf, lb, lf) to the connected robot server
        if connect:
            try:
                client.send(struct.pack('!' + 'B'*4,
                                        rb, rf, lb, lf,))
            except (ConnectionResetError, BrokenPipeError):
                # attempt to reconnect if connection breaks
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

        clock.tick(30)  # limit loop to ~30 FPS


if __name__ == "__main__":
    main()
    pygame.quit()
