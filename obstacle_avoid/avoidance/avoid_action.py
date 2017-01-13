from math import atan2, pi, sqrt, copysign

from avoid_state import AvoidState
from ..constants import STARTING_ALT, FAR_WP_DIST
from ..types import Distance


def inactive(plane):
    if plane.mode == 'GUIDED' or plane.mode == 'LOITER':
        plane.go_auto()


def standby(plane):
    plane.go_auto()

    plane.avoid_sys.standby_count = plane.avoid_sys.standby_count + 1 if \
        STARTING_ALT <= plane.loc.alt else 0


def unsafe(plane):
    plane.go_auto()


def monitor(plane):
    left_turn_circle = plane.loc.get_location(Distance.from_magnitude(
        plane.turning_radius, plane.heading - pi / 2))

    right_turn_circle = plane.loc.get_location(Distance.from_magnitude(
        plane.turning_radius, plane.heading + pi / 2))

    if plane.mode == 'GUIDED' and plane.avoid_sys.monitor_count < 5 and \
            (left_turn_circle.get_distance(plane.avoid_sys.avoid_obs)
            .get_magnitude_xy() >= plane.turning_radius or
            (right_turn_circle.get_distance(plane.avoid_sys.avoid_obs)
            .get_magnitude_xy() >= plane.turning_radius)):

        plane.avoid_sys.monitor_count += 1
        plane.turn(Distance.get_turn_angle(plane))

    plane.go_auto()


def avoid(plane):
    obs = plane.avoid_sys.avoid_obs
    obs_dist = plane.loc.get_distance(obs.loc, plane.heading)

    wp_obs_dist = obs.loc.get_distance(plane.next_wp.loc, plane.heading)

    R = obs.get_avoid_radius(plane.loc.alt)
    r = plane.turning_radius

    if obs_dist.y > 0:

        if (obs_dist.x >= 0 and wp_obs_dist.x >= 0) or (obs_dist.x <= 0 and
                wp_obs_dist.x <= 0):

            d = sqrt(obs_dist.y ** 2 + (r + abs(obs_dist.x)) ** 2 - (R + r) **
                2)

            turn_angle = -1 * copysign(pi / 2 - atan2(R + r, d) - atan2(
                abs(obs_dist.y), r + abs(obs_dist.x)), obs_dist.x)

        else:

            d = sqrt(obs_dist.y ** 2 + (r - abs(obs_dist.x)) ** 2 - (R + r) **
                2)

            turn_angle = None
            # FIXME get turning angle for cross

        plane.turn(turn_angle)

    else:
        plane.go_auto()


def dodge(plane):
    obs = plane.avoid_sys.avoid_obs
    obs_dist = plane.loc.get_distance(obs.loc, plane.heading)

    turn_angle = -1 * copysign(atan2(obs_dist.y, plane.turning_radius
        + abs(obs_dist.x)), obs_dist.x)

    plane.turn(turn_angle)


def loiter(plane):
    plane.go_loiter()


def imminent(plane):
    plane.go_auto()


def collision(plane):
    plane.go_auto()


actions = {
    AvoidState.INACTIVE:  inactive,
    AvoidState.STANDBY:   standby,
    AvoidState.UNSAFE:    unsafe,
    AvoidState.MONITOR:   monitor,
    AvoidState.DODGE:     dodge,
    AvoidState.LOITER:    loiter,
    AvoidState.IMMINENT:  imminent,
    AvoidState.COLLISION: collision
}


def do_action(state, plane):
    actions[state](plane)
