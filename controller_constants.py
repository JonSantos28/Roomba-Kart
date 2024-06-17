# Author: Jonathan Santos
# File: controller_constants.py
"""
Constants specific to 'controller.py' and 'controller_functions'
that affect internal Roomba values/commands, max speed, item
speed boosts, item duration, wobble duration, min/max turning
radii, controller threshold value, and item inclusion.
"""

# Create 1 Roomba's default baudrate.
C1_BAUD = 57600

# Create 2 Roomba's default baudrate.
C2_BAUD = 115200

# 'Full' mode command.
FULL_MODE = bytearray([128, 132])

# Drive command opcode.
DRIVE = [137]

# Stopping command.
STOP = bytearray([137, 0, 0, 0, 0])

# Command to poll for front bumper and wheeldrop sensor packet.
POLL_BUMPERS_AND_DROPS = bytearray([142, 7])

# Maximum velocity value forwards and backwards without using
# items (mm/s).
MAX_VELOCITY_NO_ITEMS = 300   # [1, 44]

# Maximum velocity value forwards after using mushroom (mm/s).
MAX_VELOCITY_W_SHROOM = 500   # [1, 244]

# Maximum velocity value forwards and backwards after using
# star (mm/s).
MAX_VELOCITY_W_STAR = 425    # [1, 169]

# Duration of mushroom's effects (seconds).
MUSHROOM_DURATION = 1.5

# Duration of star's effects (seconds).
STAR_DURATION = 6.0

# How long the user loses control after a front-side
# collision (seconds).
WOBBLE_DURATION = 1.2

# Minimum turning radius value (mm).
MIN_RADIUS = -1700  # right turn

# Maximum turning radius value (mm).
MAX_RADIUS = 1700   # left turn

# Threshold for movement detection, i.e., axis/axes must meet
# or exceed this value (x% of max/min) in order to register
# as an input. The reason we do this is that controllers can
# be susceptible to stick drift/false trigger values; 0.07~
# is about the max value personal controllers output at rest.
THRESHOLD = 0.07

"""
Implemented:
    Mushroom: (speed boost)
        - Boosts Roomba forward at max speed for a set time.
    Star: (speed boost + invincibility)
        - Increases max speed forwards/backwards for a set time.
        - Grants invulnerability to wobble/front collisions.
"""
ITEMS = ['mushroom', 'star']
