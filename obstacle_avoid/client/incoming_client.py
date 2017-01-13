from threading import Thread
from time import sleep

from base_client import BaseClient
from ..constants import IP_GROUND, IN_PORT
from ..types import Distance, Location, StaticObstacle, MovingObstacle
from ..util import deg_to_rad, meters


class IncomingClient(BaseClient):

    def __init__(self, plane):

        super(IncomingClient, self).__init__(IP_GROUND, IN_PORT)

        self.plane = plane
        self.pinged = False

        self.home_alt = None

        def receiving_thread():

            n_moving = 0

            while not self.closed:

                length = self.receive(4)
                
                if not length:

                    break

                string = self.receive(int(length)).decode('utf-8')

                if not string:

                    break

                type = string[0]
                message = string[1:].split()

                if type == 'i':

                    n_static = int(message.pop(0))
                    n_moving = int(message.pop(0))

                    static_obs = []
                    moving_obs = []

                    self.home_alt = self.plane.home_loc.alt

                    for i in range(0, n_static):

                        lat = deg_to_rad(float(message.pop(0)))
                        lon = deg_to_rad(float(message.pop(0)))
                        height = meters(float(message.pop(0)))
                        radius = meters(float(message.pop(0)))

                        alt = height / 2
                        loc = Location(lat, lon, alt)
                        obs = StaticObstacle(loc, radius, height)

                        static_obs.append(obs)

                    for i in range(0, n_moving):

                        lat = deg_to_rad(float(message.pop(0)))
                        lon = deg_to_rad(float(message.pop(0)))
                        alt = meters(float(message.pop(0))) - self.home_alt
                        radius = meters(float(message.pop(0)))

                        loc = Location(lat, lon, alt)
                        obs = MovingObstacle(loc, radius)

                        moving_obs.append(obs)

                    self.plane.avoid_sys.static_obs = static_obs
                    self.plane.avoid_sys.moving_obs = moving_obs

                    self.plane.avoid_sys.start()

                elif type == 'p':

                    self.pinged = True

                elif type == 'm':

                    obs = self.plane.avoid_sys.moving_obs

                    for i in range(0, n_moving):

                        lat = deg_to_rad(float(message.pop(0)))
                        lon = deg_to_rad(float(message.pop(0)))
                        alt = meters(float(message.pop(0)))

                        loc = Location(lat, lon, alt)
                        obs[i].loc = loc

                    self.plane.avoid_sys.moving_obs = obs

                elif type == 'k':

                    self.plane.avoid_sys.close()

                    self.plane.goto(
                        self.plane.loc.getLocation(Distance(0, 0, -500))
                    )

                elif type == 'o':

                    self.plane.avoid_sys.close()

                elif type == 'c':

                    self.plane.close()

        _receiving_thread = Thread(target=receiving_thread)
        _receiving_thread.start()
