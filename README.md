# Summary
Simulate Mario Kart controls and items on an iRobot Create 1/2 Roomba.

This is a script that runs with the Create 1/2 Roomba which allows
it to move as dictated by a PS5 Dualsense controller. Items can
be obtained through the activation of the wheeldrop(s) which
grant bonuses to the player's movement (e.g., increased speed).
In other words, it mimics the basic capabilities of Mario Kart.

Script can be run on any machine or microcontroller (e.g., Pi)
hosting either Windows or Linux, though note that the
machine/microcontroller must be connected to the Roomba through
a serial cable. The 'pySerial' and 'pygame' modules need to be
installed in order to run this script.

Wheeldrops are used so that speed bumps in the track design can
act as an analog to Mario Kart's item boxes, and as such any one
player may only have one item at a time unless they use their
current one.

Should the front bumper(s) engage (i.e., a collision occurs),
the user will experience a momentary loss of control wherein
the Roomba will shuffle backwards for some amount of time.
We refer to this event as "wobble," of which can be enabled
or disabled by the user/player at the start of execution.

# iRobot Create Open Interface for Opcode and Command References:
https://www.usna.edu/Users/weaprcon/esposito/_files/roomba.matlab/CreateOpenInterface.pdf

# Relevant Playstation 5 Controller Bindings and Usage

Left Stick: Horizontal Axis
  - turning left or right

Right Trigger: (RT)
  - modulates forward velocity.

Left Trigger: (LT)
  - modulates backward velocity.

X-Button: (Cross Button)
  - use item

# Limitations
    - Script only recognizes one type of controller (Dualsense).
    - Script allows multiple controllers to control the same
      Roomba where only one player at a time should be allowed.
    - Calculations assume a Dualsense controller is used.
    - Item effects are hardcoded into main(), ideally it should
      be modularized so that we can easier change and add
      implementation details at will (plus easier to read).
    - Many actions like item generation and usage are silent;
      some kind of feedback like playing a tone would better
      communicate the Roomba's state to the player.
