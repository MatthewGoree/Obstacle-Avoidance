"""Handles avoiding obstacles in the way of a plane.

The avoidance state of the obstacle avoidance system is determined as
one of the avoidance states in AvoidState and by determine_state*() in
the module avoid_state. The module avoid_action carries out the action
for the obstacle avoidance system based on the current avoidance state.
"""

from threading import Thread
from time import sleep
from traceback import print_exc
from avoid_action import do_action
from avoid_state import AvoidState, determine_state


class AvoidanceSystem(object):

    """Represents the obstacle avoidance system of a plane as an object.

    The AvoidanceSystem object can be started and stopped by start() and
    stop(), respectively, and can be closed by close().
    """

    def __init__(self, plane):
        """Instantiate an AvoidanceSystem object for a plane.
        
        The obstacle avoidance system cannot start until start() has
        been called.
        """

        self.plane = plane

        self.active = False
        self.closed = False

        self.monitor_count = 0
        self.standby_count = 0

        self.static_obs = []
        self.moving_obs = []

        self.avoid_obs = None

        state_strings = ['CLOSED', 'INACTIVE', 'STANDBY', 'UNSAFE', 'MONITOR',
            'AVOID', 'DODGE', 'LOITER', 'IMMINENT', 'COLLISION']

        def monitoring_thread():
            """Thread for monitoring the plane to avoid obstacles."""
            while not self.active and not self.closed:
                sleep(0.1)

            print 'Starting Obstacle Avoidance....'

            if not self.closed:
                plane_static = plane.to_static()
                self.state = determine_state(plane_static)
            else:
                self.state = AvoidState.CLOSED

            while not self.state == AvoidState.CLOSED:
                try:
                    print 'Current waypoint number: %.0f' % \
                        self.plane.next_wp_number
                    print 'AvoidState = ' + state_strings[self.state]

                    do_action(self.state, plane_static)

                    sleep(0.1)

                    plane_static = plane.to_static()
                    self.state = determine_state(plane_static)

                except:
                    print_exc()

        _monitoring_thread = Thread(target=monitoring_thread)
        _monitoring_thread.start()

    def start(self):
        """Start the obstacle avoidance system.

        The obstacle lists should be set before the start() is called.
        """

        self.active = True

    def stop(self):
        """Stop the obstacle avoidance system.

        The obstacle avoidance can be resumed after start() is called
        again. To close the obstacle avoidance system call close().
        """
        self.active = False

    def close(self):
        """Close the obstacle avoidance system."""
        self.closed = True
