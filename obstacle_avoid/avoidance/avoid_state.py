"""Handles defining and determining the avoidance states.

The obstacle avoidance system of a plane uses these avoidance states so
that it can make the correct action given the avoidance state.
"""

from math import sqrt

from ..constants import SAFE_ALT_LOWER, SAFE_ALT_UPPER, MOV_LOITER_DIST


class AvoidState(object):

    """Lists the possible avoidance states that the obstacle avoidance
    system could be in as constants.

    The following lists the cases with a corresponding description.

        AvoidState.CLOSED: Used when the obstacle avoidance system is
            closed or will close immediately.
        AvoidState.INACTIVE: Used when the plane is not in autonomous
            flight or when the obstacle avoidance system has been
            temporarily stopped.
        AvoidState.STANDBY: Used when the plane has not yet taken off or
            when the plane has not reached sufficient altitude for the
            obstacle avoidance system to active
            after take off.
        AvoidState.UNSAFE: Used when the plane's altitude is not between
            the safe altitude limits defined for the obstacle avoid
            system after the obstacle avoidance
            system as been activated after take off.
        AvoidState.MONITOR: Used when the obstacle avoidance system is
            activated but does
            not need to avoid an obstacle at the given time.
        AvoidState.AVOID: Used when the obstacle avoidance system needs
            to avoid an obstacle that is in the way of the next waypoint
            in advance while the plane is not within the obstacles's
            avoidance radius.
        AvoidState.DODGE: Used when the obstacle avoidance system needs
            to avoid an obstacle that is in the way of the next waypoint
            while the plane is within the obstacle's avoidance radius
            but not inside of the obstacle and can dodge the it without
            hitting it.
        AvoidState.LOITER: Used when the obstacle avoidance system
            detects that the next waypoint is within a moving obstacle's
            avoidance radius and the plane is closer than the defined
            distance to have to loiter.
        AvoidState.IMMINENT: Used when the plane will collide with an
            obstacle and cannot dodge it.
        AvoidState.COLLISION: Used when the plane is found to be inside
            an obstacle.

    To determine the state of the obstacle avoidance system use
    determine_state(plane).
    """

    CLOSED    = 0
    INACTIVE  = 1
    STANDBY   = 2
    UNSAFE    = 3
    MONITOR   = 4
    AVOID     = 5
    DODGE     = 6
    LOITER    = 7
    IMMINENT  = 8
    COLLISION = 9


def determine_state(plane):
    """Determine the state of the obstacle avoidance system of plane and
    return a constant as defined in AvoidState.
    """

    avoid_sys = plane.avoid_sys

    # Return AvoidState.CLOSED if the plane is closed or will close
    # immediately.
    if avoid_sys.closed:
        return AvoidState.CLOSED

    # Return AvoidState.INACTIVE if the plane is not in autonomous
    # flight or if the plane's obstacle avoidance system has been
    # temporarily stopped.

    if not plane.next_wp:
        'Did not get a next waypoint.'

    if not avoid_sys.active or not (plane.mode == 'AUTO' or plane.mode
            == 'GUIDED' or plane.mode == 'LOITER') or not plane.next_wp:
        return AvoidState.INACTIVE

    # Return AvoidState.STANDBY if the plane has not been above the
    # defined starting height for 3 consecutive times.
    if avoid_sys.standby_count < 3:
        return AvoidState.STANDBY

    # Return AvoidState.UNSAFE if the plane is not in within the safe
    # altitude limits defined.
    if plane.loc.alt < SAFE_ALT_LOWER or plane.loc.alt > SAFE_ALT_UPPER:
        return AvoidState.UNSAFE

    all_obs = avoid_sys.static_obs + avoid_sys.moving_obs

    for obs in all_obs:
        
        # Return AvoidState.COLLISION if the plane is inside of an
        # obstacle. 
        if obs.is_loc_inside(plane.loc):
            return AvoidState.COLLISION

        obs_dist = plane.loc.get_distance(obs.loc, plane.heading)

        # Determine if the plane is inside the avoidance radius of an
        # obstacle and the obstacle is in front of the plane.
        if obs.is_loc_in_avoid_radius(plane.loc) and obs_dist > 0:

            # Return AvoidState.IMMINENT if the plane cannot dodge the
            # obstacle in direction away from the obstacle.
            if obs.get_cross_sectional_radius(plane.loc.alt) > sqrt(
                    (plane.turning_radius + abs(obs_dist.x)) ** 2 + obs_dist.y
                    ** 2) - plane.turning_radius:
                return AvoidState.IMMINENT

            # Return AvoidState.DODGE otherwise.
            avoid_sys.avoid_obs = obs
            return AvoidState.DODGE

    for obs in all_obs:

        # Return AvoidState.AVOID if obs is in the way of the next
        # waypoint.
        if not plane.mode == 'LOITER' and obs.is_in_way(plane):
            return AvoidState.AVOID

    for obs in avoid_sys.moving_obs:

        # Return AvoidState.LOITER if obs is over the next waypoint.
        if obs.is_in_next_wp(plane) and obs_dist.get_magnitude_xy() < \
                MOV_LOITER_DIST:
            avoid_sys.avoid_obs = obs
            return AvoidState.LOITER

    # Return AvoidState.MONITOR if the plane is found to not be in any
    # other avoidance states.
    return AvoidState.MONITOR
