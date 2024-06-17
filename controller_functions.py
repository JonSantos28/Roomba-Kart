# Author: Jonathan Santos
# File: controller_functions.py
"""
Functions specific to 'controller.py' that affect Roomba movement
in terms of 'wobble,' velocity ranges, and turning radii. All
functions are set up such that you may rebind any of the controls
(e.g., rebind turning direction to the right analog stick by
passing in the value of said stick to the relevant function).
"""
import time
from controller_constants import POLL_BUMPERS_AND_DROPS as POLL_SENSORS


def detect_front_collision(serial_obj, used_invincibility_item,
                           wobble_duration):
    """
    Reads if either Roomba bumper was engaged, shuffles backwards 3x if so.
    User loses control of Roomba for specified duration in seconds.

    From controller_constants: .write() command to poll for sensor packet
    POLL_BUMPERS_AND_DROPS == bytearray([142, 7])

    serial_obj (pySerial obj): device to read from and write to.
    used_invincibility_item (bool): indicates to function whether player used
                                    invulnerability item or not.
    wobble_duration (double): how long the player loses control in seconds.

    returns: nothing
    """
    serial_obj.write(cc.POLL_SENSORS)
    bumper_depressed = serial_obj.read(1)[0] & 0b11

    if bumper_depressed and not used_invincibility_item:
        print("Collision detected, get wobbled on.")
        for x in range(3):
            serial_obj.write(bytearray([137, 255, 176, 0, 50]))
            time.sleep(wobble_duration / 6)
            serial_obj.write(bytearray([137, 255, 176, 255, 205]))
            time.sleep(wobble_duration / 6)


def apply_forward_velocity(given_max_velocity, trigger_value):
    """
    Return forward (positive) velocity based on a max velocity and a given
    trigger's value, or how far it's actuated.

    given_max_velocity (int): maximum velocity possible
    trigger_value (double): actuation value of trigger

    returns (int): forward velocity
    """
    return int((trigger_value + 1) / 2 * given_max_velocity)


def apply_backward_velocity(given_max_velocity, trigger_value):
    """
    Return backward (negative) velocity based on a max velocity and a given
    trigger's value, or how far it's actuated.

    given_max_velocity (int): maximum velocity possible
    trigger_value (double): actuation value of trigger

    returns (-int): backward velocity
    """
    return -(int((trigger_value + 1) / 2 * given_max_velocity))


def apply_turning_radius(stick_x_pos, given_threshold,
                         min_rad, max_rad):
    """
    Returns a list of bytes to be sent to a Roomba to determine turning direction
    and angle based on the horizontal position of a given stick on a controller.

    stick_x_pos (double): a given stick's horizontal position/value.
    given_threshold (double): the maximum value output by the stick at rest.
                              Used in order to mitigate stick drift.
    min_rad (-int): largest possible right turning radius.
    max_rad (int): largest possible left turning radius.

    returns [high, low]: binary list of bytes to be sent to the Roomba.
    """
    if stick_x_pos == 0.0:       # Stick at rest?
        output_bytes = [128, 0]  # move straight
    else:
        # Stick pushed right?
        if stick_x_pos > 0.0:
            rad = int(min_rad * (1 - stick_x_pos + given_threshold))
        # Stick pushed left?
        else:
            rad = int(max_rad * (1 + stick_x_pos + given_threshold))
        # Calculate final radius bytes.
        output_bytes = [(rad // 256) % 256] + [rad % 256]
    return output_bytes
