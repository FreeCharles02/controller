# Standardized Names
Button = "Button"
Axis = "Axis"
Hat = "Hat"

LeftBumper = "LB";  RightBumper = "RB"
LeftTrigger = "LT"; RightTrigger = "RT"

AButton = "A"; BButton = "B"
XButton = "X"; YButton = "Y"
HomeButton = "HOME"

LeftJoyLeftRight = "LJ_LR"; LeftJoyUpDown = "LJ_UD"
LeftJoyIn = "LJ_IN"
RightJoyLeftRight = "RJ_LR";RightJoyUpDown = "RJ_UD"
RightJoyIn = "RJ_IN"

DpadLeftRight = "D_LR"; DpadUpDown = "D_UD"

ControllerMappings = {
    "Nintendo Switch Pro Controller" : {
        AButton : (Button, 1), BButton : (Button, 0),
        XButton : (Button, 2), YButton : (Button, 3),
        LeftBumper : (Button, 5),  RightBumper : (Button, 6),
        LeftTrigger : (Button, 7), RightTrigger : (Button, 8),
        LeftJoyIn : (Button, 12),  RightJoyIn : (Button, 13),
        HomeButton : (Button, 11),

        LeftJoyLeftRight : (Axis, 0, 1),  LeftJoyUpDown : (Axis, 1, -1),
        RightJoyLeftRight : (Axis, 2, 1), RightJoyUpDown : (Axis, 3, -1),

        DpadLeftRight : (Hat, 0, 0), DpadUpDown : (Hat, 0, 1),
    }
    #"Wireless Gamepad" : {}, # AKA: Nintindo Joy-Con
    #"Xbox 360 Controller" : {},
    #"PS4 Controller": {},
    #"Sony Interactive Entertainment Wireless Controller": {}, #AKA PS5 Controller
}

import pygame
pygame.init()

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

    print(f"Unable to find \"{source}\"")
    exit(1)

def calculateMecanumWheel(joystick, deadzone):
    speed = pollJoy(joystick, LeftJoyUpDown)
    strafe  = pollJoy(joystick, LeftJoyLeftRight)
    turn   = pollJoy(joystick, RightJoyLeftRight)

    deadzone = abs(deadzone)
    if speed>-deadzone and speed<deadzone:
        speed = 0

    if strafe>-deadzone and strafe<deadzone:
        strafe = 0

    if turn>-deadzone and turn<deadzone:
        turn = 0

    # Map joysticks onto mecanum wheels
    lFwd = speed + strafe + turn
    lBwd = speed - strafe + turn
    rFwd = speed - strafe - turn
    rBwd = speed + strafe - turn

    # Calculate if any values exceed 1
    peak = max(abs(lFwd),abs(lBwd),abs(rFwd),abs(rBwd),1)

    # divide by that value so no value exceeds 1
    lFwd /= peak
    lBwd /= peak
    rFwd /= peak
    rBwd /= peak

    return ((lFwd, lBwd),(rFwd, rBwd))

class TextPrint:
    def __init__(self):
        self.reset()
        desiredFont = pygame.font.SysFont("Monospace", 15);
        if desiredFont:
            self.font = desiredFont
        else:
            self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

def main():
    screen = pygame.display.set_mode((500, 1000))
    pygame.display.set_caption("Joystick example")

    clock = pygame.time.Clock()
    text_print = TextPrint()

    joysticks = {}

    while True:
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
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

        screen.fill((255, 255, 255))
        text_print.reset()

        text_print.tprint(screen, f"Number of joysticks: {len(joysticks)}")
        text_print.indent()

        # For each joystick:
        for joystick in joysticks.values():

            # Get the name from the OS for the controller/joystick.
            jid = joystick.get_instance_id()
            name = joystick.get_name()
            text_print.tprint(screen, f"Joystick #{jid}, name: {name}")
            text_print.indent()

            text_print.tprint(screen, f"L_LR {pollJoy(joystick, LeftJoyLeftRight):>6.3f}")
            text_print.tprint(screen, f"L_UD {pollJoy(joystick, LeftJoyUpDown):>6.3f}")
            text_print.tprint(screen, f"R_LR {pollJoy(joystick, RightJoyLeftRight):6.3f}")
            text_print.tprint(screen, f"R_UD {pollJoy(joystick, RightJoyUpDown):6.3f}")

            text_print.tprint(screen, f"LB {pollJoy(joystick, LeftBumper):>6.3f}")
            text_print.tprint(screen, f"RB {pollJoy(joystick, RightBumper):>6.3f}")
            text_print.tprint(screen, f"LT {pollJoy(joystick, LeftTrigger):>6.3f}")
            text_print.tprint(screen, f"RT {pollJoy(joystick, RightTrigger):>6.3f}")

            text_print.tprint(screen, f"AB {pollJoy(joystick, AButton):>6.3f}")
            text_print.tprint(screen, f"BB {pollJoy(joystick, BButton):>6.3f}")
            text_print.tprint(screen, f"XB {pollJoy(joystick, XButton):>6.3f}")
            text_print.tprint(screen, f"YB {pollJoy(joystick, YButton):>6.3f}")
            text_print.tprint(screen, f"HB {pollJoy(joystick, HomeButton):>6.3f}")

            text_print.tprint(screen, f"dLR {pollJoy(joystick, DpadLeftRight):>6.3f}")
            text_print.tprint(screen, f"dUD {pollJoy(joystick, DpadUpDown):>6.3f}")

            text_print.tprint(screen, "")
            motors = calculateMecanumWheel(joystick, 0.08);
            text_print.tprint(screen, f"{motors[0][0]:>6.3f} | {motors[1][0]:>6.3f}")
            text_print.tprint(screen, f"{motors[0][1]:>6.3f} | {motors[1][1]:>6.3f}")

            text_print.unindent()

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
    pygame.quit()
