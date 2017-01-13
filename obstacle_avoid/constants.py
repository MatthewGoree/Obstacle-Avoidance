"""Contains the constants used throughout the code for the
interopability and obstacle avoidance onboard the plane.
"""

# Constants for the ip adresses of the APM and of the ground station as
# well as the ports used for the interopability.
APM_CONNECTION_STRING = '127.0.0.1:14551'
IP_GROUND = '192.168.0.90'
IN_PORT = 25001
OUT_PORT_1 = 25000
OUT_PORT_2 = 25002

# Constants for obstacle avoidance.
STARTING_ALT = 50
SAFE_ALT_LOWER = 25
SAFE_ALT_UPPER = 250
AVOID_DIST_STAT = 40
AVOID_DIST_MOV = 45
FAR_WP_DIST = 1000
MOV_LOITER_DIST = 75

# Other Constants
EARTH_RADIUS = 6378137
EARTH_ECCEN = 0.0818191908
ACCEL_GRAV = 9.80665
