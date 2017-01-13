from math import tan, sin
from time import sleep

from dronekit import connect, VehicleMode

from avoidance import AvoidanceSystem
from client import IncomingClient, OutgoingClient, TelemetryClient
from constants import ACCEL_GRAV, FAR_WP_DIST
from types import Location, Distance
from util import deg_to_rad


class Plane(object):
    
    def __init__(self, connection_string, baud_rate=115200):
        print 'Connecting Clients....'

        self.avoid_sys = AvoidanceSystem(self)
        self.in_client = IncomingClient(self)
        self.out_client = OutgoingClient(self)
        self.telem_client = TelemetryClient(self)

        self._commands = None

        def dronekit_printer(text):
            print text

            self.out_client.send_messages('d' + text)

        print 'Connecting Plane....'

        self.vehicle = connect(
            connection_string, baud=baud_rate, rate=25,
            status_printer=dronekit_printer, heartbeat_timeout=300
        )

        print 'Waiting until plane is ready....'

        self.vehicle.wait_ready(timeout=300)

        print 'Getting commands....'

        self.update_commands()
        
        self._bank_angle = deg_to_rad(
            self.vehicle.parameters['LIM_ROLL_CD'] / 100
        )
        self._wp_radius = self.vehicle.parameters['WP_RADIUS'] / 100
        self._prev_wp = 0

        self.out_client.start()
        self.telem_client.start()

    def close(self):
        self.avoid_sys.close()
        self.out_client.close()
        self.telem_client.close()
        self.in_client.close()

        sleep(1)

        self.vehicle.close()

    @property
    def airspeed(self):
        return self.vehicle.airspeed

    @property
    def heading(self):
        return deg_to_rad(self.vehicle.heading)

    @property
    def pitch(self):
        return self.vehicle.attitude.pitch

    @property
    def loc(self):
        return Location.from_dronekit_location(
            self.vehicle.location.global_relative_frame
        )
    
    @property
    def turning_radius(self):
        return self.airspeed ** 2 / ACCEL_GRAV / tan(self._bank_angle)
    
    @property
    def mode(self):
        return self.vehicle.mode.name

    @property
    def commands(self):
        return self._commands

    def update_commands(self):
        try:
            commands = self.vehicle.commands
            commands.download()
            commands.wait_ready(timeout=60)

            self._commands = commands
        except:
            print 'Failed to download commands... trying again.'

            self.update_commands()

    @property
    def wp_radius(self):
        return self._wp_radius

    @property
    def home_loc(self):
        home = self.vehicle.home_location

        while not home:
            sleep(1)

            home = self.vehicle.home_location

        return Location.from_dronekit_location(home)

    @property
    def next_wp_number(self):
        next_wp_number = self.commands.next

        if not next_wp_number:
            next_wp_number = self._prev_wp
        else:
            self._prev_wp = next_wp_number

        if next_wp_number < len(self.commands) and next_wp_number:

            next_wp = Location.from_command(self.commands[next_wp_number - 1])

            if self.loc.get_distance(next_wp).get_magnitude() \
                    <= self.wp_radius and not next_wp_number >= \
                    len(self.commands) + 1:
                next_wp_number += 1

        return next_wp_number 

    @property
    def next_wp(self):
        next_wp_number = self.next_wp_number

        try:
            return Location.from_command(self.commands[next_wp_number - 1])
        except:
            return None

    def go_loiter(self):
        if not self.mode == 'LOITER':
            self.vehcile.mode = VehicleMode('LOITER')

    def go_auto(self):
        if not self.mode == 'AUTO':
            self.vehicle.mode = VehicleMode('AUTO')

        self.avoid_sys.monitor_count = 0

    def goto(self, wp):
        self.vehicle.simple_goto(wp.to_dronekit_location())

    def turn(self, angle):
        d = 2 * self.turning_radius * sin(turn_angle / 2)

        bearing_1 = self.heading + turn_angle / 2
        bearing_2 = self.heading + turn_angle

        dist_1 = Distance.from_magnitude(d, bearing_1)
        dist_2 = Distance.from_magnitude(FAR_WP_DIST, bearing_2)
    
        wp_dist = dist_1.add(dist_2)
        wp = self.loc.get_location(wp_dist)

        self.goto(wp)

        self.avoid_sys.monitor_count = 0


    def to_static(self):
        return PlaneStatic(self)


class PlaneStatic(Plane):

    def __init__(self, plane):

        self._airspeed = plane.airspeed
        self._heading = plane.heading
        self._pitch = plane.pitch
        self._loc = plane.loc
        self._turning_radius = plane.turning_radius
        self._mode = plane.mode
        self._commands = plane.commands
        self._wp_radius = plane.wp_radius
        self._next_wp_number = plane.next_wp_number
        self._next_wp = plane.next_wp

        self.avoid_sys = plane.avoid_sys
        self.in_client = plane.in_client
        self.out_client = plane.out_client
        self.vehicle = plane.vehicle

    @property
    def airspeed(self):
        return self._airspeed

    @property
    def heading(self):
        return self._heading
    
    @property
    def pitch(self):
        return self._pitch

    @property
    def loc(self):
        return self._loc

    @property
    def turning_radius(self):
        return self._turning_radius

    @property
    def mode(self):
        return self._mode

    @property
    def commands(self):
        return self._commands
    
    @property
    def wp_radius(self):
        return self._wp_radius

    @property
    def next_wp_number(self):
        return self._next_wp_number

    @property
    def next_wp(self):
        return self._next_wp
    
