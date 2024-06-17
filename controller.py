# Author: Jonathan Santos
# File: controller.py
"""
This is a script that runs with the Create 1/2 Roomba which allows
it to move as dictated by a PS5 Dualsense controller. Items can
be obtained through the activation of the wheeldrop(s) which
grant bonuses to the player's movement (e.g., increased speed).
In other words, it mimics the basic capabilities of Mario Kart.

Script can be run on any machine or microcontroller (e.g., Pi)
hosting either Windows or Linux, though note that the
machine/microcontroller must be connected to the Roomba through
a serial cable. The 'pySerial' and 'pygame' modules need to be
installed in order to run this script. Only one controller may
be connected at any one time, connecting more controllers after
the 1st will not register any inputs from them.

Wheeldrops are used so that speed bumps in the track design can
act as an analog to Mario Kart's item boxes, and as such any one
player may only have one item at a time unless they use their
current one.

Should the front bumper(s) engage (i.e., a collision occurs),
the user will experience a momentary loss of control wherein
the Roomba will shuffle backwards for some amount of time.
We refer to this event as "wobble," of which can be enabled
or disabled by the user/player at the start of execution.

iRobot Create Open Interface for Opcode and Command References:
https://www.usna.edu/Users/weaprcon/esposito/_files/roomba.matlab/CreateOpenInterface.pdf

Limitations:
    - Script only recognizes one type of controller (Dualsense).
    - Script allows multiple controllers to control the same
      Rooma where only one player at a time should be.
    - Calculations assume a Dualsense controller is used.
    - Item effects are hardcoded into main(), ideally it should
      be modularized so that we can easier change and add
      implementation details at will (plus easier to read).
    - Many actions like item generation and usage are silent;
      some kind of feedback like playing a tone would better
      communicate the Roomba's state to the player.

Relevant Playstation 5 Controller Bindings and Axes:

Left Stick: Horizontal Axis
Usage: turning left or right
Axis/Button: axis 0
Range: left to right (-1.0 to +1.0)
Centered/Released Value: 0.0

Right Trigger: (RT)
Usage: modulates forward velocity.
Axis/Button: axis 5
Range: released to pressed (-1.0 to +1.0)
Centered/Released Value: -1.0

Left Trigger: (LT)
Usage: modulates backward velocity.
Axis/Button: axis 2 (axis 4 on Dualshock)
Range: released to pressed (-1.0 to +1.0)
Centered/Released Value: -1.0

X-Button: (Cross Button)
Usage: items
Axis/Button: button 0
Range: bool
Centered/Released Value: 0
"""

import controller_constants as cc
import controller_functions as cf
import pygame
import random
import serial
import sys
import time

pygame.init()

#-- Initialize Serial Port + Configure Wobble --#

given_baudrate = 0

while True:
    input_model = int(input("Enter the Roomba model to be used, (1) for Create 1, or (2) for Create 2: "))
    if input_model == 1:
        given_baudrate = cc.C1_BAUD
        break
    elif input_model == 2:
        given_baudrate = cc.C2_BAUD
        break
        
given_port = input("Enter the port to be used (e.g., COM8 (Windows), /dev/ttyUSB0 (Linux)): ")

roomba = serial.Serial(baudrate=given_baudrate, port=given_port)

while True:
    choice = input("Do you want to enable wobble? (y) or (n): ")
    choice = choice.lower()
    if choice == "y":
        using_wobble = True
        print("Wobble Enabled\n")
        break
    elif choice == "n":
        using_wobble = False
        print("Wobble Disabled\n")
        break

# Start Roomba in 'Full' mode to prevent wheeldrops from
# reverting its mode back to 'Passive'.
roomba.write(cc.FULL_MODE)
time.sleep(1)   # Requires 1s wait after sending.

#-- Initialize Item Related Variables --#

# Necessary to remember item status after every iteration.
has_mushroom = False
has_star = False
used_mushroom = False
used_star = False
elapsed_time = 0.0

#-- Process Controller Events and Inputs --#

