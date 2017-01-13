from threading import Thread
from time import sleep, time

from base_client import BaseClient
from ..constants import IP_GROUND, OUT_PORT_2
from ..util import rad_to_deg, feet, knots


class TelemetryClient(BaseClient):

    def __init__(self, plane):

        super(TelemetryClient, self).__init__(
            IP_GROUND, OUT_PORT_2, sending=True
        )

        self.plane = plane
        self.start_time = None

        def telemetry_thread():

            while not self.closed:

                send_time = self.time
                next_wp = self.plane.next_wp_number
                loc = self.plane.loc
                lon = rad_to_deg(loc.lon)
                lat = rad_to_deg(loc.lat)
                alt = feet(loc.alt)
                heading = rad_to_deg(self.plane.heading)
                pitch = rad_to_deg(self.plane.pitch)
                airspeed = knots(self.plane.airspeed)

                telemetry = '%.4f %.0f %.7f %.7f %.3f %.3f %.3f %.2f' % (
                    send_time, next_wp, lat, lon, alt, heading, pitch, airspeed
                )

                self.send_messages('t' + telemetry)

                sleep(0.05)

        def starting_thread():

            while not self.start_time:

                sleep(0.1)

            _telemetry_thread = Thread(target=telemetry_thread)
            _telemetry_thread.start()

        _starting_thread = Thread(target=starting_thread)
        _starting_thread.start()

    def start(self):

        self.start_time = time()

    @property
    def time(self):
    
        return time() - self.start_time