controllers = {}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("\nExiting...\n")
            roomba.write(cc.STOP)
            pygame.quit()
            sys.exit()

        # Handle hotplugging.
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            controllers[joy.get_instance_id()] = joy
            print("Player", joy.get_instance_id() + 1, "connected! B)")

        if event.type == pygame.JOYDEVICEREMOVED:
            roomba.write(cc.STOP)
            del controllers[event.instance_id]
            printf("Player {event.instance_id + 1} disconnected :(")

    for controller in controllers.values():

        #-- Detect Collisions and Apply Wobble --#

        # Star grants invulnerability in the games,
        # thus, here as well.
        if using_wobble:
            cf.detect_front_collision(roomba, used_star,
                                      cc.WOBBLE_DURATION)

        #-- Poll Sticks --#

        lstick_horiz_pos = controller.get_axis(0)

        # Account for stick drift.
        if abs(lstick_horiz_pos) < cc.THRESHOLD:
            lstick_horiz_pos = 0.0  # assume centered

        #-- Poll Triggers --#

        right_trigger_value = controller.get_axis(5)
        left_trigger_value = controller.get_axis(2)

        driving_forward = False
        driving_backward = False

        # Forward movement overrides backward movement.
        if right_trigger_value + 1.0 > cc.THRESHOLD:
            driving_forward = True
        elif left_trigger_value + 1.0 > cc.THRESHOLD:
            driving_backward = True

        #-- Poll Buttons --#

        x_button_depressed = controller.get_button(0)

        if x_button_depressed:
            used_item = True
        else:
            used_item = False

        #-- Item Generation and Usage --#

        roomba.write(cc.POLL_BUMPERS_AND_DROPS)
        wheel_dropped = roomba.read(1)[0] & 0b1100

        has_item = has_mushroom or has_star

        if wheel_dropped:
            generated_item = random.choice(cc.ITEMS)
            if generated_item == 'mushroom' and not has_item:
                has_mushroom = True
                print("You got a Mushroom!")
            elif generated_item == 'star' and not has_item:
                has_star = True
                print("You got a Star!")

        if has_mushroom and used_item:
            print("Mushroom Boost!")
            has_mushroom = False
            used_mushroom = True
            time_item_used = time.time()
        elif has_star and used_item:
            print("INVINCIBILITY activated for 6s!")
            has_star = False
            used_star = True
            time_item_used = time.time()

        #-- Item Effects and Duration --#

        # Start at rest unless mushroom used or trigger pulled.
        velocity = 0.0

        # If player used an item, determine if effects
        # should end now.
        if used_mushroom or used_star:
            # Mushroom: constantly drive forward at max speed.
            if used_mushroom and elapsed_time < cc.MUSHROOM_DURATION:
                velocity = cc.MAX_VELOCITY_W_SHROOM
                elapsed_time = time.time() - time_item_used
            # Elapsed time exceeded max time?
            elif used_mushroom and elapsed_time > cc.MUSHROOM_DURATION:
                used_mushroom = False
            # Star: increase max velocity ranges.
            elif used_star and elapsed_time < cc.STAR_DURATION:
                if driving_forward:
                    velocity = cf.apply_forward_velocity(cc.MAX_VELOCITY_W_STAR,
                                                         right_trigger_value)
                elif driving_backward:
                    velocity = cf.apply_backward_velocity(cc.MAX_VELOCITY_W_STAR,
                                                          left_trigger_value)
                elapsed_time = time.time() - time_item_used
            # Elapsed time exceeded max time?
            elif used_star and elapsed_time > cc.STAR_DURATION:
                used_star = False
                print("Invincibility OFF")
        # Didn't use item or max time exceeded? Assume
        # normal velocity ranges.
        else:
            if driving_forward:
                velocity = cf.apply_forward_velocity(cc.MAX_VELOCITY_NO_ITEMS,
                                                     right_trigger_value)
            elif driving_backward:
                velocity = cf.apply_backward_velocity(cc.MAX_VELOCITY_NO_ITEMS,
                                                      left_trigger_value)
            elapsed_time = 0.0

        #-- Final Velocity Byte Calculation --#

        velocity_bytes = [(velocity // 256) % 256] + [velocity % 256]

        #-- Final Turning Radius Byte Calculation --#

        radius_bytes = cf.apply_turning_radius(lstick_horiz_pos, cc.THRESHOLD,
                                               cc.MIN_RADIUS, cc.MAX_RADIUS)

        #-- Drive Roomba --#

        roomba.write(bytearray(cc.DRIVE + velocity_bytes + radius_bytes))
